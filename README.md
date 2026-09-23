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
| Auth | Local Flask, no login | **Same default: no token.** Optional `EKAY_TOKEN` if you want a lock |
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
git clone https://github.com/rohm8358/ekay.git
cd ekay
python3 -m venv ekay-env
source ekay-env/bin/activate
pip install -r requirements.txt

# Terminal 1 — same idea as hexstrike_server.py
python3 ekay/server.py
```

In another terminal:

```bash
python3 -m ekay health
python3 -m ekay tools --origin ekay
python3 -m ekay compare
python3 -m ekay engage scanme.nmap.org
sleep 10
python3 -m ekay agents
python3 -m ekay run nmap scanme.nmap.org
```

Or: `./scripts/demo_kali.sh`

### curl (HexStrike-style — no Authorization header)

```bash
curl -s http://127.0.0.1:8787/health | jq .
curl -s http://127.0.0.1:8787/api/tools | jq '.count'
curl -s 'http://127.0.0.1:8787/api/tools?origin=ekay' | jq '.tools[].name'
curl -s -X POST http://127.0.0.1:8787/api/engagements \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org"}' | jq .
curl -s http://127.0.0.1:8787/api/agents | jq .
curl -s -X POST http://127.0.0.1:8787/api/tools/nmap/run \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org","args":["-Pn"]}' | jq '.returncode,.duration_ms'
```

---

## Cursor / Claude MCP

Same two-process model as HexStrike (`hexstrike_server.py` + `hexstrike_mcp.py`).

1. Start the server: `python3 ekay/server.py`
2. Add this to Cursor MCP (`~/.cursor/mcp.json` or Claude desktop config). **No token.**

```json
{
  "mcpServers": {
    "ekay": {
      "command": "python3",
      "args": ["/absolute/path/ekay/ekay/mcp_server.py", "--server", "http://127.0.0.1:8787"],
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

## Tool catalog (all names)

Legend: **Previous** = already in HexStrike’s arsenal. **New** = added in EKay (not in the HexStrike README).

Counts: **117 Previous** + **30 New** = **147** catalog entries (`GET /health` → `catalog`).

### Network / pentest

| Status | Tools |
| --- | --- |
| Previous | nmap, rustscan, masscan, autorecon, arp-scan, nbtscan, rpcclient, enum4linux, enum4linux-ng, smbmap, responder, netexec |
| New | naabu, bettercap, ligolo-ng, chisel |

### Web application pentest

| Status | Tools |
| --- | --- |
| Previous | gobuster, feroxbuster, dirsearch, ffuf, dirb, httpx, katana, hakrawler, nuclei, nikto, sqlmap, wpscan, arjun, dalfox, wafw00f, jaeles, testssl, sslscan, sslyze, whatweb, jwt-tool, wfuzz, commix, nosqlmap, tplmap, x8, zap, qsreplace |
| New | kiterunner, schemathesis, wapiti, graphqlmap |

### OSINT / recon

| Status | Tools |
| --- | --- |
| Previous | amass, subfinder, fierce, dnsenum, theharvester, gau, waybackurls, paramspider, sherlock, social-analyzer, recon-ng, maltego, spiderfoot, trufflehog, subjack, aquatone, anew, uro |
| New | dnsx, gitleaks |

### Password cracking / authentication

| Status | Tools |
| --- | --- |
| Previous | hydra, john, hashcat, medusa, patator, crackmapexec, evil-winrm, hash-identifier, hashid, ophcrack |
| New | cewl, impacket-secretsdump, impacket-getnpusers |

### Active Directory / identity

| Status | Tools |
| --- | --- |
| Previous | *(HexStrike had NetExec/CME-class network auth, not a BloodHound/Azure pack)* |
| New | bloodhound, bloodhound-python, pingcastle, kerbrute, o365spray, roadtx |

### Cloud / container pentest

| Status | Tools |
| --- | --- |
| Previous | prowler, scout-suite, trivy, kube-hunter, kube-bench, docker-bench-security, falco, checkov, terrascan, pacu, kubectl, helm, aws, az, gcloud, clair, cloudmapper, cloudsploit, opa |
| New | grype, steampipe |

### Binary / reverse engineering / exploit-dev (lab)

| Status | Tools |
| --- | --- |
| Previous | gdb, radare2, ghidra, binwalk, checksec, ropgadget, ropper, one-gadget, pwntools, angr, msfvenom, strings, objdump, readelf, upx, xxd, hexdump, pwninit |
| New | — |

### Forensics / IR

| Status | Tools |
| --- | --- |
| Previous | volatility3, foremost, steghide, exiftool, autopsy, photorec, testdisk, stegsolve, bulk-extractor, zsteg, outguess, scalpel |
| New | yara, osqueryi |

### Wireless (authorized RF only)

| Status | Tools |
| --- | --- |
| Previous | — |
| New | aircrack-ng, wifite, kismet, hcxdumptool |

### Social engineering / phishing simulation (approved campaigns only)

| Status | Tools |
| --- | --- |
| Previous | — |
| New | gophish, swaks |

### Reporting

| Status | Tools |
| --- | --- |
| Previous | — |
| New | faraday-cli |

### New-only list (copy/paste)

`naabu` `dnsx` `impacket-secretsdump` `impacket-getnpusers` `bettercap` `bloodhound` `bloodhound-python` `pingcastle` `kerbrute` `ligolo-ng` `chisel` `kiterunner` `schemathesis` `wapiti` `graphqlmap` `gitleaks` `grype` `steampipe` `cewl` `aircrack-ng` `wifite` `kismet` `hcxdumptool` `yara` `osqueryi` `gophish` `swaks` `o365spray` `roadtx` `faraday-cli`

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
| `GET /api/tools` | no (unless `EKAY_TOKEN` set) | Filter `family`, `origin` |
| `POST /api/tools/<name>/run` | no (unless `EKAY_TOKEN` set) | `{target, args[]}` |
| `POST /api/engagements` | no (unless `EKAY_TOKEN` set) | Start concurrent agents |
| `GET /api/agents` | no (unless `EKAY_TOKEN` set) | Job list |
| `GET /api/evidence` | no (unless `EKAY_TOKEN` set) | JSONL records |
| `GET /api/compare/hexstrike` | no (unless `EKAY_TOKEN` set) | Difference list |

There is **no** `/api/command`.

---

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `EKAY_TOKEN` | empty | Optional. Empty = HexStrike-style open local API |
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
