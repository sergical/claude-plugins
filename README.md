# claude-plugins

Claude Code plugins and mods by [Sergiy Dybskiy](https://serg.tech). A mod is a plugin with code hooks that run inside Claude Code; a plugin can also hold skills, commands, agents and MCP servers.

## Plugins

| Plugin | Kind | What it does |
|---|---|---|
| [image-diet](plugins/image-diet) | mod | Shrinks large images from Read and MCP tools before they enter Claude's context. About 59% fewer image tokens, same answers. |

## Install

In a Claude Code session:

```
/plugin install <plugin> --marketplace sergical/claude-plugins
```

Or add the marketplace once and install by name:

```
/plugin marketplace add sergical/claude-plugins
/plugin install image-diet@sergical
```

Mods need Claude Code v2.1.287 or later.

If you installed image-diet from `sergical/image-diet` before, remove that marketplace and install again from this one. The marketplace is now named `sergical`.

## Layout

```
.claude-plugin/marketplace.json   lists every plugin
plugins/<name>/                    one folder per plugin, with its own plugin.json and README
```

To add a plugin: create `plugins/<name>/`, add an entry to `marketplace.json`, and run the checks below.

## Checks

```
claude plugin validate . --strict
claude plugin validate plugins/<name> --strict
claude plugin test plugins/<name>
```

CI runs these for every plugin on each push.

## License

MIT
