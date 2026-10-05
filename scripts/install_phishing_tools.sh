#!/usr/bin/env bash
# Install / wire the 9 SE (phishing-sim) catalog tools so status=ready.
# Authorized lab use only. No root required (user-local tools/ + ekay-bin shims).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$ROOT/ekay-bin"
TOOLS="$ROOT/tools"
mkdir -p "$BIN" "$TOOLS"
export PATH="$BIN:$PATH:${HOME}/go/bin:${HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin"

write_exec_shim() {
  local name="$1" target="$2"
  cat >"$BIN/$name" <<EOF
#!/usr/bin/env bash
exec '$target' "\$@"
EOF
  chmod 755 "$BIN/$name"
  echo "[ok] shim $name -> $target"
}

write_cwd_shim() {
  local name="$1" dir="$2" cmd="$3"
  cat >"$BIN/$name" <<EOF
#!/usr/bin/env bash
cd '$dir' || exit 1
exec $cmd "\$@"
EOF
  chmod 755 "$BIN/$name"
  echo "[ok] shim $name -> (cd $dir && $cmd)"
}

echo "==> setoolkit (point at real SET entry, not relative-exec wrapper)"
if [[ -x /usr/share/set/setoolkit ]]; then
  write_exec_shim setoolkit /usr/share/set/setoolkit
elif [[ -x /usr/bin/setoolkit ]]; then
  write_exec_shim setoolkit /usr/bin/setoolkit
else
  echo "[!] setoolkit package missing (apt install set)" >&2
fi

echo "==> gophish (prefer real ELF over deprecated kali wrapper)"
if [[ -x /usr/lib/gophish/gophish ]]; then
  write_exec_shim gophish /usr/lib/gophish/gophish
elif [[ -x /usr/bin/gophish-start ]]; then
  write_exec_shim gophish /usr/bin/gophish-start
fi

echo "==> swaks"
if [[ -x /usr/bin/swaks ]]; then
  write_exec_shim swaks /usr/bin/swaks
fi

echo "==> evilginx2 (extract Kali .deb if needed)"
EVIL_DIR="$TOOLS/evilginx2"
EVIL_BIN=""
if command -v evilginx2 >/dev/null 2>&1 && [[ "$(command -v evilginx2)" != "$BIN/"* ]]; then
  EVIL_BIN="$(command -v evilginx2)"
elif [[ -x /usr/bin/evilginx2 ]]; then
  EVIL_BIN=/usr/bin/evilginx2
elif [[ -x "$TOOLS/evilginx2-deb/usr/bin/evilginx2" ]]; then
  EVIL_BIN="$TOOLS/evilginx2-deb/usr/bin/evilginx2"
else
  mkdir -p "$EVIL_DIR"
  tmp="$(mktemp -d)"
  (cd "$tmp" && apt-get download evilginx2)
  dpkg-deb -x "$tmp"/evilginx2_*.deb "$TOOLS/evilginx2-deb"
  EVIL_BIN="$TOOLS/evilginx2-deb/usr/bin/evilginx2"
  rm -rf "$tmp"
fi
# Prefer phishlets next to binary when using extracted deb
if [[ -x "$EVIL_BIN" ]]; then
  PHISHLETS="$TOOLS/evilginx2-deb/usr/share/evilginx2/phishlets"
  REDIRS="$TOOLS/evilginx2-deb/usr/share/evilginx2/redirectors"
  if [[ -d "$PHISHLETS" ]]; then
    cat >"$BIN/evilginx" <<EOF
#!/usr/bin/env bash
exec '$EVIL_BIN' -p '$PHISHLETS' -t '$REDIRS' "\$@"
EOF
    chmod 755 "$BIN/evilginx"
    echo "[ok] shim evilginx -> $EVIL_BIN (with phishlets)"
  else
    write_exec_shim evilginx "$EVIL_BIN"
  fi
fi

echo "==> modlishka (build from source)"
MOD_DIR="$TOOLS/Modlishka"
if [[ ! -x "$MOD_DIR/modlishka" ]]; then
  if [[ ! -d "$MOD_DIR/.git" ]]; then
    git clone --depth 1 https://github.com/drk1wi/Modlishka.git "$MOD_DIR"
  fi
  (cd "$MOD_DIR" && go build -o modlishka .)
fi
write_exec_shim modlishka "$MOD_DIR/modlishka"

echo "==> zphisher"
ZPH_DIR="$TOOLS/zphisher"
if [[ ! -d "$ZPH_DIR/.git" ]]; then
  git clone --depth 1 https://github.com/htr-tech/zphisher.git "$ZPH_DIR"
fi
chmod +x "$ZPH_DIR/zphisher.sh" 2>/dev/null || true
write_cwd_shim zphisher "$ZPH_DIR" "bash ./zphisher.sh"

echo "==> socialfish"
SF_DIR="$TOOLS/SocialFish"
if [[ ! -d "$SF_DIR/.git" ]]; then
  git clone --depth 1 https://github.com/UndeadSec/SocialFish.git "$SF_DIR"
fi
if [[ ! -x "$SF_DIR/.venv/bin/python" ]]; then
  python3 -m venv "$SF_DIR/.venv"
  "$SF_DIR/.venv/bin/pip" install -U pip wheel
  if [[ -f "$SF_DIR/requirements.txt" ]]; then
    "$SF_DIR/.venv/bin/pip" install -r "$SF_DIR/requirements.txt" || true
  fi
fi
# SocialFish entry is typically SocialFish.py
ENTRY=""
for cand in SocialFish.py socialfish.py app.py; do
  if [[ -f "$SF_DIR/$cand" ]]; then ENTRY=$cand; break; fi
done
if [[ -n "$ENTRY" ]]; then
  write_cwd_shim socialfish "$SF_DIR" "'$SF_DIR/.venv/bin/python' './$ENTRY'"
else
  echo "[!] SocialFish entry script not found" >&2
fi

echo "==> hiddeneye (HiddenEyeReborn)"
HE_DIR="$TOOLS/HiddenEye"
if [[ ! -d "$HE_DIR/.git" ]]; then
  if git clone --depth 1 https://github.com/Open-Security-Group-OSG/HiddenEyeReborn.git "$HE_DIR"; then
    :
  elif git clone --depth 1 https://github.com/Morsmalleo/HiddenEye.git "$HE_DIR"; then
    :
  else
    echo "[!] could not clone HiddenEye" >&2
  fi
fi
if [[ -d "$HE_DIR" ]]; then
  if [[ ! -x "$HE_DIR/.venv/bin/python" ]]; then
    python3 -m venv "$HE_DIR/.venv"
    "$HE_DIR/.venv/bin/pip" install -U pip wheel
    if [[ -f "$HE_DIR/requirements.txt" ]]; then
      "$HE_DIR/.venv/bin/pip" install -r "$HE_DIR/requirements.txt" || true
    fi
    # HiddenEyeReborn is often pip-installable as a package
    if [[ -f "$HE_DIR/pyproject.toml" || -f "$HE_DIR/setup.py" ]]; then
      "$HE_DIR/.venv/bin/pip" install -e "$HE_DIR" || true
    fi
  fi
  if "$HE_DIR/.venv/bin/python" -c "import hiddeneye" 2>/dev/null || \
     "$HE_DIR/.venv/bin/python" -c "import HiddenEye" 2>/dev/null; then
    cat >"$BIN/hiddeneye" <<EOF
#!/usr/bin/env bash
exec '$HE_DIR/.venv/bin/python' -m hiddeneye "\$@"
EOF
    chmod 755 "$BIN/hiddeneye"
    echo "[ok] shim hiddeneye -> python -m hiddeneye"
  else
    ENTRY=""
    for cand in HiddenEye.py hiddeneye.py main.py; do
      if [[ -f "$HE_DIR/$cand" ]]; then ENTRY=$cand; break; fi
    done
    if [[ -z "$ENTRY" ]]; then
      ENTRY="$(find "$HE_DIR" -maxdepth 2 -type f \( -name 'HiddenEye.py' -o -name 'hiddeneye.py' -o -name 'main.py' \) | head -1)"
    fi
    if [[ -n "$ENTRY" ]]; then
      write_cwd_shim hiddeneye "$(dirname "$ENTRY")" "'$HE_DIR/.venv/bin/python' '$(basename "$ENTRY")'"
    else
      # last resort: CLI console script
      if [[ -x "$HE_DIR/.venv/bin/hiddeneye" ]]; then
        write_exec_shim hiddeneye "$HE_DIR/.venv/bin/hiddeneye"
      elif [[ -x "$HE_DIR/.venv/bin/hiddeneye-reborn" ]]; then
        write_exec_shim hiddeneye "$HE_DIR/.venv/bin/hiddeneye-reborn"
      else
        echo "[!] HiddenEye entry not found — listing:" >&2
        ls -la "$HE_DIR" | head -30 >&2
      fi
    fi
  fi
fi

echo "==> king-phisher"
KP_DIR="$TOOLS/king-phisher"
if [[ ! -d "$KP_DIR/.git" ]]; then
  git clone --depth 1 https://github.com/securestate/king-phisher.git "$KP_DIR"
fi
if [[ ! -x "$KP_DIR/.venv/bin/python" ]]; then
  python3 -m venv "$KP_DIR/.venv"
  "$KP_DIR/.venv/bin/pip" install -U pip wheel setuptools
  # Minimal deps so CLI can at least start / show help; full server needs more system packages
  if [[ -f "$KP_DIR/requirements.txt" ]]; then
    "$KP_DIR/.venv/bin/pip" install -r "$KP_DIR/requirements.txt" || \
      "$KP_DIR/.venv/bin/pip" install advancedhttpserver alembic boltasyncio geoip2 \
        jinja2 markdown paramiko pluginbase requests smoke-zephyr sqlalchemy \
        python-dateutil pyotp qrcode || true
  fi
fi
# king-phisher entry points
if [[ -f "$KP_DIR/KingPhisher" ]]; then
  write_cwd_shim king-phisher "$KP_DIR" "'$KP_DIR/.venv/bin/python' './KingPhisher'"
elif [[ -f "$KP_DIR/king_phisher/server.py" ]]; then
  cat >"$BIN/king-phisher" <<EOF
#!/usr/bin/env bash
cd '$KP_DIR' || exit 1
export PYTHONPATH='$KP_DIR\${PYTHONPATH:+:\$PYTHONPATH}'
exec '$KP_DIR/.venv/bin/python' -m king_phisher.server "\$@"
EOF
  chmod 755 "$BIN/king-phisher"
  echo "[ok] shim king-phisher -> python -m king_phisher.server"
elif [[ -f "$KP_DIR/tools/king_phisher" ]]; then
  write_cwd_shim king-phisher "$KP_DIR" "'$KP_DIR/.venv/bin/python' './tools/king_phisher'"
else
  echo "[!] king-phisher entry not found" >&2
  ls -la "$KP_DIR" | head -40 >&2
fi

echo "==> done. Verifying SE family..."
cd "$ROOT"
EKAY_TOOL_BIN="$BIN" PATH="$BIN:$PATH" python3 - <<'PY'
import os, sys
sys.path.insert(0, ".")
from ekay.scope import ScopeGuard
from ekay.runner import ToolRunner
from ekay.status import catalog_report
runner = ToolRunner(ScopeGuard(["*"]), allow_intrusive=True)
rep = catalog_report(runner)
se = [t for t in rep["tools"] if t["family"] == "se"]
for t in se:
    print(f"{t['status']:8} {t['name']}")
ready = sum(1 for t in se if t["status"] == "ready")
print(f"SE ready {ready}/{len(se)}")
sys.exit(0 if ready == len(se) else 1)
PY
