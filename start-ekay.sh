#!/usr/bin/env bash
# Start EKay v2 kill-chain API (HexStrike-style two-process: this + ekay_mcp.py)
set -euo pipefail
cd "$(dirname "$0")"
export EKAY_TOOL_BIN="${EKAY_TOOL_BIN:-$PWD/ekay-bin}"
export PATH="$EKAY_TOOL_BIN:$PATH"

if [[ -x "$PWD/ekay-env/bin/ekay-python" ]]; then
  exec "$PWD/ekay-env/bin/ekay-python" ekay_server.py
fi
exec python3 ekay_server.py
