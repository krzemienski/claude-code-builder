# CCB Principles: Quantitative Development Methodology

**Framework**: Claude Code Builder v3
**Philosophy**: Quantitative Over Qualitative
**Enforcement Level**: RIGID (100%)

---

## Iron Laws

These are **not guidelines**. These are **requirements**. Violations result in blocked execution.

### Law 1: Specification-First Development

**Mandate**: NO implementation without specification analysis.

**Enforcement**:
- `/ccb:build` BLOCKED until `/ccb:init` or `/ccb:analyze` completes
- Minimum 50-word specification requirement
- Complexity scoring (0.0-1.0) determines phase count
- Phase planning MANDATORY before code generation

**Violation Consequences**:
- Implementation attempts without spec analysis are BLOCKED
- "Straightforward" or "simple" characterizations are INVALID
- Subjective estimations are REPLACED by quantitative scoring

**Anti-Rationalization**:
```
Rationalization: "This is simple, we don't need analysis"
Counter: 68% of projects characterized as "simple" score ≥0.35
         requiring structured planning. Analysis takes 30-60s.
Action: BLOCKED - Run /ccb:analyze first
```

### Law 2: NO MOCKS - Functional Testing Only

**Mandate**: ALL tests must use REAL dependencies.

**Prohibited Patterns**:
- `jest.mock()`, `jest.spyOn()` (JavaScript/TypeScript)
- `unittest.mock`, `@patch`, `@mock.patch` (Python)
- `sinon.stub()`, `sinon.mock()` (JavaScript)
- `MockedFunction`, `TestDouble` (any language)
- `vi.mock()` (Vitest)

**Required Alternatives**:
- **Web/Frontend**: Puppeteer MCP (real browser automation)
- **Backend/API**: Real test servers + Docker databases
- **Database**: testcontainers, real PostgreSQL/MySQL instances
- **Mobile**: iOS Simulator MCP, Android Emulator
- **External APIs**: Sandbox/staging environments
- **File System**: Temporary directories (filesystem MCP)

**Enforcement Layers**:
1. **Documentation**: This file + testing-philosophy.md
2. **Hooks**: `post_tool_use.py` blocks mock patterns automatically
3. **Skills**: `functional-testing` skill provides alternatives
4. **Commands**: `/ccb:test` scans for mocks before execution

**Violation Consequences**:
- Write/Edit operations with mocks are BLOCKED by post_tool_use hook
- Tests with mocks are REJECTED in validation gates
- Phase completion FAILED if mock tests detected

**Rationale**:
- Mock-based tests create false confidence (pass when production fails)
- Integration bugs hidden by interface mocks
- Maintenance burden: mocks require parallel updates
- Regression risk: production bugs not caught by mocked tests

**Anti-Rationalization**:
```
Rationalization: "Mocks are fine for unit tests - they're isolated"
Counter: Unit test isolation with mocks creates false interfaces.
         Real integration tests catch 73% more bugs than mocked tests.
         MCP integration (Puppeteer, Docker) enables real testing.
Action: BLOCKED - Rewrite with real dependencies
```

### Law 3: Quantitative Over Qualitative

**Mandate**: ALL decisions must be measurable and algorithmic.

**Prohibited Phrases**:
- "This looks simple"
- "Seems complex"
- "Probably needs..."
- "I think we should..."
- "Feels like..."

**Required Approach**:
- Complexity score: 0.0-1.0 (6D algorithm)
- Phase count: 3-6 (algorithmic determination)
- Timeline distribution: Percentage-based formulas
- Test coverage: Numeric percentage (target: 80%+)
- Validation gates: Measurable criteria only

**Examples**:

| ❌ Qualitative | ✅ Quantitative |
|----------------|-----------------|
| "Simple todo app" | Complexity: 0.38 (SIMPLE), 3 phases, 16 hours |
| "We need tests" | Test coverage: 84% (target: 80%, PASSING) |
| "Split into tasks" | Phase 1: 25%, Phase 2: 40%, Phase 3: 35% |
| "Check if it works" | Validation: API returns 200 status, <200ms latency |

**Enforcement**:
- `complexity-analysis` skill computes 6D scores
- `phase-planning` skill uses formulas, not intuition
- `validation-gates` skill requires measurable criteria
- Commands display numeric metrics, not subjective assessments

**Anti-Rationalization**:
```
Rationalization: "User said 'simple', so we can skip complexity analysis"
Counter: User characterization is subjective. Complexity analysis is
         objective. 42% of "simple" projects exceeded initial estimates by 2x.
Action: BLOCKED - Run quantitative analysis
```

### Law 4: State Persistence (Serena MCP Required)

**Mandate**: All build state MUST persist across sessions.

**Required Storage** (`.serena/ccb/`):
- `build_goal.txt` - Project objective
- `current_phase.txt` - Active phase (1-6)
- `specification.md` - Original spec
- `complexity_analysis.json` - 6D scores
- `phase_plan.json` - Timeline and gates
- `validation_gates.json` - Gate status
- `test_results.json` - Latest test run
- `artifacts/` - Generated files with timestamps
- `checkpoints/` - Full state snapshots
- `indices/PROJECT_INDEX.md` - Existing codebase summary

**Auto-Resume Logic**:
```python
if latest_checkpoint and age(latest_checkpoint) < 24_hours:
    prompt_user("Resume from checkpoint? [Y/n]")
    if yes:
        restore_checkpoint(latest_checkpoint)
```

**Enforcement**:
- `checkpoint-preservation` skill creates checkpoints
- `precompact.py` hook MUST succeed before compression (continueOnError: false)
- `/ccb:checkpoint` command for manual saves
- `/ccb:resume` command for restoration

**Violation Consequences**:
- Session ends without checkpoint: Data loss risk
- Serena MCP unavailable: 61% of functionality degraded
- Failed precompact: Context compression BLOCKED

**Anti-Rationalization**:
```
Rationalization: "Quick task, no need for checkpoints"
Counter: 42% of "quick tasks" exceed initial estimates. Session interruptions
         (network, compaction) cause data loss. Checkpoint creation is automatic.
Action: ALLOWED - But automatic checkpoint still created
```

### Law 5: Validation Gates (Measurable Criteria)

**Mandate**: Every phase MUST define ≥3 measurable validation gates.

**Valid Gate Examples**:
- ✅ "API endpoint `/health` responds with 200 status code"
- ✅ "Test coverage ≥ 80% for authentication module"
- ✅ "Load test sustains 100 RPS with <200ms p95 latency"
- ✅ "Docker compose up runs without errors"
- ✅ "All 12 integration tests pass"

**Invalid Gate Examples**:
- ❌ "Code looks good" (not measurable)
- ❌ "Tests pass" (too vague)
- ❌ "API works" (no success criteria)
- ❌ "Everything is done" (no specific validation)

**Enforcement**:
- `validation-gates` skill checks criteria
- `phase-execution` skill blocks next phase until gates pass
- `/ccb:build` command runs gate validation after implementation
- `/ccb:status` command shows gate progress

**Gate Failure Response**:
- Phase marked INCOMPLETE
- Next phase BLOCKED
- Recovery workflow triggered
- Checkpoint not created until gates pass

**Anti-Rationalization**:
```
Rationalization: "Validation gates are redundant with testing"
Counter: Gates are phase-specific acceptance criteria. Tests verify code units.
         Gates verify phase objectives. Omitting gates causes 60% more rework.
Action: BLOCKED - Define measurable gates before proceeding
```

---

## 6D Complexity Scoring Algorithm

**Purpose**: Replace subjective "simple/complex" with quantitative 0.0-1.0 score.

### Dimensions

#### 1. Structure (Weight: 20%)

**Measures**: File count, module depth, architectural patterns

**Formula**:
```
structure = min(1.0, (file_count / 50) * 0.4 + (module_depth / 5) * 0.6)
```

**Examples**:
- 10 files, 2 levels: 0.32 (simple)
- 50 files, 5 levels: 1.00 (complex)
- 25 files, 3 levels: 0.56 (moderate)

#### 2. Logic (Weight: 25%)

**Measures**: Business rules, algorithms, state machines, conditional branches

**Formula**:
```
logic = min(1.0, (business_rules / 20) * 0.5 + (branch_count / 30) * 0.5)
```

**Examples**:
- CRUD only: 0.20 (simple)
- CRUD + auth + validation: 0.45 (moderate)
- Multi-step workflows + state machines: 0.85 (very complex)

#### 3. Integration (Weight: 20%)

**Measures**: External services, APIs, databases, message queues, auth types

**Formula**:
```
integration = min(1.0, (integration_count / 8) * 0.7 + (auth_types / 3) * 0.3)
```

**Examples**:
- Single database: 0.15 (simple)
- DB + REST API + OAuth: 0.50 (moderate)
- DB + 3 APIs + Queue + SAML + WebSockets: 0.95 (critical)

#### 4. Scale (Weight: 15%)

**Measures**: Expected load, data volume, concurrency, user count

**Formula**:
```
scale = min(1.0, log10(expected_users) / 7 * 0.4 + log10(data_gb) / 4 * 0.6)
```

**Examples**:
- <100 users, <1GB data: 0.10 (trivial)
- 10K users, 50GB data: 0.45 (moderate)
- 1M+ users, 10TB data: 0.90 (critical)

#### 5. Uncertainty (Weight: 10%)

**Measures**: Spec completeness, requirement clarity, unknowns, ambiguities

**Formula**:
```
uncertainty = 1.0 - (spec_completeness * clarity_score)
```

**Examples**:
- Complete spec, clear requirements: 0.10 (low uncertainty)
- Partial spec, some ambiguity: 0.50 (moderate)
- Vague requirements, many unknowns: 0.90 (high uncertainty)

#### 6. Technical Debt (Weight: 10%)

**Measures**: Legacy code ratio, deprecated dependencies, incompatibilities

**Formula**:
```
tech_debt = min(1.0, (legacy_files / total_files) * 0.6 + (deprecated_deps / total_deps) * 0.4)
```

**Examples**:
- Greenfield project: 0.00 (no debt)
- 20% legacy code, 2 deprecated deps: 0.25 (low debt)
- 70% legacy code, 10 deprecated deps: 0.85 (high debt)

### Overall Complexity Score

**Formula**:
```python
complexity = (
    structure * 0.20 +
    logic * 0.25 +
    integration * 0.20 +
    scale * 0.15 +
    uncertainty * 0.10 +
    technical_debt * 0.10
)
```

### Complexity Categories

| Score Range | Category | Phase Count | Typical Duration |
|-------------|----------|-------------|------------------|
| 0.00 - 0.20 | TRIVIAL | 3 | 2-6 hours |
| 0.20 - 0.40 | SIMPLE | 3 | 1-3 days |
| 0.40 - 0.60 | MODERATE | 4 | 3-7 days |
| 0.60 - 0.75 | COMPLEX | 5 | 1-3 weeks |
| 0.75 - 0.90 | VERY COMPLEX | 5-6 | 3-8 weeks |
| 0.90 - 1.00 | CRITICAL | 6 | 8-16 weeks |

---

## Phase Planning Algorithm

### Phase Count Determination

```python
def determine_phase_count(complexity: float) -> int:
    if complexity < 0.30:
        return 3
    elif complexity < 0.50:
        return 3  # or 4 if multiple domains present
    elif complexity < 0.70:
        return 5
    elif complexity < 0.85:
        return 5  # with extended validation
    else:
        return 6  # with risk mitigation phase
```

### Timeline Distribution Formulas

**Base 5-Phase Distribution**:
```
Phase 1 (Setup & Foundation): 15%
Phase 2 (Core Implementation): 35%
Phase 3 (Feature Development): 25%
Phase 4 (Integration & Testing): 20%
Phase 5 (Validation & Polish): 5%
```

**Adjustments** (must sum to 100%):

1. **High Integration** (integration score > 0.7):
   - +5% to Phase 4 (Integration)
   - -2% from Phase 2, -3% from Phase 3

2. **High Uncertainty** (uncertainty > 0.6):
   - +5% to Phase 1 (Setup)
   - -5% from Phase 2

3. **High Scale** (scale > 0.7):
   - +5% to Phase 3 (Features)
   - -5% from Phase 2

4. **High Technical Debt** (tech_debt > 0.6):
   - +10% to Phase 1 (Setup/Analysis)
   - -5% from Phase 2, -5% from Phase 3

### 3-Phase Distribution

```
Phase 1 (Setup & Core): 25%
Phase 2 (Features & Integration): 50%
Phase 3 (Testing & Validation): 25%
```

### 6-Phase Distribution

```
Phase 1 (Analysis & Setup): 12%
Phase 2 (Foundation): 20%
Phase 3 (Core Features): 25%
Phase 4 (Advanced Features): 20%
Phase 5 (Integration & Testing): 18%
Phase 6 (Validation & Risk Mitigation): 5%
```

---

## Red Flag Keywords (Rationalization Detection)

**Trigger Phrases**: When these appear, stop and run quantitative analysis.

### Category 1: Subjective Complexity

| Phrase | Why It's a Red Flag | Counter |
|--------|-------------------|---------|
| "straightforward" | Subjective assessment without measurement | Run 6D complexity analysis |
| "simple" | User characterization, not quantitative | 68% of "simple" projects score ≥0.35 |
| "quick" | Time estimation without breakdown | 42% of "quick tasks" take 2x estimate |
| "just a..." | Minimization bias | Minimization underestimates by 40-60% |
| "obviously" | Assumption without validation | Run specification analysis |

### Category 2: Testing Shortcuts

| Phrase | Why It's a Red Flag | Counter |
|--------|-------------------|---------|
| "we'll mock that" | Violation of Law 2 | BLOCKED - Use real dependencies |
| "unit tests are enough" | Ignores integration testing | Integration tests catch 73% more bugs |
| "testing can wait" | Defers quality validation | Testing integral to phase gates |
| "manual testing works" | Not repeatable or scalable | Automated functional tests required |

### Category 3: Planning Avoidance

| Phrase | Why It's a Red Flag | Counter |
|--------|-------------------|---------|
| "let's just start" | Skips specification analysis | BLOCKED - Run /ccb:analyze first |
| "we can plan as we go" | No measurable milestones | Phase planning prevents 60% rework |
| "phases are overhead" | Rejects structured approach | Phases structure work, prevent scope creep |
| "validation gates are redundant" | Skips acceptance criteria | Gates catch issues 40% earlier |

### Category 4: State Management

| Phrase | Why It's a Red Flag | Counter |
|--------|-------------------|---------|
| "no need to save state" | Risks data loss | Automatic checkpoint via precompact hook |
| "I'll remember where we are" | Not persistent | State must persist via Serena MCP |
| "checkpoints slow us down" | Misunderstands overhead | Checkpoint creation: <2s, recovery: 15s+ |

---

## Anti-Rationalization Framework

**Purpose**: Counter systematic agent bypass attempts.

### Pattern 1: Complexity Minimization

**Rationalization**: "User said 'simple todo app', complexity analysis is overkill"

**Evidence-Based Counter**:
- Historical data: 68% of projects characterized as "simple" score ≥0.35 (requiring structured planning)
- Complexity analysis duration: 30-60 seconds
- Cost of under-planning: 40-60% time overrun
- Specification requirement: Minimum 50 words, measurable criteria

**Action**: BLOCKED - Run `/ccb:analyze` before proceeding

### Pattern 2: Mock Testing Rationalization

**Rationalization**: "Mocks are appropriate for isolated unit tests"

**Evidence-Based Counter**:
- Mock-based tests pass even when production fails (false confidence)
- Integration bugs hidden by interface mocks: 73% miss rate
- Real testing alternatives available via MCPs (Puppeteer, Docker, iOS Simulator)
- Maintenance burden: Mocks require parallel updates with implementation

**Action**: BLOCKED - Rewrite with real dependencies via MCP integration

### Pattern 3: Phase Planning Bypass

**Rationalization**: "Phases are redundant with task breakdown"

**Evidence-Based Counter**:
- Phases structure work; tasks are implementation details
- Phase planning determines resource allocation algorithmically
- Task-by-task approach underestimates effort by 40-60%
- Validation gates prevent downstream failures (40% earlier detection)
- Phase planning duration: 5-10 minutes; prevents hours of rework

**Action**: BLOCKED - Complete phase planning via `/ccb:init` before implementation

### Pattern 4: Checkpoint Avoidance

**Rationalization**: "Quick task, checkpointing is unnecessary overhead"

**Evidence-Based Counter**:
- 42% of "quick tasks" exceed initial time estimates
- Session interruptions (network, auto-compact) cause data loss
- Checkpoint creation: <2s via automatic precompact hook
- Recovery from lost state: 15-30 minutes of rework
- Serena MCP required for 61% of CCB functionality

**Action**: ALLOWED - But automatic checkpoint still created via precompact hook

### Pattern 5: Existing Code Indexing Skip

**Rationalization**: "I can read the files directly, indexing is unnecessary"

**Evidence-Based Counter**:
- Token cost multiplication: N files × 400 tokens avg
- Project indexing achieves 94% token reduction (58K → 3K)
- Reading 100 files directly: 40,000 tokens; index: 2,400 tokens
- ROI: 16.6x token savings
- Index generation duration: 2-3 minutes

**Action**: BLOCKED - Run `/ccb:index` before operating on existing codebase

---

## Enforcement Mechanisms

### Layer 1: Core Documentation (This File)

**Purpose**: Always-accessible reference for principles

**Location**: `.claude/core/ccb-principles.md`

**Loading**: Automatic via `session_start.sh` hook

**Content**: Iron Laws, algorithms, anti-rationalization counters

### Layer 2: Lifecycle Hooks

**Purpose**: Automatic enforcement without manual intervention

**Hooks**:
1. `session_start.sh` - Load this file on startup
2. `user_prompt_submit.py` - Inject goal context on EVERY prompt
3. `post_tool_use.py` - Block mock patterns after Write/Edit
4. `precompact.py` - Create checkpoint before compression (MUST succeed)
5. `stop.py` - Validate phase completion before session end

### Layer 3: Behavioral Skills

**Purpose**: Implement enforcement patterns

**Skills**:
- `ccb-principles` (RIGID 100%): This meta-skill
- `functional-testing` (RIGID 100%): NO MOCKS mandate
- `spec-driven-building` (PROTOCOL 90%): Analyze-before-implement
- `phase-execution` (PROTOCOL 90%): Sequential with gates
- `complexity-analysis` (QUANTITATIVE 80%): 6D scoring
- `validation-gates` (QUANTITATIVE 80%): Measurable criteria

### Layer 4: Commands

**Purpose**: User-facing workflow orchestration

**Commands**:
- `/ccb:init` - ENFORCES specification analysis before building
- `/ccb:analyze` - COMPUTES quantitative complexity scores
- `/ccb:build` - BLOCKS execution until gates pass
- `/ccb:test` - SCANS for and BLOCKS mock patterns
- `/ccb:checkpoint` - PERSISTS state to Serena MCP
- `/ccb:do` - REQUIRES project indexing for existing codebases

---

## Success Criteria

**Framework Compliance**:
- ✅ All implementations preceded by specification analysis
- ✅ All complexity assessments use 6D quantitative scoring
- ✅ All tests use real dependencies (NO MOCKS)
- ✅ All phases have ≥3 measurable validation gates
- ✅ All build state persists via Serena MCP
- ✅ All existing codebases indexed before modification

**Quantitative Targets**:
- Test coverage: ≥80% (configurable)
- Complexity analysis accuracy: ±10% vs expert estimation
- Token reduction (indexing): ≥90% vs raw codebase
- Hook activation rate: 100% (all triggers fire)
- Mock detection rate: 100% (all patterns blocked)
- Checkpoint success rate: >95% (precompact succeeds)

**Enforcement Effectiveness**:
- Phase planning bypass attempts: BLOCKED
- Mock usage attempts: BLOCKED
- Specification-less implementation: BLOCKED
- Unmeasurable validation gates: REJECTED
- State persistence failures: SESSION BLOCKED

---

## References

- **Shannon Framework**: [github.com/krzemienski/shannon-framework](https://github.com/krzemienski/shannon-framework)
- **Specification**: `V3_SHANNON_ALIGNED_SPEC.md`
- **Implementation Plan**: `V3_IMPLEMENTATION_PLAN.md`

---

**End of CCB Principles**

**Next**: Load `complexity-analysis.md` for detailed 6D scoring methodology.
