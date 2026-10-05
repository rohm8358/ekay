#!/usr/bin/env python3
"""Make as many EKay catalog tools genuinely runnable as Kali allows.

1) Remove broken ekay-bin placeholder shims (they hide real PATH tools)
2) apt / pip / go install for stub+missing catalog entries
3) Recreate ONLY real exec wrappers for binary name aliases
"""

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

# Prefer project bin, then user go/pip, then system
HOME = Path.home()
PATH_PREFIX = [
    str(BIN),
    str(HOME / "go" / "bin"),
    str(HOME / ".local" / "bin"),
    "/usr/local/bin",
    "/usr/bin",
]
os.environ["PATH"] = os.pathsep.join(PATH_PREFIX + os.environ.get("PATH", "").split(os.pathsep))
os.environ.setdefault("GOPATH", str(HOME / "go"))

from ekay.aliases import BINARY_ALIASES  # noqa: E402
from ekay.catalog import CATALOG  # noqa: E402
from ekay.runner import ToolRunner  # noqa: E402
from ekay.scope import ScopeGuard  # noqa: E402
from ekay.status import catalog_report, is_real_tool  # noqa: E402

APT = [
    # core / network / web
    "nmap", "masscan", "gobuster", "ffuf", "nikto", "sqlmap", "hydra", "john", "hashcat",
    "medusa", "whatweb", "wafw00f", "smbmap", "enum4linux", "enum4linux-ng", "nbtscan",
    "netexec", "responder", "arp-scan", "dnsenum", "fierce", "theharvester", "amass",
    "subfinder", "feroxbuster", "dirsearch", "dirb", "wapiti", "seclists",
    # binary / forensics
    "binwalk", "exiftool", "foremost", "steghide", "gdb", "radare2", "checksec",
    "yara", "osquery", "sleuthkit", "testdisk", "scalpel", "bulk-extractor",
    # wireless
    "aircrack-ng", "wifite", "kismet", "bettercap", "reaver", "bully",
    "hcxdumptool", "hcxtools", "wifiphisher",
    # mobile / cloud helpers
    "apktool", "adb", "jadx", "bloodhound",
    "kubectl", "helm", "awscli", "azure-cli", "google-cloud-cli",
    "trivy", "grype", "opa", "gitleaks", "trufflehog",
    # misc
    "socat", "proxychains4", "chisel", "cupp", "cewl", "crunch", "swaks",
    "testssl.sh", "zaproxy", "golang-go", "python3-impacket", "python3-pip",
    "jq", "curl", "wget", "git", "unzip", "default-jre-headless",
]

PIP = [
    "holehe", "maigret", "instaloader", "socialscan", "objection", "frida-tools",
    "schemathesis", "httpie", "arjun", "toutatis", "snscrape", "roadtx",
    "o365spray", "apkleaks", "quark-engine", "mvt", "ropgadget", "pwntools",
    "scoutsuite", "pacu", "waymore", "graphw00f", "jwt_tool", "shodan",
    "ldapdomaindump", "bloodhound", "certipy-ad", "coercer", "mitm6",
    "androguard", "drozer", "semgrep",
]

GO = [
    "github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
    "github.com/projectdiscovery/katana/cmd/katana@latest",
    "github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
    "github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest",
    "github.com/projectdiscovery/notify/cmd/notify@latest",
    "github.com/ffuf/ffuf/v2@latest",
    "github.com/OJ/gobuster/v3@latest",
    "github.com/tomnomnom/waybackurls@latest",
    "github.com/lc/gau/v2/cmd/gau@latest",
    "github.com/hakluke/hakrawler@latest",
    "github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest",
    "github.com/s0md3v/uro@latest",
    "github.com/tomnomnom/anew@latest",
    "github.com/tomnomnom/qsreplace@latest",
    "github.com/ffuf/puredns/v2@latest",
    "github.com/BishopFox/cloudfox@latest",
    "github.com/ropnop/kerbrute@latest",
    "github.com/lkarlslund/ldapnomnom@latest",
    "github.com/nhoya/gOSINT/cmd/gosint@latest",
]


def run(cmd: list[str], **kw) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=False, **kw).returncode


def is_stub_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return "ekay-shim" in text or "missing — install" in text or "missing - install" in text


def purge_bad_shims() -> int:
    removed = 0
    for path in list(BIN.iterdir()):
        if not path.is_file():
            continue
        if is_stub_file(path):
            path.unlink(missing_ok=True)
            removed += 1
            continue
        # Drop wrappers whose final target is not a real tool
        if not is_real_tool(str(path)):
            path.unlink(missing_ok=True)
            removed += 1
    print(f"[ekay] removed {removed} bad shims from {BIN}")
    return removed


def write_wrapper(name: str, target: str) -> None:
    path = BIN / name
    path.write_text(f"#!/usr/bin/env bash\nexec '{target}' \"$@\"\n", encoding="utf-8")
    path.chmod(0o755)


def resolve(names: list[str]) -> str | None:
    for n in names:
        # Prefer non-ekay-bin first when checking system, but PATH already has BIN first.
        # Skip stub files explicitly.
        p = shutil.which(n)
        if p and is_real_tool(p):
            return p
        local = BIN / n
        if local.is_file() and is_real_tool(str(local)):
            return str(local)
        # also search without BIN poisoning: scan common dirs
        for base in (HOME / "go" / "bin", HOME / ".local" / "bin", Path("/usr/bin"), Path("/usr/local/bin")):
            cand = base / n
            if cand.is_file() and os.access(cand, os.X_OK) and is_real_tool(str(cand)):
                return str(cand)
    return None


def install_packages() -> None:
    if shutil.which("sudo"):
        run(["sudo", "apt-get", "update"])
        # install in chunks so one missing package doesn't abort all
        chunk: list[str] = []
        for pkg in APT:
            chunk.append(pkg)
            if len(chunk) >= 25:
                run(["sudo", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-y", *chunk])
                chunk = []
        if chunk:
            run(["sudo", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-y", *chunk])
    pip = shutil.which("pip3") or shutil.which("pip")
    if pip:
        run([pip, "install", "--break-system-packages", "-U", *PIP])
    # also into project venv if present
    vpip = ROOT / "ekay-env" / "bin" / "pip3"
    if vpip.is_file():
        run([str(vpip), "install", "-U", *PIP])
    if shutil.which("go"):
        gopath = Path(os.environ["GOPATH"])
        (gopath / "bin").mkdir(parents=True, exist_ok=True)
        for pkg in GO:
            run(["go", "install", "-v", pkg])


def download_extras() -> None:
    """Fetch a few high-value binaries not always in apt."""
    tmp = ROOT / ".tool-cache"
    tmp.mkdir(exist_ok=True)

    # pspy
    pspy = BIN / "pspy64"
    if not pspy.is_file() or not is_real_tool(str(pspy)):
        url = "https://github.com/DominicBreuker/pspy/releases/download/v1.2.1/pspy64"
        dest = tmp / "pspy64"
        if run(["curl", "-fsSL", "-o", str(dest), url]) == 0:
            dest.chmod(0o755)
            shutil.copy2(dest, pspy)
            print("[ekay] installed pspy64")

    # linpeas
    linpeas = BIN / "linpeas.sh"
    if not linpeas.is_file() or not is_real_tool(str(linpeas)):
        url = "https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh"
        dest = tmp / "linpeas.sh"
        if run(["curl", "-fsSL", "-L", "-o", str(dest), url]) == 0:
            dest.chmod(0o755)
            shutil.copy2(dest, linpeas)
            write_wrapper("peass", str(linpeas))
            print("[ekay] installed linpeas.sh")

    # winpeas PE for Windows targets
    winpeas = BIN / "winPEASx64.exe"
    if not winpeas.is_file() or not is_real_tool(str(winpeas)):
        url = "https://github.com/peass-ng/PEASS-ng/releases/latest/download/winPEASx64.exe"
        dest = tmp / "winPEASx64.exe"
        if run(["curl", "-fsSL", "-L", "-o", str(dest), url]) == 0:
            shutil.copy2(dest, winpeas)
            winpeas.chmod(0o755)
            print("[ekay] installed winPEASx64.exe")

    # pretender
    if not resolve(["pretender"]):
        run(["go", "install", "-v", "github.com/RedTeamPentesting/pretender@latest"])


def rebuild_wrappers() -> None:
    extras = {
        "zap.sh": ["zap.sh", "zaproxy", "zap"],
        "testssl.sh": ["testssl.sh", "testssl"],
        "jwt_tool": ["jwt_tool", "jwt-tool"],
        "scout": ["scout", "scout.py"],
        "kr": ["kr", "kiterunner"],
        "nxc": ["nxc", "netexec", "crackmapexec"],
        "crackmapexec": ["crackmapexec", "nxc", "netexec"],
        "osrf": ["osrf", "usufy.py"],
        "vol": ["vol", "volatility3", "vol3"],
        "http": ["http", "httpie"],
        "enum4linux-ng": ["enum4linux-ng"],
        "secretsdump.py": ["impacket-secretsdump", "secretsdump.py"],
        "GetNPUsers.py": ["impacket-GetNPUsers", "GetNPUsers.py"],
        "smbclient.py": ["impacket-smbclient", "smbclient.py"],
        "psexec.py": ["impacket-psexec", "psexec.py"],
        "ntlmrelayx.py": ["impacket-ntlmrelayx", "ntlmrelayx.py", "ntlmrelayx"],
        "certipy": ["certipy", "certipy-ad"],
        "pspy64": ["pspy64", "pspy"],
        "linpeas.sh": ["linpeas.sh", "linpeas"],
        "docker-bench-security": ["docker-bench-security"],
        "osqueryi": ["osqueryi", "osquery"],
    }
    for spec in CATALOG:
        names = [spec.binary, *BINARY_ALIASES.get(spec.binary, ()), *extras.get(spec.binary, [])]
        # unique preserve order
        seen: set[str] = set()
        ordered: list[str] = []
        for n in names:
            if n not in seen:
                seen.add(n)
                ordered.append(n)
        target = resolve(ordered)
        if not target:
            continue
        # Ensure catalog binary name exists and is real
        dest = BIN / spec.binary
        if not dest.exists() or is_stub_file(dest) or not is_real_tool(str(dest)):
            if Path(target).resolve() != dest.resolve():
                write_wrapper(spec.binary, target)
                print(f"wrapper {spec.binary} -> {target}")


def report() -> dict:
    runner = ToolRunner(ScopeGuard(["127.0.0.1"]), allow_intrusive=True)
    return catalog_report(runner)


def main() -> int:
    print("[ekay] fixing catalog runnability…")
    purge_bad_shims()
    install_packages()
    download_extras()
    # second purge in case apt dropped conflicting names
    purge_bad_shims()
    rebuild_wrappers()
    r = report()
    print(
        json_dumps := __import__("json").dumps(
            {
                "catalog": r["catalog"],
                "ready": r["ready"],
                "stub": r["stub"],
                "missing": r["missing"],
                "gated": r["gated"],
            },
            indent=2,
        )
    )
    not_ready = [t for t in r["tools"] if t["status"] != "ready"]
    print(f"[ekay] still not ready: {len(not_ready)}")
    for t in not_ready[:80]:
        print(f"  {t['status']:8} {t['name']:28} {t['binary']}")
    if len(not_ready) > 80:
        print(f"  … +{len(not_ready) - 80} more")
    return 0 if r["ready"] == r["catalog"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
