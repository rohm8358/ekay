"""Append-only evidence log for the professor demo and thesis artefacts."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

from ekay.runner import RunResult, evidence_dir


class EvidenceStore:
    def __init__(self, path: str | None = None):
        self.path = Path(path or evidence_dir()) / "evidence.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def add(self, engagement_id: str, result: RunResult) -> None:
        record = {
            "ts": time.time(),
            "engagement_id": engagement_id,
            "tool": result.tool,
            "binary": result.binary,
            "argv": result.argv,
            "returncode": result.returncode,
            "duration_ms": result.duration_ms,
            "available": result.available,
            "blocked_reason": result.blocked_reason,
            "stdout_tail": (result.stdout or "")[-4000:],
            "stderr_tail": (result.stderr or "")[-2000:],
        }
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")

    def list(self, engagement_id: str | None = None) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                if engagement_id and item.get("engagement_id") != engagement_id:
                    continue
                rows.append(item)
        return rows[-200:]
