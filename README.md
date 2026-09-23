# EKay

### Concurrent MCP cybersecurity orchestrator for **authorized** testing

**EKay** keeps a HexStrike-class tool catalog (Nmap, Nuclei, SQLMap, Hashcat, Prowler, …) but **does not copy HexStrike’s architecture**. HexStrike is one MCP planner calling tools **one stage at a time**. EKay is a **trigger bus**: each agent has a predicate and **fires concurrently**.

PhD / Kali lab project. Author: [rohm8358](https://github.com/rohm8358). MIT license.

> Use only on assets you own or have **written permission** to test. Phishing, password spraying, wireless, and AD tools stay **restricted** until `EKAY_ALLOW_INTRUSIVE=1`.

---

## How EKay is different (and more advanced) than HexStrike

| Topic | HexStrike-AI | EKay |
| --- | --- | --- |
| Control flow | Single LLM planner, sequential tool calls | **TriggerBus** — many agents, each with a predicate, **parallel** |
| API shell | Documented `/api/command` arbitrary commands | **No raw shell API** |
| Auth | Local Flask often unauthenticated | **Bearer token required** (except `/health`) |
| Scope | Wrong flags can scan out of scope | **ScopeGuard** before every binary |
| Tool schemas | 150+ MCP tools dumped every LLM turn | **7 meta MCP tools**; catalog is queried |
| Health | Historically blocked on many `which` subprocesses | `shutil.which` + cache |
| Dangerous tools | Same path as nmap | **Risk classes** + `EKAY_ALLOW_INTRUSIVE` |
| Evidence | Logs / visual cards | Append-only **JSONL** with argv + output tails |
| New families | Weak on phishing-sim, BloodHound, wifi, reporting | **Gophish, BloodHound, Kerbrute, Aircrack, Faraday, …** (wrappers) |
| Binding | Reports of binding beyond loopback | Default **127.0.0.1** |
| Windows `/tmp` | Known crash class | `tempfile` evidence dir |

EKay is **not** “zero-bug software”. It is **designed to remove HexStrike’s classes of faults** (open command API, no scope, sequential planner, schema bloat). Tests cover scope, arg sanitization, intrusive gating, and concurrent agents.

---

## Architecture

```
LLM / Cursor / Claude
        |  MCP (7 tools)
        v
 ekay/mcp_server.py  --->  HTTP 127.0.0.1:8787
                                |
                                +-- ScopeGuard
                                +-- ToolRunner (no shell=True)
                                +-- TriggerBus (thread pool)
                                      |- ReconAgent      trigger: engagement.started
                                      |- OsintAgent      trigger: engagement.started + osint
                                      |- HttpProbeAgent  trigger: port.open in {80,443,...}
                                      |- NucleiAgent     trigger: same ports  (PARALLEL with HTTP)
                                      |- EvidenceAgent   trigger: start/tool events
```

When recon finishes, EKay emits `port.open` events. **httpx and nuclei start at the same time**, not after each other.

---

## Quick start (Kali)

```bash
sudo git clone https://github.com/rohm8358/ekay.git
cd ekay
python3 -m venv ekay-env
source ekay-env/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit EKAY_TOKEN to a long random string
export $(grep -v '^#' .env | xargs)
chmod +x scripts/install_kali.sh scripts/demo_kali.sh
# optional: sudo ./scripts/install_kali.sh
python3 -m ekay serve
```

In another terminal:

```bash
export EKAY_TOKEN='your-token-from-.env'
export EKAY_URL=http://127.0.0.1:8787

python3 -m ekay health
python3 -m ekay tools --origin ekay
python3 -m ekay compare

# Legal public test host from Nmap project — still confirm policy with your supervisor
python3 -m ekay engage scanme.nmap.org
sleep 10
python3 -m ekay agents

python3 -m ekay run nmap scanme.nmap.org
```

Or one-shot demo:

```bash
EKAY_TOKEN=kali-demo-token ./scripts/demo_kali.sh
```

### curl (same as HexStrike-style writeups)

```bash
# health does not require a token
curl -s http://127.0.0.1:8787/health | jq .

# catalog
curl -s -H "Authorization: Bearer $EKAY_TOKEN" \
  http://127.0.0.1:8787/api/tools | jq '.count'

# only new EKay tools
curl -s -H "Authorization: Bearer $EKAY_TOKEN" \
  'http://127.0.0.1:8787/api/tools?origin=ekay' | jq '.tools[].name'

# concurrent engagement
curl -s -X POST http://127.0.0.1:8787/api/engagements \
  -H "Authorization: Bearer $EKAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org"}' | jq .

# agent timeline
curl -s -H "Authorization: Bearer $EKAY_TOKEN" \
  http://127.0.0.1:8787/api/agents | jq .

# one tool
curl -s -X POST http://127.0.0.1:8787/api/tools/nmap/run \
  -H "Authorization: Bearer $EKAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org","args":["-Pn"]}' | jq '.returncode,.duration_ms'
```

---

## Cursor / Claude MCP

1. Start `python3 -m ekay serve`
2. Copy `ekay-mcp.json` into Cursor MCP config and set the real path + `EKAY_TOKEN`

```json
{
  "mcpServers": {
    "ekay": {
      "command": "python3",
      "args": ["/absolute/path/ekay/ekay/mcp_server.py", "--server", "http://127.0.0.1:8787"],
      "env": { "EKAY_TOKEN": "your-token" },
      "timeout": 300
    }
  }
}
```

MCP tools (intentionally small): `ekay_health`, `ekay_list_tools`, `ekay_run_tool`, `ekay_start_engagement`, `ekay_agent_jobs`, `ekay_evidence`, `ekay_vs_hexstrike`.

---

## Tests

```bash
pip install -r requirements.txt
python3 -m pytest -q
```

---

## Tool catalog

HexStrike-class names are tagged `origin=hexstrike`. EKay-only names are `origin=ekay`.

**EKay-only (not in HexStrike README):** naabu, dnsx, Impacket helpers, bettercap, BloodHound, bloodhound-python, PingCastle, kerbrute, ligolo-ng, chisel, kiterunner, schemathesis, wapiti, graphqlmap, gitleaks, grype, steampipe, cewl, aircrack-ng, wifite, kismet, hcxdumptool, yara, osqueryi, gophish, swaks, o365spray, roadtx, faraday-cli.

Intrusive/restricted binaries **will not execute** until:

```bash
export EKAY_ALLOW_INTRUSIVE=1
```

and the target is inside `EKAY_SCOPE`.

---

## HTTP API

| Endpoint | Auth | Description |
| --- | --- | --- |
| `GET /health` | no | Catalog size, installed count, concurrency |
| `GET /api/tools` | yes | Filter `family`, `origin` |
| `POST /api/tools/<name>/run` | yes | `{target, args[]}` |
| `POST /api/engagements` | yes | Start concurrent agents |
| `GET /api/agents` | yes | Job list |
| `GET /api/evidence` | yes | JSONL records |
| `GET /api/compare/hexstrike` | yes | Difference list |

There is **no** `/api/command`.

---

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `EKAY_TOKEN` | `change-me-before-demo` | API bearer token |
| `EKAY_HOST` | `127.0.0.1` | Bind address |
| `EKAY_PORT` | `8787` | Bind port |
| `EKAY_SCOPE` | `127.0.0.1,localhost,scanme.nmap.org` | Allowed hosts/CIDRs |
| `EKAY_ALLOW_INTRUSIVE` | `0` | Hydra/Hashcat/Gophish/wifi/AD dump |
| `EKAY_MAX_CONCURRENCY` | `8` | Agent thread pool |
| `EKAY_TOOL_TIMEOUT` | `180` | Seconds per binary |

---

## What a supervisor should see in 5 minutes

1. `GET /health` shows `architecture: trigger-bus-concurrent` and a large catalog.
2. `POST /api/engagements` returns multiple `agents_fired_on_start`.
3. `GET /api/agents` shows **recon** plus **http_probe** and **nuclei** overlapping in time (if those ports exist / tools installed).
4. Out-of-scope host returns **403**.
5. `hydra` without `EKAY_ALLOW_INTRUSIVE` returns `blocked_reason`.
6. `pytest -q` is green.

---

## Disclaimer

EKay wraps **local** security programs. Installing Nuclei does not make EKay “autonomous pentest.” The LLM still needs a human engagement, a scope file, and verification of findings. Social-engineering modules are **simulation platforms** (e.g. Gophish) for approved awareness tests, not crimeware.
