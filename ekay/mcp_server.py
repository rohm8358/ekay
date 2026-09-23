"""Thin MCP facade. Few tools on purpose — hexstrike dumps 150 schemas every turn."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import httpx


def _client(base: str, token: str) -> httpx.Client:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.Client(
        base_url=base.rstrip("/"),
        headers=headers,
        timeout=float(os.environ.get("EKAY_MCP_TIMEOUT", "300")),
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="EKay MCP stdio bridge")
    parser.add_argument("--server", default=os.environ.get("EKAY_URL", "http://127.0.0.1:8787"))
    parser.add_argument("--token", default=os.environ.get("EKAY_TOKEN", ""))
    args = parser.parse_args(argv)

    try:
        from mcp.server.fastmcp import FastMCP
    except Exception:
        sys.stderr.write("Install mcp: pip install mcp\n")
        raise

    mcp = FastMCP("ekay")
    http = _client(args.server, args.token)

    @mcp.tool()
    def ekay_health() -> dict[str, Any]:
        """Server health: catalog size, ready/missing/gated binary counts."""
        return http.get("/health").json()

    @mcp.tool()
    def ekay_doctor(status: str = "") -> dict[str, Any]:
        """Diagnose tools. status=ready|missing|gated or empty for full report."""
        params = {"status": status} if status else {}
        resp = http.get("/api/doctor", params=params)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_list_tools(family: str = "", origin: str = "", only_ready: bool = True) -> dict[str, Any]:
        """List tools. Default only_ready=True so Cursor never sees missing binaries."""
        params: dict[str, str] = {}
        if family:
            params["family"] = family
        if origin:
            params["origin"] = origin
        if only_ready:
            params["only_ready"] = "1"
        resp = http.get("/api/tools", params=params)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_run_tool(name: str, target: str, args_json: str = "[]") -> dict[str, Any]:
        """Run one catalog tool against an in-scope target. args_json is a JSON list of extra flags."""
        extra = json.loads(args_json or "[]")
        resp = http.post(f"/api/tools/{name}/run", json={"target": target, "args": extra})
        return resp.json()

    @mcp.tool()
    def ekay_start_engagement(target: str, osint: bool = False) -> dict[str, Any]:
        """Start concurrent agents (recon, then HTTP+Nuclei in parallel on open web ports)."""
        resp = http.post("/api/engagements", json={"target": target, "osint": osint})
        return resp.json()

    @mcp.tool()
    def ekay_agent_jobs() -> dict[str, Any]:
        """Show concurrent agent jobs and results."""
        resp = http.get("/api/agents")
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_evidence(engagement_id: str = "") -> dict[str, Any]:
        """List evidence JSONL records."""
        params = {"engagement_id": engagement_id} if engagement_id else {}
        resp = http.get("/api/evidence", params=params)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_vs_hexstrike() -> dict[str, Any]:
        """How EKay differs from HexStrike."""
        resp = http.get("/api/compare/hexstrike")
        resp.raise_for_status()
        return resp.json()

    mcp.run()


if __name__ == "__main__":
    main()
