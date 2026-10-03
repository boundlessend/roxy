"""check the real hook output with disposable state files for both hosts"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT: Path = Path(__file__).resolve().parents[1]
HOOK: Path = ROOT / "hooks" / "load-roxy-persona.py"
PERSONA: Path = ROOT / "skills" / "roxy" / "persona.md"
WRAPPER: str = (
    "import runpy, sys; "
    "namespace = runpy.run_path(sys.argv[1]); "
    "assert namespace['PLUGIN_ROOT'] == sys.argv[4]; "
    "assert namespace['STATE_ROOT'] == sys.argv[5]; "
    "namespace['main'](sys.argv[2], sys.argv[3])"
)


def run_hook(persona: Path, state: Path, host: str) -> subprocess.CompletedProcess[str]:
    environment: dict[str, str] = dict(os.environ)
    state_root: str
    if host == "codex":
        environment["PLUGIN_ROOT"] = str(ROOT)
        environment["CLAUDE_PLUGIN_ROOT"] = str(ROOT / "unused-claude-root")
        state_root = environment.get("CODEX_HOME", os.path.expanduser("~/.codex"))
    else:
        environment.pop("PLUGIN_ROOT", None)
        environment["CLAUDE_PLUGIN_ROOT"] = str(ROOT)
        state_root = os.path.expanduser("~/.claude")
    return subprocess.run(
        [sys.executable, "-c", WRAPPER, str(HOOK), str(persona), str(state), str(ROOT), state_root],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> None:
    checks: int = 0
    result: subprocess.CompletedProcess[str]
    with tempfile.TemporaryDirectory(prefix="roxy-hook-") as temporary:
        state: Path = Path(temporary) / ".roxy-active"
        missing_persona: Path = Path(temporary) / "missing-persona.md"
        for host in ("claude", "codex"):
            if state.exists():
                state.unlink()
            result = run_hook(PERSONA, state, host)
            assert result.returncode == 0, result.stderr
            assert "Current level: **full**." in result.stdout
            checks += 1
            for level in ("lite", "full", "ultra"):
                state.write_text(level, encoding="utf-8")
                result = run_hook(PERSONA, state, host)
                assert result.returncode == 0, result.stderr
                output: dict[str, object] = json.loads(result.stdout)
                specific: object = output["hookSpecificOutput"]
                assert isinstance(specific, dict)
                context: object = specific["additionalContext"]
                assert isinstance(context, str)
                assert specific["hookEventName"] == "SessionStart"
                assert f"Current level: **{level}**." in context
                assert f"- **{level}**:" in context
                for other in {"lite", "full", "ultra"} - {level}:
                    assert f"- **{other}**:" not in context
                    assert f"- {other}:" not in context
                checks += 1
            state.write_text("off", encoding="utf-8")
            result = run_hook(missing_persona, state, host)
            assert result.returncode == 0 and result.stdout == "", result.stderr
            checks += 1
            state.write_text("invalid", encoding="utf-8")
            result = run_hook(PERSONA, state, host)
            assert result.returncode == 2 and "invalid level" in result.stderr
            checks += 1
            state.write_text("full", encoding="utf-8")
            result = run_hook(missing_persona, state, host)
            assert result.returncode == 2 and "file not found" in result.stderr
            checks += 1
    print(f"OK: {checks} hook checks across Claude Code and Codex")


if __name__ == "__main__":
    main()
