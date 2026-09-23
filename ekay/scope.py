"""Engagement scope lock — refuse out-of-scope hosts before any binary runs."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

_HOST_RE = re.compile(r"^[A-Za-z0-9._:-]+$")


class ScopeError(ValueError):
    pass


class ScopeGuard:
    def __init__(self, allowed: list[str]):
        self._hosts: set[str] = set()
        self._nets: list[ipaddress._BaseNetwork] = []
        for raw in allowed:
            item = raw.strip().lower()
            if not item:
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
        if host in self._hosts:
            return host
        try:
            ip = ipaddress.ip_address(host)
            if any(ip in net for net in self._nets):
                return host
        except ValueError:
            pass
        raise ScopeError(f"target {host!r} is outside EKAY_SCOPE")
