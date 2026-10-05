"""EKay MCP bridge — kill-chain meta tools + full catalog (Cursor / Claude)."""

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
        help="1=register all catalog tools as MCP tools. 0=meta tools only.",
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
        """Server health: kill-chain edition, catalog, ready/missing/gated counts."""
        return http.get("/health").json()

    @mcp.tool()
    def ekay_doctor(status: str = "") -> dict[str, Any]:
        """Diagnose tools. status=ready|missing|gated|stub or empty for full report."""
        params = {"status": status} if status else {}
        resp = http.get("/api/doctor", params=params)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_phases() -> dict[str, Any]:
        """List kill-chain phases (osint→recon→external→ad→…) and tool counts."""
        resp = http.get("/api/phases")
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_list_tools(
        family: str = "",
        origin: str = "",
        phase: str = "",
        only_ready: bool = False,
    ) -> dict[str, Any]:
        """List catalog tools. Filter by family, origin (hexstrike|ekay), or kill-chain phase."""
        params: dict[str, str] = {}
        if family:
            params["family"] = family
        if origin:
            params["origin"] = origin
        if phase:
            params["phase"] = phase
        if only_ready:
            params["only_ready"] = "1"
        resp = http.get("/api/tools", params=params)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_run_tool(name: str, target: str, args_json: str = "[]", engagement_id: str = "") -> dict[str, Any]:
        """Run one catalog tool against an in-scope target. Prefer recon/OSINT/report tools from chat."""
        extra = json.loads(args_json or "[]")
        body: dict[str, Any] = {"target": target, "args": extra}
        if engagement_id:
            body["engagement_id"] = engagement_id
        resp = http.post(f"/api/tools/{name}/run", json=body)
        return resp.json()

    @mcp.tool()
    def ekay_start_engagement(target: str, osint: bool = True, phases_json: str = "") -> dict[str, Any]:
        """Start a kill-chain engagement (recon + parallel web agents). osint=true also runs subfinder."""
        body: dict[str, Any] = {"target": target, "osint": osint}
        if phases_json.strip():
            body["phases"] = json.loads(phases_json)
        resp = http.post("/api/engagements", json=body)
        return resp.json()

    @mcp.tool()
    def ekay_advance_phase(engagement_id: str, phase: str) -> dict[str, Any]:
        """Advance engagement to a phase: osint|recon|external|creds|ad|cloud|post|report."""
        resp = http.post(f"/api/engagements/{engagement_id}/phase", json={"phase": phase})
        return resp.json()

    @mcp.tool()
    def ekay_finalize(engagement_id: str) -> dict[str, Any]:
        """Finalize engagement and build report summary findings."""
        resp = http.post(f"/api/engagements/{engagement_id}/finalize", json={})
        return resp.json()

    @mcp.tool()
    def ekay_findings(engagement_id: str = "", kind: str = "", phase: str = "") -> dict[str, Any]:
        """List structured findings (ports, URLs, vulns, AD hints) for an engagement."""
        params: dict[str, str] = {}
        if engagement_id:
            params["engagement_id"] = engagement_id
        if kind:
            params["kind"] = kind
        if phase:
            params["phase"] = phase
        resp = http.get("/api/findings", params=params)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_next_actions(engagement_id: str) -> dict[str, Any]:
        """Suggest next tools from the finding graph (planner aid — better than HexStrike random picks)."""
        resp = http.get("/api/next", params={"engagement_id": engagement_id})
        return resp.json()

    @mcp.tool()
    def ekay_agent_jobs() -> dict[str, Any]:
        """Show concurrent agent jobs and results."""
        resp = http.get("/api/agents")
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_evidence(engagement_id: str = "") -> dict[str, Any]:
        """List evidence JSONL records (argv + output tails)."""
        params = {"engagement_id": engagement_id} if engagement_id else {}
        resp = http.get("/api/evidence", params=params)
        resp.raise_for_status()
        return resp.json()

    @mcp.tool()
    def ekay_vs_hexstrike() -> dict[str, Any]:
        """How EKay kill-chain edition differs from HexStrike."""
        resp = http.get("/api/compare/hexstrike")
        resp.raise_for_status()
        return resp.json()

    meta = {
        "ekay_health",
        "ekay_doctor",
        "ekay_phases",
        "ekay_list_tools",
        "ekay_run_tool",
        "ekay_start_engagement",
        "ekay_advance_phase",
        "ekay_finalize",
        "ekay_findings",
        "ekay_next_actions",
        "ekay_agent_jobs",
        "ekay_evidence",
        "ekay_vs_hexstrike",
    }

    if str(args.catalog_tools).strip() not in {"0", "false", "False", "no"}:
        used_names = set(meta)
        for spec in CATALOG:
            tool_name = _mcp_name(spec.name)
            if tool_name in used_names:
                tool_name = f"ekay_{tool_name}"
            used_names.add(tool_name)

            def _register(spec=spec, tool_name=tool_name) -> None:
                description = (
                    f"[phase={spec.phase}/{spec.family}/{spec.origin}/{spec.risk}] {spec.summary}. "
                    f"Binary={spec.binary}. Target must be in EKAY_SCOPE. "
                    f"Missing binary => blocked_reason (install via scripts/install_kali.sh)."
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

        sys.stderr.write(
            f"[ekay-mcp] registered {len(CATALOG)} catalog tools + {len(meta)} kill-chain meta tools\n"
        )

    mcp.run()


if __name__ == "__main__":
    main()
