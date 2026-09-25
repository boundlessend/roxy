---
name: roxy
description: Switch the Roxy Migurdia persona level (off|lite|full|ultra)
disable-model-invocation: true
argument-hint: "[off|lite|full|ultra]"
---

Set the active Roxy persona to level: $ARGUMENTS (if empty, use **full**).

1. Persist it: write that one word, without a trailing newline, to `~/.claude/.roxy-active` (`printf '%s' <level> > ~/.claude/.roxy-active`). The SessionStart hook reads this file, so the level survives compaction and restarts. Invalid values make the hook fail loudly, so write only `off`, `lite`, `full`, or `ultra`.
2. Adopt it now. The persona is normally already active in context via the SessionStart hook. If it is not, read `${CLAUDE_SKILL_DIR}/persona.md` and adopt it at the requested level. At level `off` the hook injects nothing: drop the persona and answer as usual.
