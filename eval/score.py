import json, math, os, re, glob
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
truth = json.load(open(os.path.join(ROOT, "truth.json")))
TYPES = ["ui", "table", "code", "chart", "tinytext", "visual"]
SIZES = [2000, 1568, 1280, 1024, 768]
DIMS = {2000: (2000, 1250), 1568: (1568, 980), 1280: (1280, 800), 1024: (1024, 640), 768: (768, 480)}


def norm(s):
    s = str(s).strip().lower()
    s = re.sub(r"^\$", "", s)
    if re.fullmatch(r"[\d,\.\s%]+", s):
        s = s.replace(",", "").replace(" ", "").rstrip("%")
        try:
            return repr(float(s))
        except ValueError:
            pass
    return s


def parse_answers(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


acc = defaultdict(lambda: [0, 0])          # (type,size) -> [correct, total]
wrong = defaultdict(int)                   # (type,size) -> confident wrong
unread = defaultdict(int)                  # (type,size) -> UNREADABLE / missing
tok = defaultdict(list)                    # size -> total input tokens per call
tt_ok = defaultdict(lambda: [0, 0])        # (size, css_px) -> [correct, total]
misreads = []
failed = []

for t in TYPES:
    qs = truth[t]["questions"]
    for n in SIZES:
        for f in sorted(glob.glob(os.path.join(ROOT, "raw", f"{t}_{n}_r*.json"))):
            try:
                d = json.load(open(f))
            except Exception:
                failed.append(os.path.basename(f)); continue
            if d.get("is_error"):
                failed.append(os.path.basename(f)); continue
            u = d.get("usage", {})
            tok[n].append(u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0))
            ans = parse_answers(d.get("result")) or {}
            for q, (_, gt, *_) in qs.items():
                a = ans.get(q)
                acc[(t, n)][1] += 1
                ok = a is not None and norm(a) == norm(gt)
                if t == "tinytext":
                    px = truth[t]["css_px"][q]
                    tt_ok[(n, px)][1] += 1
                    tt_ok[(n, px)][0] += ok
                if ok:
                    acc[(t, n)][0] += 1
                elif a is None or "unreadable" in str(a).lower():
                    unread[(t, n)] += 1
                else:
                    wrong[(t, n)] += 1
                    misreads.append((t, n, q, gt, a))

L = []
L.append("# Image downscale eval: Claude Opus 5.5 via the Read tool\n")
L.append("Masters: 2000x1250 retina screenshots (headless Chrome, CSS 1000x625 at 2x). Copies made with `sips -Z`. "
         "One `claude -p --model claude-opus-5-5 --safe-mode --tools Read --strict-mcp-config` call per image x size x repeat (2 repeats). "
         "`--bare` was not usable (it needs ANTHROPIC_API_KEY); `--safe-mode` turns off plugins, hooks and CLAUDE.md. "
         "Exact match after trim and lowercase; numbers ignore `,`, `$` and `%`. Codes exclude 0/O/1/I/l.\n")
L.append("## Accuracy (correct / asked, both repeats)\n")
L.append("| type | " + " | ".join(str(n) for n in SIZES) + " |")
L.append("|---|" + "---|" * len(SIZES))
for t in TYPES:
    cells = []
    for n in SIZES:
        c, k = acc[(t, n)]
        cells.append(f"{c}/{k} ({100*c/k:.0f}%)" if k else "n/a")
    L.append(f"| {t} | " + " | ".join(cells) + " |")
tc = {n: sum(acc[(t, n)][0] for t in TYPES) for n in SIZES}
tk = {n: sum(acc[(t, n)][1] for t in TYPES) for n in SIZES}
L.append("| **all** | " + " | ".join(f"**{tc[n]}/{tk[n]} ({100*tc[n]/max(tk[n],1):.0f}%)**" for n in SIZES) + " |")

L.append("\n## Errors: confident wrong answer vs UNREADABLE\n")
L.append("Cell format: wrong / UNREADABLE. A wrong answer is a silent misread.\n")
L.append("| type | " + " | ".join(str(n) for n in SIZES) + " |")
L.append("|---|" + "---|" * len(SIZES))
for t in TYPES:
    L.append(f"| {t} | " + " | ".join(f"{wrong[(t,n)]} / {unread[(t,n)]}" for n in SIZES) + " |")
L.append("| **all** | " + " | ".join(f"**{sum(wrong[(t,n)] for t in TYPES)} / {sum(unread[(t,n)] for t in TYPES)}**" for n in SIZES) + " |")

L.append("\n## Tokens per size\n")
L.append("| long edge | dims | ceil(w/28)*ceil(h/28) | measured mean input tokens per call | delta vs 2000 |")
L.append("|---|---|---|---|---|")
base = sum(tok[2000]) / len(tok[2000]) if tok[2000] else 0
for n in SIZES:
    w, h = DIMS[n]
    est = math.ceil(w / 28) * math.ceil(h / 28)
    m = sum(tok[n]) / len(tok[n]) if tok[n] else 0
    L.append(f"| {n} | {w}x{h} | {est} | {m:.0f} | {m-base:+.0f} |")
L.append("\nMeasured input = input + cache_creation + cache_read over the whole call (prompt text differs per type, but the type mix is the same at every size).\n")

L.append("## tinytext legibility (correct / asked, 4 per cell)\n")
pxs = sorted({v for v in truth["tinytext"]["css_px"].values()})
L.append("| long edge (scale) | " + " | ".join(f"CSS {p}px" for p in pxs) + " | smallest CSS px with all correct | that size in device px |")
L.append("|---|" + "---|" * (len(pxs) + 2))
for n in SIZES:
    scale = 2 * n / 2000
    cells = [f"{tt_ok[(n,p)][0]}/{tt_ok[(n,p)][1]}" for p in pxs]
    floor = None
    for p in pxs:
        if all(tt_ok[(n, q)][0] == tt_ok[(n, q)][1] and tt_ok[(n, q)][1] for q in pxs if q >= p):
            floor = p
            break
    fl = f"{floor}" if floor else "none"
    dp = f"{floor*scale:.1f}" if floor else "-"
    L.append(f"| {n} ({scale:.2f}x CSS) | " + " | ".join(cells) + f" | {fl} | {dp} |")

L.append("\n## Misreads (type, size, question, truth, answer)\n")
for m in misreads:
    L.append(f"- {m[0]} {m[1]} {m[2]}: `{m[3]}` -> `{m[4]}`")
if failed:
    L.append("\nFailed calls: " + ", ".join(failed))

open(os.path.join(ROOT, "results.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L[:40]))
