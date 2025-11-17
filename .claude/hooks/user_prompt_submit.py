#!/usr/bin/env python3
"""
CCB UserPromptSubmit Hook

Injects build goal and phase context on EVERY user prompt.
This ensures Claude always has the current build context.
"""

import json
import sys
from pathlib import Path


def get_serena_dir() -> Path:
    """Get .serena/ccb directory."""
    # Try SERENA_PROJECT_ROOT first, then CLAUDE_PROJECT_DIR
    serena_root = Path(os.getenv("SERENA_PROJECT_ROOT") or os.getenv("CLAUDE_PROJECT_DIR") or Path.cwd())
    return serena_root / ".serena" / "ccb"


def get_build_goal() -> str:
    """Get current build goal from Serena MCP."""
    serena_dir = get_serena_dir()
    goal_file = serena_dir / "build_goal.txt"

    if not goal_file.exists():
        return None

    try:
        return goal_file.read_text().strip()
    except Exception:
        return None


def get_current_phase() -> tuple:
    """Get current phase and progress."""
    serena_dir = get_serena_dir()
    phase_file = serena_dir / "current_phase.txt"
    progress_file = serena_dir / "phase_progress.json"

    if not phase_file.exists():
        return None, None

    try:
        phase = int(phase_file.read_text().strip())

        if progress_file.exists():
            progress_data = json.loads(progress_file.read_text())
            progress = progress_data.get("phases", {}).get(str(phase), {}).get("progress", 0)
        else:
            progress = 0

        return phase, progress
    except Exception:
        return None, None


def main():
    """Inject build context into user prompt."""
    try:
        # Read hook input (JSON with user's prompt)
        hook_input = json.load(sys.stdin)

        # Get build context from Serena MCP
        build_goal = get_build_goal()
        phase, progress = get_current_phase()

        # If no build context, pass through silently
        if not build_goal:
            return

        # Inject context before prompt processing
        context_injection = []

        if build_goal:
            context_injection.append(f"🎯 **Build Goal**: {build_goal}")

        if phase:
            context_injection.append(f"📍 **Current Phase**: {phase} ({progress}% complete)")

        if context_injection:
            print("\n".join(context_injection))
            print("")  # Blank line separator

    except Exception as e:
        # Silent failure - don't break user's prompt
        print(f"⚠️  CCB context injection warning: {e}", file=sys.stderr)


if __name__ == "__main__":
    import os
    main()
