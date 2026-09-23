"""CLI: ekay serve | ekay health | ekay tools | ekay engage HOST"""

from __future__ import annotations

import argparse
import json
import os
import sys

import httpx


def _url() -> str:
    return os.environ.get("EKAY_URL", f"http://{os.environ.get('EKAY_HOST', '127.0.0.1')}:{os.environ.get('EKAY_PORT', '8787')}")


def _token() -> str:
    return os.environ.get("EKAY_TOKEN", "change-me-before-demo")


def _http() -> httpx.Client:
    return httpx.Client(
        base_url=_url(),
        headers={"Authorization": f"Bearer {_token()}"},
        timeout=30.0,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ekay")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("serve", help="Run the EKay API on EKAY_HOST:EKAY_PORT")
    sub.add_parser("health", help="GET /health")
    p_tools = sub.add_parser("tools", help="List catalog")
    p_tools.add_argument("--family")
    p_tools.add_argument("--origin")
    p_run = sub.add_parser("run", help="Run one tool")
    p_run.add_argument("name")
    p_run.add_argument("target")
    p_run.add_argument("args", nargs="*")
    p_eng = sub.add_parser("engage", help="Start concurrent engagement")
    p_eng.add_argument("target")
    p_eng.add_argument("--osint", action="store_true")
    sub.add_parser("agents", help="List agent jobs")
    sub.add_parser("compare", help="EKay vs HexStrike")

    args = parser.parse_args(argv)

    if args.cmd == "serve":
        from ekay.server import main as serve_main

        serve_main()
        return 0

    client = _http()
    if args.cmd == "health":
        print(json.dumps(client.get("/health").json(), indent=2))
        return 0
    if args.cmd == "tools":
        params = {}
        if args.family:
            params["family"] = args.family
        if args.origin:
            params["origin"] = args.origin
        print(json.dumps(client.get("/api/tools", params=params).json(), indent=2))
        return 0
    if args.cmd == "run":
        body = {"target": args.target, "args": args.args}
        print(json.dumps(client.post(f"/api/tools/{args.name}/run", json=body).json(), indent=2))
        return 0
    if args.cmd == "engage":
        print(json.dumps(client.post("/api/engagements", json={"target": args.target, "osint": args.osint}).json(), indent=2))
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
