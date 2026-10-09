# Image downscale eval: Claude Opus 5.5 via the Read tool

Masters: 2000x1250 retina screenshots (headless Chrome, CSS 1000x625 at 2x). Copies made with `sips -Z`. One `claude -p --model claude-opus-5-5 --safe-mode --tools Read --strict-mcp-config` call per image x size x repeat (2 repeats). `--bare` was not usable (it needs ANTHROPIC_API_KEY); `--safe-mode` turns off plugins, hooks and CLAUDE.md. Exact match after trim and lowercase; numbers ignore `,`, `$` and `%`. Codes exclude 0/O/1/I/l.

## Accuracy (correct / asked, both repeats)

| type | 2000 | 1568 | 1280 | 1024 | 768 |
|---|---|---|---|---|---|
| ui | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) | 14/16 (88%) |
| table | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) |
| code | 12/12 (100%) | 12/12 (100%) | 12/12 (100%) | 12/12 (100%) | 12/12 (100%) |
| chart | 14/14 (100%) | 14/14 (100%) | 14/14 (100%) | 14/14 (100%) | 14/14 (100%) |
| tinytext | 28/28 (100%) | 28/28 (100%) | 28/28 (100%) | 28/28 (100%) | 24/28 (86%) |
| visual | 4/4 (100%) | 4/4 (100%) | 4/4 (100%) | 4/4 (100%) | 4/4 (100%) |
| **all** | **90/90 (100%)** | **90/90 (100%)** | **90/90 (100%)** | **90/90 (100%)** | **84/90 (93%)** |

## Errors: confident wrong answer vs UNREADABLE

Cell format: wrong / UNREADABLE. A wrong answer is a silent misread.

| type | 2000 | 1568 | 1280 | 1024 | 768 |
|---|---|---|---|---|---|
| ui | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 2 |
| table | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| code | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| chart | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| tinytext | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 4 |
| visual | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| **all** | **0 / 0** | **0 / 0** | **0 / 0** | **0 / 0** | **0 / 6** |

## Tokens per size

| long edge | dims | ceil(w/28)*ceil(h/28) | measured mean input tokens per call | delta vs 2000 |
|---|---|---|---|---|
| 2000 | 2000x1250 | 3240 | 10142 | +0 |
| 1568 | 1568x980 | 1960 | 8862 | -1280 |
| 1280 | 1280x800 | 1334 | 8236 | -1906 |
| 1024 | 1024x640 | 851 | 7753 | -2389 |
| 768 | 768x480 | 504 | 7403 | -2739 |

Measured input = input + cache_creation + cache_read over the whole call (prompt text differs per type, but the type mix is the same at every size).

## tinytext legibility (correct / asked, 4 per cell)

| long edge (scale) | CSS 7px | CSS 8px | CSS 9px | CSS 10px | CSS 11px | CSS 12px | CSS 14px | smallest CSS px with all correct | that size in device px |
|---|---|---|---|---|---|---|---|---|---|
| 2000 (2.00x CSS) | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 7 | 14.0 |
| 1568 (1.57x CSS) | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 7 | 11.0 |
| 1280 (1.28x CSS) | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 7 | 9.0 |
| 1024 (1.02x CSS) | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 7 | 7.2 |
| 768 (0.77x CSS) | 0/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 8 | 6.1 |

## Misreads (type, size, question, truth, answer)


None. No size produced a confident wrong answer. All 6 losses at 768 were reported as UNREADABLE: the 4 tinytext codes at CSS 7px, and the ui build ID (CSS 11px, gray #8a91a6 on dark #1e2230) in both repeats. No call failed and no call needed a retry.

## Interpretation

- Accuracy did not drop from 2000 down to 1024 for any type. The first loss is at 768.
- The token formula matches the measurements exactly. Each delta vs 2000 equals the formula difference (for example, 3240 - 1960 = 1280). At these dims, Opus 5.5 takes the 2000 px image at full resolution, with no server-side downscale.
- Legibility depends on device px per glyph, not on the long edge. Text was read at 7.2 device px (CSS 7px at 1024) and failed at 5.4 device px (CSS 7px at 768). Low-contrast 11px text failed at 8.4 device px (768).
- These masters are 1000 CSS px wide. A full-screen retina capture is wider (for example, 3456x2234 = 1728 CSS px). At a 1024 long edge, that capture is 0.59x CSS, so 11px text becomes about 6.5 device px, which is close to the failure point. At 1280 it is 0.74x CSS, so 11px text becomes about 8.1 device px.
- Limits: 2 repeats per cell, one random seed, and one model. The visual test (a 1px vs 2px border at CSS scale) did not discriminate between sizes.
