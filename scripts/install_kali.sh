#!/usr/bin/env bash
# Install as many EKay catalog binaries as Kali apt/go/pip can provide.
# This does NOT make 234/234 ready — some tools are manual (Gophish, MobSF, Postman, …).
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

apt-get update
apt-get install -y \
  python3 python3-venv python3-pip python3-impacket \
  nmap masscan gobuster ffuf nikto sqlmap hydra john hashcat medusa \
  whatweb wafw00f smbmap enum4linux enum4linux-ng nbtscan netexec \
  binwalk exiftool foremost steghide gdb radare2 checksec \
  aircrack-ng wifite kismet bettercap reaver bully hcxdumptool \
  bloodhound \
  seclists curl jq wget git socat proxychains4 \
  wapiti dirb dirsearch feroxbuster \
  theharvester amass subfinder fierce dnsenum \
  apktool adb \
  yara osquery \
  swaks cewl crunch cupp \
  golang-go || true

export GOPATH="${GOPATH:-$HOME/go}"
export PATH="$PATH:$GOPATH/bin:/usr/local/go/bin"
mkdir -p "$GOPATH/bin"

go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest || true
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest || true
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest || true
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest || true
go install -v github.com/projectdiscovery/katana/cmd/katana@latest || true
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest || true
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest || true
go install -v github.com/projectdiscovery/notify/cmd/notify@latest || true
go install -v github.com/ffuf/ffuf/v2@latest || true
go install -v github.com/OJ/gobuster/v3@latest || true
go install -v github.com/tomnomnom/waybackurls@latest || true
go install -v github.com/lc/gau/v2/cmd/gau@latest || true
go install -v github.com/hakluke/hakrawler@latest || true

pip3 install --break-system-packages \
  holehe maigret instaloader socialscan objection frida-tools \
  schemathesis httpie arjun || true

# Repo Python venv (HexStrike-style)
if [ ! -d "$REPO_DIR/ekay-env" ]; then
  python3 -m venv "$REPO_DIR/ekay-env"
fi
# shellcheck disable=SC1091
source "$REPO_DIR/ekay-env/bin/activate"
pip install -U pip
pip install -r "$REPO_DIR/requirements.txt"

echo
echo "[ekay] Installing SE/phishing-sim tools (user-local, no root)..."
bash "$REPO_DIR/scripts/install_phishing_tools.sh" || true

echo
echo "[ekay] Done."
echo "[ekay] Start server:  cd $REPO_DIR && source ekay-env/bin/activate && python3 ekay_server.py"
echo "[ekay] Check tools:   python3 -m ekay doctor"
echo "[ekay] Phishing tools: bash $REPO_DIR/scripts/install_phishing_tools.sh"
echo "[ekay] Expect some 'missing' until optional tools (mobsf, …) are installed manually."
