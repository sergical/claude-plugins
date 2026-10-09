# handoffs

A Claude Code mod that switches subagent handoffs during a session with one command.

Claude Code hands work to subagents: built-in ones such as Explore and general-purpose, and any you or your plugins add. Most agents run on a smaller model than your session, and CLAUDE.md files and skills often tell Claude to delegate. Sometimes you want the main model to do the work itself: the task needs its judgement, a subagent keeps getting it wrong, or you want to see every step in the main thread. handoffs gives you that switch without a restart or a config edit.

## Install

In a Claude Code terminal session:

```
/plugin install handoffs --marketplace sergical/claude-plugins
```

Needs a Claude Code version with mods (v2.1.287 or later).

## Use

```
/handoffs          show the current mode
/handoffs on       normal: subagents run as their definitions say (the default)
/handoffs main     every subagent runs on this session's model
/handoffs off      no subagents: Claude does the work in the main thread
```

The status line shows `handoffs: main` or `handoffs: off` while a mode other than `on` is active. The mode lasts for the session and survives `/compact`.

## What each mode does

The mod acts on every spawn, whatever the agent is called. It has no list of agent names, so it works the same with built-in agents, your own agents, and agents from other plugins.

- **main:** each new subagent's model is set to the model of the agent that starts it, also when the agent definition or the Agent call names another model. For agents that Claude starts from the main thread, this is the session's model. Forks already run on the session's model. Workflow agents keep their own model, because Claude Code does not let a mod change it.
- **off:**
  - Every agent type is hidden from Claude, so the agent list leaves the prompt.
  - Calls to the Agent and Workflow tools are refused with a reason that tells Claude to do the work itself.
  - Every other spawn is refused too: forks, teammates, workflow agents, and agents that other plugins start.
  - A short note in the system prompt tells Claude that handoffs are off and that this overrides delegation instructions in CLAUDE.md and skills.
- **on:** the mod does nothing.

## Limits

- Claude Code's own background helpers (compaction, memory) do not go through the spawn event, so they are not affected.
- A mode switch changes the system prompt and the agent list, so the next request after a switch does not use the prompt cache.
- A mode switch does not change or stop agents that are already running. It applies to the next spawn.
- In `main` mode, an agent that was started on a smaller model before the switch starts its own subagents on that smaller model.

## Checks

```
claude plugin validate plugins/handoffs --strict
claude plugin test plugins/handoffs
```
