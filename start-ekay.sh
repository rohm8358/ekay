#!/usr/bin/env bash
# Simple HexStrike-style start helper
cd "$(dirname "$0")"
export EKAY_TOOL_BIN="${EKAY_TOOL_BIN:-$PWD/ekay-bin}"
export PATH="$EKAY_TOOL_BIN:$PATH"
exec python3 ekay_server.py
