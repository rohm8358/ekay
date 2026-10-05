# EKay Tool Catalog

**Total tools:** 223  
**HexStrike-origin:** 113 · **EKay-only:** 110

Generated from `ekay/catalog.py` via `scripts/export_catalog.py`.

## Phase inventory

| Phase | Tools | Summary |
| --- | ---: | --- |
| `osint` | 33 | Passive / open-source intel on the target org or domain |
| `recon` | 20 | Host/port/service discovery inside engagement scope |
| `external` | 49 | Web/API attack-surface probing and vuln templates |
| `initial_access` | 9 | Authorized foothold simulation (gated) |
| `creds` | 19 | Credential access / spray / offline crack (gated) |
| `ad` | 12 | Active Directory enumeration and path analysis (gated) |
| `cloud` | 19 | Cloud posture and identity assessment |
| `post` | 37 | Post-exploitation / host triage (gated) |
| `report` | 1 | Evidence packaging and report export |
| `mobile` | 12 | Mobile app / device assessment (owned devices) |
| `wireless` | 12 | RF / Wi-Fi assessment (requires RF authorization) |

## Tools by kill-chain phase

### `osint` (33)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `amass` | `amass` | osint | passive | hexstrike | Subdomain enum |
| `anew` | `anew` | osint | passive | hexstrike | Append unique lines |
| `aquatone` | `aquatone` | osint | passive | hexstrike | Visual recon |
| `blackbird` | `blackbird` | osint | passive | ekay | Username OSINT across sites |
| `dnsenum` | `dnsenum` | osint | active | hexstrike | DNS enumeration |
| `dnsx` | `dnsx` | osint | passive | ekay | DNS toolkit |
| `fierce` | `fierce` | osint | active | hexstrike | DNS recon |
| `finalrecon` | `finalrecon` | osint | passive | ekay | Web recon suite |
| `gau` | `gau` | osint | passive | hexstrike | GetAllUrls |
| `ghunt` | `ghunt` | osint | passive | ekay | Google account OSINT |
| `gitleaks` | `gitleaks` | osint | passive | ekay | Repo secret scan |
| `holehe` | `holehe` | osint | passive | ekay | Email registration OSINT |
| `instaloader` | `instaloader` | osint | passive | ekay | Instagram public media/metadata |
| `maigret` | `maigret` | osint | passive | ekay | Username search across sites |
| `maltego` | `maltego` | osint | passive | hexstrike | Link analysis |
| `metagoofil` | `metagoofil` | osint | passive | ekay | Public document metadata |
| `osintgram` | `osintgram` | osint | passive | ekay | Instagram public OSINT shell |
| `paramspider` | `paramspider` | osint | passive | hexstrike | Archive parameter mine |
| `phoneinfoga` | `phoneinfoga` | osint | passive | ekay | Phone number OSINT |
| `photon` | `photon` | osint | passive | ekay | Fast web crawler OSINT |
| `recon-ng` | `recon-ng` | osint | passive | hexstrike | Recon framework |
| `sherlock` | `sherlock` | osint | passive | hexstrike | Username OSINT |
| `snscrape` | `snscrape` | osint | passive | ekay | Social scrape without API keys |
| `social-analyzer` | `social-analyzer` | osint | passive | hexstrike | Social OSINT |
| `socialscan` | `socialscan` | osint | passive | ekay | Username/email availability |
| `spiderfoot` | `spiderfoot` | osint | passive | hexstrike | OSINT automation |
| `subfinder` | `subfinder` | osint | passive | hexstrike | Passive subdomains |
| `subjack` | `subjack` | osint | active | hexstrike | Takeover check |
| `theharvester` | `theHarvester` | osint | passive | hexstrike | Email/host OSINT |
| `toutatis` | `toutatis` | osint | passive | ekay | Instagram email/phone OSINT |
| `trufflehog` | `trufflehog` | osint | passive | hexstrike | Secret scan |
| `uro` | `uro` | osint | passive | hexstrike | URL dedupe |
| `waybackurls` | `waybackurls` | osint | passive | hexstrike | Wayback URLs |

### `recon` (20)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `arp-scan` | `arp-scan` | network | active | hexstrike | LAN ARP discovery |
| `autorecon` | `autorecon` | network | active | hexstrike | Automated recon wrapper |
| `bettercap` | `bettercap` | network | intrusive | ekay | Network attack framework (lab) |
| `chisel` | `chisel` | network | restricted | ekay | Tunnel helper (engagement) |
| `enum4linux` | `enum4linux` | network | active | hexstrike | SMB enum |
| `enum4linux-ng` | `enum4linux-ng` | network | active | hexstrike | SMB enum (ng) |
| `ligolo-ng` | `ligolo-ng` | network | restricted | ekay | Pivoting proxy (engagement) |
| `masscan` | `masscan` | network | active | hexstrike | High-rate port scan |
| `naabu` | `naabu` | network | active | ekay | ProjectDiscovery port scan |
| `nbtscan` | `nbtscan` | network | active | hexstrike | NetBIOS scan |
| `netexec` | `nxc` | network | active | hexstrike | NetExec |
| `nmap` | `nmap` | network | active | hexstrike | Port/service scan |
| `nmap-nse-vuln` | `nmap` | network | active | ekay | Nmap vuln NSE scripts |
| `proxychains` | `proxychains4` | network | restricted | ekay | Proxy chain wrapper |
| `responder` | `responder` | network | intrusive | hexstrike | Name-resolution poisoner (lab only) |
| `rpcclient` | `rpcclient` | network | active | hexstrike | MSRPC enum |
| `rustscan` | `rustscan` | network | active | hexstrike | Fast port scan |
| `rustscan-ultrarange` | `rustscan` | network | active | ekay | Full-port rustscan wrapper |
| `smbmap` | `smbmap` | network | active | hexstrike | SMB share map |
| `socat` | `socat` | network | restricted | ekay | Relay / port forward |

### `external` (49)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `arjun` | `arjun` | web | active | hexstrike | Parameter discovery |
| `cariddi` | `cariddi` | web | active | ekay | Crawl + secret / endpoint hunt |
| `clairvoyance` | `clairvoyance` | api | active | ekay | GraphQL schema recovery |
| `commix` | `commix` | web | intrusive | hexstrike | Command-injection tester |
| `dalfox` | `dalfox` | web | active | hexstrike | XSS scanner |
| `dirb` | `dirb` | web | active | hexstrike | Classic dir brute |
| `dirsearch` | `dirsearch` | web | active | hexstrike | Directory search |
| `feroxbuster` | `feroxbuster` | web | active | hexstrike | Recursive content discovery |
| `ffuf` | `ffuf` | web | active | hexstrike | Web fuzzer |
| `gau-plus` | `gau` | web | passive | ekay | GetAllUrls multi-source |
| `gobuster` | `gobuster` | web | active | hexstrike | Dir/vhost brute |
| `graphql-cop` | `graphql-cop` | api | active | ekay | GraphQL security checks |
| `graphqlmap` | `graphqlmap` | api | active | ekay | GraphQL interactive tester |
| `graphw00f` | `graphw00f` | api | passive | ekay | GraphQL engine fingerprint |
| `hakrawler` | `hakrawler` | web | active | hexstrike | Endpoint crawl |
| `hakrawler-deep` | `hakrawler` | web | active | ekay | Deep crawl profile |
| `httpie` | `http` | api | passive | ekay | CLI HTTP client |
| `httpx` | `httpx` | web | passive | hexstrike | HTTP probe |
| `inql` | `inql` | api | active | ekay | GraphQL introspection helper |
| `insomnia` | `insomnia` | api | passive | ekay | API client for authz suites |
| `interactsh-client` | `interactsh-client` | web | active | ekay | OOB interaction client |
| `jaeles` | `jaeles` | web | active | hexstrike | Signature scanner |
| `jwt-tool` | `jwt_tool` | web | active | hexstrike | JWT tester |
| `katana` | `katana` | web | active | hexstrike | Crawler |
| `kiterunner` | `kr` | api | active | ekay | API-aware route brute |
| `mitmdump` | `mitmdump` | api | active | ekay | mitmproxy headless dump |
| `mitmproxy` | `mitmproxy` | api | active | ekay | Scriptable HTTP/HTTPS proxy |
| `nikto` | `nikto` | web | active | hexstrike | Web server checks |
| `nosqlmap` | `nosqlmap` | web | intrusive | hexstrike | NoSQL injection tester |
| `notify` | `notify` | web | passive | ekay | Alert pipe for findings |
| `nuclei` | `nuclei` | web | active | hexstrike | Template vuln scan |
| `openapi-generator` | `openapi-generator` | api | passive | ekay | Generate clients from OpenAPI |
| `postman` | `postman` | api | passive | ekay | API collections / role tokens |
| `qsreplace` | `qsreplace` | web | passive | hexstrike | Query string replace |
| `schemathesis` | `schemathesis` | api | active | ekay | OpenAPI property fuzzing |
| `sqlmap` | `sqlmap` | web | intrusive | hexstrike | SQLi tester (authorized only) |
| `sslscan` | `sslscan` | web | passive | hexstrike | Cipher enum |
| `sslyze` | `sslyze` | web | passive | hexstrike | TLS analyzer |
| `testssl` | `testssl.sh` | web | passive | hexstrike | TLS assessment |
| `tplmap` | `tplmap` | web | intrusive | hexstrike | SSTI tester |
| `urlfinder` | `urlfinder` | web | passive | ekay | URL discovery helper |
| `wafw00f` | `wafw00f` | web | passive | hexstrike | WAF fingerprint |
| `wapiti` | `wapiti` | web | active | ekay | Web vuln scanner |
| `waymore` | `waymore` | web | passive | ekay | Wayback + CommonCrawl URLs |
| `wfuzz` | `wfuzz` | web | active | hexstrike | Web fuzzer |
| `whatweb` | `whatweb` | web | passive | hexstrike | Tech fingerprint |
| `wpscan` | `wpscan` | web | active | hexstrike | WordPress scan |
| `x8` | `x8` | web | active | hexstrike | Hidden parameter discovery |
| `zap` | `zap.sh` | web | active | hexstrike | OWASP ZAP CLI |

### `initial_access` (9)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `evilginx2` | `evilginx` | se | restricted | ekay | MFA phishing-sim reverse proxy (lab) |
| `gophish` | `gophish` | se | restricted | ekay | Phishing simulation platform |
| `hiddeneye` | `hiddeneye` | se | restricted | ekay | Legacy phishing-sim templates (lab) |
| `king-phisher` | `king-phisher` | se | restricted | ekay | Phishing campaign server |
| `modlishka` | `modlishka` | se | restricted | ekay | Reverse-proxy phishing sim |
| `setoolkit` | `setoolkit` | se | restricted | ekay | Social-Engineer Toolkit |
| `socialfish` | `socialfish` | se | restricted | ekay | Phishing-sim framework (authorized) |
| `swaks` | `swaks` | se | active | ekay | SMTP test / mail path check |
| `zphisher` | `zphisher` | se | restricted | ekay | Phishing-sim templates (authorized only) |

### `creds` (19)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `cewl` | `cewl` | auth | passive | ekay | Target-specific wordlist |
| `crackmapexec` | `crackmapexec` | auth | active | hexstrike | CME (legacy name) |
| `crunch` | `crunch` | auth | passive | ekay | Wordlist generator |
| `cupp` | `cupp` | auth | passive | ekay | Common User Password Profiler |
| `evil-winrm` | `evil-winrm` | auth | active | hexstrike | WinRM shell (lab) |
| `hash-identifier` | `hash-identifier` | auth | passive | hexstrike | Hash ID |
| `hashcat` | `hashcat` | auth | intrusive | hexstrike | GPU hash cracking |
| `hashid` | `hashid` | auth | passive | hexstrike | Hash algorithm ID |
| `hydra` | `hydra` | auth | intrusive | hexstrike | Online login tester (lockout-aware policy) |
| `impacket-getnpusers` | `GetNPUsers.py` | auth | active | ekay | AS-REP roast (authorized AD) |
| `impacket-psexec` | `psexec.py` | auth | restricted | ekay | Impacket PsExec (lab) |
| `impacket-secretsdump` | `secretsdump.py` | auth | restricted | ekay | Impacket DC/host dump (lab) |
| `impacket-smbclient` | `smbclient.py` | auth | active | ekay | Impacket SMB client |
| `john` | `john` | auth | intrusive | hexstrike | Offline hash cracking |
| `medusa` | `medusa` | auth | intrusive | hexstrike | Parallel login tester |
| `ophcrack` | `ophcrack` | auth | intrusive | hexstrike | Rainbow tables |
| `patator` | `patator` | auth | intrusive | hexstrike | Modular brute helper |
| `sprayhound` | `sprayhound` | auth | intrusive | ekay | AD spray with lockout awareness |
| `username-anarchy` | `username-anarchy` | auth | passive | ekay | Username mutation |

### `ad` (12)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `bloodhound` | `bloodhound` | ad | passive | ekay | AD path analysis UI |
| `bloodhound-python` | `bloodhound-python` | ad | active | ekay | Python AD collector |
| `certipy` | `certipy` | ad | active | ekay | AD CS enumeration / abuse paths (authorized) |
| `coercer` | `coercer` | ad | intrusive | ekay | Auth coerce tester (lab / authorized) |
| `kerbrute` | `kerbrute` | ad | active | ekay | Kerberos user enum |
| `ldapdomaindump` | `ldapdomaindump` | ad | active | ekay | LDAP domain dump for AD recon |
| `ldapsearch` | `ldapsearch` | ad | active | ekay | OpenLDAP query client |
| `mitm6` | `mitm6` | ad | restricted | ekay | IPv6 DNS takeover lab helper |
| `ntlmrelayx` | `ntlmrelayx.py` | ad | restricted | ekay | Impacket NTLM relay (lab) |
| `o365spray` | `o365spray` | identity | intrusive | ekay | O365 enum/spray (policy gated) |
| `pretender` | `pretender` | ad | intrusive | ekay | mDNS/DNS spoof helper (lab) |
| `roadtx` | `roadtx` | identity | active | ekay | ROADTools Azure identity |

### `cloud` (19)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `aws` | `aws` | cloud | passive | hexstrike | AWS CLI |
| `az` | `az` | cloud | passive | hexstrike | Azure CLI |
| `checkov` | `checkov` | cloud | passive | hexstrike | IaC scanning |
| `clair` | `clair` | cloud | passive | hexstrike | Container CVE |
| `cloudbrute` | `cloudbrute` | cloud | passive | ekay | Cloud enum across providers |
| `enumerate-iam` | `enumerate-iam` | cloud | active | ekay | AWS IAM permission enum |
| `falco` | `falco` | cloud | passive | hexstrike | Runtime detection |
| `grype` | `grype` | cloud | passive | ekay | SBOM/CVE scan |
| `helm` | `helm` | cloud | passive | hexstrike | Helm CLI |
| `kube-bench` | `kube-bench` | cloud | passive | hexstrike | CIS K8s |
| `kube-hunter` | `kube-hunter` | cloud | active | hexstrike | K8s pentest |
| `kubectl` | `kubectl` | cloud | passive | hexstrike | K8s CLI |
| `opa` | `opa` | cloud | passive | hexstrike | Policy engine |
| `pacu` | `pacu` | cloud | active | hexstrike | AWS assessment framework |
| `prowler` | `prowler` | cloud | passive | hexstrike | Cloud posture |
| `s3scanner` | `s3scanner` | cloud | passive | ekay | S3 bucket discovery |
| `scout-suite` | `scout` | cloud | passive | hexstrike | Multi-cloud audit |
| `terrascan` | `terrascan` | cloud | passive | hexstrike | IaC policy |
| `trivy` | `trivy` | cloud | passive | hexstrike | Container/IaC vulns |

### `post` (37)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `angr` | `python3` | binary | passive | hexstrike | Symbolic execution |
| `autopsy` | `autopsy` | forensics | passive | hexstrike | Forensics UI |
| `binwalk` | `binwalk` | binary | passive | hexstrike | Firmware carve |
| `bulk-extractor` | `bulk_extractor` | forensics | passive | hexstrike | Feature extract |
| `checksec` | `checksec` | binary | passive | hexstrike | Binary mitigations |
| `exiftool` | `exiftool` | forensics | passive | hexstrike | Metadata |
| `foremost` | `foremost` | forensics | passive | hexstrike | File carving |
| `gdb` | `gdb` | binary | passive | hexstrike | Debugger |
| `ghidra` | `ghidra` | binary | passive | hexstrike | NSA SRE suite |
| `hexdump` | `hexdump` | binary | passive | hexstrike | Hex viewer |
| `linpeas` | `linpeas.sh` | binary | active | ekay | Linux priv-esc enumeration script |
| `msfvenom` | `msfvenom` | binary | restricted | hexstrike | Payload generator (lab) |
| `objdump` | `objdump` | binary | passive | hexstrike | Disassemble |
| `one-gadget` | `one_gadget` | binary | passive | hexstrike | libc one-shot gadgets |
| `osqueryi` | `osqueryi` | forensics | passive | ekay | Host SQL inventory |
| `outguess` | `outguess` | forensics | passive | hexstrike | JPEG stego |
| `peass-ng` | `peass` | binary | active | ekay | PEASS-ng priv-esc suite wrapper |
| `photorec` | `photorec` | forensics | passive | hexstrike | File recovery |
| `pspy` | `pspy64` | binary | passive | ekay | Linux process snooping (no root) |
| `pwninit` | `pwninit` | binary | passive | hexstrike | Pwn setup |
| `pwntools` | `python3` | binary | passive | hexstrike | Exploit-dev library (import only) |
| `radare2` | `r2` | binary | passive | hexstrike | RE framework |
| `readelf` | `readelf` | binary | passive | hexstrike | ELF headers |
| `ropgadget` | `ROPgadget` | binary | passive | hexstrike | ROP gadget search |
| `ropper` | `ropper` | binary | passive | hexstrike | ROP helper |
| `scalpel` | `scalpel` | forensics | passive | hexstrike | Carver |
| `sleuthkit` | `fls` | forensics | passive | ekay | Sleuth Kit file listing |
| `steghide` | `steghide` | forensics | passive | hexstrike | Stego extract |
| `stegsolve` | `stegsolve` | forensics | passive | hexstrike | Stego visual |
| `strings` | `strings` | binary | passive | hexstrike | Extract strings |
| `testdisk` | `testdisk` | forensics | passive | hexstrike | Partition recovery |
| `upx` | `upx` | binary | passive | hexstrike | Packer |
| `volatility3` | `vol` | forensics | passive | hexstrike | Memory forensics |
| `winpeas` | `winPEASx64.exe` | binary | active | ekay | Windows priv-esc enumeration |
| `xxd` | `xxd` | binary | passive | hexstrike | Hex dump |
| `yara` | `yara` | forensics | passive | ekay | Pattern matching |
| `zsteg` | `zsteg` | forensics | passive | hexstrike | PNG/BMP stego |

### `report` (1)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `faraday-cli` | `faraday-cli` | report | passive | ekay | Faraday reporting CLI |

### `mobile` (12)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `adb` | `adb` | mobile | restricted | ekay | Android Debug Bridge (owned device) |
| `apkleaks` | `apkleaks` | mobile | passive | ekay | Secrets in APK strings |
| `apktool` | `apktool` | mobile | passive | ekay | APK decode / rebuild |
| `drozer` | `drozer` | mobile | active | ekay | Android IPC / component testing |
| `frida` | `frida` | mobile | active | ekay | Runtime instrumentation (owned device) |
| `frida-ps` | `frida-ps` | mobile | passive | ekay | List processes on USB device |
| `jadx` | `jadx` | mobile | passive | ekay | APK to Java decompiler |
| `jadx-gui` | `jadx-gui` | mobile | passive | ekay | JADX graphical UI |
| `mvt-android` | `mvt-android` | mobile | passive | ekay | Mobile Verification Toolkit Android |
| `mvt-ios` | `mvt-ios` | mobile | passive | ekay | Mobile Verification Toolkit iOS |
| `objection` | `objection` | mobile | active | ekay | Frida mobile exploration toolkit |
| `quark-engine` | `quark` | mobile | passive | ekay | Android malware score engine |

### `wireless` (12)

| Tool | Binary | Family | Risk | Origin | Summary |
| --- | --- | --- | --- | --- | --- |
| `aircrack-ng` | `aircrack-ng` | wireless | intrusive | ekay | Wi-Fi crypto (RF permission) |
| `aireplay-ng` | `aireplay-ng` | wireless | intrusive | ekay | Wi-Fi injection (authorized) |
| `airmon-ng` | `airmon-ng` | wireless | intrusive | ekay | Monitor-mode helper |
| `airodump-ng` | `airodump-ng` | wireless | intrusive | ekay | Wi-Fi traffic capture |
| `bully` | `bully` | wireless | intrusive | ekay | WPS PIN audit |
| `fern-wifi-cracker` | `fern-wifi-cracker` | wireless | intrusive | ekay | GUI Wi-Fi audit suite |
| `hcxdumptool` | `hcxdumptool` | wireless | intrusive | ekay | PMKID/handshake capture |
| `hcxpcapngtool` | `hcxpcapngtool` | wireless | passive | ekay | Convert captures for hashcat |
| `kismet` | `kismet` | wireless | passive | ekay | Wireless IDS/sniffer |
| `reaver` | `reaver` | wireless | intrusive | ekay | WPS audit (authorized RF) |
| `wifiphisher` | `wifiphisher` | wireless | restricted | ekay | Authorized evil-twin awareness lab |
| `wifite` | `wifite` | wireless | intrusive | ekay | Automated Wi-Fi audit |

## Families

| Family | Count |
| --- | ---: |
| `ad` | 10 |
| `api` | 13 |
| `auth` | 19 |
| `binary` | 22 |
| `cloud` | 19 |
| `forensics` | 15 |
| `identity` | 2 |
| `mobile` | 12 |
| `network` | 20 |
| `osint` | 33 |
| `report` | 1 |
| `se` | 9 |
| `web` | 36 |
| `wireless` | 12 |
