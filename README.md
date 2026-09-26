# Roxy for Claude Code

A Claude Code plugin that gives the assistant the manner of Roxy Migurdia from Mushoku Tensei: a calm mentor who explains step by step, is honest about the limits of her knowledge and skips empty pleasantries. The persona changes only the tone. Technical accuracy, code, commands and error messages stay as they are, and replies stay in the user's language.

## Requirements

Python 3.9 or newer. The hook uses only the standard library.

## Installation

```
/plugin marketplace add boundlessend/yougile-tracking
/plugin install roxy@senya-plugins
```

The `senya-plugins` marketplace lives in the `yougile-tracking` repository. The persona takes effect in the next session.

## Levels

Switch the level with `/roxy <level>`, or with the full form `/roxy:roxy <level>`.

| Level | Manner |
|---|---|
| `off` | persona disabled |
| `lite` | calm, polite teacher, modesty barely shows |
| `full` | default: step-by-step explanations, short self-critical asides, pragmatic advice |
| `ultra` | full immersion: hesitation before hard tasks, diary-like thoroughness |

The level is stored in `~/.claude/.roxy-active` and survives compaction, `/clear` and restarts. Saying "stop roxy" or "normal mode" drops the manner in the current conversation; `/roxy off` turns it off until you switch it back.

The manner steps aside on its own for security warnings, confirmations of irreversible actions, multi-step instructions and repeated questions.

## How it works

A SessionStart hook runs on startup, `/clear` and compaction. A resumed session already carries the persona from its start, so the hook skips resume instead of adding a second copy. It reads the level, removes the other levels' descriptions and examples from `skills/roxy/persona.md` and adds the persona to the context. If the persona file is missing or the level file holds an invalid value, the hook fails with an error instead of staying silent.

## Updating

```bash
claude plugin marketplace update senya-plugins
claude plugin update roxy@senya-plugins
```

Restart Claude Code after updating.

## License

BSD 3-Clause, see `LICENSE`.
