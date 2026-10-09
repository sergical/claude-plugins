import { test, expect, mock } from 'claude-code/testing'

const spawn = (extra: object = {}) =>
  ({
    tool_use_id: 'toolu_1',
    prompt: 'look around',
    description: 'look around',
    subagentType: 'Explore',
    model: 'haiku',
    parentModel: 'opus',
    background: false,
    fork: false,
    ...extra,
  }) as never

const handoffs = (args: string) => ({ command: 'handoffs', args, origin: { kind: 'user' } }) as never

test('on: a spawn runs as asked', async ($, on) => {
  mock.env(on, {})
  on('agent.spawn', ($, e) => ({ model: e.model ?? 'none' }))

  expect(await $.agent.spawn(spawn())).toEqual({ model: 'haiku' })
})

test('main: a spawn runs on the parent model, whatever the agent is called', async ($, on) => {
  mock.env(on, {})
  on('agent.spawn', ($, e) => ({ model: e.model ?? 'none' }))
  await $.command.run(handoffs('main'))

  expect(await $.agent.spawn(spawn())).toEqual({ model: 'opus' })
  expect(await $.agent.spawn(spawn({ subagentType: 'my-own-helper', model: 'sonnet' }))).toEqual({ model: 'opus' })
})

test('main: forks and workflow agents pass through unchanged', async ($, on) => {
  mock.env(on, {})
  on('agent.spawn', ($, e) => ({ model: e.model ?? 'none' }))
  await $.command.run(handoffs('main'))

  expect(await $.agent.spawn(spawn({ fork: true }))).toEqual({ model: 'haiku' })
  expect(await $.agent.spawn(spawn({ workflow: { runId: 'wf_1', agentIndex: 0 } }))).toEqual({ model: 'haiku' })
})

test('off: every spawn is denied and no agent type is offered', async ($, on) => {
  mock.env(on, {})
  on('agent.spawn', () => ({ model: 'should-not-run' }))
  on('agent.offer', () => ({ isOffered: true }))
  await $.command.run(handoffs('off'))

  for (const extra of [{}, { subagentType: 'general-purpose' }, { fork: true }, { isTeammate: true }]) {
    const result = (await $.agent.spawn(spawn(extra))) as { deny?: string }
    expect(result.deny).toContain('/handoffs off')
  }
  expect(await $.agent.offer({ agent: 'anything', description: '', source: 'built-in', provider: {} } as never)).toEqual({
    isOffered: false,
  })
})

test('off: Agent and Workflow tool calls are refused with the reason', async ($, on) => {
  mock.env(on, {})
  on('tool.call', () => ({ result: 'ran' }) as never)
  await $.command.run(handoffs('off'))

  for (const tool of ['Agent', 'Workflow']) {
    const result = (await $.tool.call({ tool, prompt: 'x' } as never)) as { deny?: string }
    expect(result.deny).toContain('/handoffs off')
  }
  expect(((await $.tool.call({ tool: 'Bash', command: 'ls' } as never)) as { result?: string }).result).toBe('ran')
})

test('off: the system prompt carries the mode; on and main: it does not', async ($, on) => {
  mock.env(on, {})
  on('prompt.compose', () => ({ sections: [{ id: 'core', text: 'core', scope: 'shared' }] }))
  const ids = async () => (await $.prompt.compose({ model: 'opus', promptModel: 'opus', surfaces: ['terminal'], tools: [], outputStyle: null, traits: [] } as never)).sections.map(s => s.id)

  expect(await ids()).toEqual(['core'])
  await $.command.run(handoffs('main'))
  expect(await ids()).toEqual(['core'])
  await $.command.run(handoffs('off'))
  expect(await ids()).toEqual(['core', 'handoffs:mode'])
  await $.command.run(handoffs('on'))
  expect(await ids()).toEqual(['core'])
})

test('the command shows the mode, switches it and rejects unknown modes', async ($, on) => {
  mock.env(on, {})
  const text = async (args: string) => ((await $.command.run(handoffs(args))) as { text: string }).text

  expect(await text('')).toContain('Handoffs are on')
  expect(await text('banana')).toContain('Unknown mode "banana"')
  expect(await text('OFF')).toContain('Handoffs are off')
  expect(await text('')).toContain('Handoffs are off')
})

test('inherited object keys are not modes and leave off in place', async ($, on) => {
  mock.env(on, {})
  on('agent.spawn', () => ({ model: 'should-not-run' }))
  await $.command.run(handoffs('off'))

  for (const bad of ['constructor', '__proto__', 'toString']) {
    const result = (await $.command.run(handoffs(bad))) as { text: string }
    expect(result.text).toContain('Unknown mode')
  }
  expect(((await $.agent.spawn(spawn())) as { deny?: string }).deny).toContain('/handoffs off')
})
