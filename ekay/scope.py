"""Engagement scope lock — refuse out-of-scope hosts before any binary runs."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

_HOST_RE = re.compile(r"^[A-Za-z0-9._:-]+$")


class ScopeError(ValueError):
    pass


class ScopeGuard:
    # Entries that switch the guard into allow-all (lab / CTF) mode.
    _WILDCARDS = {"*", "any", "all", "0.0.0.0/0", "::/0"}

    def __init__(self, allowed: list[str]):
        self._hosts: set[str] = set()
        self._nets: list[ipaddress._BaseNetwork] = []
        self._allow_all = False
        for raw in allowed:
            item = raw.strip().lower()
            if not item:
                continue
            if item in self._WILDCARDS:
                # EKAY_SCOPE=* (or any/all/0.0.0.0/0) => run any target,
                # HexStrike-style. Use only in an authorized lab.
                self._allow_all = True
                continue
            try:
                self._nets.append(ipaddress.ip_network(item, strict=False))
            except ValueError:
                self._hosts.add(item)

    def extract_host(self, target: str) -> str:
        value = target.strip()
        if "://" in value:
            host = urlparse(value).hostname or ""
        else:
            host = value.split("/")[0].split(":")[0]
        host = host.strip().lower().strip("[]")
        if not host or not _HOST_RE.match(host):
            raise ScopeError(f"invalid target host: {target!r}")
        return host

    def check(self, target: str) -> str:
        host = self.extract_host(target)
        if self._allow_all:
            return host
        if host in self._hosts:
            return host
        try:
            ip = ipaddress.ip_address(host)
            if any(ip in net for net in self._nets):
                return host
        except ValueError:
            pass
        raise ScopeError(f"target {host!r} is outside EKAY_SCOPE")
