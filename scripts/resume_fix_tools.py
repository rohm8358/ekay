#!/usr/bin/env python3
"""Resume: rebuild wrappers + install remaining missing packages (disk-safe)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BIN = ROOT / "ekay-bin"
BIN.mkdir(exist_ok=True)
CACHE = ROOT / ".tool-cache"
CACHE.mkdir(exist_ok=True)
os.environ["GOTMPDIR"] = str(CACHE / "gotmp")
os.environ["GOCACHE"] = str(CACHE / "gocache")
os.environ["TMPDIR"] = str(CACHE / "tmp")
(CACHE / "gotmp").mkdir(exist_ok=True)
(CACHE / "gocache").mkdir(exist_ok=True)
(CACHE / "tmp").mkdir(exist_ok=True)

HOME = Path.home()
os.environ["PATH"] = os.pathsep.join(
    [
        str(BIN),
        str(ROOT / "ekay-env" / "bin"),
        str(HOME / "go" / "bin"),
        str(HOME / ".local" / "bin"),
        "/usr/local/bin",
        "/usr/sbin",
        "/sbin",
        "/usr/bin",
        "/bin",
        os.environ.get("PATH", ""),
    ]
)
os.environ["EKAY_TOOL_BIN"] = str(BIN)

from ekay.aliases import BINARY_ALIASES  # noqa: E402
from ekay.catalog import CATALOG  # noqa: E402
from ekay.runner import ToolRunner  # noqa: E402
from ekay.scope import ScopeGuard  # noqa: E402
from ekay.status import catalog_report, is_real_tool  # noqa: E402

APT = [
    "arp-scan", "responder", "john", "yara", "osquery", "bettercap", "chisel",
    "gitleaks", "trufflehog", "kubectl", "helm", "awscli", "grype", "opa",
    "apktool", "adb", "jadx", "cupp", "wifite", "hcxdumptool", "hcxtools",
    "wifiphisher", "testssl.sh", "zaproxy", "aircrack-ng", "bloodhound",
    "enum4linux-ng", "foremost", "steghide", "gdb", "python3-impacket",
]
PIP = [
    "holehe", "maigret", "instaloader", "socialscan", "objection", "frida-tools",
    "schemathesis", "httpie", "arjun", "toutatis", "snscrape", "roadtx",
    "o365spray", "apkleaks", "quark-engine", "mvt", "ropgadget", "pwntools",
    "scoutsuite", "pacu", "waymore", "graphw00f", "ldapdomaindump", "certipy-ad",
    "coercer", "mitm6", "jwt_tool", "checkov", "prowler",
]
GO = [
    "github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
    "github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest",
    "github.com/projectdiscovery/notify/cmd/notify@latest",
    "github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest",
    "github.com/ropnop/kerbrute@latest",
    "github.com/ffuf/ffuf/v2@latest",
]


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=False).returncode


def resolve(names: list[str]) -> str | None:
    for n in names:
        for base in (
            HOME / "go" / "bin",
            HOME / ".local" / "bin",
            Path("/usr/sbin"),
            Path("/usr/bin"),
            Path("/usr/local/bin"),
            BIN,
        ):
            cand = base / n
            if cand.is_file() and os.access(cand, os.X_OK) and is_real_tool(str(cand)):
                # Prefer non-wrapper real binaries over ekay-bin wrappers when searching
                if base == BIN:
                    continue
                return str(cand)
        p = shutil.which(n)
        if p and is_real_tool(p) and not str(p).startswith(str(BIN)):
            return p
        if p and is_real_tool(p):
            return p
    return None


def write_wrapper(name: str, target: str) -> None:
    path = BIN / name
    path.write_text(f"#!/usr/bin/env bash\nexec '{target}' \"$@\"\n", encoding="utf-8")
    path.chmod(0o755)


def purge_broken_wrappers() -> None:
    n = 0
    for path in list(BIN.iterdir()):
        if path.is_file() and not is_real_tool(str(path)):
            path.unlink(missing_ok=True)
            n += 1
    # also rewrite wrappers whose target is wrong/missing
    for path in list(BIN.iterdir()):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "exec '" not in text:
            continue
        # force rebuild later
    print(f"[ekay] purged {n} broken wrappers")


def rebuild_all_wrappers() -> None:
    for spec in CATALOG:
        names = [spec.binary, *BINARY_ALIASES.get(spec.binary, ())]
        # common aliases
        extra = {
            "gau": ["gau"],
            "anew": ["anew"],
            "naabu": ["naabu"],
            "john": ["john"],
            "airmon-ng": ["airmon-ng"],
            "testssl.sh": ["testssl.sh", "testssl"],
            "zap.sh": ["zap.sh", "zaproxy", "zap"],
            "jwt_tool": ["jwt_tool", "jwt-tool"],
            "scout": ["scout"],
            "kr": ["kr", "kiterunner"],
            "osqueryi": ["osqueryi", "osquery"],
            "vol": ["vol", "volatility3"],
            "ROPgadget": ["ROPgadget", "ropgadget"],
            "certipy": ["certipy", "certipy-ad"],
            "ntlmrelayx.py": ["impacket-ntlmrelayx", "ntlmrelayx"],
            "secretsdump.py": ["impacket-secretsdump"],
            "GetNPUsers.py": ["impacket-GetNPUsers"],
            "smbclient.py": ["impacket-smbclient"],
            "psexec.py": ["impacket-psexec"],
            "http": ["http", "httpie"],
            "pspy64": ["pspy64", "pspy"],
            "linpeas.sh": ["linpeas.sh", "linpeas"],
        }.get(spec.binary, [])
        target = resolve(list(dict.fromkeys([*names, *extra])))
        if not target:
            continue
        dest = BIN / spec.binary
        # Always point catalog name at the real resolved binary
        if Path(target).resolve() != dest.resolve():
            write_wrapper(spec.binary, target)


def install() -> None:
    if shutil.which("sudo"):
        run(["sudo", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-y", *APT])
    pip = ROOT / "ekay-env" / "bin" / "pip3"
    if pip.is_file():
        run([str(pip), "install", "-U", *PIP])
    else:
        run(["pip3", "install", "--break-system-packages", "-U", *PIP])
    # go installs only if missing
    for pkg in GO:
        name = pkg.rsplit("/", 1)[-1].split("@")[0]
        if resolve([name]):
            print(f"[skip go] {name} already present")
            continue
        run(["go", "install", "-v", pkg])
    # downloads
    pspy = BIN / "pspy64"
    if not pspy.is_file():
        url = "https://github.com/DominicBreuker/pspy/releases/download/v1.2.1/pspy64"
        dest = CACHE / "pspy64"
        if run(["curl", "-fsSL", "-o", str(dest), url]) == 0:
            dest.chmod(0o755)
            shutil.copy2(dest, pspy)
    linpeas = BIN / "linpeas.sh"
    if not resolve(["linpeas.sh", "linpeas"]):
        url = "https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh"
        dest = CACHE / "linpeas.sh"
        if run(["curl", "-fsSL", "-L", "-o", str(dest), url]) == 0:
            dest.chmod(0o755)
            shutil.copy2(dest, linpeas)
    winpeas = BIN / "winPEASx64.exe"
    if not winpeas.is_file():
        url = "https://github.com/peass-ng/PEASS-ng/releases/latest/download/winPEASx64.exe"
        dest = CACHE / "winPEASx64.exe"
        if run(["curl", "-fsSL", "-L", "-o", str(dest), url]) == 0:
            shutil.copy2(dest, winpeas)
            winpeas.chmod(0o755)
    if not resolve(["pretender"]):
        run(["go", "install", "-v", "github.com/RedTeamPentesting/pretender@latest"])


def main() -> int:
    purge_broken_wrappers()
    install()
    rebuild_all_wrappers()
    r = catalog_report(ToolRunner(ScopeGuard(["127.0.0.1"]), allow_intrusive=True))
    print(
        __import__("json").dumps(
            {k: r[k] for k in ("catalog", "ready", "stub", "missing", "gated")},
            indent=2,
        )
    )
    left = [t for t in r["tools"] if t["status"] != "ready"]
    print(f"still not ready: {len(left)}")
    for t in left:
        print(f"  {t['status']:8} {t['name']:28} bin={t['binary']}")
    return 0 if not left else 1


if __name__ == "__main__":
    raise SystemExit(main())
