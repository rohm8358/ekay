"""Blue-themed kill-chain startup banner for EKay v2."""

from __future__ import annotations

import os
from typing import Any


class BlueVisualEngine:
    """Terminal colors — neon blue / cyan cyber theme."""

    COLORS = {
        "NEON_BLUE": "\033[38;5;51m",
        "ELECTRIC_BLUE": "\033[38;5;39m",
        "DEEP_BLUE": "\033[38;5;27m",
        "ROYAL_BLUE": "\033[38;5;33m",
        "ICE_BLUE": "\033[38;5;117m",
        "STEEL_BLUE": "\033[38;5;67m",
        "MATRIX_GREEN": "\033[38;5;46m",
        "CYBER_ORANGE": "\033[38;5;208m",
        "ELECTRIC_PURPLE": "\033[38;5;129m",
        "TERMINAL_GRAY": "\033[38;5;240m",
        "BRIGHT_WHITE": "\033[97m",
        "WARNING": "\033[38;5;208m",
        "RESET": "\033[0m",
        "BOLD": "\033[1m",
        "DIM": "\033[2m",
        "PRIMARY_BORDER": "\033[38;5;39m",
        "ACCENT_LINE": "\033[38;5;51m",
        "ACCENT_GRADIENT": "\033[38;5;27m",
    }

    LOGO = r"""
███████╗██╗  ██╗ █████╗ ██╗   ██╗
██╔════╝██║ ██╔╝██╔══██╗╚██╗ ██╔╝
█████╗  █████╔╝ ███████║ ╚████╔╝
██╔══╝  ██╔═██╗ ██╔══██║  ╚██╔╝
███████╗██║  ██╗██║  ██║   ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝
"""

    @classmethod
    def create_banner(
        cls,
        host: str,
        port: int,
        catalog: int = 246,
        ready: int = 0,
        *,
        phases: dict[str, int] | None = None,
    ) -> str:
        c = cls.COLORS
        border = c["PRIMARY_BORDER"]
        accent = c["ACCENT_LINE"]
        gradient = c["ACCENT_GRADIENT"]
        reset = c["RESET"]
        bold = c["BOLD"]
        gray = c["TERMINAL_GRAY"]
        white = c["BRIGHT_WHITE"]
        green = c["MATRIX_GREEN"]
        orange = c["CYBER_ORANGE"]

        phase_line = ""
        if phases:
            order = ["osint", "recon", "external", "creds", "ad", "cloud", "post", "report"]
            bits = [f"{p}:{phases.get(p, 0)}" for p in order if p in phases]
            phase_line = " | ".join(bits)

        logo = "\n".join(f"{accent}{bold}{line}{reset}" for line in cls.LOGO.strip("\n").splitlines())

        banner = f"""
{logo}
{border}╔═══════════════════════════════════════════════════════════════════════════╗
║  {white}{bold}EKay v2{reset}{border}  ·  Red-Team Kill-Chain MCP Orchestrator                         ║
║  {accent}Phases + Findings Graph{border}  ·  {accent}Parallel Agents{border}  ·  {accent}Scope-Locked Runs{border}         ║
║  {gradient}Authorized Red Team{border} · Ethical Pentest · Kali Lab · Cursor/Claude MCP     ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  {green}▶{border} Beyond HexStrike: next actions come from {white}findings{border}, not tool spam       ║
║  {orange}▶{border} Kill-chain: osint → recon → external → creds → ad → cloud → report     ║
╚═══════════════════════════════════════════════════════════════════════════╝{reset}

{gray}[INFO] Binding http://{host}:{port}
[INFO] Catalog {catalog} tools | {ready} ready on PATH | architecture=kill-chain-trigger-bus
[INFO] Use only on assets you own or have written authorization to test{reset}
"""
        if phase_line:
            banner += f"{gray}[INFO] Phase inventory: {phase_line}{reset}\n"
        return banner

    @classmethod
    def create_startup_box(
        cls,
        host: str,
        port: int,
        *,
        catalog: int = 246,
        ready: int = 0,
        missing: int = 0,
        gated: int = 0,
        stub: int = 0,
        intrusive: bool = False,
        concurrency: int = 8,
        timeout: int = 180,
    ) -> str:
        c = cls.COLORS
        lock = "ENABLED (authorized lab)" if intrusive else "off (safe default)"
        return f"""
{c['ELECTRIC_BLUE']}{c['BOLD']}╭──────────────────────────────────────────────────────────────────────────────╮{c['RESET']}
{c['BOLD']}│{c['RESET']} {c['NEON_BLUE']}{c['BOLD']}◆ Starting EKay v2 Kill-Chain API{c['RESET']}
{c['BOLD']}├──────────────────────────────────────────────────────────────────────────────┤{c['RESET']}
{c['BOLD']}│{c['RESET']} {c['CYBER_ORANGE']}Bind{c['RESET']}         {host}:{port}
{c['BOLD']}│{c['RESET']} {c['ICE_BLUE']}Catalog{c['RESET']}      {catalog}  (ready {ready} · missing {missing} · gated {gated} · stub {stub})
{c['BOLD']}│{c['RESET']} {c['WARNING']}Intrusive{c['RESET']}    {lock}
{c['BOLD']}│{c['RESET']} {c['ELECTRIC_PURPLE']}Concurrency{c['RESET']}  {concurrency} workers · tool timeout {timeout}s
{c['BOLD']}│{c['RESET']} {c['MATRIX_GREEN']}MCP{c['RESET']}          ekay_mcp.py → this server (Cursor / Claude)
{c['BOLD']}│{c['RESET']} {c['STEEL_BLUE']}Health{c['RESET']}       curl -s http://{host}:{port}/health
{c['ELECTRIC_BLUE']}{c['BOLD']}╰──────────────────────────────────────────────────────────────────────────────╯{c['RESET']}
"""


def print_startup_banner(app: Any | None = None) -> tuple[str, int]:
    """Print banner + startup box. Returns (host, port)."""
    host = os.environ.get("EKAY_HOST", "127.0.0.1")
    port = int(os.environ.get("EKAY_PORT", "8787"))
    catalog = ready = missing = gated = stub = 0
    phases: dict[str, int] | None = None
    intrusive = os.environ.get("EKAY_ALLOW_INTRUSIVE", "0") == "1"
    concurrency = int(os.environ.get("EKAY_MAX_CONCURRENCY", "8"))
    timeout = int(os.environ.get("EKAY_TOOL_TIMEOUT", "180"))

    if app is not None:
        try:
            from ekay.catalog import phases_count
            from ekay.status import catalog_report

            runner = app.config["EKAY"]["runner"]
            report = catalog_report(runner)
            catalog = report["catalog"]
            ready = report["ready"]
            missing = report["missing"]
            gated = report["gated"]
            stub = report.get("stub", 0)
            phases = phases_count()
        except Exception:
            catalog = 246

    print(
        BlueVisualEngine.create_banner(
            host, port, catalog=catalog or 246, ready=ready, phases=phases
        )
    )
    print(
        BlueVisualEngine.create_startup_box(
            host,
            port,
            catalog=catalog or 246,
            ready=ready,
            missing=missing,
            gated=gated,
            stub=stub,
            intrusive=intrusive,
            concurrency=concurrency,
            timeout=timeout,
        )
    )
    return host, port
