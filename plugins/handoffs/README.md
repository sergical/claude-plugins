# handoffs

Turn subagents on, off, or onto your main model in the middle of a session.

Claude Code hands work to subagents, which usually run on a smaller model. When you want the main model to do the work itself, type `/handoffs off` and keep going.

## Install

```
/plugin install handoffs --marketplace sergical/claude-plugins
```

Needs Claude Code v2.1.287 or later.

## Use

```
/handoffs          show the current mode
/handoffs on       subagents run as defined (default)
/handoffs main     subagents run on your session's model
/handoffs off      no subagents, Claude does the work itself
```

The mode lasts for the session and shows in the status line. It works on every agent, whatever its name: built-in, your own, or another plugin's.

**main** overrides the model an agent asks for. Workflow agents keep their own model, because Claude Code doesn't let a mod change it.

**off** hides all agent types and refuses every spawn, including forks, teammates and workflow agents. Claude gets a message telling it to do the work itself, and the turn continues.

## Limits

- Agents already running are not affected by a switch.
- In `main` mode, an agent that started on a smaller model before the switch gives its own subagents that model too.
- Switching into or out of `off` misses the prompt cache once.

## Checks

```
claude plugin validate plugins/handoffs --strict
claude plugin test plugins/handoffs
```
