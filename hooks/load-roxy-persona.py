#!/usr/bin/env python3
"""загрузка персоны Roxy в контекст на старте сессии и после компакта

активный уровень персоны берётся из ~/.claude/.roxy-active (пишет команда
/roxy), при отсутствии файла используется full, при уровне off хук молча
ничего не вбрасывает

при отсутствии, пустоте или ошибке чтения файла персоны пишет заметное
сообщение в stderr и завершается ненулевым кодом, чтобы Claude Code показал
сбой хука, а не молчал
"""
import json
import os
import sys

PERSONA_PATH: str = os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"], "skills", "roxy", "persona.md")
LEVEL_PATH: str = os.path.expanduser("~/.claude/.roxy-active")
DEFAULT_LEVEL: str = "full"
VALID_LEVELS: frozenset[str] = frozenset({"off", "lite", "full", "ultra"})


def read_persona(path: str) -> str:
    """прочитать файл персоны или упасть с понятной ошибкой в stderr"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[roxy-persona] файл не найден: {path}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"[roxy-persona] не удалось прочитать {path}: {e}", file=sys.stderr)
        sys.exit(2)

    if not content.strip():
        print(f"[roxy-persona] файл пустой: {path}", file=sys.stderr)
        sys.exit(2)

    return content


def read_level(path: str) -> str:
    """прочитать активный уровень персоны, при отсутствии файла вернуть full"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            level = f.read().strip().lower()
    except FileNotFoundError:
        return DEFAULT_LEVEL
    except OSError as e:
        print(f"[roxy-persona] не удалось прочитать {path}: {e}", file=sys.stderr)
        sys.exit(2)

    if level not in VALID_LEVELS:
        print(
            f"[roxy-persona] недопустимый уровень {level!r} в {path}, "
            f"ожидается один из {sorted(VALID_LEVELS)}",
            file=sys.stderr,
        )
        sys.exit(2)

    return level


def slice_to_level(persona: str, level: str) -> str:
    """оставить из секций Intensity и Example только строки активного уровня"""
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
        # персона выключена: файл персоны не читаем и в контекст ничего не кладём
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
