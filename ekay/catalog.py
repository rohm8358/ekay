"""EKay tool catalog: HexStrike-class binaries plus EKay-only modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Risk = Literal["passive", "active", "intrusive", "restricted"]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    binary: str
    family: str
    risk: Risk
    origin: Literal["hexstrike", "ekay"]
    summary: str
    default_args: tuple[str, ...] = ()


def _t(
    name: str,
    binary: str,
    family: str,
    risk: Risk,
    origin: str,
    summary: str,
    default_args: tuple[str, ...] = (),
) -> ToolSpec:
    return ToolSpec(name, binary, family, risk, origin, summary, default_args)  # type: ignore[arg-type]


HEXSTRIKE_TOOLS: list[ToolSpec] = [
    _t("nmap", "nmap", "network", "active", "hexstrike", "Port/service scan", ("-Pn", "-sV", "-T4", "--top-ports", "100")),
    _t("rustscan", "rustscan", "network", "active", "hexstrike", "Fast port scan", ("-a",)),
    _t("masscan", "masscan", "network", "active", "hexstrike", "High-rate port scan", ("-p", "1-1024", "--rate", "1000")),
    _t("autorecon", "autorecon", "network", "active", "hexstrike", "Automated recon wrapper"),
    _t("amass", "amass", "osint", "passive", "hexstrike", "Subdomain enum", ("enum", "-d")),
    _t("subfinder", "subfinder", "osint", "passive", "hexstrike", "Passive subdomains", ("-d",)),
    _t("fierce", "fierce", "osint", "active", "hexstrike", "DNS recon", ("--domain",)),
    _t("dnsenum", "dnsenum", "osint", "active", "hexstrike", "DNS enumeration"),
    _t("theharvester", "theHarvester", "osint", "passive", "hexstrike", "Email/host OSINT", ("-d", "{target}", "-b", "all")),
    _t("arp-scan", "arp-scan", "network", "active", "hexstrike", "LAN ARP discovery"),
    _t("nbtscan", "nbtscan", "network", "active", "hexstrike", "NetBIOS scan"),
    _t("rpcclient", "rpcclient", "network", "active", "hexstrike", "MSRPC enum"),
    _t("enum4linux", "enum4linux", "network", "active", "hexstrike", "SMB enum"),
    _t("enum4linux-ng", "enum4linux-ng", "network", "active", "hexstrike", "SMB enum (ng)"),
    _t("smbmap", "smbmap", "network", "active", "hexstrike", "SMB share map", ("-H",)),
    _t("responder", "responder", "network", "intrusive", "hexstrike", "Name-resolution poisoner (lab only)"),
    _t("netexec", "nxc", "network", "active", "hexstrike", "Network exploitation helper"),
    _t("gobuster", "gobuster", "web", "active", "hexstrike", "Dir/vhost brute", ("dir", "-u", "{url}", "-w", "/usr/share/wordlists/dirb/common.txt", "-q")),
    _t("feroxbuster", "feroxbuster", "web", "active", "hexstrike", "Recursive content discovery", ("-u",)),
    _t("dirsearch", "dirsearch", "web", "active", "hexstrike", "Directory search", ("-u",)),
    _t("ffuf", "ffuf", "web", "active", "hexstrike", "Web fuzzer", ("-u",)),
    _t("dirb", "dirb", "web", "active", "hexstrike", "Classic dir brute"),
    _t("httpx", "httpx", "web", "passive", "hexstrike", "HTTP probe", ("-silent", "-title", "-status-code", "-u")),
    _t("katana", "katana", "web", "active", "hexstrike", "Crawler", ("-u",)),
    _t("hakrawler", "hakrawler", "web", "active", "hexstrike", "Endpoint crawl"),
    _t("gau", "gau", "osint", "passive", "hexstrike", "GetAllUrls"),
    _t("waybackurls", "waybackurls", "osint", "passive", "hexstrike", "Wayback URLs"),
    _t("nuclei", "nuclei", "web", "active", "hexstrike", "Template vuln scan", ("-silent", "-u")),
    _t("nikto", "nikto", "web", "active", "hexstrike", "Web server checks", ("-h",)),
    _t("sqlmap", "sqlmap", "web", "intrusive", "hexstrike", "SQLi tester (authorized only)", ("-u", "{url}", "--batch", "--smart")),
    _t("wpscan", "wpscan", "web", "active", "hexstrike", "WordPress scan", ("--url",)),  # unique by name later
    _t("arjun", "arjun", "web", "active", "hexstrike", "Parameter discovery", ("-u",)),
    _t("paramspider", "paramspider", "osint", "passive", "hexstrike", "Archive parameter mine", ("-d",)),
    _t("dalfox", "dalfox", "web", "active", "hexstrike", "XSS scanner", ("url",)),
    _t("wafw00f", "wafw00f", "web", "passive", "hexstrike", "WAF fingerprint", ("-a",)),
    _t("jaeles", "jaeles", "web", "active", "hexstrike", "Signature scanner"),
    _t("testssl", "testssl.sh", "web", "passive", "hexstrike", "TLS assessment"),
    _t("sslscan", "sslscan", "web", "passive", "hexstrike", "Cipher enum"),
    _t("sslyze", "sslyze", "web", "passive", "hexstrike", "TLS analyzer"),
    _t("whatweb", "whatweb", "web", "passive", "hexstrike", "Tech fingerprint"),
    _t("jwt-tool", "jwt_tool", "web", "active", "hexstrike", "JWT tester"),
    _t("wfuzz", "wfuzz", "web", "active", "hexstrike", "Web fuzzer"),
    _t("commix", "commix", "web", "intrusive", "hexstrike", "Command-injection tester"),
    _t("nosqlmap", "nosqlmap", "web", "intrusive", "hexstrike", "NoSQL injection tester"),
    _t("tplmap", "tplmap", "web", "intrusive", "hexstrike", "SSTI tester"),
    _t("x8", "x8", "web", "active", "hexstrike", "Hidden parameter discovery"),
    _t("hydra", "hydra", "auth", "intrusive", "hexstrike", "Online login tester (lockout-aware policy)"),
    _t("john", "john", "auth", "intrusive", "hexstrike", "Offline hash cracking"),
    _t("hashcat", "hashcat", "auth", "intrusive", "hexstrike", "GPU hash cracking"),
    _t("medusa", "medusa", "auth", "intrusive", "hexstrike", "Parallel login tester"),
    _t("patator", "patator", "auth", "intrusive", "hexstrike", "Modular brute helper"),
    _t("crackmapexec", "crackmapexec", "auth", "active", "hexstrike", "CME (legacy name)"),
    _t("evil-winrm", "evil-winrm", "auth", "active", "hexstrike", "WinRM shell (lab)"),
    _t("hash-identifier", "hash-identifier", "auth", "passive", "hexstrike", "Hash type guess"),
    _t("hashid", "hashid", "auth", "passive", "hexstrike", "Hash algorithm ID"),
    _t("ophcrack", "ophcrack", "auth", "intrusive", "hexstrike", "Rainbow tables"),
    _t("gdb", "gdb", "binary", "passive", "hexstrike", "Debugger"),
    _t("radare2", "r2", "binary", "passive", "hexstrike", "RE framework"),
    _t("ghidra", "ghidra", "binary", "passive", "hexstrike", "NSA SRE suite"),
    _t("binwalk", "binwalk", "binary", "passive", "hexstrike", "Firmware carve"),
    _t("checksec", "checksec", "binary", "passive", "hexstrike", "Binary mitigations"),
    _t("ropgadget", "ROPgadget", "binary", "passive", "hexstrike", "ROP gadget search"),
    _t("ropper", "ropper", "binary", "passive", "hexstrike", "ROP helper"),
    _t("one-gadget", "one_gadget", "binary", "passive", "hexstrike", "libc one-shot gadgets"),
    _t("pwntools", "python3", "binary", "passive", "hexstrike", "Exploit-dev library (import only)"),
    _t("angr", "python3", "binary", "passive", "hexstrike", "Symbolic execution"),
    _t("msfvenom", "msfvenom", "binary", "restricted", "hexstrike", "Payload generator (lab)"),
    _t("volatility3", "vol", "forensics", "passive", "hexstrike", "Memory forensics"),
    _t("foremost", "foremost", "forensics", "passive", "hexstrike", "File carving"),
    _t("steghide", "steghide", "forensics", "passive", "hexstrike", "Stego extract"),
    _t("exiftool", "exiftool", "forensics", "passive", "hexstrike", "Metadata"),
    _t("autopsy", "autopsy", "forensics", "passive", "hexstrike", "Forensics UI"),
    _t("prowler", "prowler", "cloud", "passive", "hexstrike", "Cloud posture"),
    _t("scout-suite", "scout", "cloud", "passive", "hexstrike", "Multi-cloud audit"),
    _t("trivy", "trivy", "cloud", "passive", "hexstrike", "Container/IaC vulns"),
    _t("kube-hunter", "kube-hunter", "cloud", "active", "hexstrike", "K8s pentest"),
    _t("kube-bench", "kube-bench", "cloud", "passive", "hexstrike", "CIS K8s"),
    _t("docker-bench-security", "docker-bench-security", "cloud", "passive", "hexstrike", "CIS Docker"),
    _t("falco", "falco", "cloud", "passive", "hexstrike", "Runtime detection"),
    _t("checkov", "checkov", "cloud", "passive", "hexstrike", "IaC scanning"),
    _t("terrascan", "terrascan", "cloud", "passive", "hexstrike", "IaC policy"),
    _t("pacu", "pacu", "cloud", "active", "hexstrike", "AWS assessment framework"),
    _t("sherlock", "sherlock", "osint", "passive", "hexstrike", "Username OSINT"),
    _t("social-analyzer", "social-analyzer", "osint", "passive", "hexstrike", "Social OSINT"),
    _t("recon-ng", "recon-ng", "osint", "passive", "hexstrike", "Recon framework"),
    _t("maltego", "maltego", "osint", "passive", "hexstrike", "Link analysis"),
    _t("spiderfoot", "spiderfoot", "osint", "passive", "hexstrike", "OSINT automation"),
    _t("trufflehog", "trufflehog", "osint", "passive", "hexstrike", "Secret scan"),
    _t("subjack", "subjack", "osint", "active", "hexstrike", "Takeover check"),
    _t("aquatone", "aquatone", "osint", "passive", "hexstrike", "Visual recon"),
    _t("zap", "zap.sh", "web", "active", "hexstrike", "OWASP ZAP CLI"),
    _t("strings", "strings", "binary", "passive", "hexstrike", "Extract strings"),
    _t("objdump", "objdump", "binary", "passive", "hexstrike", "Disassemble"),
    _t("readelf", "readelf", "binary", "passive", "hexstrike", "ELF headers"),
    _t("upx", "upx", "binary", "passive", "hexstrike", "Packer"),
    _t("photorec", "photorec", "forensics", "passive", "hexstrike", "File recovery"),
    _t("testdisk", "testdisk", "forensics", "passive", "hexstrike", "Partition recovery"),
    _t("stegsolve", "stegsolve", "forensics", "passive", "hexstrike", "Stego visual"),
    _t("bulk-extractor", "bulk_extractor", "forensics", "passive", "hexstrike", "Feature extract"),
    _t("kubectl", "kubectl", "cloud", "passive", "hexstrike", "K8s CLI"),
    _t("helm", "helm", "cloud", "passive", "hexstrike", "Helm CLI"),
    _t("aws", "aws", "cloud", "passive", "hexstrike", "AWS CLI"),
    _t("az", "az", "cloud", "passive", "hexstrike", "Azure CLI"),
    _t("gcloud", "gcloud", "cloud", "passive", "hexstrike", "GCP CLI"),
    _t("anew", "anew", "osint", "passive", "hexstrike", "Append unique lines"),
    _t("qsreplace", "qsreplace", "web", "passive", "hexstrike", "Query string replace"),
    _t("uro", "uro", "osint", "passive", "hexstrike", "URL dedupe"),
    _t("xxd", "xxd", "binary", "passive", "hexstrike", "Hex dump"),
    _t("hexdump", "hexdump", "binary", "passive", "hexstrike", "Hex viewer"),
    _t("pwninit", "pwninit", "binary", "passive", "hexstrike", "Pwn setup"),
    _t("zsteg", "zsteg", "forensics", "passive", "hexstrike", "PNG/BMP stego"),
    _t("outguess", "outguess", "forensics", "passive", "hexstrike", "JPEG stego"),
    _t("scalpel", "scalpel", "forensics", "passive", "hexstrike", "Carver"),
    _t("clair", "clair", "cloud", "passive", "hexstrike", "Container CVE"),
    _t("cloudmapper", "cloudmapper", "cloud", "passive", "hexstrike", "AWS viz"),
    _t("cloudsploit", "cloudsploit", "cloud", "passive", "hexstrike", "Cloud scan"),
    _t("opa", "opa", "cloud", "passive", "hexstrike", "Policy engine"),
    _t("hash-identifier", "hash-identifier", "auth", "passive", "hexstrike", "Hash ID"),
    _t("netexec", "nxc", "network", "active", "hexstrike", "NetExec"),
]

EKAY_TOOLS: list[ToolSpec] = [
    _t("naabu", "naabu", "network", "active", "ekay", "ProjectDiscovery port scan", ("-host",)),
    _t("dnsx", "dnsx", "osint", "passive", "ekay", "DNS toolkit", ("-l",)),
    _t("impacket-secretsdump", "secretsdump.py", "auth", "restricted", "ekay", "Impacket DC/host dump (lab)"),
    _t("impacket-getnpusers", "GetNPUsers.py", "auth", "active", "ekay", "AS-REP roast (authorized AD)"),
    _t("bettercap", "bettercap", "network", "intrusive", "ekay", "Network attack framework (lab)"),
    _t("bloodhound", "bloodhound", "ad", "passive", "ekay", "AD path analysis UI"),
    _t("bloodhound-python", "bloodhound-python", "ad", "active", "ekay", "SharpHound-class collector (Python)"),
    _t("pingcastle", "PingCastle.exe", "ad", "passive", "ekay", "AD health (Windows/wine)"),
    _t("kerbrute", "kerbrute", "ad", "active", "ekay", "Kerberos user enum (authorized)"),
    _t("ligolo-ng", "ligolo-ng", "network", "restricted", "ekay", "Pivoting proxy (engagement)"),
    _t("chisel", "chisel", "network", "restricted", "ekay", "Tunnel helper (engagement)"),
    _t("kiterunner", "kr", "web", "active", "ekay", "API wordlist routing"),
    _t("schemathesis", "schemathesis", "web", "active", "ekay", "OpenAPI property testing"),
    _t("wapiti", "wapiti", "web", "active", "ekay", "Web vuln scanner", ("-u",)),
    _t("graphqlmap", "graphqlmap", "web", "active", "ekay", "GraphQL tester"),
    _t("gitleaks", "gitleaks", "osint", "passive", "ekay", "Repo secret scan", ("detect",)),
    _t("grype", "grype", "cloud", "passive", "ekay", "SBOM/CVE scan"),
    _t("steampipe", "steampipe", "cloud", "passive", "ekay", "Cloud SQL inventory"),
    _t("cewl", "cewl", "auth", "passive", "ekay", "Target-specific wordlist"),
    _t("aircrack-ng", "aircrack-ng", "wireless", "intrusive", "ekay", "Wi-Fi crypto (RF permission required)"),
    _t("wifite", "wifite", "wireless", "intrusive", "ekay", "Wi-Fi audit helper"),
    _t("kismet", "kismet", "wireless", "passive", "ekay", "Wireless IDS/sniffer"),
    _t("hcxdumptool", "hcxdumptool", "wireless", "intrusive", "ekay", "PMKID/handshake capture"),
    _t("yara", "yara", "forensics", "passive", "ekay", "Pattern matching"),
    _t("osqueryi", "osqueryi", "forensics", "passive", "ekay", "Host SQL inventory"),
    _t("gophish", "gophish", "se", "restricted", "ekay", "Authorized phishing simulation platform"),
    _t("swaks", "swaks", "se", "active", "ekay", "SMTP test tool"),
    _t("o365spray", "o365spray", "identity", "intrusive", "ekay", "O365 enum/spray (policy gated)"),
    _t("roadtx", "roadtx", "identity", "active", "ekay", "ROADTools Azure identity"),
    _t("faraday-cli", "faraday-cli", "report", "passive", "ekay", "Faraday reporting CLI"),
]


def _dedupe(items: list[ToolSpec]) -> list[ToolSpec]:
    seen: dict[str, ToolSpec] = {}
    for spec in items:
        seen[spec.name] = spec
    return list(seen.values())


CATALOG: list[ToolSpec] = _dedupe(HEXSTRIKE_TOOLS + EKAY_TOOLS)
CATALOG_BY_NAME: dict[str, ToolSpec] = {t.name: t for t in CATALOG}


def families() -> dict[str, int]:
    out: dict[str, int] = {}
    for t in CATALOG:
        out[t.family] = out.get(t.family, 0) + 1
    return dict(sorted(out.items()))
