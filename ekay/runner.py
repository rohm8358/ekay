"""Argument-safe subprocess runner. Never uses shell=True."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from typing import Sequence

from ekay.catalog import CATALOG_BY_NAME, ToolSpec
from ekay.scope import ScopeGuard

_SAFE_ARG = re.compile(r"^[A-Za-z0-9_.:/=+\-@%,]+$")


class RunnerError(RuntimeError):
    pass


@dataclass
class RunResult:
    tool: str
    binary: str
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str
    duration_ms: int
    available: bool
    blocked_reason: str | None = None
    extra: dict = field(default_factory=dict)


class ToolRunner:
    def __init__(
        self,
        scope: ScopeGuard,
        timeout: int = 180,
        allow_intrusive: bool = False,
    ):
        self.scope = scope
        self.timeout = timeout
        self.allow_intrusive = allow_intrusive
        self._which_cache: dict[str, str | None] = {}

    def which(self, binary: str) -> str | None:
        if binary not in self._which_cache:
            self._which_cache[binary] = shutil.which(binary)
        return self._which_cache[binary]

    def availability(self) -> dict[str, bool]:
        return {spec.name: bool(self.which(spec.binary)) for spec in CATALOG_BY_NAME.values()}

    def _resolve(self, name: str) -> ToolSpec:
        spec = CATALOG_BY_NAME.get(name)
        if not spec:
            raise RunnerError(f"unknown tool: {name}")
        return spec

    def sanitize_args(self, extra: Sequence[str] | None) -> list[str]:
        clean: list[str] = []
        for item in extra or []:
            if not _SAFE_ARG.match(item):
                raise RunnerError(f"rejected unsafe argument: {item!r}")
            clean.append(item)
        return clean

    def build_argv(self, spec: ToolSpec, target: str, extra: Sequence[str] | None) -> list[str]:
        path = self.which(spec.binary)
        if not path:
            raise RunnerError(f"binary not installed: {spec.binary}")
        argv = [path]
        for token in spec.default_args:
            argv.append(token.replace("{target}", target).replace("{url}", target))
        argv.extend(self.sanitize_args(extra))
        if spec.name in {"nmap", "masscan", "nikto", "whatweb", "wafw00f", "wapiti"}:
            if target not in argv:
                argv.append(target)
        elif spec.name in {"httpx", "nuclei", "feroxbuster", "dirsearch"}:
            if target not in argv:
                argv.append(target)
        elif spec.name == "rustscan" and target not in argv:
            argv.append(target)
        elif spec.name in {"gobuster"}:
            pass
        elif spec.name in {"naabu"} and target not in argv:
            argv.append(target)
        return argv

    def run(self, name: str, target: str, extra: Sequence[str] | None = None) -> RunResult:
        spec = self._resolve(name)
        host = self.scope.check(target)
        if spec.risk in {"intrusive", "restricted"} and not self.allow_intrusive:
            return RunResult(
                tool=name,
                binary=spec.binary,
                argv=[],
                returncode=-1,
                stdout="",
                stderr="",
                duration_ms=0,
                available=bool(self.which(spec.binary)),
                blocked_reason=(
                    f"{spec.risk} tool blocked. Set EKAY_ALLOW_INTRUSIVE=1 and "
                    "confirm written authorization before enabling."
                ),
            )
        path = self.which(spec.binary)
        if not path:
            return RunResult(
                tool=name,
                binary=spec.binary,
                argv=[],
                returncode=-1,
                stdout="",
                stderr="",
                duration_ms=0,
                available=False,
                blocked_reason=f"{spec.binary} not on PATH",
            )
        argv = self.build_argv(spec, target, extra)
        started = time.perf_counter()
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                env={**os.environ, "EKAY_TARGET": host},
            )
        except subprocess.TimeoutExpired as exc:
            out = (exc.stdout or b"") if isinstance(exc.stdout, (bytes, bytearray)) else (exc.stdout or "")
            err = (exc.stderr or b"") if isinstance(exc.stderr, (bytes, bytearray)) else (exc.stderr or "")
            if isinstance(out, bytes):
                out = out.decode("utf-8", "replace")
            if isinstance(err, bytes):
                err = err.decode("utf-8", "replace")
            return RunResult(
                tool=name,
                binary=spec.binary,
                argv=argv,
                returncode=-2,
                stdout=out[-8000:],
                stderr=(err + "\nTIMEOUT")[-4000:],
                duration_ms=int((time.perf_counter() - started) * 1000),
                available=True,
            )
        return RunResult(
            tool=name,
            binary=spec.binary,
            argv=argv,
            returncode=proc.returncode,
            stdout=(proc.stdout or "")[-12000:],
            stderr=(proc.stderr or "")[-4000:],
            duration_ms=int((time.perf_counter() - started) * 1000),
            available=True,
        )


def evidence_dir() -> str:
    root = os.path.join(tempfile.gettempdir(), "ekay-evidence")
    os.makedirs(root, exist_ok=True)
    return root
