---
name: validation-gates
skill-type: QUANTITATIVE
enforcement: 80
---

# Validation Gates: Measurable Acceptance Criteria

**Enforcement**: QUANTITATIVE (80%)

## Requirements

Every phase MUST define ≥3 measurable gates.

**Valid**: "API returns 200", "Coverage ≥80%", "Latency <200ms"
**Invalid**: "Code looks good", "Tests pass" (vague)

## Enforcement

- Phase progression BLOCKED until all gates pass
- `/ccb:build` validates gates after execution
- `/ccb:status` shows gate status

## References

- `.claude/core/phase-planning.md`
