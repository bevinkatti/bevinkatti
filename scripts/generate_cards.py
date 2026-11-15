
#!/usr/bin/env python3
"""Generate animated SVG cards for Abhishek's GitHub profile."""

import base64
import json
import os
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
DATA = ROOT / "data" / "contributions.json"
FONTS = ROOT / "assets" / "fonts"

STATIC = os.getenv("STATIC", "0") == "1"

BG = "#0D1117"
CARD = "#161B22"
BORDER = "#30363D"
BLUE = "#58A6FF"
WHITE = "#F0F6FC"
MUTED = "#8B949E"
GREEN = "#39D353"

FONT = "'Fira Code', 'Courier New', monospace"
CARD_WIDTH = 900


def font_css():
    """Embed a locally subsetted WOFF font when available."""
    font_file = FONTS / "FiraCode.woff"
    if not font_file.exists():
        return ""
    encoded = base64.b64encode(font_file.read_bytes()).decode("ascii")
    return (
        "@font-face{font-family:'Fira Code';"
        "src:url(data:font/woff;base64,"
        + encoded
        + ") format('woff');font-weight:100 700;}"
    )


def animation_css(delay=0):
    if STATIC:
        return ""
    return f"""
    .card {{
      opacity: 0;
      animation: appear .9s ease-out {delay}s forwards;
    }}
    @keyframes appear {{
      from {{ opacity: 0; transform: translateY(18px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation: none !important;
        transition: none !important;
        opacity: 1 !important;
        transform: none !important;
      }}
    }}
    """


def svg_start(width, height, delay=0):
    return f"""<svg xmlns="http://www.w3.org/2000/svg"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      width="{width}" height="{height}"
      viewBox="0 0 {width} {height}">
      <style>
        {font_css()}
        text {{ font-family: {FONT}; }}
        {animation_css(delay)}
      </style>
      <rect width="100%" height="100%" rx="18" fill="{BG}"/>
      <rect x="1" y="1" width="{width-2}" height="{height-2}"
        rx="17" fill="none" stroke="{BORDER}"/>
      <g class="card">
    """


def svg_end():
    return "</g></svg>"


def text(x, y, value, size=20, color=WHITE, weight="400"):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}">'
        f'{escape(str(value))}</text>'
    )


def load_data():
    if not DATA.exists():
        return {
            "months": [],
            "streak": 0,
            "active_days": 0,
            "busiest_day": "—",
            "daily": [],
            "total_contributions": 0,
        }
    with DATA.open(encoding="utf-8") as file:
        return json.load(file)


def save(name, content):
    CARDS.mkdir(parents=True, exist_ok=True)
    (CARDS / name).write_text(content, encoding="utf-8")
    print(f"Generated cards/{name}")


def hero():
    body = (
        text(48, 76, "HELLO, I'M", 16, BLUE, "600")
        + text(48, 145, "Abhishek Bevinkatti", 43, WHITE, "700")
        + text(48, 190, "AI/ML · Software Engineering · Open Source", 19, MUTED)
        + text(48, 240, "Building intelligent systems, one commit at a time.", 17, BLUE)
        + text(48, 290, "PYTHON  /  BACKEND  /  MACHINE LEARNING  /  OPEN SOURCE", 12, MUTED)
    )
    save("hero.svg", svg_start(900, 330, 0) + body + svg_end())


def links():
    tiles = [
        ("PORTFOLIO", "Explore my work", "https://bevinkatti-portfolio.vercel.app"),
        ("GITHUB", "Open repositories", "https://github.com/bevinkatti"),
        ("LINKEDIN", "Let's connect", "https://linkedin.com/in/abhishekbevinkatti"),
    ]

    body = ""
    for index, (title, subtitle, url) in enumerate(tiles):
        x = 8 + index * 300
        body += f"""
        <a href="{escape(url, {'"': '&quot;'})}">
          <rect x="{x}" y="8" width="285" height="114"
            rx="13" fill="{CARD}" stroke="{BORDER}"/>
          {text(x+20, 53, title, 17, BLUE, "700")}
          {text(x+20, 85, subtitle, 13, MUTED)}
        </a>
        """
    save("links.svg", svg_start(900, 130, 0.3) + body + svg_end())


def activity(data):
    months = data.get("months", [])[-12:]
    daily = data.get("daily", [])

    body = (
        text(35, 55, "CONTRIBUTION ACTIVITY", 21, WHITE, "700")
        + text(35, 105, f"Current streak: {data.get('streak', 0)} days", 16, BLUE)
        + text(330, 105, f"Active days: {data.get('active_days', 0)}", 16, GREEN)
        + text(600, 105, f"Total: {data.get('total_contributions', 0)}", 16, WHITE)
        + text(35, 155, f"Busiest day: {data.get('busiest_day', '—')}", 14, MUTED)
    )

    max_value = max([m.get("count", 0) for m in months] or [1])
    for index, month in enumerate(months):
        x = 45 + index * 69
        height = 110 * month.get("count", 0) / max_value
        y = 305 - height
        body += f'<rect x="{x}" y="{y:.1f}" width="38" height="{height:.1f}" rx="5" fill="{BLUE}"/>'
        body += text(x, 335, month.get("month", "")[:3], 11, MUTED)

    body += text(35, 380, "Monthly contributions · Last 12 months", 12, MUTED)

    save("activity.svg", svg_start(900, 410, 0.6) + body + svg_end())


def repository_cards():
    repositories = [
        {
            "file": "repo-pdfzero.svg",
            "name": "PdfZero",
            "description": "PDF tools and document processing",
            "url": "https://github.com/bevinkatti/PdfZero",
            "tech": "Python · Open Source",
        },
        {
            "file": "repo-pipdash.svg",
            "name": "pipdash",
            "description": "Python package and developer tooling",
            "url": "https://github.com/bevinkatti/pipdash",
            "tech": "Python · Developer Tools",
        },
        {
            "file": "repo-research.svg",
            "name": "Multi-Agent Research Assistant",
            "description": "Research workflows powered by agents",
            "url": "https://github.com/bevinkatti/multi-agent-research-assistant",
            "tech": "Python · Agentic AI",
        },
    ]

    for index, repo in enumerate(repositories):
        body = (
            f'<a href="{escape(repo["url"])}">'
            + text(32, 65, repo["name"], 24, BLUE, "700")
            + text(32, 110, repo["description"], 15, WHITE)
            + text(32, 155, repo["tech"], 13, MUTED)
            + text(32, 205, "VIEW REPOSITORY  →", 13, GREEN)
            + "</a>"
        )
        save(
            repo["file"],
            svg_start(900, 240, 0.9 + index * 0.2) + body + svg_end(),
        )


def contributions(data):
    daily = data.get("daily", [])[-364:]
    body = text(30, 50, "CONTRIBUTION GRAPH", 20, WHITE, "700")

    cell = 12
    gap = 4
    start_x = 30
    start_y = 80

    for index, item in enumerate(daily):
        week = index // 7
        day = index % 7
        x = start_x + week * (cell + gap)
        y = start_y + day * (cell + gap)

        count = item.get("count", 0)
        color = (
            BG if count == 0 else
            "#0E4429" if count <= 2 else
            "#006D32" if count <= 5 else
            "#26A641" if count <= 10 else
            GREEN
        )

        body += (
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'rx="2" fill="{color}"/>'
        )

    save("contributions.svg", svg_start(900, 170, 1.5) + body + svg_end())


def main():
    CARDS.mkdir(parents=True, exist_ok=True)
    data = load_data()

    hero()
    links()
    activity(data)
    repository_cards()
    contributions(data)

    print("All SVG cards generated successfully.")


if __name__ == "__main__":
    main()
