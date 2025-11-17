# Phase Planning: Algorithmic Timeline Distribution

**Framework**: Claude Code Builder v3
**Purpose**: Complexity-adaptive phase planning with measurable validation gates
**Input**: Complexity score (0.0-1.0) from complexity-analysis.md
**Output**: Phase count + timeline percentages + validation gates

---

## Core Principle

**Phase planning is ALGORITHMIC, not intuitive.**

All timeline distributions are calculated using formulas based on:
- Complexity score (0.0-1.0)
- Dimension scores (Structure, Logic, Integration, Scale, Uncertainty, Technical Debt)
- Historical project data
- Domain-specific adjustments

**Subjective planning is PROHIBITED.**

---

## Phase Count Algorithm

```python
def determine_phase_count(complexity: float, domain_composition: dict) -> int:
    """
    Algorithmically determine phase count based on complexity.

    Args:
        complexity: Overall complexity score (0.0-1.0)
        domain_composition: Dict of domain percentages (e.g., {'backend': 70, 'frontend': 30})

    Returns:
        Phase count (3-6)
    """
    if complexity < 0.30:
        return 3

    elif complexity < 0.50:
        # Check if multiple domains
        domains_over_30 = sum(1 for pct in domain_composition.values() if pct >= 30)
        return 4 if domains_over_30 >= 2 else 3

    elif complexity < 0.70:
        return 5

    elif complexity < 0.85:
        return 5  # Consider 6 if high uncertainty

    else:
        return 6  # Critical complexity always gets 6 phases
```

---

## Timeline Distribution by Phase Count

### 3-Phase Distribution (TRIVIAL, SIMPLE)

**Base Percentages**:
```python
PHASE_3_BASE = {
    1: 25,  # Setup & Core
    2: 50,  # Features & Integration
    3: 25,  # Testing & Validation
}
```

**Phase 1: Setup & Core (25%)**
- Project structure creation
- Dependency installation
- Core data models
- Basic configuration

**Validation Gates** (≥3 required):
1. Project runs without errors
2. Database/storage initialized
3. Health check endpoint responds 200

**Phase 2: Features & Integration (50%)**
- Core business logic implementation
- API endpoint development
- External service integration
- Primary feature set

**Validation Gates** (≥3 required):
1. All core API endpoints functional
2. Integration tests pass
3. Feature acceptance criteria met

**Phase 3: Testing & Validation (25%)**
- Comprehensive testing
- Performance validation
- Documentation
- Final polish

**Validation Gates** (≥3 required):
1. Test coverage ≥80%
2. All functional tests pass (NO MOCKS)
3. Documentation complete

### 4-Phase Distribution (MODERATE)

**Base Percentages**:
```python
PHASE_4_BASE = {
    1: 20,  # Setup
    2: 35,  # Core Implementation
    3: 25,  # Features
    4: 20,  # Integration & Testing
}
```

**Phase 1: Setup (20%)**
- Architecture planning
- Project scaffolding
- Database schema design
- Infrastructure setup

**Phase 2: Core Implementation (35%)**
- Core business logic
- Primary data operations
- Authentication/authorization
- Core API endpoints

**Phase 3: Features (25%)**
- Additional features
- Advanced functionality
- External integrations
- Feature-specific tests

**Phase 4: Integration & Testing (20%)**
- System integration
- End-to-end testing
- Performance tuning
- Documentation

### 5-Phase Distribution (COMPLEX, VERY COMPLEX)

**Base Percentages**:
```python
PHASE_5_BASE = {
    1: 15,  # Foundation
    2: 35,  # Core Development
    3: 25,  # Feature Development
    4: 20,  # Integration
    5: 5,   # Validation & Polish
}
```

**Phase 1: Foundation (15%)**
- Architecture design
- Infrastructure provisioning
- Framework setup
- Security foundation
- Development environment

**Phase 2: Core Development (35%)**
- Core business logic
- Primary database operations
- Essential APIs
- Authentication system
- Core unit tests

**Phase 3: Feature Development (25%)**
- Extended features
- Complex workflows
- Advanced integrations
- Feature tests
- Performance optimization

**Phase 4: Integration (20%)**
- System integration
- Third-party service integration
- Integration testing
- Load testing
- Security testing

**Phase 5: Validation & Polish (5%)**
- Final validation
- Bug fixes
- Documentation
- Performance tuning
- Deployment preparation

### 6-Phase Distribution (CRITICAL)

**Base Percentages**:
```python
PHASE_6_BASE = {
    1: 12,  # Analysis & Setup
    2: 20,  # Foundation
    3: 25,  # Core Features
    4: 20,  # Advanced Features
    5: 18,  # Integration & Testing
    6: 5,   # Validation & Risk Mitigation
}
```

**Phase 1: Analysis & Setup (12%)**
- Requirements analysis
- Risk assessment
- Compliance review
- Architecture planning
- Technology selection

**Phase 2: Foundation (20%)**
- Infrastructure setup
- Security framework
- Monitoring system
- Core frameworks
- CI/CD pipeline

**Phase 3: Core Features (25%)**
- Primary business logic
- Core workflows
- Data management
- Authentication/authorization
- Core tests

**Phase 4: Advanced Features (20%)**
- Complex features
- Advanced workflows
- Sophisticated integrations
- Feature tests
- Performance optimization

**Phase 5: Integration & Testing (18%)**
- System integration
- End-to-end testing
- Security testing
- Performance testing
- Compliance validation

**Phase 6: Validation & Risk Mitigation (5%)**
- Final system validation
- Risk mitigation implementation
- Disaster recovery testing
- Documentation completion
- Deployment readiness

---

## Adjustment Formulas

**All adjustments MUST sum to exactly 100%.**

### Adjustment 1: High Integration

**Condition**: `integration_score > 0.7`

**Adjustment**:
```python
if integration_score > 0.7:
    # Add 5% to integration phase
    if phase_count == 3:
        distribution[2] += 5
        distribution[1] -= 5
    elif phase_count == 4:
        distribution[4] += 5
        distribution[2] -= 2
        distribution[3] -= 3
    elif phase_count >= 5:
        distribution[4] += 5
        distribution[2] -= 2
        distribution[3] -= 3
```

**Rationale**: High integration complexity requires dedicated integration time.

### Adjustment 2: High Uncertainty

**Condition**: `uncertainty > 0.6`

**Adjustment**:
```python
if uncertainty > 0.6:
    # Add 5% to setup/analysis phase
    distribution[1] += 5
    distribution[2] -= 5
```

**Rationale**: High uncertainty requires more upfront analysis and planning.

### Adjustment 3: High Scale

**Condition**: `scale > 0.7`

**Adjustment**:
```python
if scale > 0.7:
    # Add 5% to feature development phase
    if phase_count == 3:
        distribution[2] += 5
        distribution[3] -= 5
    elif phase_count >= 4:
        feature_phase = 3 if phase_count == 4 else 3
        distribution[feature_phase] += 5
        distribution[2] -= 5
```

**Rationale**: High scale requires more time for performance optimization and scalability features.

### Adjustment 4: High Technical Debt

**Condition**: `technical_debt > 0.6`

**Adjustment**:
```python
if technical_debt > 0.6:
    # Add 10% to setup/analysis phase
    distribution[1] += 10
    distribution[2] -= 5
    distribution[3] -= 5
```

**Rationale**: High technical debt requires upfront refactoring and legacy code analysis.

---

## Validation Gate Requirements

**Every phase MUST define ≥3 measurable validation gates.**

### Valid Gate Characteristics

1. **Measurable**: Can be objectively verified
2. **Specific**: Clearly defined success criteria
3. **Testable**: Can be validated programmatically or manually
4. **Relevant**: Directly related to phase objectives

### Valid Gate Examples

**API Development**:
- ✅ "Endpoint `/api/users` responds with 200 status code"
- ✅ "POST `/api/users` creates user in database"
- ✅ "API responds within 200ms for 95% of requests"

**Database**:
- ✅ "Migrations run without errors"
- ✅ "All tables created with correct schema"
- ✅ "Database connection pool sustains 50 connections"

**Testing**:
- ✅ "Test coverage ≥ 80%"
- ✅ "All 25 integration tests pass"
- ✅ "NO MOCKS detected in test files"

**Performance**:
- ✅ "Load test sustains 100 RPS"
- ✅ "P95 latency < 200ms"
- ✅ "Memory usage < 512MB under load"

### Invalid Gate Examples

- ❌ "Code looks good" (not measurable)
- ❌ "Tests pass" (too vague, which tests?)
- ❌ "API works" (no specific success criteria)
- ❌ "Everything is done" (not specific)
- ❌ "Quality is high" (subjective)

---

## Phase Gate Enforcement

### Gate Validation Process

```python
def validate_phase_gates(phase: int, gates: List[Gate]) -> bool:
    """
    Validate all gates for a phase.

    Returns:
        True if ALL gates pass, False otherwise
    """
    if len(gates) < 3:
        raise ValidationError(f"Phase {phase} requires ≥3 gates, got {len(gates)}")

    results = []
    for gate in gates:
        if not gate.is_measurable():
            raise ValidationError(f"Gate '{gate.description}' is not measurable")

        result = gate.execute()
        results.append(result)

    return all(results)
```

### Gate Failure Response

**If any gate fails**:
1. Mark phase as INCOMPLETE
2. Block progression to next phase
3. Trigger recovery workflow
4. Do NOT create checkpoint
5. Display failed gate details to user

**Recovery Options**:
- Fix issue and re-run gate validation
- Adjust gate criteria (requires justification)
- Skip gate (requires explicit user approval with warning)

---

## Timeline Calculation

### Duration Estimation

```python
def calculate_phase_durations(
    complexity: float,
    phase_count: int,
    distribution: Dict[int, int]
) -> Dict[int, float]:
    """
    Calculate duration in hours for each phase.

    Returns:
        Dict mapping phase number to duration in hours
    """
    # Base duration by complexity category
    if complexity < 0.20:
        total_hours = 4  # TRIVIAL
    elif complexity < 0.40:
        total_hours = 16  # SIMPLE (2 days * 8 hours)
    elif complexity < 0.60:
        total_hours = 40  # MODERATE (5 days * 8 hours)
    elif complexity < 0.75:
        total_hours = 120  # COMPLEX (15 days * 8 hours)
    elif complexity < 0.90:
        total_hours = 320  # VERY COMPLEX (40 days * 8 hours)
    else:
        total_hours = 640  # CRITICAL (80 days * 8 hours)

    # Calculate per-phase durations
    durations = {}
    for phase, percentage in distribution.items():
        durations[phase] = total_hours * (percentage / 100.0)

    return durations
```

### Example Calculation

**Project**: REST API (Complexity: 0.38)

**Category**: SIMPLE
**Phase Count**: 3
**Total Duration**: 16 hours

**Distribution**:
- Phase 1: 25% = 4 hours
- Phase 2: 50% = 8 hours
- Phase 3: 25% = 4 hours

---

## Anti-Rationalization Patterns

### Pattern 1: "Phases are redundant with tasks"

**Rationalization**: "We can just break it into tasks, phases are overhead"

**Counter**:
- Phases structure work; tasks are implementation details
- Phases determine resource allocation algorithmically
- Task-by-task approach underestimates effort by 40-60%
- Phase planning takes 5-10 minutes; prevents hours of rework

**Action**: BLOCKED - Complete phase planning before task breakdown

### Pattern 2: "3 phases work for everything"

**Rationalization**: "All projects can use the same 3-phase template"

**Counter**:
- Phase count is determined by complexity score algorithmically
- Template oversimplification underestimates effort by 40-60%
- Historical data: MODERATE projects (0.40-0.60) require 4-5 phases

**Action**: BLOCKED - Use algorithmic phase count determination

### Pattern 3: "Validation gates are redundant with testing"

**Rationalization**: "Tests cover everything, gates are unnecessary"

**Counter**:
- Gates are phase-specific acceptance criteria
- Tests verify code units; gates verify phase objectives
- Gates catch issues 40% earlier than end-of-project testing
- Omitting gates creates downstream failures

**Action**: BLOCKED - Define ≥3 measurable gates per phase

### Pattern 4: "Timeline percentages feel wrong"

**Rationalization**: "20% for setup seems excessive, let's adjust"

**Counter**:
- Percentages derive from mathematical formulas and historical data
- "Feel" is not a valid input to quantitative planning
- Intuition underestimates setup time by 50% on average
- Only recalculate if formula errors identified

**Action**: BLOCKED - Use formula-based percentages unless calculation error proven

---

## Phase Plan Storage (Serena MCP)

### File: `.serena/ccb/phase_plan.json`

```json
{
  "created_at": "2025-01-17T14:30:22Z",
  "complexity_score": 0.385,
  "complexity_category": "SIMPLE",
  "phase_count": 3,
  "total_duration_hours": 16,
  "phases": [
    {
      "number": 1,
      "name": "Setup & Core",
      "percentage": 25,
      "duration_hours": 4,
      "objectives": [
        "Project structure",
        "Database setup",
        "Core models"
      ],
      "validation_gates": [
        {
          "id": "p1g1",
          "description": "Project runs without errors",
          "criteria": "python manage.py runserver succeeds",
          "status": "pending"
        },
        {
          "id": "p1g2",
          "description": "Database initialized",
          "criteria": "Migrations applied, tables created",
          "status": "pending"
        },
        {
          "id": "p1g3",
          "description": "Health check responds",
          "criteria": "GET /health returns 200",
          "status": "pending"
        }
      ]
    },
    {
      "number": 2,
      "name": "Features & Integration",
      "percentage": 50,
      "duration_hours": 8,
      "objectives": [
        "API endpoints",
        "Business logic",
        "Authentication"
      ],
      "validation_gates": [
        {
          "id": "p2g1",
          "description": "All API endpoints functional",
          "criteria": "8 endpoints return expected responses",
          "status": "pending"
        },
        {
          "id": "p2g2",
          "description": "JWT authentication works",
          "criteria": "Login returns valid token, protected routes check token",
          "status": "pending"
        },
        {
          "id": "p2g3",
          "description": "Integration tests pass",
          "criteria": "12 integration tests pass (NO MOCKS)",
          "status": "pending"
        }
      ]
    },
    {
      "number": 3,
      "name": "Testing & Validation",
      "percentage": 25,
      "duration_hours": 4,
      "objectives": [
        "Test coverage",
        "Performance validation",
        "Documentation"
      ],
      "validation_gates": [
        {
          "id": "p3g1",
          "description": "Test coverage ≥80%",
          "criteria": "pytest-cov reports ≥80%",
          "status": "pending"
        },
        {
          "id": "p3g2",
          "description": "All functional tests pass",
          "criteria": "25 tests pass, NO MOCKS detected",
          "status": "pending"
        },
        {
          "id": "p3g3",
          "description": "Documentation complete",
          "criteria": "README.md, API docs, deployment guide present",
          "status": "pending"
        }
      ]
    }
  ],
  "adjustments": [
    "No adjustments - standard SIMPLE project"
  ]
}
```

---

## Usage in Commands

### `/ccb:init`

1. Calculate complexity score
2. Determine phase count algorithmically
3. Apply base distribution for phase count
4. Apply adjustment formulas
5. Generate validation gates (≥3 per phase)
6. Calculate phase durations
7. Save to `.serena/ccb/phase_plan.json`

### `/ccb:build`

1. Load phase plan from Serena MCP
2. Check current phase from `.serena/ccb/current_phase.txt`
3. Display phase objectives and gates
4. Execute phase tasks (guided by skills)
5. Run validation gates
6. If all gates pass: mark complete, create checkpoint, advance phase
7. If any gate fails: mark incomplete, block progression, show recovery options

### `/ccb:status`

- Display current phase and progress
- Show validation gate status (✅ passed, ⏳ pending, ❌ failed)
- Display time spent vs. allocated time per phase
- Warn if trending over allocated time

---

## References

- **Complexity Analysis**: `.claude/core/complexity-analysis.md`
- **CCB Principles**: `.claude/core/ccb-principles.md`
- **Shannon Phase Planning**: [shannon-framework/skills/phase-planning](https://github.com/krzemienski/shannon-framework)

---

**End of Phase Planning**

**Next**: Load `testing-philosophy.md` for NO MOCKS enforcement.
