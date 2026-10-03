# Roxy for Claude Code and Codex

A plugin for Claude Code and Codex that gives the assistant the manner of Roxy Migurdia from Mushoku Tensei: a calm mentor who explains step by step, is honest about the limits of her knowledge and skips empty pleasantries. The persona changes only the tone. Technical accuracy, code, commands and error messages stay as they are, and replies stay in the user's language.

## Requirements

Python 3.9 or newer. The hook uses only the standard library.

## Installation

### Claude Code

```
/plugin marketplace add boundlessend/yougile-tracking
/plugin install roxy@senya-plugins
```

The `senya-plugins` marketplace lives in the `yougile-tracking` repository. The persona takes effect in the next session.

### Codex

```bash
codex plugin marketplace add boundlessend/yougile-tracking
codex plugin add roxy@senya-plugins
```

In the Codex desktop app, open the plugin directory, select **Senya Plugins**, and install **Roxy**. Review and trust its SessionStart hook when Codex requests it, then start a new chat. Hook trust is required for automatic activation and reloading after compaction.

For a standalone skill, ask Codex:

```text
$skill-installer install https://github.com/boundlessend/roxy/tree/main/skills/roxy
```

This installs the level-switching skill without the SessionStart hook. Invoke `$roxy full` in each new chat to activate it.

## Levels

Switch the level with `/roxy <level>` (or `/roxy:roxy <level>`) in Claude Code, or `$roxy <level>` in Codex.

| Level | Manner |
|---|---|
| `off` | persona disabled |
| `lite` | calm, polite teacher, modesty barely shows |
| `full` | default: step-by-step explanations, short self-critical asides, pragmatic advice |
| `ultra` | full immersion: hesitation before hard tasks, diary-like thoroughness |

Claude Code stores the level in `~/.claude/.roxy-active`; Codex stores it in `${CODEX_HOME:-$HOME/.codex}/.roxy-active`. The settings are independent. With the plugin's hooks enabled and trusted, the level survives compaction, `/clear` and restarts. Saying "stop roxy" or "normal mode" drops the manner until the next hook reload; `/roxy off` in Claude Code or `$roxy off` in Codex turns it off until you switch it back.

The manner steps aside on its own for security warnings, confirmations of irreversible actions, multi-step instructions and repeated questions.

## How it works

A SessionStart hook runs on startup, `/clear` and compaction. A resumed session already carries the persona from its start, so the hook skips resume instead of adding a second copy. It reads the level, removes the other levels' descriptions and examples from `skills/roxy/persona.md` and adds the persona to the context. If the persona file is missing or the level file holds an invalid value, the hook fails with an error instead of staying silent.

## Updating

Claude Code:

```bash
claude plugin marketplace update senya-plugins
claude plugin update roxy@senya-plugins
```

Codex:

```bash
codex plugin marketplace upgrade senya-plugins
codex plugin add roxy@senya-plugins
```

Restart the host after updating. If Codex requests hook trust again after an update, review the changed definition before enabling it.

## Tests

```bash
python3 tests/smoke_hook.py
```

## License

BSD 3-Clause, see `LICENSE`.
