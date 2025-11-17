# State Management: Serena MCP Integration

**Framework**: Claude Code Builder v3
**Purpose**: Cross-session build state persistence
**Critical Dependency**: Serena MCP (61% of CCB functionality requires it)

---

## Overview

**State persistence enables**:
- Resume builds after session interruptions
- Auto-restore context within 24 hours
- Checkpoint creation at phase boundaries
- Recovery from failures without data loss
- Cross-session continuity

**Without Serena MCP**: 61% of CCB functionality is degraded or unavailable.

---

## Storage Structure

### Directory: `.serena/ccb/`

```
.serena/ccb/
├── build_goal.txt              # Current build objective
├── current_phase.txt           # Active phase number (1-6)
├── phase_progress.json         # Phase completion percentage
├── specification.md            # Original specification text
├── complexity_analysis.json    # 6D scores and category
├── phase_plan.json             # Timeline and validation gates
├── validation_gates.json       # Gate status per phase
├── test_results.json           # Latest test run results
├── artifacts/                  # Generated files with timestamps
│   ├── 20250117_143022/
│   │   ├── src/
│   │   ├── tests/
│   │   └── manifest.json
│   └── 20250117_150000/
├── checkpoints/                # Full state snapshots
│   ├── ckpt_20250117_143022.tar.gz
│   ├── ckpt_20250117_150000.tar.gz
│   └── latest -> ckpt_20250117_150000.tar.gz
└── indices/
    └── PROJECT_INDEX.md        # Existing codebase summary
```

---

## File Formats

### `build_goal.txt`

Simple text file with project objective.

```
Build a REST API for a todo app with JWT authentication and rate limiting
```

### `current_phase.txt`

Single integer representing active phase.

```
3
```

### `phase_progress.json`

```json
{
  "current_phase": 3,
  "phases": {
    "1": {"status": "completed", "progress": 100, "completed_at": "2025-01-17T14:30:22Z"},
    "2": {"status": "completed", "progress": 100, "completed_at": "2025-01-17T15:45:10Z"},
    "3": {"status": "in_progress", "progress": 67, "started_at": "2025-01-17T16:00:00Z"}
  },
  "overall_progress": 67
}
```

### `specification.md`

Original specification provided by user.

```markdown
# Project Specification

Build a REST API for a todo application.

## Requirements
- User authentication with JWT
- CRUD operations for todos
- Rate limiting (100 req/min per user)
- PostgreSQL database

## Acceptance Criteria
- API responds within 200ms
- Test coverage ≥80%
- Deployed via Docker
```

### `complexity_analysis.json`

```json
{
  "timestamp": "2025-01-17T14:30:22Z",
  "overall_score": 0.385,
  "category": "SIMPLE",
  "dimensions": {
    "structure": {"score": 0.42, "details": "20 files, 3 levels deep"},
    "logic": {"score": 0.55, "details": "11 business rules, 22 conditional branches"},
    "integration": {"score": 0.45, "details": "PostgreSQL + JWT + rate limiting"},
    "scale": {"score": 0.25, "details": "1K expected users, 10GB data"},
    "uncertainty": {"score": 0.35, "details": "70% spec complete, some ambiguity"},
    "technical_debt": {"score": 0.00, "details": "Greenfield project"}
  },
  "phase_recommendation": {
    "count": 3,
    "rationale": "SIMPLE category with clear requirements"
  },
  "risk_level": "Low",
  "recommended_team_size": "1-2"
}
```

### `phase_plan.json`

Full phase plan with gates (see phase-planning.md for complete example).

### `validation_gates.json`

```json
{
  "phases": {
    "1": {
      "gates": [
        {"id": "p1g1", "description": "Project runs without errors", "status": "passed", "validated_at": "2025-01-17T14:30:22Z"},
        {"id": "p1g2", "description": "Database initialized", "status": "passed", "validated_at": "2025-01-17T14:30:22Z"},
        {"id": "p1g3", "description": "Health check responds 200", "status": "passed", "validated_at": "2025-01-17T14:30:22Z"}
      ],
      "all_passed": true
    },
    "2": {
      "gates": [
        {"id": "p2g1", "description": "All API endpoints functional", "status": "passed", "validated_at": "2025-01-17T15:45:10Z"},
        {"id": "p2g2", "description": "JWT authentication works", "status": "passed", "validated_at": "2025-01-17T15:45:10Z"},
        {"id": "p2g3", "description": "Integration tests pass", "status": "passed", "validated_at": "2025-01-17T15:45:10Z"}
      ],
      "all_passed": true
    },
    "3": {
      "gates": [
        {"id": "p3g1", "description": "Test coverage ≥80%", "status": "passed", "validated_at": "2025-01-17T16:30:00Z"},
        {"id": "p3g2", "description": "All functional tests pass", "status": "in_progress"},
        {"id": "p3g3", "description": "Documentation complete", "status": "pending"}
      ],
      "all_passed": false
    }
  }
}
```

### `test_results.json`

```json
{
  "timestamp": "2025-01-17T16:30:00Z",
  "framework": "pytest",
  "summary": {
    "total": 25,
    "passed": 23,
    "failed": 2,
    "skipped": 0
  },
  "coverage": {
    "percentage": 84,
    "lines_covered": 420,
    "lines_total": 500
  },
  "no_mocks_check": {
    "passed": true,
    "patterns_found": []
  },
  "failed_tests": [
    {
      "name": "test_rate_limiting",
      "file": "tests/test_api.py",
      "line": 45,
      "error": "AssertionError: Expected 429, got 200"
    },
    {
      "name": "test_todo_deletion",
      "file": "tests/test_todos.py",
      "line": 78,
      "error": "Foreign key constraint violation"
    }
  ],
  "duration_seconds": 12.4
}
```

---

## Checkpoint Format

### Checkpoint Naming

```
ckpt_YYYYMMDD_HHMMSS.tar.gz
```

**Example**: `ckpt_20250117_143022.tar.gz`

### Checkpoint Contents

```
checkpoint/
├── metadata.json              # Checkpoint metadata
├── build_state/               # All .serena/ccb/ files
├── artifacts/                 # Generated code at checkpoint time
└── environment.json           # Environment info (Python version, deps)
```

### `metadata.json`

```json
{
  "checkpoint_id": "ckpt_20250117_143022",
  "created_at": "2025-01-17T14:30:22Z",
  "build_goal": "REST API for todo app with JWT authentication",
  "complexity_score": 0.385,
  "current_phase": 2,
  "phase_progress": 45,
  "validation_gates_status": {
    "phase_1": ["✅", "✅", "✅"],
    "phase_2": ["✅", "⏳", "⏳"]
  },
  "test_coverage": 78,
  "generated_files": [
    "src/api/server.py",
    "src/api/routes/auth.py",
    "src/api/routes/todos.py",
    "tests/test_auth.py"
  ],
  "mcps_active": ["serena", "context7", "fetch"],
  "environment": {
    "python_version": "3.11.5",
    "dependencies": ["fastapi==0.109.0", "sqlalchemy==2.0.25"]
  }
}
```

---

## Auto-Resume Logic

### On `/ccb:init` or `/ccb:resume`

```python
def auto_resume_check() -> Optional[str]:
    """
    Check if auto-resume should occur.

    Returns:
        Checkpoint ID if resuming, None if starting fresh
    """
    serena_dir = Path(".serena/ccb")
    if not serena_dir.exists():
        return None  # No previous build

    checkpoint_dir = serena_dir / "checkpoints"
    if not checkpoint_dir.exists():
        return None  # No checkpoints

    latest_link = checkpoint_dir / "latest"
    if not latest_link.exists():
        return None  # No latest checkpoint

    latest_checkpoint = latest_link.resolve()
    checkpoint_age = time.time() - latest_checkpoint.stat().st_mtime

    # Auto-resume if checkpoint <24 hours old
    if checkpoint_age < 86400:  # 24 hours in seconds
        # Prompt user for confirmation
        response = input(f"Resume from checkpoint {latest_checkpoint.name}? [Y/n]: ")
        if response.lower() in ['y', 'yes', '']:
            return latest_checkpoint.stem
        else:
            return None  # User declined
    else:
        # Checkpoint too old, start fresh
        return None
```

### Resume Process

```python
def restore_checkpoint(checkpoint_id: str) -> None:
    """
    Restore build state from checkpoint.

    Args:
        checkpoint_id: Checkpoint identifier (e.g., 'ckpt_20250117_143022')
    """
    checkpoint_path = Path(f".serena/ccb/checkpoints/{checkpoint_id}.tar.gz")

    # Extract checkpoint
    with tarfile.open(checkpoint_path, "r:gz") as tar:
        tar.extractall(".serena/ccb/restored")

    # Restore build state files
    shutil.copytree(
        ".serena/ccb/restored/build_state",
        ".serena/ccb",
        dirs_exist_ok=True
    )

    # Restore artifacts
    shutil.copytree(
        ".serena/ccb/restored/artifacts",
        ".",  # Restore to project root
        dirs_exist_ok=True
    )

    # Load metadata
    metadata = json.load(open(".serena/ccb/restored/metadata.json"))

    # Display restored state
    print(f"✅ Restored checkpoint: {checkpoint_id}")
    print(f"🎯 Build Goal: {metadata['build_goal']}")
    print(f"📍 Phase: {metadata['current_phase']} ({metadata['phase_progress']}%)")
    print(f"📊 Test Coverage: {metadata['test_coverage']}%")
    print(f"🗓️  Created: {metadata['created_at']}")
```

---

## Checkpoint Creation

### Automatic (via `precompact.py` hook)

**Trigger**: Before context auto-compaction

**Hook Configuration** (`hooks/hooks.json`):
```json
{
  "PreCompact": {
    "command": ["python", "${CLAUDE_PLUGIN_ROOT}/hooks/precompact.py"],
    "timeout": 15000,
    "continueOnError": false
  }
}
```

**Critical**: `continueOnError: false` means compaction is BLOCKED if checkpoint fails.

**Hook Logic** (`precompact.py`):
```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def create_checkpoint():
    """Create checkpoint before compaction."""
    serena_dir = Path(".serena/ccb")
    if not serena_dir.exists():
        # No build state, nothing to checkpoint
        return

    checkpoint_id = datetime.now().strftime("ckpt_%Y%m%d_%H%M%S")

    # Create checkpoint
    checkpoint_path = serena_dir / "checkpoints" / f"{checkpoint_id}.tar.gz"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(checkpoint_path, "w:gz") as tar:
        # Add build state
        tar.add(serena_dir, arcname="build_state")

        # Add current artifacts
        tar.add("src", arcname="artifacts/src")
        tar.add("tests", arcname="artifacts/tests")

        # Add metadata
        metadata = generate_checkpoint_metadata(checkpoint_id)
        metadata_file = serena_dir / "checkpoint_metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        tar.add(metadata_file, arcname="metadata.json")

    # Update latest symlink
    latest_link = serena_dir / "checkpoints" / "latest"
    if latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(checkpoint_path.name)

    print(f"✅ Checkpoint created: {checkpoint_id}")

if __name__ == "__main__":
    try:
        create_checkpoint()
    except Exception as e:
        print(f"❌ Checkpoint failed: {e}", file=sys.stderr)
        sys.exit(1)  # BLOCK compaction on failure
```

### Manual (via `/ccb:checkpoint` command)

**Usage**:
```bash
/ccb:checkpoint
```

**Output**:
```
✅ Checkpoint created: ckpt_20250117_163000

Saved:
- Build goal and phase progress
- All generated artifacts
- Test results (25 tests, 84% coverage)
- Validation gates status

Checkpoint ID: ckpt_20250117_163000
Location: .serena/ccb/checkpoints/ckpt_20250117_163000.tar.gz
Size: 2.4 MB
```

---

## State Queries

### Current Phase

```python
def get_current_phase() -> int:
    """Get active phase number."""
    phase_file = Path(".serena/ccb/current_phase.txt")
    if not phase_file.exists():
        return 0  # No build started

    return int(phase_file.read_text().strip())
```

### Phase Progress

```python
def get_phase_progress() -> Dict[str, Any]:
    """Get progress for all phases."""
    progress_file = Path(".serena/ccb/phase_progress.json")
    if not progress_file.exists():
        return {}

    return json.loads(progress_file.read_text())
```

### Build Goal

```python
def get_build_goal() -> str:
    """Get current build objective."""
    goal_file = Path(".serena/ccb/build_goal.txt")
    if not goal_file.exists():
        return ""

    return goal_file.read_text().strip()
```

### Validation Gates Status

```python
def get_validation_gates() -> Dict[int, List[Dict]]:
    """Get validation gate status for all phases."""
    gates_file = Path(".serena/ccb/validation_gates.json")
    if not gates_file.exists():
        return {}

    return json.loads(gates_file.read_text())["phases"]
```

---

## Integration with Commands

### `/ccb:init`

1. Parse specification
2. Calculate complexity
3. Generate phase plan
4. **Save to Serena MCP**:
   - `.serena/ccb/build_goal.txt`
   - `.serena/ccb/specification.md`
   - `.serena/ccb/complexity_analysis.json`
   - `.serena/ccb/phase_plan.json`
   - `.serena/ccb/current_phase.txt` (set to 0 or 1)

### `/ccb:build`

1. Load phase plan from `.serena/ccb/phase_plan.json`
2. Read current phase from `.serena/ccb/current_phase.txt`
3. Execute phase tasks
4. Run validation gates
5. **Update Serena MCP**:
   - `.serena/ccb/phase_progress.json`
   - `.serena/ccb/validation_gates.json`
   - `.serena/ccb/test_results.json`
6. If phase complete: increment `.serena/ccb/current_phase.txt`
7. **Create checkpoint** (via automatic precompact hook)

### `/ccb:status`

1. Read all state files from `.serena/ccb/`
2. Display:
   - Build goal
   - Current phase and progress
   - Validation gates status
   - Test coverage
   - Recent checkpoints

### `/ccb:checkpoint`

1. Call checkpoint creation logic (same as precompact hook)
2. Return checkpoint ID to user

### `/ccb:resume`

1. Check for checkpoints in `.serena/ccb/checkpoints/`
2. If checkpoint ID provided: restore that checkpoint
3. If no ID: use auto-resume logic (latest <24hrs)
4. Extract checkpoint and restore state
5. Display restored state to user

---

## Serena MCP Configuration

### `.serena/config.json`

```json
{
  "project_name": "claude-code-builder",
  "storage_backend": "filesystem",
  "base_path": ".serena",
  "namespaces": {
    "ccb": {
      "description": "Claude Code Builder build state",
      "retention_days": 30
    }
  }
}
```

### MCP Server Setup

**Installation**:
```bash
npm install -g @modelcontextprotocol/server-memory
```

**Configuration** (`.claude-plugin/manifest.json`):
```json
{
  "mcps": {
    "serena": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "required": true,
      "description": "State persistence for cross-session continuity"
    }
  }
}
```

---

## Failure Scenarios and Recovery

### Scenario 1: Checkpoint Creation Fails

**Cause**: Disk full, permission error

**Detection**: precompact.py returns exit code 1

**Consequence**: Context compaction BLOCKED (continueOnError: false)

**Recovery**:
1. User notified: "Checkpoint failed, compaction blocked"
2. User resolves issue (free disk space, fix permissions)
3. Manual checkpoint: `/ccb:checkpoint`
4. Compaction proceeds

### Scenario 2: Serena MCP Unavailable

**Cause**: MCP server not running

**Detection**: File operations to `.serena/ccb/` fail

**Consequence**: 61% of CCB functionality degraded

**Degraded Operations**:
- No auto-resume
- No checkpoints
- No cross-session continuity
- Phase progress not persisted

**Still Available**:
- Session-only builds
- Commands work within single session
- Skills still enforce behavior

**Recovery**:
1. Start Serena MCP server
2. Create `.serena/ccb/` directory
3. Resume normal operation

### Scenario 3: Corrupted Checkpoint

**Cause**: Incomplete tar.gz, corrupted data

**Detection**: Extraction fails during resume

**Consequence**: Unable to restore from that checkpoint

**Recovery**:
1. Try previous checkpoint (if available)
2. Start fresh build if no valid checkpoints
3. Warn user about data loss

---

## Success Criteria

**State Persistence**:
- ✅ All build state persisted to `.serena/ccb/`
- ✅ Checkpoints created automatically before compaction
- ✅ Auto-resume works within 24 hours
- ✅ Manual checkpoints available via command

**Quantitative Targets**:
- Checkpoint creation success rate: >95%
- Checkpoint size: <10MB avg
- Resume success rate: >90%
- State query latency: <50ms

---

## References

- **Shannon Context Preservation**: [shannon-framework/skills/context-preservation](https://github.com/krzemienski/shannon-framework)
- **Serena MCP**: [@modelcontextprotocol/server-memory](https://github.com/modelcontextprotocol/servers)
- **CCB Principles**: `.claude/core/ccb-principles.md` (Law 4: State Persistence)

---

**End of State Management**

**Next**: Load `project-indexing.md` for existing codebase support.
