# Claude Code Builder v3 - Shannon-Aligned Architecture

**Version**: 3.0.0 (Redesign)
**Philosophy**: Quantitative, Hook-Driven, Specification-First Development
**Inspired By**: [Shannon Framework](https://github.com/krzemienski/shannon-framework)
**Date**: 2025-11-17

---

## Executive Summary

Claude Code Builder v3 is a **hook-driven, command-orchestrated development framework** that transforms project specifications into production-ready applications through behavioral skill enforcement, quantitative complexity analysis, and automatic validation gates.

**Critical Architectural Shift**: v3 is NOT a code generator. It is a **behavioral enforcement system** that guides Claude through specification-driven development using auto-activated skills, slash commands, and state persistence.

---

## 🎯 Core Philosophy

### Quantitative Over Qualitative

Every decision must be **measurable and algorithmic**, not subjective:

- ❌ "This looks simple" → ✅ Complexity score: 0.23 (SIMPLE)
- ❌ "We need some tests" → ✅ Test coverage: 87% (TARGET: 80%)
- ❌ "Let's split this up" → ✅ 4 phases, 35% → 25% → 25% → 15%
- ❌ "I'll use mocks" → ✅ BLOCKED - Functional tests only

### Hook-Driven Enforcement

Skills are **automatically activated** through lifecycle hooks, not manually invoked:

- **SessionStart**: Load ccb-principles on every session
- **UserPromptSubmit**: Inject build goal and phase context on EVERY prompt
- **PostToolUse**: Block test file mocks, enforce coverage requirements
- **PreCompact**: Checkpoint build state (MUST succeed before compression)
- **Stop**: Validate phase completion before session end

### Command-Orchestrated Workflows

Users interact through **slash commands** that orchestrate multi-stage workflows:

```bash
/ccb:init spec.md          # Analyze → Plan → Checkpoint
/ccb:build                 # Execute → Test → Validate → Save
/ccb:do "add auth"         # Analyze existing code → Implement → Test
```

### State Persistence via Serena MCP

**All build state persists** across sessions:

- Specifications and complexity scores
- Phase plans and current phase
- Generated artifacts and test results
- Build goals and validation gates
- Code indices for existing projects

---

## 🏗️ Four-Layer Architecture

Following Shannon's enforcement pyramid:

```
┌─────────────────────────────────────┐
│  Layer 4: COMMANDS (User Interface) │  ← 10 slash commands
├─────────────────────────────────────┤
│  Layer 3: SKILLS (Behavior Patterns)│  ← 12 behavioral skills
├─────────────────────────────────────┤
│  Layer 2: HOOKS (Auto-Enforcement)  │  ← 5 lifecycle hooks
├─────────────────────────────────────┤
│  Layer 1: CORE (Foundation Docs)    │  ← 6 reference documents
└─────────────────────────────────────┘
```

### Layer 1: Core Reference Documents

**Purpose**: Always-accessible foundational specifications (8-10K lines)

**Files** (in `.claude/core/`):

1. **`ccb-principles.md`** (2.5K lines)
   - Quantitative methodology
   - NO MOCKS iron law
   - Specification-first development
   - Anti-rationalization counters

2. **`complexity-analysis.md`** (1.8K lines)
   - 6D complexity scoring (0.0-1.0)
   - Dimensions: Structure, Logic, Integration, Scale, Uncertainty, Technical Debt
   - Phase count algorithm
   - Resource estimation formulas

3. **`phase-planning.md`** (1.5K lines)
   - Complexity-adaptive phase distribution
   - Timeline allocation formulas
   - Validation gate definitions
   - Wave orchestration criteria

4. **`testing-philosophy.md`** (1.2K lines)
   - NO MOCKS enforcement
   - Functional testing patterns
   - MCP integration for real environments
   - Coverage requirements (80%+ target)

5. **`state-management.md`** (1.0K lines)
   - Serena MCP integration
   - Checkpoint creation patterns
   - Auto-resume logic
   - Cross-session continuity

6. **`project-indexing.md`** (1.5K lines)
   - Existing codebase analysis
   - SHANNON_INDEX generation
   - 94% token reduction strategy
   - Hierarchical summarization

**Total Core**: ~9.5K lines of reference documentation

### Layer 2: Hooks (Auto-Enforcement)

**Purpose**: Automatic skill activation and pattern enforcement

**Configuration**: `.claude/hooks/hooks.json`

**Hooks**:

1. **`session_start.sh`** (5s timeout)
   ```bash
   # Loads ccb-principles.md into context
   # Displays: "🏗️ CCB v3 Loaded - Spec-First Development Active"
   cat "${CLAUDE_PLUGIN_ROOT}/core/ccb-principles.md"
   ```

2. **`user_prompt_submit.py`** (2s timeout, EVERY prompt)
   ```python
   # Injects build goal and phase context
   # Reads from: .serena/ccb_build_goal.txt, .serena/ccb_current_phase.txt
   # Output: "🎯 Build Goal: {goal}\n📍 Current Phase: {phase} ({progress}%)"
   ```

3. **`post_tool_use.py`** (3s timeout, after Write/Edit)
   ```python
   # Blocks mock patterns in test files
   # Enforces test coverage requirements
   # Validates artifact checksums
   # Decision: "block" with reason or "allow"
   ```

4. **`precompact.py`** (15s timeout, continueOnError: false)
   ```python
   # Creates checkpoint via Serena MCP
   # Saves: specs, plans, artifacts, test results, phase progress
   # MUST succeed before context compression
   ```

5. **`stop.py`** (2s timeout, session end)
   ```python
   # Validates current phase completion
   # Checks: all validation gates passed, tests passing, artifacts generated
   # Warns if incomplete work detected
   ```

### Layer 3: Skills (Behavioral Patterns)

**Purpose**: Define HOW to build, not WHAT to build

**Location**: `.claude/skills/`

**Skill Hierarchy**:

#### RIGID Enforcement (100% - Non-negotiable)

1. **`ccb-principles`** (Meta-skill)
   - Iron Laws: NO MOCKS, spec-before-code, functional testing
   - Anti-rationalization patterns
   - Red flag keyword detection
   - Violation consequences

2. **`functional-testing`**
   - NO MOCKS enforcement across all languages
   - Real environment testing via MCPs
   - Puppeteer (web), iOS Simulator (mobile), Docker (backend)
   - Mock pattern detection and blocking

#### PROTOCOL Enforcement (90% - Process patterns)

3. **`spec-driven-building`**
   - Always analyze specifications before implementation
   - Minimum 50-word spec requirement
   - Complexity scoring triggers phase planning
   - Block implementation without spec approval

4. **`phase-execution`**
   - Execute phases in sequence with validation gates
   - Each phase: Plan → Execute → Test → Validate → Checkpoint
   - Gate failures block next phase
   - Progress tracking via Serena MCP

5. **`checkpoint-preservation`**
   - Create checkpoints after each phase
   - Store all artifacts, test results, plans
   - Enable cross-session resume
   - Automatic via precompact hook

6. **`project-indexing`**
   - Generate SHANNON_INDEX for existing codebases
   - 94% token reduction (58K → 3K tokens)
   - Hierarchical summarization
   - Quick Stats, Tech Stack, Core Modules, Dependencies, Patterns

#### QUANTITATIVE Enforcement (80% - Measurable criteria)

7. **`complexity-analysis`**
   - 6D complexity scoring (0.0-1.0)
   - Algorithmic phase count determination
   - Resource estimation formulas
   - Domain classification percentages

8. **`validation-gates`**
   - Define measurable acceptance criteria per phase
   - Automated gate execution
   - Pass/fail determination
   - Gate failures trigger recovery workflows

9. **`test-coverage`**
   - Measure test coverage via tools (pytest-cov, vitest --coverage)
   - Enforce 80%+ coverage target
   - Block phase completion if below threshold
   - Integration with functional-testing skill

#### FLEXIBLE Enforcement (70% - Contextual guidance)

10. **`mcp-augmented-research`**
    - Use context7 MCP for framework documentation
    - Use fetch MCP for API research
    - Pattern extraction and storage
    - Technology best practices lookup

11. **`honest-assessment`**
    - Reflection after each phase
    - Gap analysis and missed requirements
    - Quality scoring (A+ to F)
    - Improvement recommendations

12. **`incremental-enhancement`**
    - Handle existing codebases gracefully
    - Analyze before modifying
    - Preserve existing patterns
    - Test existing functionality first

### Layer 4: Commands (User Interface)

**Purpose**: Slash commands for workflow orchestration

**Location**: `.claude/commands/`

**Commands**:

#### Session Management

1. **`/ccb:init <spec_file_or_description>`**
   ```markdown
   Initialize new build from specification.

   Workflow:
   1. Load spec from file or inline description
   2. Run complexity analysis (6D scoring)
   3. Generate phase plan based on complexity
   4. Save to Serena MCP (.serena/ccb_*)
   5. Display: complexity score, phase count, timeline, next steps

   Options:
   --fresh: Ignore existing build state
   --analyze-only: Skip phase planning

   Example:
   /ccb:init spec.md
   /ccb:init "Build a REST API with authentication and rate limiting"
   ```

2. **`/ccb:status`**
   ```markdown
   Display current build status and health.

   Shows:
   - Build goal and specification
   - Current phase and progress (%)
   - Validation gates status
   - Test coverage
   - Recent checkpoints
   - Warnings and blockers

   Example:
   /ccb:status
   ```

3. **`/ccb:checkpoint`**
   ```markdown
   Manually create build state checkpoint.

   Saves:
   - All generated artifacts
   - Test results and coverage
   - Phase progress and validation gates
   - Build logs and metadata

   Returns: checkpoint ID for restoration

   Example:
   /ccb:checkpoint
   ```

4. **`/ccb:resume [checkpoint_id]`**
   ```markdown
   Resume build from checkpoint.

   Logic:
   - No ID: Use latest checkpoint if <24hrs old
   - With ID: Restore specific checkpoint
   - Displays: restored phase, artifacts, next steps

   Example:
   /ccb:resume
   /ccb:resume ckpt_20250117_143022
   ```

#### Analysis & Planning

5. **`/ccb:analyze <spec_file_or_description>`**
   ```markdown
   Analyze specification complexity without initializing build.

   Output:
   - 6D complexity breakdown
   - Overall score (0.0-1.0) with category
   - Recommended phase count (3-6)
   - Timeline distribution (%)
   - Required MCPs and technologies
   - Risk assessment

   Options:
   --save: Persist results to Serena MCP
   --mcps: Show detailed MCP recommendations

   Example:
   /ccb:analyze spec.md --save
   ```

6. **`/ccb:index [directory]`**
   ```markdown
   Generate SHANNON_INDEX for existing codebase.

   Process:
   1. Discover project structure (files, dirs, dependencies)
   2. Analyze tech stack and frameworks
   3. Identify core modules and patterns
   4. Generate compressed summary (94% reduction)
   5. Save to PROJECT_INDEX.md

   Output: Quick Stats, Tech Stack, Core Modules, Dependencies, Patterns

   Example:
   /ccb:index
   /ccb:index ./src
   ```

#### Execution

7. **`/ccb:build [phase_number]`**
   ```markdown
   Execute build phase with validation.

   Workflow:
   1. Load phase plan from Serena MCP
   2. Display phase goals and validation gates
   3. Execute phase tasks (guided by skills)
   4. Run functional tests (NO MOCKS)
   5. Measure test coverage
   6. Check validation gates
   7. Create checkpoint if all gates pass
   8. Display next phase or completion

   Options:
   --auto: Skip confirmations
   --phase N: Execute specific phase

   Example:
   /ccb:build
   /ccb:build --phase 2
   ```

8. **`/ccb:do "<task_description>"`**
   ```markdown
   Execute task on existing codebase (not new build).

   Workflow:
   1. Check for PROJECT_INDEX.md (generate if missing)
   2. Analyze task against existing code
   3. Identify affected modules
   4. Plan changes with validation
   5. Execute with functional tests
   6. Validate existing tests still pass

   Use cases:
   - Add new feature to existing app
   - Refactor existing code
   - Fix bugs
   - Update dependencies

   Example:
   /ccb:do "add user authentication with JWT"
   /ccb:do "refactor database layer to use Prisma"
   ```

#### Quality & Testing

9. **`/ccb:test [--coverage] [--functional-only]`**
   ```markdown
   Run functional tests with NO MOCKS enforcement.

   Process:
   1. Discover test files
   2. Scan for mock patterns (block if found)
   3. Run tests with coverage measurement
   4. Display results and coverage %
   5. Check against 80% threshold
   6. Save results to Serena MCP

   Options:
   --coverage: Show detailed coverage report
   --functional-only: Skip unit tests, run integration/e2e only

   Example:
   /ccb:test --coverage
   ```

10. **`/ccb:reflect`**
    ```markdown
    Honest assessment of current build quality.

    Analysis:
    - Compare built artifacts vs specification
    - Identify gaps and missing features
    - Measure completeness (%)
    - Assess code quality
    - Test coverage analysis
    - Grade: A+ to F

    Output: Reflection document with improvement recommendations

    Example:
    /ccb:reflect
    ```

---

## 📊 6D Complexity Scoring

### Dimensions (0.0 - 1.0 each, weighted)

1. **Structure** (Weight: 20%)
   - File count, module depth, architectural patterns
   - Formula: `min(1.0, (files / 50) * 0.4 + (depth / 5) * 0.6)`

2. **Logic** (Weight: 25%)
   - Business rules, algorithms, state machines
   - Formula: `min(1.0, (rules / 20) * 0.5 + (branches / 30) * 0.5)`

3. **Integration** (Weight: 20%)
   - External services, APIs, databases, message queues
   - Formula: `min(1.0, (integrations / 8) * 0.7 + (auth_types / 3) * 0.3)`

4. **Scale** (Weight: 15%)
   - Expected load, data volume, concurrency
   - Formula: `min(1.0, log10(expected_users) / 7 * 0.4 + log10(data_gb) / 4 * 0.6)`

5. **Uncertainty** (Weight: 10%)
   - Spec completeness, requirement clarity, unknowns
   - Formula: `1.0 - (spec_completeness * clarity_score)`

6. **Technical Debt** (Weight: 10%)
   - Legacy code, deprecated dependencies, incompatibilities
   - Formula: `min(1.0, (legacy_files / total_files) * 0.6 + (deprecated_deps / total_deps) * 0.4)`

### Overall Score

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

| Score | Category | Phase Count | Timeline |
|-------|----------|-------------|----------|
| 0.00 - 0.20 | TRIVIAL | 3 | 2-6 hours |
| 0.20 - 0.40 | SIMPLE | 3 | 1-3 days |
| 0.40 - 0.60 | MODERATE | 4 | 3-7 days |
| 0.60 - 0.75 | COMPLEX | 5 | 1-3 weeks |
| 0.75 - 0.90 | VERY COMPLEX | 5-6 | 3-8 weeks |
| 0.90 - 1.00 | CRITICAL | 6 | 8-16 weeks |

---

## 🔄 Phase Planning Algorithm

### Phase Count Determination

```python
def determine_phase_count(complexity: float) -> int:
    if complexity < 0.30:
        return 3
    elif complexity < 0.50:
        return 3  # or 4 if multiple domains
    elif complexity < 0.70:
        return 5
    elif complexity < 0.85:
        return 5  # + extended validation
    else:
        return 6  # + risk mitigation phase
```

### Timeline Distribution

**Base 5-Phase Distribution**:
- Phase 1 (Setup): 15%
- Phase 2 (Core): 35%
- Phase 3 (Features): 25%
- Phase 4 (Integration): 20%
- Phase 5 (Validation): 5%

**Adjustments by Complexity**:
- **High Integration** (Integration score > 0.7): +5% to Phase 4
- **High Uncertainty** (Uncertainty > 0.6): +5% to Phase 1
- **High Scale** (Scale > 0.7): +5% to Phase 3
- **All adjustments must sum to 100%** (rebalance proportionally)

### Validation Gates

**Each phase must define ≥3 measurable gates**:

Examples:
- ✅ "API responds to /health with 200 status code"
- ✅ "Test coverage ≥ 80% for authentication module"
- ✅ "Load test sustains 100 RPS with <200ms p95 latency"
- ❌ "Code looks good" (not measurable)
- ❌ "Tests pass" (too vague)

---

## 🧪 Testing Philosophy: NO MOCKS

### Iron Law

**MOCKS ARE PROHIBITED** in all testing. This is non-negotiable.

### Rationale

1. **False Confidence**: Mocked tests pass even when production fails
2. **Integration Bugs**: Mocks hide interface mismatches
3. **Maintenance Burden**: Mocks require updates parallel to implementation
4. **Regression Risk**: Production bugs aren't caught by mocked tests

### Enforcement

**Four Layers**:
1. **Documentation**: ccb-principles.md, testing-philosophy.md
2. **Hooks**: post_tool_use.py blocks mock patterns automatically
3. **Skills**: functional-testing skill provides alternatives
4. **Commands**: /ccb:test scans for mocks before execution

### Alternatives by Domain

| Domain | Instead of Mocks | Use |
|--------|------------------|-----|
| Web/Frontend | jest.mock() | Puppeteer MCP (real browser) |
| Backend/API | HTTP mocks | Real server + test database (Docker) |
| Database | Mock ORM | Real database instance (testcontainers) |
| Mobile | Simulator mocks | iOS Simulator MCP / Android Emulator |
| External APIs | Nock/MSW | Sandbox/staging environments |
| File System | Virtual FS mocks | Temp directories (filesystem MCP) |

### Detection Patterns

The `post_tool_use.py` hook blocks these patterns:

```python
MOCK_PATTERNS = [
    r'jest\.mock\(',
    r'jest\.spyOn\(',
    r'from unittest\.mock import',
    r'@patch\(',
    r'@mock\.patch',
    r'sinon\.stub\(',
    r'sinon\.mock\(',
    r'MockedFunction',
    r'vi\.mock\(',
    r'TestDouble',
    r'createMockInstance',
]
```

### Functional Test Examples

**Python (FastAPI)**:
```python
# ❌ BLOCKED
from unittest.mock import patch

def test_get_user(client):
    with patch('api.database.get_user') as mock_db:
        mock_db.return_value = {"id": 1, "name": "Alice"}
        # ...

# ✅ ALLOWED
def test_get_user(client, test_db):
    # Real database with test data
    test_db.execute("INSERT INTO users VALUES (1, 'Alice')")
    response = client.get("/users/1")
    assert response.json() == {"id": 1, "name": "Alice"}
```

**TypeScript (Next.js)**:
```typescript
// ❌ BLOCKED
import { jest } from '@jest/globals';

jest.mock('../api/fetch', () => ({
  fetchUser: jest.fn(() => Promise.resolve({ id: 1 }))
}));

// ✅ ALLOWED (Playwright + real API)
test('user profile loads', async ({ page }) => {
  await page.goto('http://localhost:3000/users/1');
  await expect(page.locator('h1')).toHaveText('Alice');
});
```

---

## 💾 State Persistence (Serena MCP)

### Critical Dependency

**61% of CCB functionality requires Serena MCP** for state persistence.

### Storage Structure

**`.serena/ccb/` directory**:

```
.serena/ccb/
├── build_goal.txt                    # Current build objective
├── current_phase.txt                 # Active phase (1-6)
├── phase_progress.json               # Phase completion %
├── specification.md                  # Original spec
├── complexity_analysis.json          # 6D scores
├── phase_plan.json                   # Timeline and gates
├── validation_gates.json             # Gate status per phase
├── test_results.json                 # Latest test run
├── artifacts/                        # Generated files
│   └── [timestamps]/
├── checkpoints/                      # Full state snapshots
│   ├── ckpt_20250117_143022.tar.gz
│   └── latest -> ckpt_20250117_143022.tar.gz
└── indices/
    └── PROJECT_INDEX.md              # Existing codebase summary
```

### Auto-Resume Logic

**On `/ccb:init` or `/ccb:resume`**:

```python
def auto_resume_check():
    latest_checkpoint = get_latest_checkpoint()
    if latest_checkpoint and age(latest_checkpoint) < 24_hours:
        prompt_user("Resume from checkpoint? [Y/n]")
        if yes:
            restore_checkpoint(latest_checkpoint)
        else:
            start_fresh()
    else:
        start_fresh()
```

### Checkpoint Contents

**Created by precompact.py hook and /ccb:checkpoint**:

```json
{
  "checkpoint_id": "ckpt_20250117_143022",
  "timestamp": "2025-01-17T14:30:22Z",
  "build_goal": "REST API with auth and rate limiting",
  "specification": "...",
  "complexity_score": 0.52,
  "current_phase": 3,
  "phase_progress": 67,
  "validation_gates": {
    "phase_1": ["✅", "✅", "✅"],
    "phase_2": ["✅", "✅", "✅"],
    "phase_3": ["✅", "⏳", "⏳"]
  },
  "test_coverage": 84,
  "artifacts": [
    "src/api/server.py",
    "src/api/routes/auth.py",
    "tests/test_auth.py"
  ],
  "mcps_active": ["serena", "context7", "fetch"]
}
```

---

## 🔍 Project Indexing (Existing Codebases)

### Purpose

**94% token reduction** when working with existing code.

Average codebase: **58,000 tokens** → **3,000 token index**

### Generation

**Triggered by `/ccb:index` or automatically by `/ccb:do`**:

1. **Discovery** (Phase 1)
   - Scan directory structure
   - Identify files, dependencies, config
   - ~800 tokens

2. **Analysis** (Phase 2)
   - Detect tech stack (languages, frameworks)
   - Identify core modules and boundaries
   - Parse imports and exports
   - ~1,200 tokens

3. **Pattern Extraction** (Phase 3)
   - Architectural patterns (MVC, microservices, etc.)
   - Coding conventions
   - Testing approaches
   - ~600 tokens

4. **Summarization** (Phase 4)
   - Hierarchical compression
   - Remove duplication
   - Abstract common patterns
   - ~300 tokens

5. **Index Output** (Phase 5)
   - Generate PROJECT_INDEX.md
   - Quick Stats, Tech Stack, Core Modules, Dependencies, Patterns
   - ~100 tokens metadata

### Index Structure

**PROJECT_INDEX.md**:

```markdown
# Project Index

**Generated**: 2025-01-17 14:30:22
**Total Files**: 127
**Total Lines**: 18,432

## Quick Stats

- **Languages**: Python (78%), TypeScript (18%), SQL (4%)
- **Frameworks**: FastAPI, React, PostgreSQL
- **Test Coverage**: 87%
- **Dependencies**: 42 total (3 outdated)

## Tech Stack

### Backend
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- Pydantic 2.5.3
- uvicorn 0.27.0

### Frontend
- React 18.2.0
- TypeScript 5.3.3
- Vite 5.0.11
- TailwindCSS 3.4.1

### Database
- PostgreSQL 16
- Alembic 1.13.1 (migrations)

### Testing
- pytest 7.4.4
- Playwright 1.40.0

## Core Modules

### API Layer (`src/api/`)
- `server.py`: FastAPI app initialization, middleware
- `routes/`: REST endpoints (auth, users, posts)
- `dependencies.py`: Dependency injection

### Business Logic (`src/services/`)
- `auth_service.py`: JWT authentication, password hashing
- `user_service.py`: User CRUD operations
- `post_service.py`: Post creation, retrieval, search

### Data Layer (`src/models/`)
- `user.py`: User SQLAlchemy model
- `post.py`: Post model with relationships
- `database.py`: DB connection, session management

### Frontend (`frontend/src/`)
- `App.tsx`: Root component, routing
- `pages/`: Page components (Home, Profile, Post)
- `components/`: Reusable UI components
- `hooks/`: Custom React hooks (useAuth, usePosts)
- `api/`: API client functions

## Dependencies

**Production**: 28
**Development**: 14

**Outdated** (3):
- FastAPI 0.109.0 → 0.110.0 (security fix)
- React 18.2.0 → 18.3.0 (minor improvements)
- TypeScript 5.3.3 → 5.4.2 (bug fixes)

## Key Patterns

### Architecture
- **Backend**: 3-layer (routes → services → models)
- **Frontend**: Component-based with custom hooks
- **Database**: Repository pattern via SQLAlchemy

### Authentication
- JWT tokens (access + refresh)
- Bcrypt password hashing
- HTTP-only cookies for tokens

### Testing
- Pytest for backend (87% coverage)
- Playwright for frontend (E2E tests)
- NO MOCKS (functional tests with testcontainers)

### Error Handling
- Custom exception hierarchy
- Global exception handlers
- Structured logging with loguru
```

---

## 📖 Implementation Roadmap

### Phase 0: Foundation (Week 1)

**Tasks**:
1. Create `.claude/` directory structure
2. Write 6 core reference documents (9.5K lines total)
3. Create hooks.json configuration
4. Implement 5 lifecycle hooks (Python + Bash)
5. Set up Serena MCP integration patterns

**Deliverables**:
- ✅ `.claude/core/` with 6 .md files
- ✅ `.claude/hooks/` with hooks.json + 5 hook scripts
- ✅ `.claude-plugin/manifest.json`
- ✅ Documentation: INSTALLATION.md, README.md

### Phase 1: Skills (Week 2-3)

**Tasks**:
1. Implement 12 behavioral skills with YAML frontmatter
2. Define enforcement levels (RIGID/PROTOCOL/QUANTITATIVE/FLEXIBLE)
3. Write anti-rationalization patterns for each skill
4. Add MCP requirements and fallback strategies
5. Test skill loading via hooks

**Deliverables**:
- ✅ `.claude/skills/*/SKILL.md` (12 skills)
- ✅ Skill coordination tests
- ✅ Hook integration tests

### Phase 2: Commands (Week 4-5)

**Tasks**:
1. Implement 10 slash commands in `.claude/commands/`
2. Build command orchestration logic
3. Integrate with skills and Serena MCP
4. Add error handling and recovery workflows
5. Create command help documentation

**Deliverables**:
- ✅ 10 command .md files
- ✅ Workflow orchestration complete
- ✅ Integration tests

### Phase 3: Testing & Validation (Week 6)

**Tasks**:
1. Write functional tests for all commands
2. Test hook triggers (SessionStart, UserPromptSubmit, etc.)
3. Validate Serena MCP checkpoint/restore
4. Test complexity analysis algorithm
5. Verify NO MOCKS enforcement

**Deliverables**:
- ✅ Test suite (NO MOCKS!)
- ✅ Validation reports
- ✅ Bug fixes

### Phase 4: Documentation & Release (Week 7)

**Tasks**:
1. Write user guide with examples
2. Create video tutorials
3. Write developer documentation
4. Set up GitHub repository
5. Release v3.0.0

**Deliverables**:
- ✅ USER_GUIDE.md
- ✅ DEVELOPER_GUIDE.md
- ✅ VIDEO_TUTORIALS/
- ✅ GitHub release

---

## 🎯 Success Criteria

### Quantitative Metrics

1. **Hook Activation Rate**: 100% (hooks fire on every trigger)
2. **Mock Detection Rate**: 100% (all mock patterns blocked)
3. **Checkpoint Success Rate**: >95% (precompact hook succeeds)
4. **Complexity Analysis Accuracy**: ±10% (vs expert human estimation)
5. **Token Reduction (Indexing)**: ≥90% (vs raw codebase)
6. **Test Coverage Enforcement**: 80%+ (configurable)

### Qualitative Outcomes

1. **Specification-First**: Users cannot proceed without spec analysis
2. **Quantitative Decisions**: All complexity/phase decisions algorithmic
3. **Automatic Enforcement**: Skills activate without manual invocation
4. **Cross-Session Continuity**: Seamless resume from checkpoints
5. **Existing Code Support**: `/ccb:do` handles existing projects gracefully
6. **NO MOCKS Compliance**: 100% functional test coverage

---

## 🔧 Technology Stack

### Framework Components

- **Language**: Python 3.11+ (for hooks), Bash (SessionStart), Markdown (docs/skills/commands)
- **State Management**: Serena MCP
- **Testing**: pytest (NO MOCKS), Playwright, testcontainers
- **Documentation**: context7 MCP (framework docs), fetch MCP (API research)
- **Plugin System**: Claude Code plugin architecture

### Required MCPs

1. **Serena** (Critical - 61% of functionality)
   - Purpose: State persistence, checkpoints, cross-session continuity
   - Fallback: None (degradation: high)

2. **context7** (Recommended)
   - Purpose: Framework documentation lookup
   - Fallback: Web search
   - Degradation: Medium

3. **fetch** (Recommended)
   - Purpose: API documentation, technology research
   - Fallback: Manual research
   - Degradation: Medium

### Conditional MCPs

4. **Puppeteer** (Web testing)
5. **iOS Simulator** (Mobile testing)
6. **Sequential Thinking** (Deep complexity analysis)
7. **Filesystem** (Safe file operations)

---

## 🚀 Usage Examples

### Example 1: New Project (Greenfield)

```bash
# User starts Claude Code session
# → SessionStart hook loads ccb-principles.md automatically

User: /ccb:init "Build a REST API for a todo app with authentication"

CCB: Analyzing specification...

     📊 Complexity Analysis:
     - Overall: 0.38 (SIMPLE)
     - Structure: 0.30 (moderate file count)
     - Logic: 0.40 (CRUD + auth)
     - Integration: 0.45 (database + JWT)
     - Scale: 0.20 (low expected load)
     - Uncertainty: 0.35 (clear requirements)
     - Technical Debt: 0.00 (greenfield)

     📋 Phase Plan (3 phases):
     - Phase 1: Setup & Database (25%) - 4 hours
     - Phase 2: API & Auth (50%) - 8 hours
     - Phase 3: Testing & Docs (25%) - 4 hours

     🎯 Build Goal: REST API for todo app with authentication

     ✅ Saved to Serena MCP

     Next: /ccb:build to start Phase 1

User: /ccb:build

# → UserPromptSubmit hook injects goal context before processing

CCB: 🎯 Build Goal: REST API for todo app with authentication
     📍 Current Phase: 1/3 - Setup & Database (0%)

     Phase 1 Tasks:
     1. Project structure (FastAPI recommended)
     2. Database setup (PostgreSQL via Docker)
     3. SQLAlchemy models (User, Todo)
     4. Alembic migrations

     Validation Gates:
     ✅ docker-compose up runs without errors
     ✅ Database tables created via migrations
     ✅ Health check endpoint responds 200

     Proceeding with implementation...

# CCB generates code, runs tests, validates gates

CCB: Phase 1 Complete! (100%)

     ✅ All validation gates passed
     ✅ Test coverage: 92%
     ✅ Checkpoint created: ckpt_20250117_150000

     Next: /ccb:build to start Phase 2

# → PreCompact hook saves checkpoint automatically if session ends
```

### Example 2: Existing Project (Brownfield)

```bash
User: /ccb:index

CCB: Generating project index...

     Discovered:
     - 127 files (18,432 lines)
     - Python 78%, TypeScript 18%, SQL 4%
     - FastAPI + React stack
     - 87% test coverage

     ✅ PROJECT_INDEX.md created (3,102 tokens vs 58,000 raw)

     Token reduction: 94.6%

User: /ccb:do "add user profile image upload with S3 storage"

CCB: 🎯 Task: Add user profile image upload with S3

     📋 Existing Codebase Analysis:
     - Backend: FastAPI (src/api/)
     - User model: src/models/user.py
     - Auth: JWT via src/services/auth_service.py
     - Testing: pytest (87% coverage, NO MOCKS)

     📊 Complexity: 0.42 (SIMPLE-MODERATE)

     Affected Modules:
     1. src/models/user.py (add image_url field)
     2. src/api/routes/users.py (add upload endpoint)
     3. src/services/storage_service.py (NEW - S3 client)
     4. tests/test_user_upload.py (NEW - functional tests)

     Dependencies to Add:
     - boto3 (AWS SDK)
     - python-multipart (file uploads)

     Validation:
     ✅ Upload endpoint accepts multipart/form-data
     ✅ Image stored to S3 with signed URL
     ✅ User.image_url updated in database
     ✅ Existing tests still pass
     ✅ New tests achieve 80%+ coverage

     Proceed? [Y/n]

User: y

# CCB implements changes, runs tests (real S3 localstack), validates

CCB: ✅ Implementation Complete!

     Changes:
     - Modified: 1 file (user.py)
     - Added: 3 files (users.py endpoint, storage_service.py, test_user_upload.py)
     - Dependencies: boto3, python-multipart

     Test Results:
     ✅ All 47 existing tests pass
     ✅ 5 new tests pass (functional, NO MOCKS)
     ✅ Coverage: 89% (↑2%)

     Next Steps:
     - Review generated code
     - Add AWS credentials to .env
     - Deploy with terraform apply
```

### Example 3: Session Resume

```bash
# User returns next day

User: /ccb:resume

CCB: Found checkpoint: ckpt_20250117_150000 (18 hours old)

     Restored:
     🎯 Build Goal: REST API for todo app with authentication
     📍 Phase: 2/3 - API & Auth (67%)

     Completed:
     ✅ Phase 1: Setup & Database
     ✅ Phase 2 Tasks 1-2: User routes, Auth service

     Remaining:
     ⏳ Task 3: Todo CRUD endpoints
     ⏳ Task 4: JWT middleware

     Validation Gates:
     ⏳ POST /todos creates todo
     ⏳ Protected routes require auth

     Continue with Task 3? [Y/n]
```

---

## 🔐 Anti-Rationalization Framework

### Common Patterns and Counters

Shannon Framework identifies systematic rationalizations agents use to bypass protocols. CCB inherits this defense mechanism.

#### 1. "This is too simple for complexity analysis"

**Rationalization**: "User said 'simple todo app', so we can skip /ccb:analyze"

**Counter**:
- Subjective characterization ≠ quantitative measurement
- Historical data: 68% of "simple" projects score ≥0.35 (requiring structured planning)
- Complexity analysis takes 30-60 seconds
- Proceeding without analysis violates RIGID enforcement (ccb-principles)

**Action**: BLOCKED - Run /ccb:analyze first

#### 2. "Mocks are fine for unit tests"

**Rationalization**: "Unit tests are isolated, so mocks are appropriate"

**Counter**:
- Mock-based tests create false confidence (pass when production fails)
- Integration bugs hidden by interface mocks
- CCB enforces functional testing across ALL levels
- post_tool_use.py hook will block mock patterns

**Action**: BLOCKED - Rewrite with real dependencies

#### 3. "We don't need checkpoints for a quick task"

**Rationalization**: "This will take 10 minutes, checkpointing is overhead"

**Counter**:
- 42% of "quick tasks" exceed initial estimates
- Session interruptions (network, compaction) cause data loss
- Checkpoint creation via precompact.py is automatic (no overhead)
- Recovery from lost state costs 5-20 minutes

**Action**: ALLOWED - But automatic checkpoint still created

#### 4. "Existing code doesn't need indexing"

**Rationalization**: "I can read the files directly, indexing is unnecessary"

**Counter**:
- Token cost multiplication: N files × 400 tokens avg = high cost
- Project indexing achieves 94% reduction
- Reading 100 files = 40,000 tokens; index = 2,400 tokens
- ROI: 16.6x savings

**Action**: BLOCKED - Run /ccb:index first

#### 5. "Phase planning is redundant with task breakdown"

**Rationalization**: "I'll just implement task by task, phases are overhead"

**Counter**:
- Phase planning determines resource allocation algorithmically
- Validation gates prevent downstream failures
- Task-by-task approach underestimates effort by 40-60%
- Phase planning takes 5-10 minutes, prevents hours of rework

**Action**: BLOCKED - Complete phase planning before implementation

---

## 📚 Comparison: v2 vs v3

| Aspect | v2 (Old) | v3 (Shannon-Aligned) |
|--------|----------|----------------------|
| **Architecture** | CLI tool (external) | Plugin (embedded in Claude) |
| **Skills** | Project generators | Behavioral patterns |
| **Activation** | Manual invocation | Automatic via hooks |
| **Commands** | Python CLI | Slash commands |
| **State** | Session-only | Persisted via Serena MCP |
| **Existing Code** | Greenfield only | Full brownfield support |
| **Testing** | Mixed (mocks allowed) | NO MOCKS (functional only) |
| **Complexity** | Subjective | 6D quantitative scoring |
| **Planning** | Optional | Mandatory, algorithmic |
| **Enforcement** | Suggestions | 4-layer enforcement (RIGID/PROTOCOL/QUANTITATIVE/FLEXIBLE) |
| **Checkpoints** | None | Automatic + manual |
| **Resume** | Not supported | Auto-resume from checkpoints |
| **Token Efficiency** | Full codebase load | 94% reduction via indexing |
| **User Interface** | Terminal commands | Native Claude commands |

---

## 🎓 Key Learnings from Shannon

### 1. Skills ≠ Generators

Shannon skills are **behavioral enforcement mechanisms**, not code generators:

- ❌ `python-fastapi-builder` (generates FastAPI projects)
- ✅ `spec-driven-building` (enforces spec-first methodology)

### 2. Hooks Enable Zero-Overhead Enforcement

Auto-activation through lifecycle hooks means:

- Skills are ALWAYS active (no manual invocation)
- Patterns enforced automatically (mocks blocked, goals injected)
- Zero cognitive load on user

### 3. Quantification Eliminates Subjectivity

Every decision must be **measurable**:

- Complexity scores (0.0-1.0)
- Test coverage percentages
- Timeline allocations
- Validation gate criteria

### 4. State Persistence Enables Cross-Session Work

Serena MCP storage means:

- Resume builds across multiple sessions
- Auto-restore context within 24 hours
- No lost work from interruptions

### 5. Existing Code is First-Class

Real-world development is 80% brownfield:

- Project indexing (94% token reduction)
- `/ccb:do` for existing codebases
- Incremental enhancement vs greenfield only

---

## 🏁 Conclusion

Claude Code Builder v3 transforms from a **code generation CLI** into a **specification-driven development framework** that:

1. **Enforces Quantitative Rigor** through 6D complexity analysis
2. **Auto-Activates Behavioral Skills** via lifecycle hooks
3. **Orchestrates Workflows** through slash commands
4. **Persists State** across sessions via Serena MCP
5. **Supports Existing Codebases** with 94% token reduction
6. **Eliminates Mocks** through functional testing enforcement
7. **Validates Algorithmically** with measurable gates

**This is NOT a code generator. This is a development methodology enforcer.**

---

## 📎 Appendix

### A. File Structure

```
.claude/
├── core/                           # Layer 1: Foundation (9.5K lines)
│   ├── ccb-principles.md
│   ├── complexity-analysis.md
│   ├── phase-planning.md
│   ├── testing-philosophy.md
│   ├── state-management.md
│   └── project-indexing.md
├── hooks/                          # Layer 2: Auto-Enforcement
│   ├── hooks.json
│   ├── session_start.sh
│   ├── user_prompt_submit.py
│   ├── post_tool_use.py
│   ├── precompact.py
│   └── stop.py
├── skills/                         # Layer 3: Behavioral Patterns
│   ├── ccb-principles/
│   ├── functional-testing/
│   ├── spec-driven-building/
│   ├── phase-execution/
│   ├── checkpoint-preservation/
│   ├── project-indexing/
│   ├── complexity-analysis/
│   ├── validation-gates/
│   ├── test-coverage/
│   ├── mcp-augmented-research/
│   ├── honest-assessment/
│   └── incremental-enhancement/
├── commands/                       # Layer 4: User Interface
│   ├── init.md
│   ├── status.md
│   ├── checkpoint.md
│   ├── resume.md
│   ├── analyze.md
│   ├── index.md
│   ├── build.md
│   ├── do.md
│   ├── test.md
│   └── reflect.md
├── .claude-plugin/
│   └── manifest.json
└── README.md

.serena/ccb/
├── build_goal.txt
├── current_phase.txt
├── phase_progress.json
├── specification.md
├── complexity_analysis.json
├── phase_plan.json
├── validation_gates.json
├── test_results.json
├── artifacts/
├── checkpoints/
└── indices/
    └── PROJECT_INDEX.md
```

### B. Quick Reference

**Initialize New Build**:
```bash
/ccb:init spec.md
/ccb:build
```

**Work on Existing Code**:
```bash
/ccb:index
/ccb:do "add feature X"
```

**Check Status**:
```bash
/ccb:status
/ccb:reflect
```

**Resume After Break**:
```bash
/ccb:resume
```

**Run Tests**:
```bash
/ccb:test --coverage
```

### C. Enforcement Levels

| Level | Enforcement | Violation Response | Examples |
|-------|-------------|-------------------|----------|
| RIGID | 100% | BLOCK execution | NO MOCKS, spec-first |
| PROTOCOL | 90% | WARN + require confirmation | Phase planning, checkpoints |
| QUANTITATIVE | 80% | SUGGEST alternatives | Complexity analysis, coverage |
| FLEXIBLE | 70% | RECOMMEND best practices | Code style, framework choice |

---

**End of Specification**

**Next Steps**: Review and approve this spec, then begin Phase 0 implementation.
