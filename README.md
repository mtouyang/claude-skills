# mtouyang's Claude Code skills

A [Claude Code](https://code.claude.com) plugin marketplace.

## Add the marketplace

Inside a Claude Code session:

```text
/plugin marketplace add mtouyang/claude-skills
```

## Plugins

| Plugin | What it does | Install |
|---|---|---|
| [docs-for-humans](https://github.com/mtouyang/docs-for-humans) | Rewrites manuals, SOPs, and runbooks into a shape a human can follow. English and Traditional Chinese. | `/plugin install docs-for-humans@mtouyang` |

## Updates

Auto-update is off by default for third-party marketplaces. To get new versions:

```text
/plugin marketplace update mtouyang
```

Then update the plugin from the **Installed** tab in `/plugin`, or run `claude plugin update <plugin>@mtouyang` in your shell. You can also turn on auto-update for this marketplace in the **Marketplaces** tab.

## License

[MIT](LICENSE)
