import type { EngineInterface, McpContentBlock, Register } from 'claude-code'

const DEFAULT_MAX_EDGE = 1280
const FULL_SIZE_MARKER = '.full.'
// These tools take click coordinates in the pixels of the screenshot they
// returned, so a shrunk screenshot would move every click.
const DEFAULT_SKIP_TOOLS = 'computer|cua|browser_batch'
const EXT: Record<string, string> = { 'image/png': 'png', 'image/jpeg': 'jpg' }

// Prints "<oldW> <oldH> <newW> <newH>" then the resized base64 on one line.
// Exit 3 means the image already fits. sips ships with macOS; ImageMagick
// covers Linux.
const SHRINK_SH = `set -eu
max=$1 ext=$2
d=$(mktemp -d); trap 'rm -rf "$d"' EXIT
in="$d/in.$ext" out="$d/out.$ext"
base64 -d > "$in"
dims() {
  if command -v sips >/dev/null 2>&1; then
    sips -g pixelWidth -g pixelHeight "$1" | awk '/pixel/{printf "%s ", $2}'
  else
    magick identify -format '%w %h' "$1[0]"
  fi
}
set -- $(dims "$in")
[ "$1" -gt "$max" ] || [ "$2" -gt "$max" ] || exit 3
if command -v sips >/dev/null 2>&1; then
  sips -Z "$max" "$in" --out "$out" >/dev/null
else
  magick "$in[0]" -resize "\${max}x\${max}>" "$out"
fi
echo "$1 $2 $(dims "$out")"
base64 < "$out" | tr -d '\\n'
`

type Shrunk = { base64: string; from: string; to: string; width: number; height: number }
type ReadImage = {
  type: 'image'
  file: { base64: string; type: string; dimensions?: Record<string, number> }
}
type McpResult = { content: McpContentBlock[] }

const isReadImage = (r: unknown): r is ReadImage =>
  (r as ReadImage | undefined)?.type === 'image' && typeof (r as ReadImage).file?.base64 === 'string'
const isMcpResult = (r: unknown): r is McpResult => Array.isArray((r as McpResult | undefined)?.content)

async function shrink($: EngineInterface, base64: string, mime: string | undefined): Promise<Shrunk | undefined> {
  const ext = mime && EXT[mime]
  if (!ext) return undefined
  const maxEdge = Number(await $.env.get('IMAGE_DIET_MAX_EDGE')) || DEFAULT_MAX_EDGE
  const ran = await $.process.run(['sh', '-c', SHRINK_SH, 'sh', String(maxEdge), ext], {
    stdin: base64,
    timeoutMs: 10_000,
  })
  if (ran.exitCode !== 0 || ran.isStdoutTruncated) return undefined
  const newline = ran.stdout.indexOf('\n')
  const [ow, oh, w = 0, h = 0] = ran.stdout.slice(0, newline).trim().split(/\s+/).map(Number)
  const out = ran.stdout.slice(newline + 1).trim()
  if (!out || !(w > 0 && h > 0)) return undefined
  return { base64: out, from: `${ow}x${oh}`, to: `${w}x${h}`, width: w, height: h }
}

const note = (what: string, s: Shrunk) =>
  `image-diet: shrank ${what} from ${s.from} to ${s.to} to save context. ` +
  `For full resolution, copy the file to a name containing "${FULL_SIZE_MARKER}" and Read that copy.`

export const register: Register = on => {
  on('tool.call', { tool: 'Read' }, async ($, e, next) => {
    const ran = await next(e)
    try {
      if (!('result' in ran) || e.file_path.includes(FULL_SIZE_MARKER)) return ran
      const result = ran.result
      if (!isReadImage(result)) return ran
      const s = await shrink($, result.file.base64, result.file.type)
      if (!s) return ran
      const dims = result.file.dimensions
      return {
        result: {
          ...result,
          file: {
            ...result.file,
            base64: s.base64,
            dimensions: dims && { ...dims, displayWidth: s.width, displayHeight: s.height },
          },
        },
        context: [note(e.file_path, s)],
      }
    } catch {
      return ran
    }
  }).catch(($, e, next) => next(e))

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (!e.tool.startsWith('mcp__') || !('result' in ran) || !isMcpResult(ran.result)) return ran
    const result = ran.result
    try {
      const skip = new RegExp((await $.env.get('IMAGE_DIET_SKIP_TOOLS')) || DEFAULT_SKIP_TOOLS, 'i')
      if (skip.test(e.tool)) return ran
      const notes: string[] = []
      const content = await Promise.all(
        result.content.map(async block => {
          if (block.type !== 'image' || typeof block.data !== 'string') return block
          const s = await shrink($, block.data, block.mimeType)
          if (!s) return block
          notes.push(note(`a ${e.tool} image`, s))
          return { ...block, data: s.base64 }
        }),
      )
      if (!notes.length) return ran
      return { result: { ...result, content }, context: notes }
    } catch {
      return ran
    }
  }).catch(($, e, next) => next(e))
}
