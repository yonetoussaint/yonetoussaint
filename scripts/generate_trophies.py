#!/usr/bin/env python3
"""Generates assets/trophies.svg (neo-brutalist) from the GitHub API. No third-party services."""
import json, os, sys, urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "yonetoussaint")
OUT = os.environ.get("OUT", "assets/trophies.svg")

def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def fetch():
    u = api(f"/users/{USER}")
    stars, page = 0, 1
    while True:
        repos = api(f"/users/{USER}/repos?per_page=100&page={page}")
        if not repos:
            break
        stars += sum(r["stargazers_count"] for r in repos if not r["fork"])
        page += 1
    created = datetime.fromisoformat(u["created_at"].replace("Z", "+00:00"))
    years = (datetime.now(timezone.utc) - created).days // 365
    return {"FOLLOWERS": u["followers"], "STARS": stars, "REPOS": u["public_repos"], "YEARS": years}

TIERS = {  # (S, A, B) thresholds
    "FOLLOWERS": (100, 25, 5),
    "STARS": (100, 20, 5),
    "REPOS": (50, 20, 8),
    "YEARS": (8, 4, 2),
}

def rank(label, v):
    s, a, b = TIERS[label]
    return "S" if v >= s else "A" if v >= a else "B" if v >= b else "C"

COLORS = {"FOLLOWERS": "#FFE600", "STARS": "#FF6B9D", "REPOS": "#00E5A0", "YEARS": "#FFFFFF"}

def card(x, y, label, value, rk):
    c = COLORS[label]
    return f'''
  <rect x="{x+8}" y="{y+8}" width="200" height="200" fill="#000"/>
  <rect x="{x}" y="{y}" width="200" height="200" fill="{c}" stroke="#000" stroke-width="4"/>
  <rect x="{x+140}" y="{y}" width="60" height="52" fill="#000"/>
  <text x="{x+170}" y="{y+39}" text-anchor="middle" font-family="Courier New, monospace" font-weight="900" font-size="34" fill="{c}">{rk}</text>
  <g transform="translate({x+22},{y+22})" fill="#000">
    <path d="M10 0h60v26c0 18-12 30-30 30S10 44 10 26z"/>
    <path d="M10 6H0v8c0 10 6 16 14 18v-6c-4-2-6-6-6-12zM70 6h10v8c0 10-6 16-14 18v-6c4-2 6-6 6-12z"/>
    <rect x="35" y="54" width="10" height="14"/>
    <rect x="20" y="66" width="40" height="10"/>
  </g>
  <text x="{x+22}" y="{y+138}" font-family="Courier New, monospace" font-weight="900" font-size="48" fill="#000">{value}</text>
  <text x="{x+22}" y="{y+172}" font-family="Courier New, monospace" font-weight="700" font-size="18" letter-spacing="2" fill="#000">{label}</text>'''

def render(data):
    pos = [(4, 4), (228, 4), (4, 228), (228, 228)]
    body = "".join(card(x, y, k, v, rank(k, v) if isinstance(v, int) else "?")
                   for (x, y), (k, v) in zip(pos, data.items()))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 448" width="448" height="448" role="img" aria-label="GitHub trophies">{body}\n</svg>\n'

if __name__ == "__main__":
    if "--demo" in sys.argv:
        data = {"FOLLOWERS": 12, "STARS": 34, "REPOS": 21, "YEARS": 3}
    else:
        data = fetch()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(render(data))
    print("wrote", OUT, data)
