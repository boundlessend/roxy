#!/usr/bin/env python3
"""load the Roxy persona into context at session start and after compaction

the active persona level comes from ~/.claude/.roxy-active (written by the
/roxy command); without that file the level is full, and at level off the
hook silently injects nothing

if the persona file is missing, empty or unreadable, the hook writes a visible
message to stderr and exits with a non-zero code, so Claude Code reports the
hook failure instead of staying silent
"""
import json
import os
import sys

PERSONA_PATH: str = os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"], "skills", "roxy", "persona.md")
LEVEL_PATH: str = os.path.expanduser("~/.claude/.roxy-active")
DEFAULT_LEVEL: str = "full"
VALID_LEVELS: frozenset[str] = frozenset({"off", "lite", "full", "ultra"})


def read_persona(path: str) -> str:
    """read the persona file or fail with a clear error on stderr"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[roxy-persona] file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"[roxy-persona] cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)

    if not content.strip():
        print(f"[roxy-persona] file is empty: {path}", file=sys.stderr)
        sys.exit(2)

    return content


def read_level(path: str) -> str:
    """read the active persona level, full when the file is missing"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            level = f.read().strip().lower()
    except FileNotFoundError:
        return DEFAULT_LEVEL
    except OSError as e:
        print(f"[roxy-persona] cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)

    if level not in VALID_LEVELS:
        print(
            f"[roxy-persona] invalid level {level!r} in {path}, "
            f"expected one of {sorted(VALID_LEVELS)}",
            file=sys.stderr,
        )
        sys.exit(2)

    return level


def slice_to_level(persona: str, level: str) -> str:
    """keep only the active level's lines in the Intensity and Example sections"""
    others = VALID_LEVELS - {"off", level}
    kept: list[str] = []
    for line in persona.splitlines():
        stripped = line.lstrip("- ").lower()
        if any(stripped.startswith((f"**{lv}**", f"{lv}:")) for lv in others):
            continue
        kept.append(line)
    return "\n".join(kept)


def main() -> None:
    level = read_level(LEVEL_PATH)
    if level == "off":
        # persona disabled: skip reading the persona file and inject nothing
        return
    persona = read_persona(PERSONA_PATH)
    context = f"{slice_to_level(persona, level)}\nCurrent level: **{level}**.\n"
    output = {
        "systemMessage": f"ROXY PERSONA ACTIVE - level: {level}",
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        },
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
