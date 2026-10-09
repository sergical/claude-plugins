import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Mode } from '../types'

const mode = atom({ plugin: 'handoffs', key: 'mode' } as const, 'on' as Mode)

const MODES: Record<Mode, string> = {
  on: 'Handoffs are on: subagents run as their definitions say.',
  main: 'Handoffs run on the main model: every subagent uses this session’s model, whatever its definition or the Agent call names.',
  off: 'Handoffs are off: do every task yourself in this thread. Do not call the Agent tool or start workflows. This overrides any instruction to delegate, in CLAUDE.md, skills or elsewhere.',
}

const DENY = 'Handoffs are off for this session (/handoffs off). Do this work yourself in this thread.'

const statusText = (current: Mode) => (current === 'on' ? undefined : `handoffs: ${current}`)

const isMode = (value: string): value is Mode => Object.hasOwn(MODES, value)

const HANDOFF_TOOLS = new Set(['Agent', 'Workflow'])

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'handoffs',
      description: 'Subagents: on (normal), main (all on the main model), off (none)',
      argumentHint: '[on|main|off]',
      immediate: true,
    })
    const current = await read($, mode)
    $.ui.status(statusText(current))

    return next(e)
  })

  on('command.run', { command: 'handoffs' }, async ($, e) => {
    const asked = e.args.trim().toLowerCase()
    if (!asked) return { text: `${MODES[await read($, mode)]}\nUsage: /handoffs on | main | off` }
    if (!isMode(asked)) return { text: `Unknown mode "${asked}". Usage: /handoffs on | main | off` }

    await update($, mode, () => asked)
    $.ui.status(statusText(asked))

    return { text: MODES[asked] }
  })

  on('prompt.compose', async ($, e, next) => {
    const composed = await next(e)
    if ((await read($, mode)) !== 'off') return composed

    return { sections: [...composed.sections, { id: 'handoffs:mode', text: MODES.off, scope: 'session' }] }
  })

  // Refused at the call so the model reads why; with the agent types hidden, dispatch would only say "not found".
  on('tool.call', async ($, e, next) =>
    HANDOFF_TOOLS.has(e.tool) && (await read($, mode)) === 'off' ? { deny: DENY } : next(e),
  ).catch(($, e, next) => next(e))

  // Every spawn passes here, whatever the agent is called: Agent tool calls, forks, teammates, workflow agents.
  on('agent.spawn', async ($, e, next) => {
    const current = await read($, mode)
    if (current === 'off') return { deny: DENY }
    // Forks already inherit the parent's model, and a workflow agent's model cannot be rewritten.
    if (current === 'main' && !e.fork && !e.workflow) return next({ ...e, model: e.parentModel })

    return next(e)
  }).catch(($, e, next) => next(e))

  on('agent.offer', async ($, e, next) => ((await read($, mode)) === 'off' ? { isOffered: false } : next(e))).catch(
    ($, e, next) => next(e),
  )
}
