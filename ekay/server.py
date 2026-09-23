"""EKay HTTP control plane. HexStrike-style: no token by default. Loopback bind. No raw shell API."""

from __future__ import annotations

import os
import threading
import time
import uuid

from flask import Flask, jsonify, request

from ekay.agents import default_agents
from ekay.bus import Event, TriggerBus
from ekay.catalog import CATALOG, CATALOG_BY_NAME, families
from ekay.evidence import EvidenceStore
from ekay.runner import ToolRunner
from ekay.scope import ScopeError, ScopeGuard
from ekay.status import catalog_report, tool_status

VERSION = "1.0.0"


def _env_list(name: str, default: str) -> list[str]:
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def create_app() -> Flask:
    # HexStrike-style: no token by default. Set EKAY_TOKEN only if you want a lock.
    token = os.environ.get("EKAY_TOKEN", "").strip()
    scope = ScopeGuard(_env_list("EKAY_SCOPE", "127.0.0.1,localhost,scanme.nmap.org"))
    allow_intrusive = os.environ.get("EKAY_ALLOW_INTRUSIVE", "0") == "1"
    timeout = int(os.environ.get("EKAY_TOOL_TIMEOUT", "180"))
    workers = int(os.environ.get("EKAY_MAX_CONCURRENCY", "8"))

    runner = ToolRunner(scope, timeout=timeout, allow_intrusive=allow_intrusive)
    evidence = EvidenceStore()
    bus = TriggerBus(max_workers=workers)
    for agent in default_agents(runner, evidence):
        bus.register(agent)

    app = Flask("ekay")
    app.config["EKAY"] = {
        "token": token,
        "runner": runner,
        "evidence": evidence,
        "bus": bus,
        "scope": scope,
        "started": time.time(),
    }

    def _auth() -> tuple[dict, int] | None:
        if not token:
            return None
        header = request.headers.get("Authorization", "")
        if header != f"Bearer {token}":
            return jsonify({"error": "unauthorized"}), 401
        return None

    @app.get("/health")
    def health():
        report = catalog_report(runner)
        return jsonify(
            {
                "ok": True,
                "name": "ekay",
                "version": VERSION,
                "bind": f"{os.environ.get('EKAY_HOST', '127.0.0.1')}:{os.environ.get('EKAY_PORT', '8787')}",
                "catalog": report["catalog"],
                "ready": report["ready"],
                "installed": report["ready"] + report["gated"],
                "missing": report["missing"],
                "gated": report["gated"],
                "families": families(),
                "uptime_s": int(time.time() - app.config["EKAY"]["started"]),
                "intrusive_enabled": allow_intrusive,
                "concurrency": workers,
                "architecture": "trigger-bus-concurrent",
                "auth_required": bool(token),
                "honest_note": report["note"],
            }
        )

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
                "missing": report["missing"],
                "gated": report["gated"],
                "note": report["note"],
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
        q_status = request.args.get("status")  # ready|missing|gated
        only_ready = request.args.get("only_ready", "0") == "1"
        items = []
        for spec in CATALOG:
            if q_family and spec.family != q_family:
                continue
            if q_origin and spec.origin != q_origin:
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
                    "risk": spec.risk,
                    "origin": spec.origin,
                    "summary": spec.summary,
                    "status": status,
                    "installed": status != "missing",
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
        evidence.add(body.get("engagement_id") or "ad-hoc", result)
        return jsonify(result.__dict__)

    @app.post("/api/engagements")
    def start_engagement():
        denied = _auth()
        if denied:
            return denied
        body = request.get_json(silent=True) or {}
        target = str(body.get("target") or "")
        osint = bool(body.get("osint", False))
        try:
            host = scope.check(target)
        except ScopeError as exc:
            return jsonify({"error": str(exc)}), 403
        engagement_id = uuid.uuid4().hex[:10]
        started = Event(
            kind="engagement.started",
            payload={"target": host, "osint": osint},
            engagement_id=engagement_id,
        )
        fired = bus.publish(started)

        def _follow_ports() -> None:
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
            for port in ports:
                bus.publish(
                    Event(
                        kind="port.open",
                        payload={"target": host, "port": port},
                        engagement_id=engagement_id,
                    )
                )

        threading.Thread(target=_follow_ports, daemon=True).start()
        return jsonify(
            {
                "engagement_id": engagement_id,
                "target": host,
                "agents_fired_on_start": fired,
                "note": "HTTP/Nuclei agents fire concurrently when recon emits port.open",
            }
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
                "hexstrike_catalog_names": hex_n,
                "ekay_new_tools": ekay_n,
                "total": len(CATALOG),
                "differences": [
                    "Concurrent trigger-bus agents, not a single sequential planner",
                    "Optional token (off by default, HexStrike-style MCP)",
                    "ScopeGuard before every binary",
                    "No /api/command raw shell",
                    "Intrusive tools gated by EKAY_ALLOW_INTRUSIVE",
                    "MCP exposes few meta-tools; catalog is queried, not dumped every turn",
                    "Windows-safe temp/evidence paths",
                    "Health uses shutil.which, not blocking which(1) storms",
                    "Evidence JSONL with argv + hashes of outputs tails",
                    "Phishing/AD/wireless/reporting tools added as restricted wrappers",
                ],
            }
        )

    # silence unused name warning for CATALOG_BY_NAME in some linters
    app.config["CATALOG_SIZE"] = len(CATALOG_BY_NAME)
    return app


def main() -> None:
    host = os.environ.get("EKAY_HOST", "127.0.0.1")
    port = int(os.environ.get("EKAY_PORT", "8787"))
    app = create_app()
    from waitress import serve

    print(f"[ekay] listening on http://{host}:{port}  (loopback recommended)")
    serve(app, host=host, threads=16, port=port)


if __name__ == "__main__":
    main()
