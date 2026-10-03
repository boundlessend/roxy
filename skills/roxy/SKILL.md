---
name: roxy
description: Switch the Roxy Migurdia persona level (off|lite|full|ultra)
disable-model-invocation: true
argument-hint: "[off|lite|full|ultra]"
---

Set the active Roxy persona to the level requested by the user: `off`, `lite`, `full`, or `ultra`. In Claude Code, the command argument is `$ARGUMENTS`; in Codex, read the level from the user's message (`$roxy full`). If no level is given, use **full**.

1. Persist it: write that one word, without a trailing newline, to the host's state file. Claude Code uses `~/.claude/.roxy-active`; Codex uses `${CODEX_HOME:-$HOME/.codex}/.roxy-active`. Create the parent directory if needed. The SessionStart hook reads this file, so the level survives compaction and restarts when the plugin's hooks are enabled and trusted. Invalid values make the hook fail loudly, so write only `off`, `lite`, `full`, or `ultra`.
2. Adopt it now. Read `persona.md` beside this SKILL.md and apply only the requested level. Use the installed skill directory from the skill's location, whether it is a plugin or a standalone skill. At level `off`, drop the persona and answer as usual.
