"""Structured finding graph — next actions are driven by results, not random tool picks."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Finding:
    engagement_id: str
    kind: str
    title: str
    data: dict[str, Any] = field(default_factory=dict)
    source_tool: str = ""
    phase: str = "recon"
    severity: str = "info"  # info | low | medium | high | critical
    mitre: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    ts: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FindingStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._items: list[Finding] = []

    def add(self, finding: Finding) -> Finding:
        with self._lock:
            self._items.append(finding)
        return finding

    def list(
        self,
        engagement_id: str | None = None,
        kind: str | None = None,
        phase: str | None = None,
    ) -> list[dict[str, Any]]:
        with self._lock:
            rows = list(self._items)
        out = []
        for f in rows:
            if engagement_id and f.engagement_id != engagement_id:
                continue
            if kind and f.kind != kind:
                continue
            if phase and f.phase != phase:
                continue
            out.append(f.to_dict())
        return out[-500:]

    def kinds(self, engagement_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in self.list(engagement_id=engagement_id):
            k = row["kind"]
            counts[k] = counts.get(k, 0) + 1
        return counts
