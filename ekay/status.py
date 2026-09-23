"""Per-tool readiness: ready | missing | gated (intrusive blocked)."""

from __future__ import annotations

from typing import Any

from ekay.catalog import CATALOG, ToolSpec
from ekay.runner import ToolRunner


def tool_status(spec: ToolSpec, runner: ToolRunner) -> str:
    if not runner.which(spec.binary):
        return "missing"
    if spec.risk in {"intrusive", "restricted"} and not runner.allow_intrusive:
        return "gated"
    return "ready"


def catalog_report(runner: ToolRunner) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counts = {"ready": 0, "missing": 0, "gated": 0}
    for spec in CATALOG:
        status = tool_status(spec, runner)
        counts[status] += 1
        rows.append(
            {
                "name": spec.name,
                "binary": spec.binary,
                "family": spec.family,
                "origin": spec.origin,
                "risk": spec.risk,
                "status": status,
                "installed": status != "missing",
                "summary": spec.summary,
            }
        )
    return {
        "catalog": len(CATALOG),
        "ready": counts["ready"],
        "missing": counts["missing"],
        "gated": counts["gated"],
        "note": (
            "EKay wraps host binaries; it does not ship 234 scanners. "
            "Install tools on Kali (scripts/install_kali.sh), then re-check. "
            "status=ready means binary is on PATH and allowed by policy."
        ),
        "tools": rows,
    }
