#!/usr/bin/env bash
# Run this in your terminal (needs your sudo password):
#   bash scripts/sudo_install_remaining.sh
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y \
  bettercap chisel cupp yara osquery apktool adb jadx \
  hcxdumptool hcxtools wifiphisher testssl.sh zaproxy \
  awscli grype opa gitleaks trufflehog kubectl helm \
  responder john aircrack-ng bloodhound enum4linux-ng \
  foremost steghide gdb python3-impacket golang-go \
  seclists feroxbuster dirsearch || true

echo "[ekay] apt pass done. Rebuild wrappers:"
cd "$(dirname "$0")/.."
./ekay-env/bin/ekay-python scripts/resume_fix_tools.py || true
echo "[ekay] restart: pkill -f ekay_server.py; ./start-ekay.sh"
