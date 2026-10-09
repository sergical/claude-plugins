# handoffs

A Claude Code mod that turns subagent handoffs on, off, or onto your main model, mid-session, with one command.

Claude Code hands a lot of work to subagents. Some are built in, like Explore and general-purpose, and you or your plugins add more. Most of them run on a smaller model than your session, and plenty of CLAUDE.md files and skills tell Claude to delegate as often as it can.

That's usually fine. Sometimes it isn't. The task needs the big model's judgement, or a subagent keeps getting the same thing wrong, or you want to watch every step happen in the main thread. With handoffs you type `/handoffs off` and keep going, no restart or config edit.

## Install

In a Claude Code terminal session:

```
/plugin install handoffs --marketplace sergical/claude-plugins
```

You need Claude Code v2.1.287 or later, the first version with mods.

## Use

```
/handoffs          show the current mode
/handoffs on       subagents run as their definitions say (the default)
/handoffs main     subagents run on your session's model
/handoffs off      no subagents, Claude does the work in the main thread
```

While `main` or `off` is set, the status line says so. The mode lasts until the session ends, and `/compact` doesn't reset it.

## What each mode does

The mod acts on every spawn, whatever the agent is called. It keeps no list of agent names. Built-in agents, your own agents, and other plugins' agents all get the same treatment.

**main.** The mod sets each new subagent's model to the model of whoever starts it. That holds even when the agent's definition or the Agent call asks for a different model. When Claude starts an agent from the main thread, that means your session's model. Forks already run on your session's model, so the mod leaves them alone. Workflow agents keep the model their script picked, because Claude Code lets a mod refuse those agents but not change them.

**off.** The mod does four things.

- It hides every agent type, so the agent list drops out of Claude's prompt.
- It refuses calls to the Agent and Workflow tools. Claude gets back "Handoffs are off for this session (/handoffs off). Do this work yourself in this thread." and carries on in the same turn.
- It refuses every other spawn as well, which covers forks, teammates, workflow agents, and agents that other plugins start.
- It adds a short note to the system prompt. The note tells Claude that handoffs are off and that this beats any delegation instruction in CLAUDE.md or a skill.

**on.** The mod does nothing.

## Limits

- Compaction and memory run their own background helpers. Those never reach the spawn event, so the mod can't touch them.
- Switching into or out of `off` changes the system prompt and the agent list. The next request after that switch misses the prompt cache.
- A switch only affects agents that start after it. Agents already running keep going as they were.
- Say an agent started on haiku before you ran `/handoffs main`. Any subagent it starts afterwards also runs on haiku, since the mod copies the starting agent's model.

## Checks

```
claude plugin validate plugins/handoffs --strict
claude plugin test plugins/handoffs
```
