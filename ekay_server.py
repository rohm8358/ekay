#!/usr/bin/env python3
"""EKay API server — HexStrike-style root launcher.

Usage (after venv + pip install -r requirements.txt):
    python3 ekay_server.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Prefer local venv site-packages if present
for site in sorted((ROOT / "ekay-env" / "lib").glob("python*/site-packages")):
    sp = str(site)
    if sp not in sys.path:
        sys.path.insert(0, sp)

from ekay.server import main

if __name__ == "__main__":
    main()
