#!/usr/bin/env bash
# Install as many catalog binaries as Kali apt/go/pip can provide.
# EKay still will NOT show 234/234 ready — some tools are manual (Gophish, Postman, etc.).
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
  python3 python3-venv python3-pip python3-impacket \
  nmap masscan gobuster ffuf nikto sqlmap hydra john hashcat medusa \
  whatweb wafw00f smbmap enum4linux-ng nbtscan netexec crackmapexec \
  binwalk exiftool foremost steghide gdb radare2 checksec \
  aircrack-ng wifite kismet bettercap reaver bully hcxdumptool \
  bloodhound neo4j \
  seclists curl jq wget git socat proxychains4 \
  wapiti dirb dirsearch feroxbuster sqlmap \
  theharvester amass subfinder \
  apktool adb \
  yara osquery \
  swaks cewl crunch cupp \
  steghide autopsy \
  golang-go || true

# Go-based ProjectDiscovery / extras (best-effort)
export GOPATH="${GOPATH:-$HOME/go}"
export PATH="$PATH:$GOPATH/bin:/usr/local/go/bin"
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest || true
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest || true
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest || true
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest || true
go install -v github.com/projectdiscovery/katana/cmd/katana@latest || true
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest || true
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest || true
go install -v github.com/ffuf/ffuf/v2@latest || true

pip3 install --break-system-packages \
  holehe maigret instaloader socialscan objection frida-tools \
  schemathesis httpie gitleaks 2>/dev/null \
  || pip3 install holehe maigret instaloader socialscan objection frida-tools schemathesis httpie || true

python3 -m venv /opt/ekay-env || python3 -m venv "$HOME/ekay-env"
# shellcheck disable=SC1091
source /opt/ekay-env/bin/activate 2>/dev/null || source "$HOME/ekay-env/bin/activate"
pip install -U pip
pip install -r "$(dirname "$0")/../requirements.txt"

echo "[ekay] Deps installed (best-effort)."
echo "[ekay] Run: python3 -m ekay doctor"
echo "[ekay] Expect many 'missing' until you install optional tools (gophish, mobsf, nuclei templates, etc.)."
echo "[ekay] Start: python3 ekay/server.py"
