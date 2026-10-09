import json, random, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(ROOT, "html")
MAST = os.path.join(ROOT, "masters")
os.makedirs(HTML, exist_ok=True)
os.makedirs(MAST, exist_ok=True)
rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 4242)

# Glyph pairs that are ambiguous even at full resolution (0/O, 1/I/l) are excluded
# so that a miss measures downscaling loss rather than font ambiguity.
UP = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
LO = "abcdefghjkmnpqrstuvwxyz23456789"

def code(n=6, alpha=UP):
    return "".join(rng.choice(alpha) for _ in range(n))

def num(lo, hi):
    return rng.randint(lo, hi)

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1000px;height:625px;overflow:hidden;background:#f6f7f9;color:#1f2430;
font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif}
"""

truth = {}

# ---------- ui ----------
f = {
    "revenue": f"${num(10,99)},{num(100,999)}",
    "users": f"{num(1000,9999):,}",
    "order_id": "ORD-" + code(),
    "build": code(),
    "api_key": "sk_" + code(),
    "invite_code": code(),
    "error_count": str(num(11, 989)),
    "plan_seats": str(num(12, 480)),
}
ui_html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
.side{{position:absolute;left:0;top:0;bottom:0;width:190px;background:#1e2230;color:#c9cfdd;padding:16px 12px;font-size:13px}}
.side .logo{{font-weight:700;color:#fff;font-size:15px;margin-bottom:18px}}
.side .item{{padding:7px 10px;border-radius:6px;margin-bottom:2px}}
.side .item.on{{background:#353b52;color:#fff}}
.side .foot{{position:absolute;bottom:14px;left:12px;right:12px;font-size:11px;color:#8a91a6}}
.main{{position:absolute;left:190px;top:0;right:0;bottom:0;padding:18px 22px}}
.top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.top h1{{font-size:18px}}
.btn{{display:inline-block;font-size:12px;padding:6px 12px;border-radius:6px;border:1px solid #cdd2dc;background:#fff;margin-left:6px}}
.btn.p{{background:#4f46e5;color:#fff;border-color:#4f46e5}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}}
.card{{background:#fff;border:1px solid #e3e6ec;border-radius:8px;padding:12px 14px}}
.card .l{{font-size:11px;color:#6b7385;text-transform:uppercase;letter-spacing:.04em}}
.card .v{{font-size:14px;font-weight:600;margin-top:6px}}
.card .s{{font-size:11px;color:#6b7385;margin-top:4px}}
.badge{{display:inline-block;font-size:11px;padding:2px 7px;border-radius:10px;background:#e8f5ee;color:#1d7a46;margin-left:6px}}
.badge.r{{background:#fdecec;color:#b42318}}
.row2{{display:grid;grid-template-columns:2fr 1fr;gap:12px}}
.list .li{{display:flex;justify-content:space-between;font-size:12px;padding:8px 0;border-bottom:1px solid #eef0f4}}
.muted{{color:#6b7385}}
</style></head><body>
<div class="side"><div class="logo">Northwind Ops</div>
<div class="item on">Overview</div><div class="item">Orders</div><div class="item">Customers</div>
<div class="item">Deployments</div><div class="item">Billing</div><div class="item">Settings</div>
<div class="foot">Build {f['build']}<br>v4.2 &middot; eu-west</div></div>
<div class="main">
<div class="top"><h1>Overview</h1><div><span class="btn">Export</span><span class="btn">Filters</span><span class="btn p">New report</span></div></div>
<div class="grid">
<div class="card"><div class="l">Revenue (MTD)</div><div class="v">{f['revenue']}</div><div class="s">vs last month <span class="badge">+4.1%</span></div></div>
<div class="card"><div class="l">Active users</div><div class="v">{f['users']}</div><div class="s">last 30 days</div></div>
<div class="card"><div class="l">Errors today</div><div class="v">{f['error_count']}<span class="badge r">alert</span></div><div class="s">across 7 services</div></div>
<div class="card"><div class="l">Seats on plan</div><div class="v">{f['plan_seats']}</div><div class="s">Team plan</div></div>
</div>
<div class="row2">
<div class="card list"><div class="l" style="margin-bottom:6px">Recent activity</div>
<div class="li"><span>Latest order <b>{f['order_id']}</b></span><span class="muted">2 min ago</span></div>
<div class="li"><span>Invoice sent to Acme Corp</span><span class="muted">14 min ago</span></div>
<div class="li"><span>Deployment to production succeeded</span><span class="muted">1 h ago</span></div>
<div class="li"><span>New teammate invited</span><span class="muted">3 h ago</span></div>
<div class="li"><span>Webhook endpoint updated</span><span class="muted">yesterday</span></div>
</div>
<div class="card"><div class="l" style="margin-bottom:8px">Developer</div>
<div style="font-size:12px" class="muted">Publishable API key</div>
<div style="font-size:13px;font-family:Menlo,monospace;margin:4px 0 12px">{f['api_key']}</div>
<div style="font-size:12px" class="muted">Team invite code</div>
<div style="font-size:13px;font-weight:600;margin:4px 0 12px">{f['invite_code']}</div>
<span class="btn" style="margin-left:0">Rotate key</span><span class="btn">Copy</span>
</div></div></div></body></html>"""
truth["ui"] = {
    "questions": {
        "q1": ["What is the Revenue (MTD) value?", f["revenue"]],
        "q2": ["What is the Active users value?", f["users"]],
        "q3": ["What is the 'Errors today' number?", f["error_count"]],
        "q4": ["What is the 'Seats on plan' number?", f["plan_seats"]],
        "q5": ["What is the order ID after 'Latest order' in Recent activity?", f["order_id"]],
        "q6": ["What is the build identifier in the sidebar footer (after 'Build')?", f["build"]],
        "q7": ["What is the publishable API key?", f["api_key"]],
        "q8": ["What is the team invite code?", f["invite_code"]],
    }
}

# ---------- table ----------
services = ["atlas", "beacon", "cobalt", "delta", "ember", "falcon", "garnet", "harbor", "iris", "juniper",
            "kepler", "lumen", "meadow", "nimbus", "onyx", "pulsar", "quartz", "raven", "sierra", "tundra"]
cols = ["Service", "Region", "Requests", "p95 ms", "Error %", "Owner"]
rows = []
for s in services:
    rows.append([s, code(4), f"{num(1000,99999):,}", str(num(12, 980)), f"{num(1,999)/100:.2f}", code(5)])
th = "".join(f"<th>{c}</th>" for c in cols)
tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
table_html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
body{{padding:14px 20px}} h2{{font-size:14px;margin-bottom:6px}}
table{{width:100%;border-collapse:collapse;font-size:12px;background:#fff}}
th{{text-align:left;font-weight:600;color:#4b5263;background:#eef0f4;padding:4px 10px;border-bottom:1px solid #d9dde5}}
td{{padding:4px 10px;border-bottom:1px solid #eceef2;line-height:14px}}
tr:nth-child(even) td{{background:#fafbfc}}
</style></head><body><h2>Service health &mdash; last 24h</h2><table><tr>{th}</tr>{tr}</table></body></html>"""
picks = rng.sample(range(20), 8)
tq = {}
for i, ri in enumerate(picks):
    ci = [1, 2, 3, 4, 5, 1, 3, 5][i]
    tq[f"q{i+1}"] = [f"In the row for service '{rows[ri][0]}', what is the '{cols[ci]}' value?", rows[ri][ci]]
truth["table"] = {"questions": tq}

# ---------- code ----------
fns = ["fetch", "parse", "load", "build", "merge", "emit", "resolve", "map"]
lines = []
idents = []
for i in range(40):
    ident = rng.choice("abcdefghjkmnpqrstuvwxyz") + code(5, LO)
    other = rng.choice("abcdefghjkmnpqrstuvwxyz") + code(5, LO)
    idents.append(ident)
    kw = rng.choice(["const", "let"])
    fn = rng.choice(fns)
    lines.append(f'<span class="k">{kw}</span> <span class="v">{ident}</span> = {fn}(<span class="v">{other}</span>, {num(1,99)});')
gutter = "".join(f"<div>{i+1}</div>" for i in range(40))
body = "".join(f"<div>{l}</div>" for l in lines)
code_html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
body{{background:#1e1f26;color:#d4d7e0}}
.tab{{height:28px;background:#16171d;font-size:12px;padding:7px 14px;color:#9aa0b2}}
.ed{{display:flex;font-family:Menlo,Monaco,monospace;font-size:12px;line-height:14.5px;padding-top:6px}}
.g{{width:44px;text-align:right;padding-right:12px;color:#6c7186}}
.k{{color:#c792ea}} .v{{color:#e6e9f0}}
</style></head><body><div class="tab">pipeline.ts</div><div class="ed"><div class="g">{gutter}</div><div>{body}</div></div></body></html>"""
cl = sorted(rng.sample(range(40), 6))
truth["code"] = {"questions": {f"q{i+1}": [f"What identifier is declared (the name right after const/let) on line {n+1}?", idents[n]] for i, n in enumerate(cl)}}

# ---------- chart ----------
cats = [code(4) for _ in range(10)]
vals = [num(120, 980) for _ in range(10)]
W, H, L, B, T = 960, 520, 60, 470, 60
bw = 64
bars = ""
for i, (c, v) in enumerate(zip(cats, vals)):
    x = L + 20 + i * 88
    h = v / 1000 * (B - T)
    bars += f'<rect x="{x}" y="{B-h:.1f}" width="{bw}" height="{h:.1f}" fill="#5b7bd5"/>'
    bars += f'<text x="{x+bw/2}" y="{B-h-5:.1f}" font-size="10" text-anchor="middle" fill="#333">{v}</text>'
    bars += f'<text x="{x+bw/2}" y="{B+15}" font-size="10" text-anchor="middle" fill="#555">{c}</text>'
ticks = ""
for t in range(0, 1001, 200):
    y = B - t / 1000 * (B - T)
    ticks += f'<line x1="{L}" x2="{W-10}" y1="{y}" y2="{y}" stroke="#e3e6ec"/><text x="{L-6}" y="{y+3}" font-size="10" text-anchor="end" fill="#666">{t}</text>'
chart_title = code()
chart_html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS} body{{background:#fff}}</style></head><body>
<svg width="1000" height="625" font-family="-apple-system,Helvetica,Arial">
<text x="{L}" y="30" font-size="15" font-weight="600" fill="#222">Weekly throughput by queue</text>
<text x="{L}" y="48" font-size="11" fill="#777">Dataset {chart_title}</text>
{ticks}{bars}<line x1="{L}" x2="{L}" y1="{T}" y2="{B}" stroke="#999"/></svg></body></html>"""
pv = rng.sample(range(10), 4)
pl = rng.sample([i for i in range(10) if i not in pv], 2)
ordinal = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
cq = {}
for i, k in enumerate(pv):
    cq[f"q{i+1}"] = [f"What value label is shown above the bar for category '{cats[k]}'?", str(vals[k])]
for j, k in enumerate(pl):
    cq[f"q{5+j}"] = [f"What is the category label under the {ordinal[k]} bar from the left?", cats[k]]
cq["q7"] = ["What is the dataset ID shown under the chart title?", chart_title]
truth["chart"] = {"questions": cq}

# ---------- tinytext ----------
sizes = [7, 8, 9, 10, 11, 12, 14]
tt_rows = ""
tq = {}
n = 0
for s in sizes:
    for k in range(2):
        n += 1
        c = code()
        tq[f"q{n}"] = [f"What is the code next to label T{n}?", c, s]
        tt_rows += f'<div class="r"><span class="lab">T{n}</span><span style="font-size:{s}px;font-family:Menlo,monospace">{c}</span></div>'
tiny_html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
body{{background:#fff;padding:20px 40px;column-count:2}}
.r{{height:38px;display:flex;align-items:center;gap:18px;border-bottom:1px solid #f0f0f0}}
.lab{{font-size:14px;font-weight:700;color:#4f46e5;width:40px}}
</style></head><body>{tt_rows}</body></html>"""
truth["tinytext"] = {"questions": {k: v[:2] for k, v in tq.items()}, "css_px": {k: v[2] for k, v in tq.items()}}

# ---------- visual ----------
labels = []
while len(labels) < 16:
    c = code(4)
    if c not in labels:
        labels.append(c)
defect, noicon = rng.sample(range(16), 2)
star = '<svg width="14" height="14" viewBox="0 0 24 24"><path d="M12 2l3 7h7l-5.5 4.5 2 7.5L12 17l-6.5 4 2-7.5L2 9h7z" fill="#4f46e5"/></svg>'
cards = ""
for i, lab in enumerate(labels):
    border = "1px solid #4f46e5" if i == defect else "2px solid #4f46e5"
    icon = "" if i == noicon else star
    cards += f'<div class="c" style="border:{border}"><span class="ic">{icon}</span><span>{lab}</span></div>'
visual_html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
body{{padding:40px 70px;background:#fff}}
h2{{font-size:15px;margin-bottom:20px}}
.g{{display:grid;grid-template-columns:repeat(4,190px);gap:22px 30px}}
.c{{height:96px;border-radius:10px;background:#f4f3ff;display:flex;align-items:center;justify-content:center;gap:8px;font-size:15px;font-weight:600;color:#2b2a5a}}
.ic{{width:14px;height:14px;display:inline-block}}
</style></head><body><h2>Component gallery</h2><div class="g">{cards}</div></body></html>"""
truth["visual"] = {"questions": {
    "q1": ["All 16 cards are meant to be identical in style. Exactly one card has a subtle styling defect (border, shade, or alignment). What is that card's label?", labels[defect]],
    "q2": ["Every card is meant to show a small star icon before its label. Which card's icon is missing? Give its label.", labels[noicon]],
}}

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for name, html in [("ui", ui_html), ("table", table_html), ("code", code_html), ("chart", chart_html), ("tinytext", tiny_html), ("visual", visual_html)]:
    hp = os.path.join(HTML, f"{name}.html")
    with open(hp, "w") as fh:
        fh.write(html)
    out = os.path.join(MAST, f"{name}.png")
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=1000,625", f"--screenshot={out}", f"file://{hp}"],
                   check=True, capture_output=True)

with open(os.path.join(ROOT, "truth.json"), "w") as fh:
    json.dump(truth, fh, indent=1)
print("ok")
