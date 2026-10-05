#!/usr/bin/env python3
"""Capture a real EKay server startup + health check into assets/ekay-server-demo.gif."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

# xterm 256 → approximate RGB for colors we use in the banner
XTERM = {
    46: (0, 255, 0),
    51: (0, 255, 255),
    27: (0, 0, 215),
    33: (0, 135, 255),
    39: (0, 175, 255),
    67: (95, 135, 175),
    117: (135, 215, 255),
    129: (175, 0, 255),
    208: (255, 135, 0),
    240: (88, 88, 88),
}

ANSI_RE = re.compile(
    r"\033\[(?P<code>[0-9;]*)m|(?P<nl>\n)|(?P<ch>[^\033\n]+)"
)


def _font(size: int = 15):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    ):
        if os.path.isfile(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def strip_for_width(text: str) -> list[str]:
    """Return plain lines (no ANSI) for layout sizing."""
    plain = re.sub(r"\033\[[0-9;]*m", "", text)
    return plain.splitlines()


def render_ansi_frame(
    text: str,
    *,
    cols: int = 96,
    rows: int = 34,
    cell_w: int = 9,
    cell_h: int = 17,
) -> Image.Image:
    img = Image.new("RGB", (cols * cell_w + 24, rows * cell_h + 24), (8, 12, 22))
    draw = ImageDraw.Draw(img)
    font = _font(14)
    # subtle scanline / border
    draw.rectangle([0, 0, img.width - 1, img.height - 1], outline=(0, 120, 180))

    x0, y0 = 12, 10
    cx, cy = 0, 0
    color = (200, 220, 240)
    bold = False

    def put(ch: str) -> None:
        nonlocal cx, cy
        if cy >= rows:
            return
        draw.text((x0 + cx * cell_w, y0 + cy * cell_h), ch, fill=color, font=font)
        cx += 1
        if cx >= cols:
            cx = 0
            cy += 1

    for m in ANSI_RE.finditer(text):
        if m.group("nl") is not None:
            cx = 0
            cy += 1
            continue
        code = m.group("code")
        if code is not None:
            parts = [p for p in code.split(";") if p != ""]
            if not parts or parts == ["0"]:
                color = (200, 220, 240)
                bold = False
                continue
            i = 0
            while i < len(parts):
                p = int(parts[i])
                if p == 0:
                    color = (200, 220, 240)
                    bold = False
                elif p == 1:
                    bold = True
                elif p == 2:
                    color = (120, 130, 140)
                elif p == 97:
                    color = (245, 245, 245)
                elif p == 38 and i + 2 < len(parts) and int(parts[i + 1]) == 5:
                    idx = int(parts[i + 2])
                    color = XTERM.get(idx, (180, 200, 220))
                    i += 2
                i += 1
            if bold and color != (245, 245, 245):
                color = tuple(min(255, c + 25) for c in color)
            continue
        chunk = m.group("ch") or ""
        for ch in chunk:
            put(ch)
    return img


def capture_real_server(port: int = 8799) -> tuple[str, dict]:
    """Start real ekay_server.py, capture banner stdout, hit /health, stop."""
    env = os.environ.copy()
    env["EKAY_HOST"] = "127.0.0.1"
    env["EKAY_PORT"] = str(port)
    env["EKAY_SCOPE"] = "127.0.0.1,localhost"
    env["EKAY_ALLOW_INTRUSIVE"] = "0"
    env["PYTHONUNBUFFERED"] = "1"
    env["PATH"] = f"{ROOT / 'ekay-bin'}:{env.get('PATH', '')}"
    env["EKAY_TOOL_BIN"] = str(ROOT / "ekay-bin")
    py = ROOT / "ekay-env" / "bin" / "ekay-python"
    if not py.is_file():
        py = Path(sys.executable)

    proc = subprocess.Popen(
        [str(py), str(ROOT / "ekay_server.py")],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    collected: list[str] = []
    health: dict = {}
    deadline = time.time() + 25
    try:
        assert proc.stdout is not None
        banner_done = False
        while time.time() < deadline and not banner_done:
            line = proc.stdout.readline()
            if line:
                collected.append(line)
                if "╰──" in line or "Kill-Chain API" in line:
                    banner_done = True
                    time.sleep(0.3)
            elif proc.poll() is not None:
                break
            else:
                time.sleep(0.05)
        # Wait until HTTP is actually up (banner prints before waitress binds).
        for _ in range(40):
            try:
                import urllib.request

                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as resp:
                    health = json.loads(resp.read().decode())
                break
            except Exception:
                time.sleep(0.25)
        # Drain remaining stdout without blocking forever
        time.sleep(0.2)
        # one engage for demo content
        engage = {}
        try:
            import urllib.request

            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/engagements",
                data=json.dumps({"target": "127.0.0.1", "osint": False}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                engage = json.loads(resp.read().decode())
        except Exception as exc:
            engage = {"error": str(exc)}
        health["_engage"] = engage
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        # leftover stdout
        try:
            if proc.stdout:
                rest = proc.stdout.read() or ""
                if rest:
                    collected.append(rest)
        except Exception:
            pass

    banner_text = "".join(collected)
    if not banner_text.strip():
        # fallback: render from engine with live catalog
        from ekay.banner import BlueVisualEngine
        from ekay.catalog import phases_count
        from ekay.runner import ToolRunner
        from ekay.scope import ScopeGuard
        from ekay.status import catalog_report

        report = catalog_report(ToolRunner(ScopeGuard(["127.0.0.1"])))
        banner_text = BlueVisualEngine.create_banner(
            "127.0.0.1",
            port,
            catalog=report["catalog"],
            ready=report["ready"],
            phases=phases_count(),
        ) + BlueVisualEngine.create_startup_box(
            "127.0.0.1",
            port,
            catalog=report["catalog"],
            ready=report["ready"],
            missing=report["missing"],
            gated=report["gated"],
            stub=report.get("stub", 0),
        )
    return banner_text, health


def build_story(banner: str, health: dict) -> list[tuple[str, int]]:
    """Return (frame_text, duration_ms) scenes."""
    scenes: list[tuple[str, int]] = []
    lines = banner.splitlines(keepends=True)
    acc = ""
    # progressive reveal of banner
    step = max(1, len(lines) // 8)
    for i in range(0, len(lines) + 1, step):
        acc = "".join(lines[:i])
        scenes.append((acc, 180))
    scenes.append((banner, 900))

    h = {k: health.get(k) for k in ("ok", "name", "version", "edition", "catalog", "ready", "missing", "gated", "architecture")}
    health_block = (
        banner
        + "\n\033[38;5;46m$ curl -s http://127.0.0.1:8787/health | jq .\033[0m\n"
        + "\033[38;5;117m"
        + json.dumps(h, indent=2)
        + "\033[0m\n"
    )
    scenes.append((health_block, 1400))

    engage = health.get("_engage") or {}
    eng_show = {
        k: engage.get(k)
        for k in ("engagement_id", "target", "current_phase", "agents_fired_on_start", "architecture")
    }
    engage_block = (
        health_block
        + "\n\033[38;5;46m$ curl -s -X POST /api/engagements -d '{\"target\":\"127.0.0.1\"}'\033[0m\n"
        + "\033[38;5;208m"
        + json.dumps(eng_show, indent=2)
        + "\033[0m\n"
    )
    scenes.append((engage_block, 1600))

    finale = (
        engage_block
        + "\n\033[38;5;51m[EKay] Kill-chain online — connect Cursor/Claude via ekay_mcp.py\033[0m\n"
        + "\033[38;5;39m[EKay] docs/TOOLS.md catalogs every binary by phase\033[0m\n"
    )
    scenes.append((finale, 1800))
    return scenes


def main() -> int:
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    out = assets / "ekay-server-demo.gif"

    print("[demo] starting real ekay_server.py …")
    banner, health = capture_real_server()
    print(f"[demo] captured {len(banner)} banner chars; health.ok={health.get('ok')}")

    scenes = build_story(banner, health)
    frames = []
    durations = []
    for text, ms in scenes:
        frames.append(render_ansi_frame(text))
        durations.append(ms)

    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )
    # also save a static PNG poster of the final frame
    frames[-1].save(assets / "ekay-server-banner.png")
    print(f"[demo] wrote {out} ({out.stat().st_size} bytes)")
    print(f"[demo] wrote {assets / 'ekay-server-banner.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
