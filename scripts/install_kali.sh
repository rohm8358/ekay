#!/usr/bin/env bash
# Kali install helper for an authorized-lab demo. Run as root on Kali.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y python3 python3-venv python3-pip \
  nmap masscan gobuster ffuf nikto sqlmap hydra john hashcat \
  whatweb wafw00f smbmap enum4linux-ng nbtscan \
  binwalk exiftool foremost steghide gdb radare2 \
  aircrack-ng wifite kismet bettercap \
  bloodhound neo4j \
  seclists curl jq

# Optional ProjectDiscovery / extras if already in PATH via go
echo "[ekay] Core apt packages installed."
echo "[ekay] Optional (manual): nuclei httpx subfinder naabu katana gophish gitleaks grype kerbrute"

python3 -m venv /opt/ekay-env || python3 -m venv "$HOME/ekay-env"
# shellcheck disable=SC1091
source /opt/ekay-env/bin/activate 2>/dev/null || source "$HOME/ekay-env/bin/activate"
pip install -U pip
pip install -r "$(dirname "$0")/../requirements.txt"
echo "[ekay] Python deps ready. Start with: python3 ekay/server.py"
