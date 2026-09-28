# EKay

### Concurrent MCP cybersecurity orchestrator for **authorized** testing

Same **two-process** model as HexStrike (`ekay_server.py` + `ekay_mcp.py`).

> Use only on assets you own or have **written permission** to test.

---

## Quick start (HexStrike-style)

```bash
# 1. Clone
git clone https://github.com/rohm8358/ekay.git
cd ekay

# 2. Create virtual environment
python3 -m venv ekay-env
source ekay-env/bin/activate          # Linux/Mac
# ekay-env\Scripts\activate           # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. (Kali) Install as many security binaries as possible
sudo ./scripts/install_kali.sh

# 5. Start the server (Terminal 1)
python3 ekay_server.py
```

Health check (Terminal 2):

```bash
curl -s http://127.0.0.1:8787/health
python3 -m ekay doctor
```

---

## Cursor / Claude MCP

1. Keep `python3 ekay_server.py` running.
2. Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ekay": {
      "command": "/absolute/path/to/ekay/ekay-env/bin/python3",
      "args": [
        "/absolute/path/to/ekay/ekay_mcp.py",
        "--server",
        "http://127.0.0.1:8787"
      ],
      "timeout": 300
    }
  }
}
```

MCP exposes:
- **8 meta tools** — `ekay_health`, `ekay_doctor`, `ekay_list_tools`, `ekay_run_tool`, `ekay_start_engagement`, `ekay_agent_jobs`, `ekay_evidence`, `ekay_vs_hexstrike`
- **234 catalog tools** — one MCP tool per binary (`nmap`, `nuclei`, `sqlmap`, …) just like HexStrike

---

## Why requirements.txt is small (this is normal)

`requirements.txt` installs **Python packages for EKay itself** (Flask, MCP, httpx) — **not** Nmap/Nuclei/SQLMap.

| File | What it installs |
| --- | --- |
| `requirements.txt` | Orchestrator Python deps (~5 packages) |
| `scripts/install_kali.sh` | Real security tools via apt / go / pip |
| Host `PATH` | Whatever is already on your Kali |

Same model as HexStrike: the MCP server **wraps** tools; it does not ship 234 scanners inside git.

After start, `/health` shows:

| Field | Meaning |
| --- | --- |
| `catalog` | Always **234** (names in the catalog) |
| `ready` | Binary found on `PATH` + allowed by policy |
| `gated` | Installed, but needs `EKAY_ALLOW_INTRUSIVE=1` |
| `missing` | Not installed on this machine yet |

Missing tools do **not** crash the server. Running them returns `blocked_reason` so the LLM can pick another tool.

---

## How EKay differs from HexStrike

| Topic | HexStrike-AI | EKay |
| --- | --- | --- |
| Control flow | Single LLM planner, sequential | **TriggerBus** — agents fire in parallel |
| MCP tools | 150+ dumped every turn | **8 meta + 234 catalog** |
| Raw shell API | `/api/command` | **No raw shell API** |
| Scope | Easy to scan out of scope | **ScopeGuard** before every binary |
| Dangerous tools | Same path as nmap | Risk classes + `EKAY_ALLOW_INTRUSIVE` |

---

## Useful commands

```bash
python3 -m ekay doctor                 # ready / missing / gated
python3 -m ekay doctor --status missing
python3 -m ekay tools --only-ready
python3 -m ekay engage scanme.nmap.org
python3 -m ekay run nmap scanme.nmap.org
```

### curl

```bash
curl -s http://127.0.0.1:8787/health
curl -s http://127.0.0.1:8787/api/tools | jq '.count'
curl -s -X POST http://127.0.0.1:8787/api/tools/nmap/run \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org","args":["-Pn"]}'
```

---

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `EKAY_TOKEN` | empty | Optional API lock |
| `EKAY_HOST` | `127.0.0.1` | Bind address |
| `EKAY_PORT` | `8787` | Bind port |
| `EKAY_SCOPE` | `127.0.0.1,localhost,scanme.nmap.org` | Allowed targets |
| `EKAY_ALLOW_INTRUSIVE` | `0` | Hydra/Hashcat/wifi/AD/phishing-sim |
| `EKAY_MAX_CONCURRENCY` | `8` | Agent thread pool |
| `EKAY_TOOL_TIMEOUT` | `180` | Seconds per binary |
| `EKAY_MCP_CATALOG_TOOLS` | `1` | Register all 234 tools on MCP |

---

## Tests

```bash
pip install -r requirements.txt
python3 -m pytest -q
```

---

## Disclaimer

EKay wraps **local** security programs for **authorized** assessments. Installing Nuclei does not make EKay autonomous pentest. Social-engineering and wireless modules are for approved lab / contracted work only.
