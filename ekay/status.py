"""Per-tool readiness: ready | stub | missing | gated (intrusive blocked).

'stub' means a file exists on PATH for the tool but it is not a real, runnable
binary — either an EKay placeholder shim (marked with 'ekay-shim') or an
exec-wrapper whose final target is missing/garbage. These used to be reported
as 'ready' because a file existed; they are now flagged honestly.
"""

from __future__ import annotations

import os
import re
from typing import Any

from ekay.catalog import CATALOG, ToolSpec
from ekay.runner import ToolRunner

_SHIM_MARKERS = ("ekay-shim", "missing — install", "missing - install")
# Capture the first path/word after `exec` in a wrapper script.
_EXEC_RE = re.compile(r"""exec\s+['"]?([^'"\s]+)""")


def is_real_tool(path: str | None, _depth: int = 0) -> bool:
    """True only if `path` resolves to a genuine, runnable tool.

    Handles: native ELF binaries, ordinary python/bash tool scripts, and
    ekay-bin exec-wrappers (followed one hop to their target). Returns False
    for ekay-shim placeholders and for wrappers pointing at a missing or
    non-shebang/garbage target (e.g. the broken 'OK sherlock -' file).
    """
    if _depth > 5 or not path or not os.path.isfile(path) or not os.access(path, os.X_OK):
        return False
    try:
        with open(path, "rb") as fh:
            blob = fh.read(4096)
    except OSError:
        return False
    if blob[:4] == b"\x7fELF":
        return True  # native binary
    if blob[:2] != b"#!":
        return False  # not a script and not ELF -> garbage/placeholder
    text = blob.decode("utf-8", "ignore")
    if any(marker in text for marker in _SHIM_MARKERS):
        return False  # explicit ekay placeholder shim
    match = _EXEC_RE.search(text)
    if match:
        target = match.group(1)
        # Follow a real exec-wrapper (has an absolute/relative path target).
        if target and "/" in target and not target.startswith("$"):
            if not os.path.isabs(target):
                # Resolve relative to any `cd /abs/path` in the wrapper (Kali SET style),
                # else relative to the wrapper's own directory.
                cd_match = re.search(r"""(?:^|\n)\s*cd\s+['"]?(/[^'"\n]+)""", text)
                base = cd_match.group(1) if cd_match else os.path.dirname(path)
                target = os.path.normpath(os.path.join(base, target))
            return is_real_tool(target, _depth + 1)
    return True  # ordinary tool script (python/bash) that is not a shim


def tool_status(spec: ToolSpec, runner: ToolRunner) -> str:
    path = runner.which(spec.binary)
    if not path:
        return "missing"
    if not is_real_tool(path):
        return "stub"
    if spec.risk in {"intrusive", "restricted"} and not runner.allow_intrusive:
        return "gated"
    return "ready"


def catalog_report(runner: ToolRunner) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counts = {"ready": 0, "stub": 0, "missing": 0, "gated": 0}
    for spec in CATALOG:
        status = tool_status(spec, runner)
        counts[status] += 1
        rows.append(
            {
                "name": spec.name,
                "binary": spec.binary,
                "family": spec.family,
                "phase": spec.phase,
                "origin": spec.origin,
                "risk": spec.risk,
                "status": status,
                # installed=True only when a genuine, runnable tool is present.
                "installed": status in {"ready", "gated"},
                "summary": spec.summary,
            }
        )
    return {
        "catalog": len(CATALOG),
        "ready": counts["ready"],
        "stub": counts["stub"],
        "missing": counts["missing"],
        "gated": counts["gated"],
        "note": (
            "status=ready: genuine runnable binary present and allowed. "
            "status=stub: a placeholder/broken wrapper exists but will NOT run "
            "(install the real tool). status=missing: nothing on PATH. "
            "status=gated: real tool present but intrusive/restricted and blocked by policy."
        ),
        "tools": rows,
    }
