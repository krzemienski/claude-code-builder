#!/usr/bin/env python3
"""
CCB Stop Hook

Validates phase completion before session end.
Warns if incomplete work detected.
"""

import json
import sys
from pathlib import Path


def get_serena_dir() -> Path:
    """Get .serena/ccb directory."""
    import os
    serena_root = Path(os.getenv("SERENA_PROJECT_ROOT") or os.getenv("CLAUDE_PROJECT_DIR") or Path.cwd())
    return serena_root / ".serena" / "ccb"


def check_phase_completion() -> dict:
    """Check if current phase is complete."""
    serena_dir = get_serena_dir()

    if not serena_dir.exists():
        return {"has_build": False}

    # Get current phase
    phase_file = serena_dir / "current_phase.txt"
    if not phase_file.exists():
        return {"has_build": False}

    current_phase = int(phase_file.read_text().strip())

    # Get validation gates
    gates_file = serena_dir / "validation_gates.json"
    if not gates_file.exists():
        return {
            "has_build": True,
            "current_phase": current_phase,
            "gates_defined": False,
        }

    gates_data = json.loads(gates_file.read_text())
    phase_gates = gates_data.get("phases", {}).get(str(current_phase), {})

    if not phase_gates:
        return {
            "has_build": True,
            "current_phase": current_phase,
            "gates_defined": False,
        }

    # Check gate status
    gates = phase_gates.get("gates", [])
    all_passed = phase_gates.get("all_passed", False)

    pending_gates = [g for g in gates if g["status"] != "passed"]
    failed_gates = [g for g in gates if g["status"] == "failed"]

    return {
        "has_build": True,
        "current_phase": current_phase,
        "gates_defined": True,
        "total_gates": len(gates),
        "passed_gates": len([g for g in gates if g["status"] == "passed"]),
        "pending_gates": len(pending_gates),
        "failed_gates": len(failed_gates),
        "all_passed": all_passed,
        "incomplete_gates": [g["description"] for g in pending_gates],
    }


def main():
    """Check phase completion and warn if needed."""
    try:
        status = check_phase_completion()

        # No build in progress
        if not status.get("has_build"):
            print("ℹ️  No active build", file=sys.stderr)
            return

        # No gates defined (unusual but allowed)
        if not status.get("gates_defined"):
            print(f"⚠️  Phase {status['current_phase']} has no validation gates defined", file=sys.stderr)
            return

        # All gates passed - good!
        if status.get("all_passed"):
            print(f"✅ Phase {status['current_phase']} complete - all gates passed", file=sys.stderr)
            return

        # Some gates not passed - warn user
        pending = status.get("pending_gates", 0)
        failed = status.get("failed_gates", 0)

        if failed > 0:
            print(f"❌ Phase {status['current_phase']} INCOMPLETE - {failed} gates FAILED", file=sys.stderr)
            print("   Failed gates:", file=sys.stderr)
            for gate in status.get("incomplete_gates", []):
                print(f"   - {gate}", file=sys.stderr)
        elif pending > 0:
            print(f"⏳ Phase {status['current_phase']} INCOMPLETE - {pending} gates pending", file=sys.stderr)
            print("   Pending gates:", file=sys.stderr)
            for gate in status.get("incomplete_gates", []):
                print(f"   - {gate}", file=sys.stderr)

        print("", file=sys.stderr)
        print("💡 Tip: Use /ccb:checkpoint to save current state before ending session", file=sys.stderr)
        print("💡 Tip: Use /ccb:resume to continue next session", file=sys.stderr)

    except Exception as e:
        # Silent failure - don't block session end
        print(f"⚠️  CCB stop hook warning: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
