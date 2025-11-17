---
name: checkpoint-preservation
skill-type: PROTOCOL
enforcement: 90
mcp-requirements:
  required:
    - name: serena
      purpose: Checkpoint storage
---

# Checkpoint Preservation: Cross-Session Continuity

**Enforcement**: PROTOCOL (90%)

## Behavior

Automatic checkpoint creation for state persistence:

1. **Automatic**: `precompact.py` hook creates checkpoint before compression (continueOnError: false)
2. **Manual**: `/ccb:checkpoint` command
3. **Storage**: `.serena/ccb/checkpoints/ckpt_YYYYMMDD_HHMMSS.tar.gz`
4. **Auto-Resume**: Within 24 hours via `/ccb:resume`

## Checkpoint Contents

- All `.serena/ccb/` state files
- Generated artifacts (src/, tests/)
- Metadata (phase, progress, gates, coverage)

## References

- `.claude/core/state-management.md`
- `.claude/hooks/precompact.py`
