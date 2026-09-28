"""EKay MCP bridge — HexStrike-style: meta tools + full 234-tool catalog."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any

import httpx

from ekay.catalog import CATALOG

_SAFE_MCP_NAME = re.compile(r"[^a-zA-Z0-9_]")


def _mcp_name(tool_name: str) -> str:
    """Map catalog name to a valid MCP tool name (nmap -> nmap, jwt-tool -> jwt_tool)."""
    return _SAFE_MCP_NAME.sub("_", tool_name)


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
    parser.add_argument(
        "--catalog-tools",
        default=os.environ.get("EKAY_MCP_CATALOG_TOOLS", "1"),
        help="1=register all 234 catalog tools as MCP tools (HexStrike-style). 0=meta tools only.",
    )
    args = parser.parse_args(argv)

    try:
        from mcp.server.fastmcp import FastMCP
    except Exception:
        sys.stderr.write("Install mcp v1: pip install 'mcp>=1.2.0,<2'\n")
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
    def ekay_list_tools(family: str = "", origin: str = "", only_ready: bool = False) -> dict[str, Any]:
        """List catalog tools. only_ready=False shows all 234 (default, HexStrike-style)."""
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

    # HexStrike-style: expose every catalog entry as its own MCP tool.
    if str(args.catalog_tools).strip() not in {"0", "false", "False", "no"}:
        used_names = {
            "ekay_health",
            "ekay_doctor",
            "ekay_list_tools",
            "ekay_run_tool",
            "ekay_start_engagement",
            "ekay_agent_jobs",
            "ekay_evidence",
            "ekay_vs_hexstrike",
        }

        for spec in CATALOG:
            tool_name = _mcp_name(spec.name)
            if tool_name in used_names:
                tool_name = f"ekay_{tool_name}"
            used_names.add(tool_name)

            # Closure-safe factory
            def _register(spec=spec, tool_name=tool_name) -> None:
                description = (
                    f"[{spec.family}/{spec.origin}/{spec.risk}] {spec.summary}. "
                    f"Binary={spec.binary}. Target must be in EKAY_SCOPE. "
                    f"If binary is missing on PATH, returns blocked_reason=missing "
                    f"(install with sudo ./scripts/install_kali.sh)."
                )

                @mcp.tool(name=tool_name, description=description)
                def _run(target: str, args_json: str = "[]") -> dict[str, Any]:
                    extra = json.loads(args_json or "[]")
                    resp = http.post(
                        f"/api/tools/{spec.name}/run",
                        json={"target": target, "args": extra},
                    )
                    return resp.json()

            _register()

        sys.stderr.write(f"[ekay-mcp] registered {len(CATALOG)} catalog tools + 8 meta tools\n")

    mcp.run()


if __name__ == "__main__":
    main()
