"""
Builds the neofetch-style profile card for github.com/uditauniyal.

Run locally:     python scripts/build_card.py
Run in Actions:  see .github/workflows/update-card.yml (refreshes daily)

The card has two halves:
  * a DNA double helix on the left, with a pulse travelling down its strands
  * a terminal readout on the right: profile, contact, live GitHub stats,
    and a live prompt with a blinking cursor at the bottom

Edit PROFILE below to change any line. Everything else is rendering.
"""

import math
import os
import time
from datetime import date, datetime

import requests

USER = os.environ.get("GH_USER", "uditauniyal")
TOKEN = os.environ.get("GH_TOKEN", "")

# Set to her real birthday to drive the "Uptime" line, e.g. date(2005, 6, 14).
# Leave as None to hide that line entirely.
BIRTHDAY = None

WIDTH_CHARS = 56  # characters per readout line, keeps the dot leaders aligned

# (key, value) pairs. A None row prints an empty spacer line.
PROFILE = [
    ("OS", "Linux, Windows"),
    ("UPTIME", None),  # filled from BIRTHDAY, removed if BIRTHDAY is None
    ("Host", "Banasthali Vidyapith"),
    ("Kernel", "B.Tech IT, CGPA 8.9"),
    ("Role", "AI Engineer Intern @ ARTPARK, IISc"),
    ("Currently", "small language models, OSS"),
    None,
    ("Research.Focus", "RAG evaluation, calibration"),
    ("Research.Paper", "1st author, ECIR 2027 (review)"),
    ("Research.Finding", "cited 67%, retrieved 15%"),
    None,
    ("Work.Agents", "OpenClaw, OpenShell, NemoClaw"),
    ("Work.Graph", "Neo4j knowledge graph"),
    ("Work.Portals", "700+ applications to top 10"),
]

CONTACT = [
    ("Email", "udita.uniyal1630@gmail.com"),
    ("LinkedIn", "udita-uniyal"),
]

THEMES = {
    "dark": {
        "bg": "#161b22", "border": "#30363d", "text": "#c9d1d9",
        "key": "#ffa657", "value": "#a5d6ff", "dots": "#616e7f",
        "base_at": "#7ee787", "base_gc": "#d2a8ff",
        "add": "#3fb950", "del": "#f85149",
    },
    "light": {
        "bg": "#f6f8fa", "border": "#d0d7de", "text": "#24292f",
        "key": "#953800", "value": "#0a3069", "dots": "#c2cfde",
        "base_at": "#116329", "base_gc": "#8250df",
        "add": "#1a7f37", "del": "#cf222e",
    },
}


# --------------------------------------------------------------------------
# GitHub stats (REST API, works with or without a token)
# --------------------------------------------------------------------------

def _get(url, params=None, retries=6):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    for attempt in range(retries):
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 202:  # /stats endpoints compute lazily
            time.sleep(2 + attempt * 2)
            continue
        r.raise_for_status()
        return r.json()
    return None


def fetch_stats(user):
    profile = _get(f"https://api.github.com/users/{user}")

    repos, page = [], 1
    while True:
        batch = _get(f"https://api.github.com/users/{user}/repos",
                     params={"per_page": 100, "page": page, "type": "owner"})
        if not batch:
            break
        repos.extend(batch)
        page += 1

    stars = sum(r.get("stargazers_count", 0) for r in repos)

    commits = _get("https://api.github.com/search/commits",
                   params={"q": f"author:{user}", "per_page": 100}) or {"total_count": 0, "items": []}

    owned = {r["full_name"].lower() for r in repos}
    contributed = {
        item["repository"]["full_name"].lower()
        for item in commits.get("items", []) if item.get("repository")
    } - owned

    additions = deletions = 0
    for r in repos:
        if r.get("fork"):
            continue
        data = _get(f"https://api.github.com/repos/{r['full_name']}/stats/contributors")
        for contributor in data or []:
            author = contributor.get("author") or {}
            if (author.get("login") or "").lower() == user.lower():
                for week in contributor.get("weeks", []):
                    additions += week.get("a", 0)
                    deletions += week.get("d", 0)

    # Most recently pushed repo, ignoring this profile repo (the daily refresh
    # commits to it, so it would otherwise always win).
    latest, latest_when = "", ""
    others = [r for r in repos if r.get("name", "").lower() != user.lower() and r.get("pushed_at")]
    if others:
        newest = max(others, key=lambda r: r["pushed_at"])
        latest = newest["name"]
        days = (date.today() - datetime.strptime(newest["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").date()).days
        latest_when = "today" if days <= 0 else ("yesterday" if days == 1 else f"{days} days ago")

    return {
        "repos": profile.get("public_repos", len(repos)),
        "contributed": len(contributed),
        "stars": stars,
        "commits": commits.get("total_count", 0),
        "followers": profile.get("followers", 0),
        "loc": additions - deletions,
        "add": additions,
        "del": deletions,
        "latest": latest,
        "latest_when": latest_when,
    }


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def uptime(born):
    import calendar
    today = date.today()
    years = today.year - born.year
    months = today.month - born.month
    days = today.day - born.day
    if days < 0:
        months -= 1
        prev_month = today.month - 1 or 12
        prev_year = today.year if today.month > 1 else today.year - 1
        days += calendar.monthrange(prev_year, prev_month)[1]
    if months < 0:
        years -= 1
        months += 12
    return f"{years} years, {months} months, {days} days"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def dots(key, value, width=WIDTH_CHARS):
    used = len(f". {key}: ") + len(value) + 1
    return "." * max(2, width - used)


def helix(rows, width=34):
    """A DNA double helix with complementary base pairs (A-T, G-C)."""
    pairs = [("A", "T"), ("G", "C"), ("T", "A"), ("C", "G")]
    lines = []
    centre, amp = width // 2, width // 2 - 2
    for y in range(rows):
        s = math.sin(2 * math.pi * y / 12.5)
        x1, x2 = round(centre + amp * s), round(centre - amp * s)
        a, b = pairs[y % 4]
        if x1 > x2:
            x1, x2, a, b = x2, x1, b, a
        row = [" "] * width
        if x2 - x1 <= 1:
            row[x1] = a
            if x2 != x1:
                row[x2] = b
        else:
            row[x1], row[x2] = a, b
            for i in range(x1 + 1, x2):
                row[i] = "-"
        lines.append("".join(row))
    return lines


# --------------------------------------------------------------------------
# SVG rendering
# --------------------------------------------------------------------------

def render(theme, stats):
    t = THEMES[theme]
    lh, x_info, y0 = 20, 378, 34
    rows = []

    def kv(y, key, value):
        rows.append(
            f'<text x="{x_info}" y="{y}" class="mono">'
            f'<tspan fill="{t["dots"]}">. </tspan>'
            f'<tspan fill="{t["key"]}">{esc(key)}</tspan>'
            f'<tspan fill="{t["text"]}">:</tspan>'
            f'<tspan fill="{t["dots"]}"> {dots(key, value)} </tspan>'
            f'<tspan fill="{t["value"]}">{esc(value)}</tspan></text>'
        )

    def header(y, label):
        bar = "—" * max(4, WIDTH_CHARS - len(label) - 3)
        rows.append(
            f'<text x="{x_info}" y="{y}" class="mono">'
            f'<tspan fill="{t["text"]}">- {esc(label)} </tspan>'
            f'<tspan fill="{t["dots"]}">{bar}</tspan></text>'
        )

    # title: types itself out on load
    y = y0
    rows.append(
        f'<text x="{x_info}" y="{y}" class="mono type">'
        f'<tspan fill="{t["key"]}">udita</tspan><tspan fill="{t["text"]}">@</tspan>'
        f'<tspan fill="{t["key"]}">uniyal</tspan>'
        f'<tspan fill="{t["dots"]}"> {"—" * (WIDTH_CHARS - 14)}</tspan></text>'
    )
    y += lh

    for item in PROFILE:
        if item is None:
            y += lh
            continue
        key, value = item
        if key == "UPTIME":
            if BIRTHDAY is None:
                continue
            key, value = "Uptime", uptime(BIRTHDAY)
        kv(y, key, value)
        y += lh

    y += lh // 2
    header(y, "Contact")
    y += lh
    for key, value in CONTACT:
        kv(y, key, value)
        y += lh

    y += lh // 2
    header(y, "GitHub Stats")
    y += lh
    s = stats
    kv(y, "Repos", f'{s["repos"]} {{Contributed: {s["contributed"]}}} | Stars: {s["stars"]}')
    y += lh
    kv(y, "Commits", f'{s["commits"]:,} | Followers: {s["followers"]}')
    y += lh
    if s.get("latest"):
        kv(y, "Last push", f'{s["latest"]}, {s["latest_when"]}')
        y += lh
    rows.append(
        f'<text x="{x_info}" y="{y}" class="mono">'
        f'<tspan fill="{t["dots"]}">. </tspan>'
        f'<tspan fill="{t["key"]}">Lines of Code on GitHub</tspan>'
        f'<tspan fill="{t["text"]}">: </tspan>'
        f'<tspan fill="{t["value"]}">{s["loc"]:,}</tspan>'
        f'<tspan fill="{t["text"]}"> ( </tspan>'
        f'<tspan fill="{t["add"]}">{s["add"]:,}++</tspan>'
        f'<tspan fill="{t["text"]}">, </tspan>'
        f'<tspan fill="{t["del"]}">{s["del"]:,}--</tspan>'
        f'<tspan fill="{t["text"]}"> )</tspan></text>'
    )
    y += lh

    # a live prompt closes the card, cursor blinking
    y += lh // 2
    rows.append(
        f'<text x="{x_info}" y="{y}" class="mono">'
        f'<tspan fill="{t["key"]}">udita@uniyal</tspan>'
        f'<tspan fill="{t["text"]}">:~$ </tspan>'
        f'<tspan fill="{t["key"]}" class="cursor">█</tspan></text>'
    )
    y += lh
    height = y + 14

    # helix sized to the card, with a pulse that travels down the strands
    art = helix(rows=max(12, (height - 34) // lh))
    ay = max(y0, (height - len(art) * lh) // 2 + 14)
    art_rows = []
    for i, line in enumerate(art):
        spans = []
        for ch in line:
            if ch in "AT":
                spans.append(f'<tspan fill="{t["base_at"]}">{ch}</tspan>')
            elif ch in "GC":
                spans.append(f'<tspan fill="{t["base_gc"]}">{ch}</tspan>')
            elif ch == "-":
                spans.append(f'<tspan fill="{t["dots"]}">-</tspan>')
            else:
                spans.append(ch)
        delay = round(i * 0.12, 2)
        art_rows.append(
            f'<text x="24" y="{ay + i * lh}" class="mono pulse" '
            f'style="animation-delay:{delay}s" xml:space="preserve">{"".join(spans)}</text>'
        )

    period = round(len(art) * 0.12 + 1.2, 2)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1015" height="{height}" viewBox="0 0 1015 {height}" role="img" aria-label="udita@uniyal neofetch">
<style>
.mono {{ font-family: ConsolasFallback, Consolas, "SF Mono", Menlo, "DejaVu Sans Mono", "Liberation Mono", "Courier New", monospace; font-size: 16px; white-space: pre; }}
.cursor {{ animation: blink 1.1s step-end infinite; }}
.pulse {{ animation: pulse {period}s ease-in-out infinite; }}
.type {{ clip-path: inset(0 100% 0 0); animation: type 1.4s steps(28, end) .2s forwards; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@keyframes pulse {{ 0%, 100% {{ opacity: .55; }} 8% {{ opacity: 1; }} 20% {{ opacity: .55; }} }}
@keyframes type {{ to {{ clip-path: inset(0 0 0 0); }} }}
</style>
<rect width="1015" height="{height}" rx="15" fill="{t["bg"]}" stroke="{t["border"]}"/>
{chr(10).join(art_rows)}
{chr(10).join(rows)}
</svg>
'''


def main():
    try:
        stats = fetch_stats(USER)
    except Exception as exc:  # keep the card building even if the API hiccups
        print(f"stats fetch failed, using zeros: {exc}")
        stats = {k: 0 for k in ("repos", "contributed", "stars", "commits", "followers", "loc", "add", "del")}
        stats.update({"latest": "", "latest_when": ""})

    os.makedirs("assets", exist_ok=True)
    for theme in THEMES:
        with open(f"assets/{theme}_mode.svg", "w", encoding="utf-8") as f:
            f.write(render(theme, stats))
    print("card built:", stats)


if __name__ == "__main__":
    main()
