"""Suggest next red-team actions from the finding graph (planner aid for MCP)."""

from __future__ import annotations

from typing import Any

from ekay.catalog import CATALOG_BY_NAME, tools_for_phase
from ekay.findings import FindingStore
from ekay.phases import PHASE_SUMMARY, next_phase
from ekay.runner import ToolRunner
from ekay.status import tool_status


def suggest_next(
    findings: FindingStore,
    runner: ToolRunner,
    engagement_id: str,
    current_phase: str,
    *,
    allow_intrusive: bool = False,
    limit: int = 8,
) -> dict[str, Any]:
    rows = findings.list(engagement_id=engagement_id)
    kinds = findings.kinds(engagement_id)
    suggestions: list[dict[str, Any]] = []

    def _add(tool: str, reason: str, phase: str, priority: int = 50) -> None:
        spec = CATALOG_BY_NAME.get(tool)
        if not spec:
            return
        status = tool_status(spec, runner)
        if status == "missing":
            return
        if spec.risk in {"intrusive", "restricted"} and not allow_intrusive:
            return
        suggestions.append(
            {
                "tool": tool,
                "phase": phase,
                "risk": spec.risk,
                "status": status,
                "reason": reason,
                "priority": priority,
                "mcp_hint": f"Run via ekay_run_tool name={tool} or catalog tool `{tool}`",
            }
        )

    open_ports = [f for f in rows if f["kind"] == "port.open"]
    web_urls = [f for f in rows if f["kind"] == "url.http"]
    subdomains = [f for f in rows if f["kind"] == "host.subdomain"]
    smb = [f for f in rows if f["kind"] == "service.smb"]
    ldap = [f for f in rows if f["kind"] == "service.ldap"]

    if current_phase in {"osint", "recon"} and not subdomains:
        _add("subfinder", "No subdomain findings yet — start passive DNS OSINT", "osint", 90)
        _add("amass", "Broaden passive subdomain coverage", "osint", 80)

    if current_phase in {"osint", "recon"} and not open_ports:
        _add("nmap", "No open ports recorded — run host recon", "recon", 95)
        _add("naabu", "Fast port discovery alternative", "recon", 85)

    if open_ports and not web_urls:
        _add("httpx", "Open ports found — probe HTTP(S) services", "external", 92)
        _add("whatweb", "Fingerprint web stacks on discovered hosts", "external", 70)

    if web_urls:
        _add("nuclei", "HTTP services present — template vuln scan", "external", 93)
        _add("nikto", "Classic web server checks", "external", 75)
        _add("katana", "Crawl discovered web apps for endpoints", "external", 72)

    if smb:
        _add("enum4linux-ng", "SMB service seen — authorized AD/SMB enum", "ad", 88)
        _add("netexec", "SMB/WinRM credentialed checks (if creds in scope)", "creds", 70)

    if ldap:
        _add("ldapdomaindump", "LDAP exposed — domain dump for AD mapping", "ad", 90)
        _add("bloodhound-python", "Collect BloodHound graph (authorized AD)", "ad", 85)
        _add("certipy", "Check AD CS attack paths", "ad", 80)

    if current_phase == "external" and web_urls and allow_intrusive:
        _add("sqlmap", "Only with written auth — SQLi verification on in-scope URLs", "external", 40)

    # Phase progression hint tools
    nxt = next_phase(current_phase)
    if nxt and len(suggestions) < limit:
        for spec in tools_for_phase(nxt)[:3]:
            _add(spec.name, f"Candidate for next phase ({nxt}): {spec.summary}", nxt, 30)

    suggestions.sort(key=lambda s: -s["priority"])
    # dedupe by tool
    seen: set[str] = set()
    uniq: list[dict[str, Any]] = []
    for s in suggestions:
        if s["tool"] in seen:
            continue
        seen.add(s["tool"])
        uniq.append(s)
        if len(uniq) >= limit:
            break

    return {
        "engagement_id": engagement_id,
        "current_phase": current_phase,
        "phase_summary": PHASE_SUMMARY.get(current_phase, ""),
        "next_phase": nxt,
        "finding_kinds": kinds,
        "finding_count": len(rows),
        "suggestions": uniq,
        "note": (
            "Suggestions are planner aids for authorized testing. "
            "Cursor/Claude may still refuse sensitive intents — run gated tools with explicit engagement scope."
        ),
    }
