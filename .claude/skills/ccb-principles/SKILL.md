---
name: ccb-principles
skill-type: RIGID
enforcement: 100
shannon-version: ">=3.0.0"
mcp-requirements:
  required:
    - name: serena
      purpose: State persistence
      fallback: none
      degradation: high
  recommended:
    - name: sequential-thinking
      purpose: Deep complexity analysis
---

# CCB Principles: Meta-Skill for Iron Law Enforcement

**Enforcement Level**: RIGID (100%) - Non-negotiable

**Purpose**: Automatically enforce Claude Code Builder's Iron Laws on EVERY session through behavioral modification.

## Core Reference

This skill is a meta-skill that references `.claude/core/ccb-principles.md` (loaded automatically via `session_start.sh` hook).

## The 5 Iron Laws

### 1. Specification-First Development

**NO implementation without specification analysis.**

- Minimum 50-word specification requirement
- Complexity scoring (0.0-1.0) determines phase count
- Phase planning MANDATORY before code generation
- `/ccb:build` BLOCKED until `/ccb:init` or `/ccb:analyze` completes

### 2. NO MOCKS - Functional Testing Only

**ALL tests must use REAL dependencies.**

- 13 mock patterns automatically BLOCKED by `post_tool_use.py` hook
- Alternatives: Puppeteer MCP, testcontainers, iOS Simulator MCP
- Real environments only: databases, browsers, APIs, filesystems

### 3. Quantitative Over Qualitative

**ALL decisions must be measurable and algorithmic.**

- Complexity: 0.0-1.0 (6D algorithm)
- Phase count: 3-6 (algorithmic determination)
- Timeline: Percentage-based formulas
- Test coverage: Numeric (80%+ target)

### 4. State Persistence (Serena MCP Required)

**All build state MUST persist across sessions.**

- `.serena/ccb/` storage for all build data
- Auto-resume within 24 hours
- Checkpoint before compression (precompact hook, MUST succeed)
- Cross-session continuity

### 5. Validation Gates (Measurable Criteria)

**Every phase MUST define ≥3 measurable validation gates.**

- Valid: "API returns 200 status", "Coverage ≥80%"
- Invalid: "Code looks good", "Tests pass" (too vague)
- Phase progression BLOCKED until all gates pass

## When This Skill Activates

**Automatically on every session** via `session_start.sh` hook.

No manual invocation required - principles are always active.

## Behavioral Enforcement

### Detection Triggers

When these phrases appear, STOP and enforce quantitative analysis:

- "straightforward", "simple", "quick", "just a..."
- "we'll mock that", "unit tests are enough"
- "let's just start", "we can plan as we go"
- "no need to save state", "checkpoints slow us down"

### Enforcement Actions

1. **Specification Skip Detected**: BLOCK, require `/ccb:analyze`
2. **Mock Usage Detected**: BLOCK via `post_tool_use.py` hook
3. **Subjective Complexity**: BLOCK, require 6D quantitative scoring
4. **Gate Skip Detected**: BLOCK, require ≥3 measurable gates

## Anti-Rationalization Framework

### Rationalization 1: "This is too simple for analysis"

**Counter**: 68% of "simple" projects score ≥0.35 (requiring planning). Analysis takes 30-60s.

**Action**: BLOCKED - Run `/ccb:analyze` first

### Rationalization 2: "Mocks are fine for unit tests"

**Counter**: Mock tests pass when production fails. 73% more bugs caught with real dependencies.

**Action**: BLOCKED - Use real dependencies via MCP

### Rationalization 3: "Phases are redundant"

**Counter**: Phase planning prevents 40-60% underestimation. Takes 5-10 minutes, prevents hours of rework.

**Action**: BLOCKED - Complete phase planning

### Rationalization 4: "Quick task, no checkpoints needed"

**Counter**: 42% of "quick tasks" exceed estimates. Checkpoints automatic via precompact hook.

**Action**: ALLOWED - But checkpoint still created automatically

## Success Criteria

- ✅ All implementations preceded by specification analysis
- ✅ All complexity assessments use 6D quantitative scoring
- ✅ All tests use real dependencies (NO MOCKS)
- ✅ All phases have ≥3 measurable validation gates
- ✅ All build state persists via Serena MCP

## References

- **Core Doc**: `.claude/core/ccb-principles.md`
- **Shannon Framework**: [github.com/krzemienski/shannon-framework](https://github.com/krzemienski/shannon-framework)
- **Related Skills**: All other CCB skills implement these principles
