"""EKay HTTP control plane — kill-chain engagements + MCP backend."""

from __future__ import annotations

import os
import threading
import time
import uuid

from flask import Flask, jsonify, request

from ekay.agents import default_agents
from ekay.bus import Event, TriggerBus
from ekay.catalog import CATALOG, CATALOG_BY_NAME, families, phases_count
from ekay.evidence import EvidenceStore
from ekay.findings import FindingStore
from ekay.next_actions import suggest_next
from ekay.phases import KILL_CHAIN, MVP_PHASES, phase_info
from ekay.runner import ToolRunner
from ekay.scope import ScopeError, ScopeGuard
from ekay.status import catalog_report, tool_status

VERSION = "2.0.0"


def _env_list(name: str, default: str) -> list[str]:
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def create_app() -> Flask:
    token = os.environ.get("EKAY_TOKEN", "").strip()
    scope = ScopeGuard(_env_list("EKAY_SCOPE", "127.0.0.1,localhost,scanme.nmap.org"))
    allow_intrusive = os.environ.get("EKAY_ALLOW_INTRUSIVE", "0") == "1"
    timeout = int(os.environ.get("EKAY_TOOL_TIMEOUT", "180"))
    workers = int(os.environ.get("EKAY_MAX_CONCURRENCY", "8"))

    runner = ToolRunner(scope, timeout=timeout, allow_intrusive=allow_intrusive)
    evidence = EvidenceStore()
    findings = FindingStore()
    bus = TriggerBus(max_workers=workers)
    for agent in default_agents(runner, evidence, findings):
        bus.register(agent)

    engagements: dict[str, dict] = {}

    app = Flask("ekay")
    app.config["EKAY"] = {
        "token": token,
        "runner": runner,
        "evidence": evidence,
        "findings": findings,
        "bus": bus,
        "scope": scope,
        "engagements": engagements,
        "started": time.time(),
        "allow_intrusive": allow_intrusive,
    }

    def _auth() -> tuple[dict, int] | None:
        if not token:
            return None
        header = request.headers.get("Authorization", "")
        if header != f"Bearer {token}":
            return jsonify({"error": "unauthorized"}), 401
        return None

    def _publish_ports(engagement_id: str, host: str, ports: list[int]) -> None:
        for port in ports:
            bus.publish(
                Event(
                    kind="port.open",
                    payload={"target": host, "port": port},
                    engagement_id=engagement_id,
                )
            )

    def _follow_recon(engagement_id: str, host: str) -> None:
        deadline = time.time() + timeout
        ports: list[int] = []
        while time.time() < deadline:
            jobs = [
                j
                for j in bus.jobs()
                if j.agent == "recon" and j.engagement_id == engagement_id
            ]
            if jobs and jobs[-1].status in {"ok", "error"}:
                if jobs[-1].result:
                    ports = list(jobs[-1].result.get("ports") or [])
                break
            time.sleep(0.25)
        if not ports and not runner.which("nmap"):
            ports = [80, 443]
        _publish_ports(engagement_id, host, ports)
        # Emit typed finding events for AD agent hooks
        for f in findings.list(engagement_id=engagement_id, kind="service.ldap"):
            bus.publish(
                Event(
                    kind="finding.service.ldap",
                    payload={"target": host, "host": host, **(f.get("data") or {})},
                    engagement_id=engagement_id,
                )
            )

    @app.get("/health")
    def health():
        report = catalog_report(runner)
        return jsonify(
            {
                "ok": True,
                "name": "ekay",
                "version": VERSION,
                "edition": "red-team-kill-chain",
                "bind": f"{os.environ.get('EKAY_HOST', '127.0.0.1')}:{os.environ.get('EKAY_PORT', '8787')}",
                "catalog": report["catalog"],
                "ready": report["ready"],
                "installed": report["ready"] + report["gated"],
                "stub": report["stub"],
                "missing": report["missing"],
                "gated": report["gated"],
                "families": families(),
                "phases": phases_count(),
                "kill_chain": list(KILL_CHAIN),
                "mvp_phases": list(MVP_PHASES),
                "uptime_s": int(time.time() - app.config["EKAY"]["started"]),
                "intrusive_enabled": allow_intrusive,
                "concurrency": workers,
                "architecture": "kill-chain-trigger-bus",
                "auth_required": bool(token),
                "honest_note": report["note"],
            }
        )

    @app.get("/api/phases")
    def phases_api():
        denied = _auth()
        if denied:
            return denied
        return jsonify({"phases": phase_info(), "tool_counts": phases_count()})

    @app.get("/api/doctor")
    def doctor():
        denied = _auth()
        if denied:
            return denied
        report = catalog_report(runner)
        status_filter = request.args.get("status")
        tools = report["tools"]
        if status_filter:
            tools = [t for t in tools if t["status"] == status_filter]
        return jsonify(
            {
                "catalog": report["catalog"],
                "ready": report["ready"],
                "stub": report["stub"],
                "missing": report["missing"],
                "gated": report["gated"],
                "note": report["note"],
                "phases": phases_count(),
                "tools": tools,
            }
        )

    @app.get("/api/tools")
    def tools():
        denied = _auth()
        if denied:
            return denied
        q_family = request.args.get("family")
        q_origin = request.args.get("origin")
        q_phase = request.args.get("phase")
        q_status = request.args.get("status")
        only_ready = request.args.get("only_ready", "0") == "1"
        items = []
        for spec in CATALOG:
            if q_family and spec.family != q_family:
                continue
            if q_origin and spec.origin != q_origin:
                continue
            if q_phase and spec.phase != q_phase:
                continue
            status = tool_status(spec, runner)
            if only_ready and status != "ready":
                continue
            if q_status and status != q_status:
                continue
            items.append(
                {
                    "name": spec.name,
                    "binary": spec.binary,
                    "family": spec.family,
                    "phase": spec.phase,
                    "risk": spec.risk,
                    "origin": spec.origin,
                    "summary": spec.summary,
                    "status": status,
                    "installed": status in {"ready", "gated"},
                }
            )
        return jsonify({"count": len(items), "tools": items})

    @app.post("/api/tools/<name>/run")
    def run_tool(name: str):
        denied = _auth()
        if denied:
            return denied
        body = request.get_json(silent=True) or {}
        target = str(body.get("target") or "")
        extra = body.get("args") or []
        if not isinstance(extra, list):
            return jsonify({"error": "args must be a list of strings"}), 400
        try:
            result = runner.run(name, target, extra=[str(a) for a in extra])
        except ScopeError as exc:
            return jsonify({"error": str(exc)}), 403
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400
        eid = body.get("engagement_id") or "ad-hoc"
        evidence.add(eid, result)
        return jsonify(result.__dict__)

    @app.post("/api/engagements")
    def start_engagement():
        denied = _auth()
        if denied:
            return denied
        body = request.get_json(silent=True) or {}
        target = str(body.get("target") or "")
        osint = bool(body.get("osint", False))
        phases = body.get("phases") or list(MVP_PHASES)
        if not isinstance(phases, list):
            return jsonify({"error": "phases must be a list"}), 400
        try:
            host = scope.check(target)
        except ScopeError as exc:
            return jsonify({"error": str(exc)}), 403

        engagement_id = uuid.uuid4().hex[:10]
        engagements[engagement_id] = {
            "id": engagement_id,
            "target": host,
            "osint": osint,
            "phases": phases,
            "current_phase": "osint" if osint else "recon",
            "started": time.time(),
            "status": "running",
        }
        started = Event(
            kind="engagement.started",
            payload={"target": host, "osint": osint, "phases": phases},
            engagement_id=engagement_id,
        )
        fired = bus.publish(started)
        threading.Thread(target=_follow_recon, args=(engagement_id, host), daemon=True).start()
        return jsonify(
            {
                "engagement_id": engagement_id,
                "target": host,
                "current_phase": engagements[engagement_id]["current_phase"],
                "phases": phases,
                "agents_fired_on_start": fired,
                "architecture": "kill-chain-trigger-bus",
                "note": "Recon publishes port.open; HTTP/Nuclei agents run in parallel on web ports.",
            }
        )

    @app.get("/api/engagements")
    def list_engagements():
        denied = _auth()
        if denied:
            return denied
        return jsonify({"engagements": list(engagements.values()), "count": len(engagements)})

    @app.get("/api/engagements/<eid>")
    def get_engagement(eid: str):
        denied = _auth()
        if denied:
            return denied
        eng = engagements.get(eid)
        if not eng:
            return jsonify({"error": "unknown engagement"}), 404
        return jsonify(eng)

    @app.post("/api/engagements/<eid>/phase")
    def advance_phase(eid: str):
        denied = _auth()
        if denied:
            return denied
        eng = engagements.get(eid)
        if not eng:
            return jsonify({"error": "unknown engagement"}), 404
        body = request.get_json(silent=True) or {}
        phase = str(body.get("phase") or "")
        if phase not in KILL_CHAIN:
            return jsonify({"error": f"invalid phase; choose from {list(KILL_CHAIN)}"}), 400
        if phase in {"initial_access", "creds", "ad", "post"} and not allow_intrusive:
            return jsonify(
                {
                    "error": f"phase {phase!r} requires EKAY_ALLOW_INTRUSIVE=1 and written authorization",
                }
            ), 403
        eng["current_phase"] = phase
        fired = bus.publish(
            Event(
                kind="phase.started",
                payload={"phase": phase, "target": eng["target"]},
                engagement_id=eid,
            )
        )
        return jsonify({"engagement": eng, "agents_fired": fired})

    @app.post("/api/engagements/<eid>/finalize")
    def finalize_engagement(eid: str):
        denied = _auth()
        if denied:
            return denied
        eng = engagements.get(eid)
        if not eng:
            return jsonify({"error": "unknown engagement"}), 404
        eng["status"] = "finalized"
        eng["current_phase"] = "report"
        fired = bus.publish(
            Event(
                kind="engagement.finalize",
                payload={"target": eng["target"]},
                engagement_id=eid,
            )
        )
        return jsonify({"engagement": eng, "agents_fired": fired})

    @app.get("/api/findings")
    def findings_api():
        denied = _auth()
        if denied:
            return denied
        eid = request.args.get("engagement_id")
        kind = request.args.get("kind")
        phase = request.args.get("phase")
        rows = findings.list(engagement_id=eid, kind=kind, phase=phase)
        return jsonify({"count": len(rows), "records": rows})

    @app.get("/api/next")
    def next_api():
        denied = _auth()
        if denied:
            return denied
        eid = request.args.get("engagement_id") or ""
        if not eid or eid not in engagements:
            return jsonify({"error": "engagement_id required / unknown"}), 400
        eng = engagements[eid]
        return jsonify(
            suggest_next(
                findings,
                runner,
                eid,
                eng.get("current_phase", "recon"),
                allow_intrusive=allow_intrusive,
            )
        )

    @app.get("/api/agents")
    def agents():
        denied = _auth()
        if denied:
            return denied
        jobs = [
            {
                "agent": j.agent,
                "event_kind": j.event_kind,
                "status": j.status,
                "started": j.started,
                "finished": j.finished,
                "error": j.error,
                "result": j.result,
            }
            for j in bus.jobs()
        ]
        return jsonify({"jobs": jobs, "count": len(jobs)})

    @app.get("/api/evidence")
    def evidence_api():
        denied = _auth()
        if denied:
            return denied
        eid = request.args.get("engagement_id")
        return jsonify({"records": evidence.list(eid)})

    @app.get("/api/compare/hexstrike")
    def compare():
        denied = _auth()
        if denied:
            return denied
        hex_n = sum(1 for t in CATALOG if t.origin == "hexstrike")
        ekay_n = sum(1 for t in CATALOG if t.origin == "ekay")
        return jsonify(
            {
                "ekay_version": VERSION,
                "hexstrike_catalog_names": hex_n,
                "ekay_new_tools": ekay_n,
                "total": len(CATALOG),
                "architecture": "kill-chain-trigger-bus",
                "differences": [
                    "Kill-chain phases (osint→recon→external→creds→ad→cloud→report), not a flat tool list",
                    "Finding graph drives ekay_next_actions suggestions",
                    "Concurrent TriggerBus agents per phase event",
                    "ScopeGuard before every binary",
                    "No /api/command raw shell",
                    "Intrusive/AD/SE phases gated by EKAY_ALLOW_INTRUSIVE",
                    "MCP: meta kill-chain tools + full catalog tools",
                    "MITRE tactic tags on findings for thesis/report export",
                    f"Catalog size {len(CATALOG)} with red-team AD/post modules beyond HexStrike",
                ],
            }
        )

    app.config["CATALOG_SIZE"] = len(CATALOG_BY_NAME)
    return app


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tool_bin = os.environ.get("EKAY_TOOL_BIN") or os.path.join(root, "ekay-bin")
    os.environ["EKAY_TOOL_BIN"] = tool_bin
    os.makedirs(tool_bin, exist_ok=True)
    env_file = os.path.join(root, ".env")
    if os.path.isfile(env_file):
        with open(env_file, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                # Shell / demo exports win over .env (needed for GIF capture on alt port).
                if key and key not in os.environ:
                    os.environ[key] = val
    path = os.environ.get("PATH", "")
    if tool_bin not in path.split(":"):
        os.environ["PATH"] = tool_bin + ":" + path

    app = create_app()
    from waitress import serve

    from ekay.banner import print_startup_banner

    host, port = print_startup_banner(app)
    serve(app, host=host, threads=16, port=port)


if __name__ == "__main__":
    main()
