# /ccb:resume

Resume build from checkpoint.

**Usage**: `/ccb:resume [checkpoint_id]`

**Logic**:
- No ID: Use latest if <24hrs old
- With ID: Restore specific checkpoint

**Skills**: @skill checkpoint-preservation

**Displays**: Restored phase, artifacts, next steps
