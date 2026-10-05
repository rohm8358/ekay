#!/usr/bin/env python3
"""Install what Kali can provide, then create PATH shims so all 234 binaries resolve."""

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

from ekay.aliases import BINARY_ALIASES
from ekay.catalog import CATALOG

APT_PACKAGES = [
    "apktool", "adb", "jadx", "bettercap", "chisel", "gitleaks", "yara", "osquery",
    "trufflehog", "bloodhound", "cupp", "hcxdumptool", "hcxtools", "wifiphisher",
    "testssl.sh", "zaproxy", "awscli", "kubectl", "helm", "opa", "grype",
    "golang-go", "python3-impacket", "seclists", "feroxbuster", "dirsearch",
    "nuclei", "httpx-toolkit", "subfinder", "amass", "naabu",
]

PIP_PACKAGES = [
    "holehe", "maigret", "instaloader", "socialscan", "objection", "frida-tools",
    "schemathesis", "httpie", "arjun", "toutatis", "snscrape", "roadtx",
    "o365spray", "apkleaks", "quark-engine", "mvt", "ropgadget", "pwntools",
    "scoutsuite", "pacu", "waymore", "graphw00f",
]

GO_INSTALLS = [
    "github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
    "github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest",
    "github.com/projectdiscovery/notify/cmd/notify@latest",
    "github.com/projectdiscovery/katana/cmd/katana@latest",
    "github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
    "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
    "github.com/ffuf/ffuf/v2@latest",
    "github.com/tomnomnom/waybackurls@latest",
    "github.com/lc/gau/v2/cmd/gau@latest",
    "github.com/hakluke/hakrawler@latest",
    "github.com/anchore/grype@latest",
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=False)


def which_any(names: list[str]) -> str | None:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
        local = BIN / n
        if local.is_file() and os.access(local, os.X_OK):
            return str(local)
    return None


def write_shim(name: str, target: str | None = None, note: str = "") -> None:
    path = BIN / name
    if path.exists():
        return
    if target:
        path.write_text(
            f"#!/usr/bin/env bash\nexec '{target}' \"$@\"\n",
            encoding="utf-8",
        )
    else:
        msg = note or f"{name} is not installed on this host. Run: sudo ./scripts/install_kali.sh"
        path.write_text(
            "#!/usr/bin/env bash\n"
            f"echo '[ekay-shim] {msg}' >&2\n"
            "exit 127\n",
            encoding="utf-8",
        )
    path.chmod(0o755)
    print(f"shim {name} -> {target or 'stub'}")


def main() -> int:
    os.environ["PATH"] = f"{BIN}:{os.environ.get('PATH','')}"

    if shutil.which("apt-get") and os.geteuid() == 0:
        run(["apt-get", "update"])
        run(["apt-get", "install", "-y", *APT_PACKAGES])
    else:
        print("[!] not root — skipping apt (re-run with sudo for full install)")
        # still try sudo noninteractive
        if shutil.which("sudo"):
            run(["sudo", "apt-get", "update"])
            run(["sudo", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-y", *APT_PACKAGES])

    pip = shutil.which("pip3") or shutil.which("pip")
    if pip:
        run([pip, "install", "--break-system-packages", *PIP_PACKAGES])

    if shutil.which("go"):
        gopath = os.environ.get("GOPATH") or str(Path.home() / "go")
        os.environ["PATH"] = f"{gopath}/bin:{os.environ['PATH']}"
        for pkg in GO_INSTALLS:
            run(["go", "install", "-v", pkg])

    # Map common pip entrypoints into ekay-bin
    pip_bins = {
        "instaloader": "instaloader",
        "maigret": "maigret",
        "holehe": "holehe",
        "socialscan": "socialscan",
        "frida": "frida",
        "frida-ps": "frida-ps",
        "objection": "objection",
        "schemathesis": "schemathesis",
        "http": "httpie",
        "ROPgadget": "ROPgadget",
        "scout": "scout",
        "pacu": "pacu",
        "waymore": "waymore",
        "apkleaks": "apkleaks",
        "quark": "quark",
        "mvt-android": "mvt-android",
        "mvt-ios": "mvt-ios",
        "jwt_tool": "jwt_tool",
    }
    for dest, src in pip_bins.items():
        real = shutil.which(src) or shutil.which(dest)
        if real:
            write_shim(dest, real)

    # Impacket wrappers
    for dest, src in {
        "secretsdump.py": "impacket-secretsdump",
        "GetNPUsers.py": "impacket-GetNPUsers",
        "smbclient.py": "impacket-smbclient",
        "psexec.py": "impacket-psexec",
        "crackmapexec": "nxc",
    }.items():
        real = shutil.which(src)
        if real:
            write_shim(dest, real)

    # Ensure EVERY catalog binary resolves via shim (stub if needed)
    for spec in CATALOG:
        names = [spec.binary, *BINARY_ALIASES.get(spec.binary, ())]
        existing = which_any(list(names))
        if existing:
            # also ensure catalog's exact binary name exists in ekay-bin
            if not (BIN / spec.binary).exists() and Path(existing).name != spec.binary:
                write_shim(spec.binary, existing)
            elif not shutil.which(spec.binary) and not (BIN / spec.binary).exists():
                write_shim(spec.binary, existing)
        else:
            write_shim(
                spec.binary,
                None,
                note=f"{spec.name}: install manually or via apt/pip; binary '{spec.binary}' missing",
            )

    print(f"[ekay] ekay-bin has {len(list(BIN.iterdir()))} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
