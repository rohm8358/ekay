"""Kill-chain phase agents — fire from findings/events, not a single LLM loop."""

from __future__ import annotations

import re
from typing import Any

from ekay.bus import Event
from ekay.evidence import EvidenceStore
from ekay.findings import Finding, FindingStore
from ekay.phases import PHASE_MITRE
from ekay.runner import ToolRunner

_PORT_RE = re.compile(r"(\d+)/tcp\s+open", re.I)
_SERVICE_RE = re.compile(r"(\d+)/tcp\s+open\s+(\S+)", re.I)

WEB_PORTS = {80, 443, 8080, 8000, 8443, 8888, 3000, 5000}
SMB_PORTS = {139, 445}
LDAP_PORTS = {389, 636, 3268, 3269}


class BaseAgent:
    name = "base"
    phase = "recon"

    def __init__(
        self,
        runner: ToolRunner,
        evidence: EvidenceStore,
        findings: FindingStore,
    ):
        self.runner = runner
        self.evidence = evidence
        self.findings = findings

    def _finding(
        self,
        event: Event,
        kind: str,
        title: str,
        data: dict[str, Any],
        *,
        source_tool: str = "",
        severity: str = "info",
    ) -> Finding:
        return self.findings.add(
            Finding(
                engagement_id=event.engagement_id,
                kind=kind,
                title=title,
                data=data,
                source_tool=source_tool,
                phase=self.phase,
                severity=severity,
                mitre=list(PHASE_MITRE.get(self.phase, [])),
            )
        )


class OsintAgent(BaseAgent):
    name = "osint"
    phase = "osint"

    def trigger(self, event: Event) -> bool:
        return event.kind == "engagement.started" and bool(event.payload.get("osint"))

    def run(self, event: Event) -> dict[str, Any]:
        target = event.payload["target"]
        result = self.runner.run("subfinder", target)
        self.evidence.add(event.engagement_id, result)
        hosts = [
            line.strip()
            for line in (result.stdout or "").splitlines()
            if line.strip() and not line.startswith("[")
        ][:50]
        for host in hosts:
            self._finding(
                event,
                "host.subdomain",
                f"Subdomain {host}",
                {"host": host},
                source_tool="subfinder",
            )
        if not hosts and result.available and not result.blocked_reason:
            self._finding(
                event,
                "osint.empty",
                "subfinder returned no hosts",
                {"target": target},
                source_tool="subfinder",
            )
        return {
            "tool": "subfinder",
            "hosts": hosts,
            "available": result.available,
            "blocked": result.blocked_reason,
        }


class ReconAgent(BaseAgent):
    name = "recon"
    phase = "recon"

    def trigger(self, event: Event) -> bool:
        return event.kind == "engagement.started"

    def run(self, event: Event) -> dict[str, Any]:
        target = event.payload["target"]
        result = self.runner.run("nmap", target)
        self.evidence.add(event.engagement_id, result)
        ports: list[int] = []
        services: list[dict[str, Any]] = []
        for match in _SERVICE_RE.finditer(result.stdout or ""):
            port = int(match.group(1))
            svc = match.group(2).lower()
            ports.append(port)
            services.append({"port": port, "service": svc})
            self._finding(
                event,
                "port.open",
                f"Open port {port}/{svc}",
                {"host": target, "port": port, "service": svc},
                source_tool="nmap",
                severity="low",
            )
            if port in SMB_PORTS or "smb" in svc or "microsoft-ds" in svc:
                self._finding(
                    event,
                    "service.smb",
                    f"SMB on {target}:{port}",
                    {"host": target, "port": port},
                    source_tool="nmap",
                    severity="medium",
                )
            if port in LDAP_PORTS or "ldap" in svc:
                self._finding(
                    event,
                    "service.ldap",
                    f"LDAP on {target}:{port}",
                    {"host": target, "port": port},
                    source_tool="nmap",
                    severity="medium",
                )
        if not ports:
            ports = [int(p) for p in _PORT_RE.findall(result.stdout or "")]
            for port in ports:
                self._finding(
                    event,
                    "port.open",
                    f"Open port {port}",
                    {"host": target, "port": port},
                    source_tool="nmap",
                )
        return {
            "tool": "nmap",
            "ports": ports,
            "services": services,
            "available": result.available,
            "blocked": result.blocked_reason,
            "returncode": result.returncode,
            "ms": result.duration_ms,
        }


class HttpProbeAgent(BaseAgent):
    name = "http_probe"
    phase = "external"

    def trigger(self, event: Event) -> bool:
        if event.kind != "port.open":
            return False
        return int(event.payload.get("port", 0)) in WEB_PORTS

    def run(self, event: Event) -> dict[str, Any]:
        host = event.payload["target"]
        port = int(event.payload["port"])
        scheme = "https" if port in {443, 8443} else "http"
        url = f"{scheme}://{host}:{port}"
        result = self.runner.run("httpx", url)
        self.evidence.add(event.engagement_id, result)
        if result.available and not result.blocked_reason:
            self._finding(
                event,
                "url.http",
                f"HTTP service {url}",
                {"url": url, "host": host, "port": port},
                source_tool="httpx",
                severity="low",
            )
        return {"tool": "httpx", "url": url, "ms": result.duration_ms, "available": result.available}


class NucleiAgent(BaseAgent):
    name = "nuclei"
    phase = "external"

    def trigger(self, event: Event) -> bool:
        if event.kind != "port.open":
            return False
        return int(event.payload.get("port", 0)) in WEB_PORTS

    def run(self, event: Event) -> dict[str, Any]:
        host = event.payload["target"]
        port = int(event.payload["port"])
        scheme = "https" if port in {443, 8443} else "http"
        url = f"{scheme}://{host}:{port}"
        result = self.runner.run("nuclei", url)
        self.evidence.add(event.engagement_id, result)
        hits = [ln for ln in (result.stdout or "").splitlines() if ln.strip()][:30]
        for hit in hits:
            self._finding(
                event,
                "vuln.nuclei",
                hit[:200],
                {"url": url, "raw": hit},
                source_tool="nuclei",
                severity="medium",
            )
        return {"tool": "nuclei", "url": url, "hits": len(hits), "ms": result.duration_ms}


class AdEnumAgent(BaseAgent):
    """Fires when engagement advances into AD phase or LDAP/SMB findings exist."""

    name = "ad_enum"
    phase = "ad"

    def trigger(self, event: Event) -> bool:
        if event.kind == "phase.started" and event.payload.get("phase") == "ad":
            return True
        return event.kind == "finding.service.ldap"

    def run(self, event: Event) -> dict[str, Any]:
        target = event.payload.get("target") or event.payload.get("host") or ""
        if not target:
            return {"skipped": True, "reason": "no target"}
        # Prefer ldapdomaindump; fall back to enum4linux-ng
        tool = "ldapdomaindump" if self.runner.which("ldapdomaindump") else "enum4linux-ng"
        if tool == "enum4linux-ng" and not self.runner.which("enum4linux-ng"):
            tool = "enum4linux"
        result = self.runner.run(tool, target)
        self.evidence.add(event.engagement_id, result)
        self._finding(
            event,
            "ad.enum",
            f"AD/SMB enum via {tool}",
            {"host": target, "tool": tool, "blocked": result.blocked_reason},
            source_tool=tool,
            severity="medium",
        )
        return {"tool": tool, "available": result.available, "blocked": result.blocked_reason}


class ReportAgent(BaseAgent):
    name = "report"
    phase = "report"

    def trigger(self, event: Event) -> bool:
        return event.kind in {"engagement.finalize", "phase.started"} and (
            event.kind == "engagement.finalize" or event.payload.get("phase") == "report"
        )

    def run(self, event: Event) -> dict[str, Any]:
        eid = event.engagement_id
        kinds = self.findings.kinds(eid)
        summary = {
            "engagement_id": eid,
            "finding_kinds": kinds,
            "finding_count": sum(kinds.values()),
            "evidence_records": len(self.evidence.list(eid)),
        }
        self._finding(
            event,
            "report.summary",
            "Engagement report summary",
            summary,
            source_tool="ekay",
        )
        return summary


def default_agents(
    runner: ToolRunner,
    evidence: EvidenceStore,
    findings: FindingStore,
) -> list[BaseAgent]:
    return [
        OsintAgent(runner, evidence, findings),
        ReconAgent(runner, evidence, findings),
        HttpProbeAgent(runner, evidence, findings),
        NucleiAgent(runner, evidence, findings),
        AdEnumAgent(runner, evidence, findings),
        ReportAgent(runner, evidence, findings),
    ]
