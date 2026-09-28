#!/usr/bin/env python3
"""EKay MCP bridge — HexStrike-style root launcher.

Usage:
    python3 ekay_mcp.py --server http://127.0.0.1:8787
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

for site in sorted((ROOT / "ekay-env" / "lib").glob("python*/site-packages")):
    sp = str(site)
    if sp not in sys.path:
        sys.path.insert(0, sp)

from ekay.mcp_server import main

if __name__ == "__main__":
    main()
