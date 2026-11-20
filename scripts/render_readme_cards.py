"""Render animated SVG cards for the GitHub profile README.
   python scripts/render_readme_cards.py          # animated
   STATIC=1 python scripts/render_readme_cards.py # final frame (for screenshots)
   Windows PowerShell:  $env:STATIC=1; python scripts/render_readme_cards.py
"""
import json, os, random, datetime as dt
from collections import OrderedDict

# ---------- edit these ----------
NAME = "kongkiat"
SUBTITLE = "Computer Science student · Maejo University"
TAGLINE = "Learning by building."
LINE1, LINE2 = "CS", "MJU"          # the 2 pixel-art lines
ACCENT = "#2f81f7"
# --------------------------------
STATIC = os.environ.get("STATIC") == "1"
MONO = "ui-monospace,SFMono-Regular,Consolas,Menlo,monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

FONT5x7 = {
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
}

CSS = f"""
:root{{--ink:#1f2328;--mute:#656d76;--accent:{ACCENT};--l0:#ebedf0;--l1:#b6d4fe;--l2:#6fa8fb;--l3:#2f81f7;--l4:#1858b8}}
@media (prefers-color-scheme:dark){{:root{{--ink:#e6edf3;--mute:#8b949e;--l0:#161b22;--l1:#0c2d6b;--l2:#1158c7;--l3:#388bfd;--l4:#79c0ff}}}}
text{{fill:var(--ink)}} .mute{{fill:var(--mute)}} .acc{{fill:var(--accent)}}
"""
if not STATIC:
    CSS += """
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:scale(1)}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
.rise{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}
.fade{animation:fade .5s ease-out both}
.pop{transform-box:fill-box;transform-origin:center;animation:pop .35s ease-out both}
.bar{transform-box:fill-box;transform-origin:bottom;animation:grow .7s ease-out both}
.cursor{animation:blink 1.1s steps(1) infinite;animation-delay:2.6s}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title><style>{CSS}</style>{body}</svg>')


def delay(s):
    return "" if STATIC else f' style="animation-delay:{s:.2f}s"'


# ---------------- hero ----------------
def hero():
    cell, gap, x0, y0 = 11, 1, 600, 38
    out = [f'<text x="40" y="80" class="mute rise" font-family="{MONO}" font-size="16"{delay(0)}>~/ hello, I\'m</text>',
           f'<text x="40" y="150" class="rise" font-family="{SANS}" font-size="68" font-weight="700" letter-spacing="-2"{delay(.15)}>{NAME}</text>',
           f'<text x="42" y="190" class="mute rise" font-family="{SANS}" font-size="20"{delay(.35)}>{SUBTITLE}</text>',
           f'<text x="42" y="222" class="acc rise" font-family="{MONO}" font-size="16"{delay(.5)}>&gt; {TAGLINE}</text>']
    t, y, last_x = 0.6, y0, x0
    for line in (LINE1, LINE2):
        for r in range(7):
            g, x = [], x0
            for ch in line:
                for c, v in enumerate(FONT5x7[ch][r]):
                    if v == "#":
                        g.append(f'<rect x="{x+c*cell}" y="{y+r*cell}" width="{cell-gap}" height="{cell-gap}" rx="2" fill="var(--accent)"/>')
                x += 6 * cell
            last_x = max(last_x, x - cell)
            out.append(f'<g class="fade"{delay(t)}>{"".join(g)}</g>')
            t += 0.11
        y += 7 * cell + 22
    cy = y - 22 - cell * 2
    out.append(f'<rect class="cursor" x="{last_x+10}" y="{cy}" width="{cell*1.4:.0f}" height="{cell*2-gap}" fill="var(--accent)"/>')
    return svg(900, 300, "".join(out), f"{NAME} - {SUBTITLE}")


# ---------------- data ----------------
def load_days():
    p = "data/contributions.json"
    if os.path.exists(p):
        return [(dt.date.fromisoformat(d["date"]), d["count"]) for d in json.load(open(p))["days"]]
    print("no data/contributions.json -> using demo data")
    random.seed(7)
    end = dt.date.today()
    return [(end - dt.timedelta(days=i), max(0, int(random.gauss(2, 3)))) for i in range(370, -1, -1)]


def heatmap(days):
    days = days[-371:]
    offset = (days[0][0].weekday() + 1) % 7            # week starts Sunday
    vals = sorted(c for _, c in days if c)
    q = lambda p: vals[int(len(vals) * p)] if vals else 1
    cuts = [q(.25), q(.5), q(.75)]
    lvl = lambda c: 0 if c == 0 else 1 + sum(c > k for k in cuts)
    S, G, x0, y0 = 11, 3, 24, 40
    cells = []
    for i, (d, c) in enumerate(days):
        wk, dow = divmod(i + offset, 7)
        cells.append(f'<rect class="pop" x="{x0+wk*(S+G)}" y="{y0+dow*(S+G)}" width="{S}" height="{S}" rx="2" '
                     f'fill="var(--l{lvl(c)})"{delay(1.2+wk*0.025)}><title>{d}: {c}</title></rect>')
    w = x0 * 2 + 54 * (S + G)
    total = sum(c for _, c in days)
    head = f'<text x="{x0}" y="26" class="mute" font-family="{MONO}" font-size="13">{total} contributions in the last year</text>'
    return svg(w, y0 + 7 * (S + G) + 14, head + "".join(cells), "Contribution graph")


def activity(days):
    last = days[-365:]
    months = OrderedDict()
    for d, c in last:
        months[(d.year, d.month)] = months.get((d.year, d.month), 0) + c
    keys = list(months)[-12:]
    vals = [months[k] for k in keys]
    mx, best = max(vals + [1]), vals.index(max(vals))
    active = sum(1 for _, c in last if c)
    run = longest = 0
    for _, c in last:
        run = run + 1 if c else 0
        longest = max(longest, run)
    busy_d, busy_c = max(last, key=lambda x: x[1])
    out, bx, base, H, bw = [], 40, 225, 105, 36
    for i, k in enumerate(keys):
        h = max(2, vals[i] / mx * H)
        x = bx + i * (bw + 14)
        fill = "var(--accent)" if i == best else "var(--l1)"
        out.append(f'<rect class="bar" x="{x}" y="{base-h:.1f}" width="{bw}" height="{h:.1f}" rx="4" fill="{fill}"{delay(.2+i*.06)}>'
                   f'<title>{k[0]}-{k[1]:02d}: {vals[i]}</title></rect>')
        out.append(f'<text x="{x+bw/2}" y="{base+18}" text-anchor="middle" class="mute" font-family="{MONO}" font-size="11">{dt.date(k[0], k[1], 1):%b}</text>')
        if i == best:
            out.append(f'<text class="fade acc" x="{x+bw/2}" y="{base-h-8:.1f}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700"{delay(1.1)}>{vals[i]}</text>')
    stats = [("active days", active), ("longest streak", f"{longest}d"), ("busiest day", f"{busy_c} · {busy_d:%b %d}")]
    for i, (lab, v) in enumerate(stats):
        out.append(f'<text x="{40+i*220}" y="40" font-family="{SANS}" font-size="26" font-weight="700" class="rise"{delay(.2+i*.1)}>{v}</text>'
                   f'<text x="{40+i*220}" y="60" class="mute" font-family="{MONO}" font-size="12">{lab}</text>')
    return svg(40 * 2 + 12 * (bw + 14), 255, "".join(out), "Contributions per month")


if __name__ == "__main__":
    os.makedirs("cards", exist_ok=True)
    d = sorted(load_days())
    for name, s in (("hero", hero()), ("heatmap", heatmap(d)), ("activity", activity(d))):
        open(f"cards/{name}.svg", "w", encoding="utf-8").write(s)
        print("wrote", f"cards/{name}.svg")
