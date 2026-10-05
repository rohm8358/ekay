"""CLI: ekay serve | health | doctor | tools | engage | findings | next …"""

from __future__ import annotations

import argparse
import json
import os
import sys

import httpx


def _url() -> str:
    return os.environ.get(
        "EKAY_URL",
        f"http://{os.environ.get('EKAY_HOST', '127.0.0.1')}:{os.environ.get('EKAY_PORT', '8787')}",
    )


def _token() -> str:
    return os.environ.get("EKAY_TOKEN", "").strip()


def _http() -> httpx.Client:
    headers = {}
    if _token():
        headers["Authorization"] = f"Bearer {_token()}"
    return httpx.Client(base_url=_url(), headers=headers, timeout=30.0)


def _doctor_local(status_filter: str | None, only_ready: bool) -> int:
    from ekay.runner import ToolRunner
    from ekay.scope import ScopeGuard
    from ekay.status import catalog_report
    from ekay.catalog import phases_count

    scope = ScopeGuard(
        [x.strip() for x in os.environ.get("EKAY_SCOPE", "127.0.0.1,localhost").split(",") if x.strip()]
    )
    allow = os.environ.get("EKAY_ALLOW_INTRUSIVE", "0") == "1"
    report = catalog_report(ToolRunner(scope, allow_intrusive=allow))
    tools = report["tools"]
    if status_filter:
        tools = [t for t in tools if t["status"] == status_filter]
    if only_ready:
        tools = [t for t in tools if t["status"] == "ready"]
    out = {
        "edition": "red-team-kill-chain",
        "catalog": report["catalog"],
        "ready": report["ready"],
        "missing": report["missing"],
        "gated": report["gated"],
        "phases": phases_count(),
        "note": report["note"],
        "tools": tools if status_filter or only_ready else tools,
        "summary_only": not (status_filter or only_ready),
    }
    if out["summary_only"]:
        out["tools"] = [t for t in tools if t["status"] == "ready"][:50]
        out["tip"] = "Full lists: ekay doctor --status missing | --status ready | --status gated"
    print(json.dumps(out, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ekay")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("serve", help="Run the EKay API on EKAY_HOST:EKAY_PORT")
    sub.add_parser("health", help="GET /health")
    p_doc = sub.add_parser("doctor", help="Show ready / missing / gated tools (no server needed)")
    p_doc.add_argument("--status", choices=["ready", "missing", "gated", "stub"])
    p_doc.add_argument("--only-ready", action="store_true")
    p_doc.add_argument("--remote", action="store_true", help="Query running server /api/doctor")
    p_tools = sub.add_parser("tools", help="List catalog")
    p_tools.add_argument("--family")
    p_tools.add_argument("--origin")
    p_tools.add_argument("--phase")
    p_tools.add_argument("--status", choices=["ready", "missing", "gated", "stub"])
    p_tools.add_argument("--only-ready", action="store_true")
    p_run = sub.add_parser("run", help="Run one tool")
    p_run.add_argument("name")
    p_run.add_argument("target")
    p_run.add_argument("args", nargs="*")
    p_eng = sub.add_parser("engage", help="Start kill-chain engagement")
    p_eng.add_argument("target")
    p_eng.add_argument("--osint", action="store_true")
    p_phase = sub.add_parser("phase", help="Advance engagement phase")
    p_phase.add_argument("engagement_id")
    p_phase.add_argument("phase")
    p_find = sub.add_parser("findings", help="List findings")
    p_find.add_argument("--engagement-id", default="")
    p_find.add_argument("--kind", default="")
    p_next = sub.add_parser("next", help="Suggest next actions from findings")
    p_next.add_argument("engagement_id")
    sub.add_parser("phases", help="List kill-chain phases")
    sub.add_parser("agents", help="List agent jobs")
    sub.add_parser("compare", help="EKay vs HexStrike")
    p_fin = sub.add_parser("finalize", help="Finalize engagement / report summary")
    p_fin.add_argument("engagement_id")

    args = parser.parse_args(argv)

    if args.cmd == "serve":
        from ekay.server import main as serve_main

        serve_main()
        return 0

    if args.cmd == "doctor" and not args.remote:
        return _doctor_local(args.status, args.only_ready)

    client = _http()
    if args.cmd == "health":
        print(json.dumps(client.get("/health").json(), indent=2))
        return 0
    if args.cmd == "doctor":
        params = {}
        if args.status:
            params["status"] = args.status
        print(json.dumps(client.get("/api/doctor", params=params).json(), indent=2))
        return 0
    if args.cmd == "tools":
        params = {}
        if args.family:
            params["family"] = args.family
        if args.origin:
            params["origin"] = args.origin
        if args.phase:
            params["phase"] = args.phase
        if args.status:
            params["status"] = args.status
        if args.only_ready:
            params["only_ready"] = "1"
        print(json.dumps(client.get("/api/tools", params=params).json(), indent=2))
        return 0
    if args.cmd == "run":
        body = {"target": args.target, "args": args.args}
        print(json.dumps(client.post(f"/api/tools/{args.name}/run", json=body).json(), indent=2))
        return 0
    if args.cmd == "engage":
        print(
            json.dumps(
                client.post("/api/engagements", json={"target": args.target, "osint": args.osint}).json(),
                indent=2,
            )
        )
        return 0
    if args.cmd == "phase":
        print(
            json.dumps(
                client.post(f"/api/engagements/{args.engagement_id}/phase", json={"phase": args.phase}).json(),
                indent=2,
            )
        )
        return 0
    if args.cmd == "finalize":
        print(json.dumps(client.post(f"/api/engagements/{args.engagement_id}/finalize", json={}).json(), indent=2))
        return 0
    if args.cmd == "findings":
        params = {}
        if args.engagement_id:
            params["engagement_id"] = args.engagement_id
        if args.kind:
            params["kind"] = args.kind
        print(json.dumps(client.get("/api/findings", params=params).json(), indent=2))
        return 0
    if args.cmd == "next":
        print(json.dumps(client.get("/api/next", params={"engagement_id": args.engagement_id}).json(), indent=2))
        return 0
    if args.cmd == "phases":
        print(json.dumps(client.get("/api/phases").json(), indent=2))
        return 0
    if args.cmd == "agents":
        print(json.dumps(client.get("/api/agents").json(), indent=2))
        return 0
    if args.cmd == "compare":
        print(json.dumps(client.get("/api/compare/hexstrike").json(), indent=2))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
