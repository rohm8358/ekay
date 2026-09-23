"""Built-in concurrent agents. Each fires only when its predicate matches."""

from __future__ import annotations

import re
from typing import Any

from ekay.bus import Event
from ekay.evidence import EvidenceStore
from ekay.runner import ToolRunner

_PORT_RE = re.compile(r"(\d+)/tcp\s+open", re.I)


class BaseAgent:
    name = "base"

    def __init__(self, runner: ToolRunner, evidence: EvidenceStore):
        self.runner = runner
        self.evidence = evidence


class ReconAgent(BaseAgent):
    name = "recon"

    def trigger(self, event: Event) -> bool:
        return event.kind == "engagement.started"

    def run(self, event: Event) -> dict[str, Any]:
        target = event.payload["target"]
        result = self.runner.run("nmap", target)
        self.evidence.add(event.engagement_id, result)
        ports = [int(p) for p in _PORT_RE.findall(result.stdout or "")]
        return {
            "tool": "nmap",
            "ports": ports,
            "available": result.available,
            "blocked": result.blocked_reason,
            "returncode": result.returncode,
            "ms": result.duration_ms,
        }


class HttpProbeAgent(BaseAgent):
    name = "http_probe"

    def trigger(self, event: Event) -> bool:
        if event.kind != "port.open":
            return False
        return int(event.payload.get("port", 0)) in {80, 443, 8080, 8000, 8443}

    def run(self, event: Event) -> dict[str, Any]:
        host = event.payload["target"]
        port = int(event.payload["port"])
        scheme = "https" if port in {443, 8443} else "http"
        url = f"{scheme}://{host}:{port}"
        result = self.runner.run("httpx", url)
        self.evidence.add(event.engagement_id, result)
        return {"tool": "httpx", "url": url, "ms": result.duration_ms, "available": result.available}


class NucleiAgent(BaseAgent):
    name = "nuclei"

    def trigger(self, event: Event) -> bool:
        if event.kind != "port.open":
            return False
        return int(event.payload.get("port", 0)) in {80, 443, 8080, 8000, 8443}

    def run(self, event: Event) -> dict[str, Any]:
        host = event.payload["target"]
        port = int(event.payload["port"])
        scheme = "https" if port in {443, 8443} else "http"
        url = f"{scheme}://{host}:{port}"
        result = self.runner.run("nuclei", url)
        self.evidence.add(event.engagement_id, result)
        return {"tool": "nuclei", "url": url, "ms": result.duration_ms, "available": result.available}


class OsintAgent(BaseAgent):
    name = "osint"

    def trigger(self, event: Event) -> bool:
        return event.kind == "engagement.started" and bool(event.payload.get("osint"))

    def run(self, event: Event) -> dict[str, Any]:
        target = event.payload["target"]
        result = self.runner.run("subfinder", target, extra=[target])
        self.evidence.add(event.engagement_id, result)
        return {"tool": "subfinder", "available": result.available, "blocked": result.blocked_reason}


class EvidenceAgent(BaseAgent):
    name = "evidence_index"

    def trigger(self, event: Event) -> bool:
        return event.kind.startswith("tool.") or event.kind == "engagement.started"

    def run(self, event: Event) -> dict[str, Any]:
        return {"indexed": event.id, "kind": event.kind}


def default_agents(runner: ToolRunner, evidence: EvidenceStore) -> list[BaseAgent]:
    return [
        ReconAgent(runner, evidence),
        HttpProbeAgent(runner, evidence),
        NucleiAgent(runner, evidence),
        OsintAgent(runner, evidence),
        EvidenceAgent(runner, evidence),
    ]
