"""Concurrent trigger bus. Agents subscribe with predicates and fire in parallel."""

from __future__ import annotations

import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class Event:
    kind: str
    payload: dict[str, Any]
    engagement_id: str
    ts: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


class Agent(Protocol):
    name: str

    def trigger(self, event: Event) -> bool: ...

    def run(self, event: Event) -> dict[str, Any]: ...


@dataclass
class AgentJob:
    agent: str
    event_id: str
    event_kind: str
    engagement_id: str
    status: str
    started: float
    finished: float | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class TriggerBus:
    def __init__(self, max_workers: int = 8):
        self._agents: list[Agent] = []
        self._lock = threading.Lock()
        self._jobs: list[AgentJob] = []
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ekay")
        self._futures: list[Future] = []

    def register(self, agent: Agent) -> None:
        self._agents.append(agent)

    def publish(self, event: Event) -> list[str]:
        fired: list[str] = []
        for agent in list(self._agents):
            try:
                if agent.trigger(event):
                    fired.append(agent.name)
                    job = AgentJob(
                        agent=agent.name,
                        event_id=event.id,
                        event_kind=event.kind,
                        engagement_id=event.engagement_id,
                        status="running",
                        started=time.time(),
                    )
                    with self._lock:
                        self._jobs.append(job)
                    fut = self._pool.submit(self._execute, agent, event, job)
                    self._futures.append(fut)
            except Exception as exc:  # agent predicate must not kill the bus
                with self._lock:
                    self._jobs.append(
                        AgentJob(
                            agent=agent.name,
                            event_id=event.id,
                            event_kind=event.kind,
                            engagement_id=event.engagement_id,
                            status="predicate_error",
                            started=time.time(),
                            finished=time.time(),
                            error=str(exc),
                        )
                    )
        return fired

    def _execute(self, agent: Agent, event: Event, job: AgentJob) -> None:
        try:
            result = agent.run(event)
            job.status = "ok"
            job.result = result
        except Exception as exc:
            job.status = "error"
            job.error = str(exc)
        finally:
            job.finished = time.time()

    def jobs(self) -> list[AgentJob]:
        with self._lock:
            return list(self._jobs)

    def wait(self, timeout: float | None = None) -> None:
        for fut in list(self._futures):
            fut.result(timeout=timeout)

    def shutdown(self) -> None:
        self._pool.shutdown(wait=False)
