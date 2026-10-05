#!/usr/bin/env python3
"""Export the live EKay tool catalog to docs/TOOLS.md and docs/catalog.json."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ekay.catalog import CATALOG, families, phases_count  # noqa: E402
from ekay.phases import PHASE_SUMMARY, KILL_CHAIN  # noqa: E402


def main() -> int:
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)

    by_phase: dict[str, list] = defaultdict(list)
    rows = []
    for spec in CATALOG:
        row = {
            "name": spec.name,
            "binary": spec.binary,
            "family": spec.family,
            "phase": spec.phase,
            "risk": spec.risk,
            "origin": spec.origin,
            "summary": spec.summary,
        }
        rows.append(row)
        by_phase[spec.phase].append(row)

    catalog_json = {
        "name": "ekay",
        "version": "2.0.0",
        "total": len(rows),
        "phases": phases_count(),
        "families": families(),
        "tools": rows,
    }
    (docs / "catalog.json").write_text(json.dumps(catalog_json, indent=2) + "\n", encoding="utf-8")

    hex_n = sum(1 for r in rows if r["origin"] == "hexstrike")
    ekay_n = sum(1 for r in rows if r["origin"] == "ekay")

    lines: list[str] = [
        "# EKay Tool Catalog",
        "",
        f"**Total tools:** {len(rows)}  ",
        f"**HexStrike-origin:** {hex_n} · **EKay-only:** {ekay_n}",
        "",
        "Generated from `ekay/catalog.py` via `scripts/export_catalog.py`.",
        "",
        "## Phase inventory",
        "",
        "| Phase | Tools | Summary |",
        "| --- | ---: | --- |",
    ]
    counts = phases_count()
    for phase in list(KILL_CHAIN) + sorted(set(counts) - set(KILL_CHAIN)):
        if phase not in counts:
            continue
        lines.append(f"| `{phase}` | {counts[phase]} | {PHASE_SUMMARY.get(phase, '')} |")

    lines += ["", "## Tools by kill-chain phase", ""]

    phase_order = [p for p in KILL_CHAIN if p in by_phase] + sorted(
        set(by_phase) - set(KILL_CHAIN)
    )
    for phase in phase_order:
        tools = sorted(by_phase[phase], key=lambda t: t["name"])
        lines += [
            f"### `{phase}` ({len(tools)})",
            "",
            "| Tool | Binary | Family | Risk | Origin | Summary |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for t in tools:
            lines.append(
                f"| `{t['name']}` | `{t['binary']}` | {t['family']} | {t['risk']} | {t['origin']} | {t['summary']} |"
            )
        lines.append("")

    lines += [
        "## Families",
        "",
        "| Family | Count |",
        "| --- | ---: |",
    ]
    for fam, n in families().items():
        lines.append(f"| `{fam}` | {n} |")
    lines.append("")

    (docs / "TOOLS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {docs / 'TOOLS.md'} ({len(rows)} tools)")
    print(f"wrote {docs / 'catalog.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
