---
name: spec-driven-building
skill-type: PROTOCOL
enforcement: 90
mcp-requirements:
  required:
    - name: serena
      purpose: Store specification and analysis
---

# Spec-Driven Building: Analyze Before Implement

**Enforcement**: PROTOCOL (90%)

## Core Behavior

**NO implementation without specification analysis.**

1. User provides specification (≥50 words)
2. Run `/ccb:analyze` for 6D complexity scoring (0.0-1.0)
3. Generate phase plan based on complexity
4. Save to `.serena/ccb/`
5. ONLY THEN proceed to implementation

## Blocking Conditions

- Specification <50 words: BLOCKED
- No complexity analysis: BLOCKED
- No phase plan: BLOCKED
- `/ccb:build` before `/ccb:init`: BLOCKED

## Workflow

```
User Spec → /ccb:init → Complexity Analysis → Phase Planning → /ccb:build
```

## Anti-Rationalization

**"User said 'simple', skip analysis"**
→ 68% of "simple" projects score ≥0.35
→ BLOCKED - Run analysis

## References

- `.claude/core/ccb-principles.md` (Law 1)
- `.claude/skills/complexity-analysis/SKILL.md`
