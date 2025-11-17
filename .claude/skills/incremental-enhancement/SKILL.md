---
name: incremental-enhancement
skill-type: FLEXIBLE
enforcement: 70
---

# Incremental Enhancement: Brownfield Support

**Enforcement**: FLEXIBLE (70%)

## Purpose

Handle existing codebases gracefully:

1. Generate PROJECT_INDEX (94% token reduction)
2. Analyze before modifying
3. Preserve existing patterns
4. Test existing functionality first

## Workflow

```
/ccb:index → PROJECT_INDEX.md → /ccb:do "add feature" → Test existing + new
```

## Anti-Rationalization

**"Can skip indexing, I'll read files"**
→ 16.6x ROI after 6 operations
→ BLOCKED - Run `/ccb:index`

## References

- `.claude/core/project-indexing.md`
- `.claude/commands/do.md`
