#!/usr/bin/env python3
"""
CCB PreCompact Hook

Creates checkpoint BEFORE context auto-compaction.
MUST succeed (continueOnError: false) - blocks compaction if fails.
"""

import json
import sys
import tarfile
from datetime import datetime
from pathlib import Path


def get_serena_dir() -> Path:
    """Get .serena/ccb directory."""
    import os
    serena_root = Path(os.getenv("SERENA_PROJECT_ROOT") or os.getenv("CLAUDE_PROJECT_DIR") or Path.cwd())
    return serena_root / ".serena" / "ccb"


def create_checkpoint() -> str:
    """Create checkpoint before compaction."""
    serena_dir = get_serena_dir()

    # If no build state, nothing to checkpoint
    if not serena_dir.exists():
        print("ℹ️  No build state to checkpoint", file=sys.stderr)
        return None

    # Generate checkpoint ID
    checkpoint_id = datetime.now().strftime("ckpt_%Y%m%d_%H%M%S")

    # Create checkpoints directory
    checkpoints_dir = serena_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    # Create checkpoint tar.gz
    checkpoint_path = checkpoints_dir / f"{checkpoint_id}.tar.gz"

    with tarfile.open(checkpoint_path, "w:gz") as tar:
        # Add all .serena/ccb/ files
        tar.add(serena_dir, arcname="build_state", filter=lambda t: t if 'checkpoints' not in t.name else None)

        # Add generated artifacts if they exist
        project_root = serena_dir.parent.parent
        for artifact_dir in ['src', 'tests']:
            artifact_path = project_root / artifact_dir
            if artifact_path.exists():
                tar.add(artifact_path, arcname=f"artifacts/{artifact_dir}")

        # Create and add metadata
        metadata = generate_metadata(checkpoint_id, serena_dir)
        metadata_file = serena_dir / "checkpoint_metadata_temp.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        tar.add(metadata_file, arcname="metadata.json")
        metadata_file.unlink()  # Remove temp file

    # Update latest symlink
    latest_link = checkpoints_dir / "latest"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(checkpoint_path.name)

    return checkpoint_id


def generate_metadata(checkpoint_id: str, serena_dir: Path) -> dict:
    """Generate checkpoint metadata."""
    metadata = {
        "checkpoint_id": checkpoint_id,
        "created_at": datetime.now().isoformat(),
    }

    # Load build goal
    goal_file = serena_dir / "build_goal.txt"
    if goal_file.exists():
        metadata["build_goal"] = goal_file.read_text().strip()

    # Load complexity analysis
    complexity_file = serena_dir / "complexity_analysis.json"
    if complexity_file.exists():
        complexity = json.loads(complexity_file.read_text())
        metadata["complexity_score"] = complexity.get("overall_score")

    # Load current phase
    phase_file = serena_dir / "current_phase.txt"
    if phase_file.exists():
        metadata["current_phase"] = int(phase_file.read_text().strip())

    # Load phase progress
    progress_file = serena_dir / "phase_progress.json"
    if progress_file.exists():
        progress = json.loads(progress_file.read_text())
        metadata["phase_progress"] = progress.get("overall_progress", 0)

    # Load validation gates
    gates_file = serena_dir / "validation_gates.json"
    if gates_file.exists():
        gates = json.loads(gates_file.read_text())
        metadata["validation_gates_status"] = {
            f"phase_{phase}": ["✅" if g["status"] == "passed" else "⏳" if g["status"] == "in_progress" else "⏳"
                               for g in phase_gates["gates"]]
            for phase, phase_gates in gates.get("phases", {}).items()
        }

    # Load test results
    test_file = serena_dir / "test_results.json"
    if test_file.exists():
        tests = json.loads(test_file.read_text())
        metadata["test_coverage"] = tests.get("coverage", {}).get("percentage", 0)

    return metadata


def main():
    """Create checkpoint and report status."""
    try:
        checkpoint_id = create_checkpoint()

        if checkpoint_id:
            print(f"✅ Checkpoint created: {checkpoint_id}", file=sys.stderr)
            print(json.dumps({"status": "success", "checkpoint_id": checkpoint_id}))
        else:
            print(json.dumps({"status": "skipped", "reason": "No build state"}))

    except Exception as e:
        # CRITICAL: Exit with error code to BLOCK compaction
        print(f"❌ Checkpoint failed: {e}", file=sys.stderr)
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)  # BLOCK compaction on failure


if __name__ == "__main__":
    main()
