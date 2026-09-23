#!/usr/bin/env bash
# Professor demo on Kali. Scope is scanme.nmap.org (Nmap's public test host).
set -euo pipefail
cd "$(dirname "$0")/.."
export EKAY_TOKEN="${EKAY_TOKEN:-kali-demo-token}"
export EKAY_SCOPE="${EKAY_SCOPE:-127.0.0.1,localhost,scanme.nmap.org}"
export EKAY_ALLOW_INTRUSIVE=0
export EKAY_HOST=127.0.0.1
export EKAY_PORT=8787

python3 -m ekay serve &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 2

echo "=== HEALTH ==="
curl -sS "http://127.0.0.1:8787/health" | python3 -m json.tool | head -n 40

echo "=== ENGAGE scanme.nmap.org (concurrent agents) ==="
curl -sS -X POST "http://127.0.0.1:8787/api/engagements" \
  -H "Authorization: Bearer $EKAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org"}' | python3 -m json.tool

sleep 8
echo "=== AGENT JOBS ==="
curl -sS "http://127.0.0.1:8787/api/agents" \
  -H "Authorization: Bearer $EKAY_TOKEN" | python3 -m json.tool | head -n 80

echo "=== VS HEXSTRIKE ==="
curl -sS "http://127.0.0.1:8787/api/compare/hexstrike" \
  -H "Authorization: Bearer $EKAY_TOKEN" | python3 -m json.tool
