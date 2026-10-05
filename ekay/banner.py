"""Blue-themed HexStrike-style startup banner for EKay."""

from __future__ import annotations

import os
from typing import Any


class BlueVisualEngine:
    """Terminal colors — blue / cyan cyber theme (HexStrike-style layout)."""

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

    @classmethod
    def create_banner(cls, host: str, port: int, catalog: int = 234, ready: int = 0) -> str:
        c = cls.COLORS
        border = c["PRIMARY_BORDER"]
        accent = c["ACCENT_LINE"]
        gradient = c["ACCENT_GRADIENT"]
        reset = c["RESET"]
        bold = c["BOLD"]
        gray = c["TERMINAL_GRAY"]
        white = c["BRIGHT_WHITE"]

        title = f"{accent}{bold}"
        banner = f"""
{title}
███████╗██╗  ██╗ █████╗ ██╗   ██╗
██╔════╝██║ ██╔╝██╔══██╗╚██╗ ██╔╝
█████╗  █████╔╝ ███████║ ╚████╔╝
██╔══╝  ██╔═██╗ ██╔══██║  ╚██╔╝
███████╗██║  ██╗██║  ██║   ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝
{reset}
{border}┌─────────────────────────────────────────────────────────────────────┐
│  {white}EKay v2 — Red-Team Kill-Chain MCP Orchestrator{border}                    │
│  {accent}Phases + Findings Graph | Parallel Agents | Scope-Locked{border}           │
│  {gradient}Authorized Red Team | Ethical Pentest | Kali Lab | PhD demos{border}       │
└─────────────────────────────────────────────────────────────────────┘{reset}

{gray}[INFO] Server starting on {host}:{port}
[INFO] {catalog} catalog tools | {ready} ready on PATH | Kill-chain trigger-bus
[INFO] Beyond HexStrike: findings drive next actions (authorized use only){reset}
"""
        return banner

    @classmethod
    def create_startup_box(
        cls,
        host: str,
        port: int,
        *,
        catalog: int = 234,
        ready: int = 0,
        missing: int = 0,
        gated: int = 0,
        intrusive: bool = False,
        concurrency: int = 8,
        timeout: int = 180,
    ) -> str:
        c = cls.COLORS
        return f"""
{c['ELECTRIC_BLUE']}{c['BOLD']}╭─────────────────────────────────────────────────────────────────────────────╮{c['RESET']}
{c['BOLD']}│{c['RESET']} {c['NEON_BLUE']}Starting EKay v2 Kill-Chain API Server{c['RESET']}
{c['BOLD']}├─────────────────────────────────────────────────────────────────────────────┤{c['RESET']}
{c['BOLD']}│{c['RESET']} {c['CYBER_ORANGE']}🌐 Bind:{c['RESET']} {host}:{port}
{c['BOLD']}│{c['RESET']} {c['ICE_BLUE']}📦 Catalog:{c['RESET']} {catalog} | Ready: {ready} | Missing: {missing} | Gated: {gated}
{c['BOLD']}│{c['RESET']} {c['WARNING']}🔓 Intrusive:{c['RESET']} {intrusive}
{c['BOLD']}│{c['RESET']} {c['ELECTRIC_PURPLE']}🧵 Concurrency:{c['RESET']} {concurrency} | Tool Timeout: {timeout}s
{c['BOLD']}│{c['RESET']} {c['MATRIX_GREEN']}✨ Blue Visual Engine:{c['RESET']} Active
{c['ELECTRIC_BLUE']}{c['BOLD']}╰─────────────────────────────────────────────────────────────────────────────╯{c['RESET']}
"""


def print_startup_banner(app: Any | None = None) -> tuple[str, int]:
    """Print banner + startup box. Returns (host, port)."""
    host = os.environ.get("EKAY_HOST", "127.0.0.1")
    port = int(os.environ.get("EKAY_PORT", "8787"))
    catalog = ready = missing = gated = 0
    intrusive = os.environ.get("EKAY_ALLOW_INTRUSIVE", "0") == "1"
    concurrency = int(os.environ.get("EKAY_MAX_CONCURRENCY", "8"))
    timeout = int(os.environ.get("EKAY_TOOL_TIMEOUT", "180"))

    if app is not None:
        try:
            from ekay.status import catalog_report

            runner = app.config["EKAY"]["runner"]
            report = catalog_report(runner)
            catalog = report["catalog"]
            ready = report["ready"]
            missing = report["missing"]
            gated = report["gated"]
        except Exception:
            catalog = 234

    print(BlueVisualEngine.create_banner(host, port, catalog=catalog or 234, ready=ready))
    print(
        BlueVisualEngine.create_startup_box(
            host,
            port,
            catalog=catalog or 234,
            ready=ready,
            missing=missing,
            gated=gated,
            intrusive=intrusive,
            concurrency=concurrency,
            timeout=timeout,
        )
    )
    return host, port
