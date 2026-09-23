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

# Minimum 70 EKay-only tools (not in HexStrike README). Dual-use / intrusive stay gated.
EKAY_TOOLS: list[ToolSpec] = [
    # --- Network / pivot ---
    _t("naabu", "naabu", "network", "active", "ekay", "ProjectDiscovery port scan", ("-host",)),
    _t("bettercap", "bettercap", "network", "intrusive", "ekay", "Network attack framework (lab)"),
    _t("ligolo-ng", "ligolo-ng", "network", "restricted", "ekay", "Pivoting proxy (engagement)"),
    _t("chisel", "chisel", "network", "restricted", "ekay", "Tunnel helper (engagement)"),
    _t("proxychains", "proxychains4", "network", "restricted", "ekay", "Proxy chain wrapper"),
    _t("socat", "socat", "network", "restricted", "ekay", "Relay / port forward"),
    _t("nmap-nse-vuln", "nmap", "network", "active", "ekay", "Nmap vuln NSE scripts", ("--script", "vuln", "-Pn")),
    _t("rustscan-ultrarange", "rustscan", "network", "active", "ekay", "Full-port rustscan wrapper", ("-a", "{target}", "--ulimit", "5000")),
    # --- API security ---
    _t("kiterunner", "kr", "api", "active", "ekay", "API-aware route brute", ("scan", "apis")),
    _t("schemathesis", "schemathesis", "api", "active", "ekay", "OpenAPI property fuzzing"),
    _t("mitmproxy", "mitmproxy", "api", "active", "ekay", "Scriptable HTTP/HTTPS proxy"),
    _t("mitmdump", "mitmdump", "api", "active", "ekay", "mitmproxy headless dump"),
    _t("postman", "postman", "api", "passive", "ekay", "API collections / role tokens"),
    _t("insomnia", "insomnia", "api", "passive", "ekay", "API client for authz suites"),
    _t("httpie", "http", "api", "passive", "ekay", "CLI HTTP client"),
    _t("curl-impersonate", "curl-impersonate", "api", "passive", "ekay", "Browser-like TLS fingerprint"),
    _t("graphw00f", "graphw00f", "api", "passive", "ekay", "GraphQL engine fingerprint"),
    _t("clairvoyance", "clairvoyance", "api", "active", "ekay", "GraphQL schema recovery"),
    _t("inql", "inql", "api", "active", "ekay", "GraphQL introspection helper"),
    _t("graphql-cop", "graphql-cop", "api", "active", "ekay", "GraphQL security checks"),
    _t("restler", "restler", "api", "active", "ekay", "Microsoft RESTler API fuzzer"),
    _t("apisprout", "apisprout", "api", "passive", "ekay", "Mock OpenAPI server for labs"),
    _t("openapi-generator", "openapi-generator", "api", "passive", "ekay", "Generate clients from OpenAPI"),
    _t("spectral", "spectral", "api", "passive", "ekay", "OpenAPI lint / governance"),
    _t("wapiti", "wapiti", "web", "active", "ekay", "Web vuln scanner", ("-u",)),
    _t("graphqlmap", "graphqlmap", "api", "active", "ekay", "GraphQL interactive tester"),
    # --- Web extras ---
    _t("hakrawler-deep", "hakrawler", "web", "active", "ekay", "Deep crawl profile"),
    _t("gau-plus", "gau", "web", "passive", "ekay", "GetAllUrls multi-source"),
    _t("waymore", "waymore", "web", "passive", "ekay", "Wayback + CommonCrawl URLs"),
    _t("urlfinder", "urlfinder", "web", "passive", "ekay", "URL discovery helper"),
    _t("cariddi", "cariddi", "web", "active", "ekay", "Crawl + secret / endpoint hunt"),
    _t("interactsh-client", "interactsh-client", "web", "active", "ekay", "OOB interaction client"),
    _t("notify", "notify", "web", "passive", "ekay", "Alert pipe for findings"),
    # --- OSINT / social / Instagram ---
    _t("dnsx", "dnsx", "osint", "passive", "ekay", "DNS toolkit", ("-l",)),
    _t("gitleaks", "gitleaks", "osint", "passive", "ekay", "Repo secret scan", ("detect",)),
    _t("osintgram", "osintgram", "osint", "passive", "ekay", "Instagram public OSINT shell"),
    _t("instaloader", "instaloader", "osint", "passive", "ekay", "Instagram public media/metadata"),
    _t("toutatis", "toutatis", "osint", "passive", "ekay", "Instagram email/phone OSINT"),
    _t("insto", "insto", "osint", "passive", "ekay", "Modern Instagram OSINT CLI"),
    _t("maigret", "maigret", "osint", "passive", "ekay", "Username search across sites"),
    _t("socialscan", "socialscan", "osint", "passive", "ekay", "Username/email availability"),
    _t("holehe", "holehe", "osint", "passive", "ekay", "Email registration OSINT"),
    _t("ghunt", "ghunt", "osint", "passive", "ekay", "Google account OSINT"),
    _t("phoneinfoga", "phoneinfoga", "osint", "passive", "ekay", "Phone number OSINT"),
    _t("blackbird", "blackbird", "osint", "passive", "ekay", "Username OSINT across sites"),
    _t("twint", "twint", "osint", "passive", "ekay", "Twitter/X OSINT (legacy)"),
    _t("snscrape", "snscrape", "osint", "passive", "ekay", "Social scrape without API keys"),
    _t("metagoofil", "metagoofil", "osint", "passive", "ekay", "Public document metadata"),
    _t("exiflooter", "exiflooter", "osint", "passive", "ekay", "EXIF from public images"),
    _t("photon", "photon", "osint", "passive", "ekay", "Fast web crawler OSINT"),
    _t("finalrecon", "finalrecon", "osint", "passive", "ekay", "Web recon suite"),
    _t("reconspider", "reconspider", "osint", "passive", "ekay", "Multi-source recon"),
    _t("osrframework", "osrf", "osint", "passive", "ekay", "OSINT username frameworks"),
    # --- Password / auth extras ---
    _t("cewl", "cewl", "auth", "passive", "ekay", "Target-specific wordlist"),
    _t("crunch", "crunch", "auth", "passive", "ekay", "Wordlist generator"),
    _t("cupp", "cupp", "auth", "passive", "ekay", "Common User Password Profiler"),
    _t("username-anarchy", "username-anarchy", "auth", "passive", "ekay", "Username mutation"),
    _t("impacket-secretsdump", "secretsdump.py", "auth", "restricted", "ekay", "Impacket DC/host dump (lab)"),
    _t("impacket-getnpusers", "GetNPUsers.py", "auth", "active", "ekay", "AS-REP roast (authorized AD)"),
    _t("impacket-smbclient", "smbclient.py", "auth", "active", "ekay", "Impacket SMB client"),
    _t("impacket-psexec", "psexec.py", "auth", "restricted", "ekay", "Impacket PsExec (lab)"),
    _t("sprayhound", "sprayhound", "auth", "intrusive", "ekay", "AD spray with lockout awareness"),
    # --- AD / identity ---
    _t("bloodhound", "bloodhound", "ad", "passive", "ekay", "AD path analysis UI"),
    _t("bloodhound-python", "bloodhound-python", "ad", "active", "ekay", "Python AD collector"),
    _t("pingcastle", "PingCastle.exe", "ad", "passive", "ekay", "AD health assessment"),
    _t("kerbrute", "kerbrute", "ad", "active", "ekay", "Kerberos user enum"),
    _t("o365spray", "o365spray", "identity", "intrusive", "ekay", "O365 enum/spray (policy gated)"),
    _t("roadtx", "roadtx", "identity", "active", "ekay", "ROADTools Azure identity"),
    _t("aadinternals", "AADInternals", "identity", "active", "ekay", "Azure AD assessment module"),
    _t("graphrunner", "GraphRunner", "identity", "active", "ekay", "Microsoft Graph post-auth assessment"),
    _t("mfasweep", "MFASweep", "identity", "active", "ekay", "MFA status enumeration"),
    # --- Cloud extras ---
    _t("grype", "grype", "cloud", "passive", "ekay", "SBOM/CVE scan"),
    _t("steampipe", "steampipe", "cloud", "passive", "ekay", "Cloud SQL inventory"),
    _t("s3scanner", "s3scanner", "cloud", "passive", "ekay", "S3 bucket discovery"),
    _t("cloudbrute", "cloudbrute", "cloud", "passive", "ekay", "Cloud enum across providers"),
    _t("enumerate-iam", "enumerate-iam", "cloud", "active", "ekay", "AWS IAM permission enum"),
    # --- Wireless ---
    _t("aircrack-ng", "aircrack-ng", "wireless", "intrusive", "ekay", "Wi-Fi crypto (RF permission)"),
    _t("airmon-ng", "airmon-ng", "wireless", "intrusive", "ekay", "Monitor-mode helper"),
    _t("airodump-ng", "airodump-ng", "wireless", "intrusive", "ekay", "Wi-Fi traffic capture"),
    _t("aireplay-ng", "aireplay-ng", "wireless", "intrusive", "ekay", "Wi-Fi injection (authorized)"),
    _t("wifite", "wifite", "wireless", "intrusive", "ekay", "Automated Wi-Fi audit"),
    _t("kismet", "kismet", "wireless", "passive", "ekay", "Wireless IDS/sniffer"),
    _t("hcxdumptool", "hcxdumptool", "wireless", "intrusive", "ekay", "PMKID/handshake capture"),
    _t("hcxpcapngtool", "hcxpcapngtool", "wireless", "passive", "ekay", "Convert captures for hashcat"),
    _t("reaver", "reaver", "wireless", "intrusive", "ekay", "WPS audit (authorized RF)"),
    _t("bully", "bully", "wireless", "intrusive", "ekay", "WPS PIN audit"),
    _t("fern-wifi-cracker", "fern-wifi-cracker", "wireless", "intrusive", "ekay", "GUI Wi-Fi audit suite"),
    _t("wifiphisher", "wifiphisher", "wireless", "restricted", "ekay", "Authorized evil-twin awareness lab"),
    # --- Phishing / SE simulation (approved campaigns) ---
    _t("gophish", "gophish", "se", "restricted", "ekay", "Phishing simulation platform"),
    _t("king-phisher", "king-phisher", "se", "restricted", "ekay", "Phishing campaign server"),
    _t("setoolkit", "setoolkit", "se", "restricted", "ekay", "Social-Engineer Toolkit"),
    _t("evilginx2", "evilginx", "se", "restricted", "ekay", "MFA phishing-sim reverse proxy (lab)"),
    _t("modlishka", "modlishka", "se", "restricted", "ekay", "Reverse-proxy phishing sim"),
    _t("swaks", "swaks", "se", "active", "ekay", "SMTP test / mail path check"),
    _t("hiddeneye", "hiddeneye", "se", "restricted", "ekay", "Legacy phishing-sim templates (lab)"),
    _t("zphisher", "zphisher", "se", "restricted", "ekay", "Phishing-sim templates (authorized only)"),
    _t("socialfish", "socialfish", "se", "restricted", "ekay", "Phishing-sim framework (authorized)"),
    # --- Mobile app / device assessment (authorized lab devices ONLY — not remote spyware) ---
    _t("mobsf", "mobsf", "mobile", "passive", "ekay", "Mobile app SAST/DAST framework"),
    _t("frida", "frida", "mobile", "active", "ekay", "Runtime instrumentation (owned device)"),
    _t("frida-ps", "frida-ps", "mobile", "passive", "ekay", "List processes on USB device"),
    _t("objection", "objection", "mobile", "active", "ekay", "Frida mobile exploration toolkit"),
    _t("apktool", "apktool", "mobile", "passive", "ekay", "APK decode / rebuild"),
    _t("jadx", "jadx", "mobile", "passive", "ekay", "APK to Java decompiler"),
    _t("jadx-gui", "jadx-gui", "mobile", "passive", "ekay", "JADX graphical UI"),
    _t("drozer", "drozer", "mobile", "active", "ekay", "Android IPC / component testing"),
    _t("adb", "adb", "mobile", "restricted", "ekay", "Android Debug Bridge (owned device)"),
    _t("apkleaks", "apkleaks", "mobile", "passive", "ekay", "Secrets in APK strings"),
    _t("quark-engine", "quark", "mobile", "passive", "ekay", "Android malware score engine"),
    _t("mvt-android", "mvt-android", "mobile", "passive", "ekay", "Mobile Verification Toolkit Android"),
    _t("mvt-ios", "mvt-ios", "mobile", "passive", "ekay", "Mobile Verification Toolkit iOS"),
    # --- Forensics extras ---
    _t("yara", "yara", "forensics", "passive", "ekay", "Pattern matching"),
    _t("osqueryi", "osqueryi", "forensics", "passive", "ekay", "Host SQL inventory"),
    _t("sleuthkit", "fls", "forensics", "passive", "ekay", "Sleuth Kit file listing"),
    # --- Reporting ---
    _t("faraday-cli", "faraday-cli", "report", "passive", "ekay", "Faraday reporting CLI"),
    _t("sysreptor", "sysreptor", "report", "passive", "ekay", "Pentest report platform"),
    _t("pwndoc", "pwndoc", "report", "passive", "ekay", "Collaborative pentest reports"),
    _t("defectdojo", "defectdojo", "report", "passive", "ekay", "Vulnerability management"),
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
