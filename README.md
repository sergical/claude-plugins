# image-diet

A Claude Code mod that shrinks large images before they enter Claude's context.

Screenshots are expensive. On Claude Opus 4.7 and later, an image costs about `ceil(width/28) × ceil(height/28)` tokens, and a 2000 px screenshot costs 3,000–4,800 tokens. A long session with many screenshots fills the context fast and triggers more compactions. image-diet shrinks each image to 1280 px on the long edge. That saves about 60% of the image tokens, and in our tests Claude lost no information.

## Install

In a Claude Code terminal session:

```
/plugin install image-diet --marketplace sergical/image-diet
```

Answer `y` to add the marketplace, then pick a scope (user scope loads it in every session).

Needs a Claude Code version with mods (function hooks), and `sips` (built into macOS) or ImageMagick (`magick`) on Linux.

## What it does

- **Read tool:** a PNG or JPEG larger than 1280 px on its long edge is shrunk before Claude sees it.
- **MCP tools:** image blocks in any `mcp__*` tool result (browser screenshots, Figma, and so on) are shrunk the same way.
- **Click tools are skipped:** computer-use and browser tools that click by screenshot pixel position (names containing `computer`, `cua` or `browser_batch`) are left alone. A smaller screenshot would make every click land in the wrong place.
- **Claude is told:** each shrink adds a short note with the old and new size, so Claude knows it is looking at a smaller copy.
- **Full size on demand:** a file with `.full.` in its name is never shrunk. When Claude needs full detail, it can copy the file to such a name and Read it.
- **Safe failure:** if the resize fails for any reason, Claude gets the original image.

It does **not** shrink images you paste into the prompt. A mod can see that a pasted image exists, but not change it.

## Settings

| Env var | Default | Effect |
|---|---|---|
| `IMAGE_DIET_MAX_EDGE` | `1280` | Long-edge size in pixels. `1024` saves more; `1568` keeps more detail. |
| `IMAGE_DIET_SKIP_TOOLS` | `computer\|cua\|browser_batch` | Regex (case-insensitive) of MCP tool names to leave alone. Add any tool that takes click coordinates from its own screenshots. |

## Why 1280

We found no published evals of vision accuracy versus image size for screenshots, so we measured it. See [`eval/`](eval/).

Opus 5.5 answered questions with known answers about six kinds of retina screenshots (app dashboard, dense table, code, chart, tiny text from 7 to 14 px, a subtle visual defect) at five sizes, through the real Read tool:

| Long edge | Correct | Image tokens |
|---|---|---|
| 2000 | 100% | 3,240 |
| 1568 | 100% | 1,960 |
| **1280** | **100%** | **1,334** |
| 1024 | 100% | 851 |
| 768 | 93% | 504 |

- At 768 px, every miss came back as "unreadable". Claude never gave a confident wrong answer.
- The first thing to fail is text smaller than about 7 device pixels after the shrink.
- The test pages were window-sized (1000 CSS px wide). A full-screen MacBook capture is wider, so 1024 px takes its 11 px text down to about 6.5 px, near the failure point. At 1280 px, that text stays at about 8 px. That is why the default is 1280, not 1024.
- Limits: one model, two repeats per cell, synthetic pages. Anthropic's own guidance points the same way: start near 1080p on newer Opus models, and avoid going below 960×540.

Run it yourself with `eval/run.sh` (macOS, Google Chrome, and a logged-in `claude` CLI). Full tables are in [`eval/results.md`](eval/results.md).

## Develop

```
claude plugin validate .
claude plugin test .
claude --plugin-dir .
```

## License

MIT
