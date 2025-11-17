---
name: phase-execution
skill-type: PROTOCOL
enforcement: 90
mcp-requirements:
  required:
    - name: serena
      purpose: Phase progress tracking
---

# Phase Execution: Sequential with Validation Gates

**Enforcement**: PROTOCOL (90%)

## Behavior

Execute phases sequentially with validation gates:

1. Load phase plan from `.serena/ccb/phase_plan.json`
2. Display phase objectives and gates
3. Execute phase tasks
4. Run validation gates (≥3 required)
5. If all gates pass: mark complete, checkpoint, advance
6. If any gate fails: mark incomplete, BLOCK next phase

## Gate Requirements

- ≥3 measurable gates per phase
- Valid: "API returns 200", "Coverage ≥80%"
- Invalid: "Code looks good", "Tests pass" (vague)

## Workflow

```
Phase N → Execute → Validate Gates → All Pass? → Checkpoint → Phase N+1
                                   → Any Fail? → BLOCKED, Fix Issues
```

## References

- `.claude/core/phase-planning.md`
- `.claude/commands/build.md`
