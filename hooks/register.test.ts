import { test, expect, mock } from 'claude-code/testing'

const BIG = 'QklHSU1BR0U='
const SMALL = 'U01BTEw='

const readImage = (base64: string) => ({
  type: 'image',
  file: {
    base64,
    type: 'image/png',
    originalSize: 1000,
    dimensions: { originalWidth: 2000, originalHeight: 1250, displayWidth: 2000, displayHeight: 1250 },
  },
})

const ok = (stdout: string, exitCode = 0) => ({
  value: { exitCode, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false },
})

test('shrinks a large image from Read and tells the model', async ($, on) => {
  mock.env(on, {})
  const runs: (readonly string[])[] = []
  on('process.run', ($, e) => {
    runs.push(e.argv)
    return ok(`2000 1250 1280 800\n${SMALL}`)
  })
  on('tool.call', { tool: 'Read' }, () => ({ result: readImage(BIG) }) as never)

  const ran = (await $.tool.call({ tool: 'Read', file_path: '/tmp/shot.png' })) as any
  expect(runs.length).toBe(1)
  expect(runs[0]?.slice(-2)).toEqual(['1280', 'png'])
  expect(ran.result.file.base64).toBe(SMALL)
  expect(ran.result.file.dimensions.displayWidth).toBe(1280)
  expect(ran.result.file.dimensions.originalWidth).toBe(2000)
  expect(ran.context[0]).toContain('from 2000x1250 to 1280x800')
})

test('leaves an image alone when it already fits', async ($, on) => {
  mock.env(on, {})
  on('process.run', () => ok('', 3))
  on('tool.call', { tool: 'Read' }, () => ({ result: readImage(BIG) }) as never)

  const ran = (await $.tool.call({ tool: 'Read', file_path: '/tmp/small.png' })) as any
  expect(ran.result.file.base64).toBe(BIG)
  expect(ran.context ?? []).toEqual([])
})

test('skips files marked .full.', async ($, on) => {
  mock.env(on, {})
  let runs = 0
  on('process.run', () => {
    runs++
    return ok(`2000 1250 1280 800\n${SMALL}`)
  })
  on('tool.call', { tool: 'Read' }, () => ({ result: readImage(BIG) }) as never)

  const ran = (await $.tool.call({ tool: 'Read', file_path: '/tmp/shot.full.png' })) as any
  expect(runs).toBe(0)
  expect(ran.result.file.base64).toBe(BIG)
})

test('shrinks image blocks in MCP results and keeps text blocks', async ($, on) => {
  mock.env(on, {})
  on('process.run', () => ok(`2560 1600 1280 800\n${SMALL}`))
  on('tool.call', () =>
    ({
      result: {
        isError: false,
        content: [
          { type: 'text', text: 'screenshot taken' },
          { type: 'image', data: BIG, mimeType: 'image/jpeg' },
        ],
      },
    }) as never,
  )

  const ran = (await $.tool.call({ tool: 'mcp__browser__screenshot' } as never)) as any
  expect(ran.result.content[0]).toEqual({ type: 'text', text: 'screenshot taken' })
  expect(ran.result.content[1].data).toBe(SMALL)
  expect(ran.context[0]).toContain('from 2560x1600 to 1280x800')
})

test('skips tools that click by screenshot coordinates', async ($, on) => {
  mock.env(on, {})
  let runs = 0
  on('process.run', () => {
    runs++
    return ok(`2560 1600 1280 800\n${SMALL}`)
  })
  on('tool.call', () =>
    ({ result: { isError: false, content: [{ type: 'image', data: BIG, mimeType: 'image/png' }] } }) as never,
  )

  for (const tool of ['mcp__computer-use__screenshot', 'mcp__claude-in-chrome__computer', 'mcp__cmux-cua__zoom']) {
    const ran = (await $.tool.call({ tool } as never)) as any
    expect(ran.result.content[0].data).toBe(BIG)
  }
  expect(runs).toBe(0)
})

test('IMAGE_DIET_SKIP_TOOLS replaces the skip list', async ($, on) => {
  mock.env(on, { IMAGE_DIET_SKIP_TOOLS: 'figma' })
  on('process.run', () => ok(`2560 1600 1280 800\n${SMALL}`))
  on('tool.call', () =>
    ({ result: { isError: false, content: [{ type: 'image', data: BIG, mimeType: 'image/png' }] } }) as never,
  )

  const skipped = (await $.tool.call({ tool: 'mcp__figma__get_screenshot' } as never)) as any
  expect(skipped.result.content[0].data).toBe(BIG)
  const shrunk = (await $.tool.call({ tool: 'mcp__computer-use__screenshot' } as never)) as any
  expect(shrunk.result.content[0].data).toBe(SMALL)
})

test('IMAGE_DIET_MAX_EDGE sets the size', async ($, on) => {
  mock.env(on, { IMAGE_DIET_MAX_EDGE: '1024' })
  const runs: (readonly string[])[] = []
  on('process.run', ($, e) => {
    runs.push(e.argv)
    return ok(`2000 1250 1024 640\n${SMALL}`)
  })
  on('tool.call', { tool: 'Read' }, () => ({ result: readImage(BIG) }) as never)

  await $.tool.call({ tool: 'Read', file_path: '/tmp/shot.png' })
  expect(runs[0]?.slice(-2)).toEqual(['1024', 'png'])
})

test('passes the original through when resizing fails', async ($, on) => {
  mock.env(on, {})
  on('process.run', () => ok('', 1))
  on('tool.call', { tool: 'Read' }, () => ({ result: readImage(BIG) }) as never)

  const ran = (await $.tool.call({ tool: 'Read', file_path: '/tmp/shot.png' })) as any
  expect(ran.result.file.base64).toBe(BIG)
})
