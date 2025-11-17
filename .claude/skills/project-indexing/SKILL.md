---
name: project-indexing
skill-type: PROTOCOL
enforcement: 90
mcp-requirements:
  required:
    - name: serena
      purpose: Store PROJECT_INDEX
---

# Project Indexing: 94% Token Reduction

**Enforcement**: PROTOCOL (90%)

## Behavior

Generate PROJECT_INDEX.md for existing codebases (58K → 3K tokens):

1. Discover files and structure (800 tokens)
2. Analyze tech stack (1,200 tokens)
3. Identify architecture (600 tokens)
4. Extract patterns (300 tokens)
5. Generate index (100 tokens)

**Total**: ~3,000 tokens (94.6% reduction)

## When to Index

- **Mandatory**: Before `/ccb:do` (existing codebase operations)
- **Recommended**: Project analysis, onboarding, multi-agent workflows

## Output

PROJECT_INDEX.md with:
- Quick Stats (languages, frameworks, coverage)
- Tech Stack (versions)
- Core Modules (descriptions)
- Dependencies (outdated flagged)
- Key Patterns (architecture, auth, testing)

## ROI

- Generation: 3,000 tokens (one-time)
- Subsequent queries: 50 tokens (index) vs 5,000 tokens (files)
- Savings: 16.6x after 6 operations

## References

- `.claude/core/project-indexing.md`
- `.claude/commands/index.md`
