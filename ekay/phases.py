"""Red-team kill-chain phases — what makes EKay more than a HexStrike tool dump."""

from __future__ import annotations

from typing import Any, Literal

Phase = Literal[
    "osint",
    "recon",
    "external",
    "initial_access",
    "creds",
    "ad",
    "cloud",
    "post",
    "report",
    "wireless",
    "mobile",
]

# Ordered playbook for a full authorized engagement (MVP runs the first three).
KILL_CHAIN: list[Phase] = [
    "osint",
    "recon",
    "external",
    "initial_access",
    "creds",
    "ad",
    "cloud",
    "post",
    "report",
]

MVP_PHASES: list[Phase] = ["osint", "recon", "external", "report"]

FAMILY_TO_PHASE: dict[str, Phase] = {
    "osint": "osint",
    "network": "recon",
    "web": "external",
    "api": "external",
    "auth": "creds",
    "ad": "ad",
    "identity": "ad",
    "cloud": "cloud",
    "wireless": "wireless",
    "mobile": "mobile",
    "binary": "post",
    "forensics": "post",
    "se": "initial_access",
    "report": "report",
}

# High-level MITRE ATT&CK tactic tags per phase (thesis / report friendly).
PHASE_MITRE: dict[str, list[str]] = {
    "osint": ["TA0043"],  # Reconnaissance
    "recon": ["TA0043", "TA0007"],  # Reconnaissance / Discovery
    "external": ["TA0001", "TA0002"],  # Initial Access / Execution (web)
    "initial_access": ["TA0001"],
    "creds": ["TA0006"],  # Credential Access
    "ad": ["TA0007", "TA0008"],  # Discovery / Lateral Movement
    "cloud": ["TA0007", "TA0003"],
    "post": ["TA0003", "TA0004"],
    "report": [],
    "wireless": ["TA0001"],
    "mobile": ["TA0001"],
}

PHASE_SUMMARY: dict[str, str] = {
    "osint": "Passive / open-source intel on the target org or domain",
    "recon": "Host/port/service discovery inside engagement scope",
    "external": "Web/API attack-surface probing and vuln templates",
    "initial_access": "Authorized foothold simulation (gated)",
    "creds": "Credential access / spray / offline crack (gated)",
    "ad": "Active Directory enumeration and path analysis (gated)",
    "cloud": "Cloud posture and identity assessment",
    "post": "Post-exploitation / host triage (gated)",
    "report": "Evidence packaging and report export",
    "wireless": "RF / Wi-Fi assessment (requires RF authorization)",
    "mobile": "Mobile app / device assessment (owned devices)",
}


def phase_for_family(family: str) -> Phase:
    return FAMILY_TO_PHASE.get(family, "recon")


def phase_info() -> list[dict[str, Any]]:
    return [
        {
            "phase": p,
            "summary": PHASE_SUMMARY.get(p, ""),
            "mitre_tactics": PHASE_MITRE.get(p, []),
            "mvp": p in MVP_PHASES,
        }
        for p in KILL_CHAIN
    ]


def next_phase(current: str) -> str | None:
    try:
        idx = KILL_CHAIN.index(current)  # type: ignore[arg-type]
    except ValueError:
        return None
    if idx + 1 >= len(KILL_CHAIN):
        return None
    return KILL_CHAIN[idx + 1]
