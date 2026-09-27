# mtouyang-skills

Claude Code skills by mtouyang, published as one plugin in a Claude Code plugin marketplace.

[繁體中文說明](README.zh-TW.md)

## Skills

| Skill | What it does | Invoke |
|---|---|---|
| [docs-for-humans](#docs-for-humans) | Rewrites manuals, SOPs, and runbooks into a shape a human can follow. English and Traditional Chinese. | `/mtouyang-skills:docs-for-humans` |

## Install

Requires [Claude Code](https://code.claude.com). The skills use `${CLAUDE_SKILL_DIR}` to find their scripts, so they are not supported on claude.ai or the API.

### As a plugin (recommended)

Inside a Claude Code session:

```text
/plugin marketplace add mtouyang/claude-skills
/plugin install mtouyang-skills@mtouyang
```

This installs every skill in the plugin. A plugin's skills can only be enabled or disabled together.

### One skill, by copying its folder

```bash
git clone https://github.com/mtouyang/claude-skills.git
cp -r claude-skills/skills/docs-for-humans ~/.claude/skills/
```

### Updates

Auto-update is off by default for third-party marketplaces. To get new versions:

```text
/plugin marketplace update mtouyang
```

Then update the plugin from the **Installed** tab in `/plugin`, or run `claude plugin update mtouyang-skills@mtouyang` in your shell. You can also turn on auto-update for this marketplace in the **Marketplaces** tab.

## docs-for-humans

Rewrites manuals, SOPs, and runbooks into a shape a person can actually follow.

Operating docs are rarely hard because they lack detail. They are hard because "what to do now" and "why it is this way" are glued into the same sentence. This skill separates the two without deleting either:

1. **A routing table first:** why you are here → which section → how long it takes.
2. **The full command sequence first:** one copy-paste block per procedure, with the expected output in comments.
3. **A bold budget:** at most a quarter of the original's bold survives, and each one must name what breaks if it is ignored.
4. **Rationale in an appendix:** reasons that do not change the reader's next action move to numbered notes (C1, C2, …) with a one-line anchor left in place.
5. **Asides become sentences:** em-dash and parenthetical insertions are split out.
6. **Full-width punctuation (Chinese only)**, fixed and checked by a script.

Every rewrite ends with a change summary whose numbers come from a script, not an estimate.

### See it

The same fictional runbook, before and after:

| | Before | After |
|---|---|---|
| English | [before.md](examples/docs-for-humans/en/before.md) | [after.md](examples/docs-for-humans/en/after.md) |
| 繁體中文 | [before.md](examples/docs-for-humans/zh-TW/before.md) | [after.md](examples/docs-for-humans/zh-TW/after.md) |

Bold 23 → 2 in both. The docs get longer, not shorter: 17 → 75 lines in English. What you gain is that the person following the steps only needs the first third.

### Use

Ask in plain words, for example "this runbook is hard to follow, rewrite it" or "這份 SOP 看不懂，幫我改寫". Claude picks the skill up from its description. It can also be invoked directly as `/mtouyang-skills:docs-for-humans`.

The skill writes a draft next to the original with a change summary at the end. When you accept it, ask Claude to finalise the draft.

### Languages

| Language | Rules | Extra checks |
|---|---|---|
| English | 1–5 | – |
| Traditional Chinese (zh-TW) | 1–6 | `check_punct.py` |

Other languages get rules 1–4. A Simplified Chinese (zh-CN) module is welcome as a pull request: quotation marks and word choice differ from zh-TW, so it needs someone who writes zh-CN daily.

### Scripts

All scripts use only the Python standard library (3.9+). Each exits with code 1 when a check fails.

| Script | What it does |
|---|---|
| `doc_stats.py [--baseline ORIGINAL] FILE…` | Line count, bold count, broken relative links; with `--baseline`, fails if bold is above a quarter of the original |
| `fix_punct.py FILE…` | zh-TW: converts half-width punctuation next to Chinese characters to full-width, in place. Leaves code, URLs, link targets, and times alone |
| `check_punct.py FILE…` | zh-TW: reports half-width punctuation next to Chinese characters |

## Develop

```bash
pip install pytest
pytest -q
```

Each skill's tests live in `tests/<skill>/`. CI runs them on Python 3.9 and 3.13.

A skill is published only when it is listed in the `skills` array of `.claude-plugin/plugin.json`.

### How to release

All skills share one version.

1. Bump `version` in `.claude-plugin/plugin.json`, commit, and push to `main`.
2. Tag the same version and push the tag: `git tag v1.2.3 && git push origin v1.2.3`. CI fails if the tag and `plugin.json` disagree.
3. Set the plugin's `ref` in `.claude-plugin/marketplace.json` to the new tag, commit, and push to `main`.

Changes on `main` reach users only through step 3.

## License

[MIT](LICENSE)
