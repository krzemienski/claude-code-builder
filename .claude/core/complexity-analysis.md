# Complexity Analysis: 6D Quantitative Scoring

**Framework**: Claude Code Builder v3
**Purpose**: Replace subjective assessments with measurable complexity scores
**Output**: 0.0-1.0 score + phase count + timeline distribution

---

## Overview

Complexity analysis transforms subjective characterizations ("simple", "complex") into quantitative 0.0-1.0 scores across six weighted dimensions.

**Why Quantitative Scoring**:
- Eliminates estimation bias (40-60% underestimation common)
- Enables algorithmic phase planning
- Provides reproducible resource estimates
- Prevents scope creep through objective measurement

---

## The 6 Dimensions

### 1. Structure (Weight: 20%)

**What It Measures**:
- Total file count
- Module/package depth
- Architectural patterns (layered, microservices, monolith)
- Component dependencies

**Scoring Formula**:
```python
structure_score = min(1.0,
    (file_count / 50) * 0.4 +
    (module_depth / 5) * 0.6
)
```

**Scoring Examples**:

| Files | Depth | Calculation | Score | Category |
|-------|-------|-------------|-------|----------|
| 5 | 2 | (5/50)*0.4 + (2/5)*0.6 | 0.28 | Low |
| 25 | 3 | (25/50)*0.4 + (3/5)*0.6 | 0.56 | Moderate |
| 50 | 5 | (50/50)*0.4 + (5/5)*0.6 | 1.00 | High |
| 100 | 7 | min(1.0, ...) | 1.00 | Critical |

**Architectural Pattern Multipliers**:
- Monolith: 1.0x (base)
- Layered (3-tier): 1.1x
- Microservices: 1.3x
- Event-driven: 1.4x

### 2. Logic (Weight: 25%)

**What It Measures**:
- Business rule count
- Algorithm complexity (sorting, search, optimization)
- State machines / workflows
- Conditional branch count
- Data transformations

**Scoring Formula**:
```python
logic_score = min(1.0,
    (business_rules / 20) * 0.5 +
    (branch_count / 30) * 0.5
)
```

**Rule Complexity Categories**:

| Type | Examples | Weight |
|------|----------|--------|
| Simple CRUD | Create, Read, Update, Delete | 0.1 per rule |
| Validation | Input validation, format checking | 0.2 per rule |
| Business Logic | Discount calculation, eligibility checks | 0.4 per rule |
| Workflow | Multi-step approval, state transitions | 0.7 per rule |
| Algorithm | Sorting, pathfinding, optimization | 1.0 per rule |

**Scoring Examples**:

| Rules | Branches | Calculation | Score | Category |
|-------|----------|-------------|-------|----------|
| 5 (CRUD only) | 10 | (5/20)*0.5 + (10/30)*0.5 | 0.29 | Simple |
| 10 (CRUD+auth) | 20 | (10/20)*0.5 + (20/30)*0.5 | 0.58 | Moderate |
| 20 (workflows) | 30 | (20/20)*0.5 + (30/30)*0.5 | 1.00 | Complex |

### 3. Integration (Weight: 20%)

**What It Measures**:
- External service count (APIs, databases, queues)
- Authentication types (OAuth, SAML, JWT, API keys)
- Data format conversions (JSON, XML, Protocol Buffers)
- Network protocols (HTTP, WebSockets, gRPC)
- Third-party SDK integrations

**Scoring Formula**:
```python
integration_score = min(1.0,
    (integration_count / 8) * 0.7 +
    (auth_types / 3) * 0.3
)
```

**Integration Types**:

| Type | Examples | Complexity |
|------|----------|------------|
| Database | PostgreSQL, MongoDB | 1 point |
| REST API | External REST endpoint | 1 point |
| GraphQL | External GraphQL API | 1.5 points |
| Message Queue | RabbitMQ, Kafka | 2 points |
| WebSockets | Real-time connections | 1.5 points |
| File Storage | S3, Azure Blob | 0.5 points |
| Email/SMS | SendGrid, Twilio | 0.5 points |
| Auth Provider | OAuth, SAML, LDAP | 1 point each |

**Scoring Examples**:

| Integrations | Auth Types | Calculation | Score | Category |
|--------------|------------|-------------|-------|----------|
| 1 (DB only) | 0 | (1/8)*0.7 + (0/3)*0.3 | 0.09 | Low |
| 4 (DB+2 APIs+Queue) | 1 (JWT) | (4/8)*0.7 + (1/3)*0.3 | 0.45 | Moderate |
| 8 (many services) | 3 (OAuth+SAML+JWT) | (8/8)*0.7 + (3/3)*0.3 | 1.00 | High |

### 4. Scale (Weight: 15%)

**What It Measures**:
- Expected user count (concurrent & total)
- Data volume (storage requirements)
- Request throughput (requests per second)
- Geographic distribution (single region vs global)

**Scoring Formula**:
```python
scale_score = min(1.0,
    log10(expected_users) / 7 * 0.4 +
    log10(data_gb) / 4 * 0.6
)
```

**Scoring Examples**:

| Users | Data (GB) | Calculation | Score | Category |
|-------|-----------|-------------|-------|----------|
| 10 | 0.1 | log10(10)/7*0.4 + log10(0.1)/4*0.6 | 0.21 | Low |
| 1,000 | 10 | log10(1000)/7*0.4 + log10(10)/4*0.6 | 0.32 | Moderate |
| 100,000 | 1,000 | log10(100000)/7*0.4 + log10(1000)/4*0.6 | 0.68 | High |
| 10,000,000 | 100,000 | log10(10^7)/7*0.4 + log10(10^5)/4*0.6 | 0.95 | Critical |

**Throughput Considerations**:
- <10 RPS: 0x adjustment
- 10-100 RPS: +0.1 to scale score
- 100-1000 RPS: +0.2 to scale score
- >1000 RPS: +0.3 to scale score

### 5. Uncertainty (Weight: 10%)

**What It Measures**:
- Specification completeness (0-100%)
- Requirement clarity (clear, ambiguous, vague)
- Unknown unknowns count
- Stakeholder alignment level

**Scoring Formula**:
```python
# Inverse: More complete spec = Lower uncertainty
uncertainty_score = 1.0 - (spec_completeness * clarity_factor)

# Where clarity_factor:
# - Clear requirements: 1.0
# - Some ambiguity: 0.7
# - Many unknowns: 0.4
```

**Specification Completeness Assessment**:

| Spec Element | Weight | Present | Score |
|--------------|--------|---------|-------|
| Project goal | 15% | Yes/No | 0.15 or 0 |
| User stories | 15% | Yes/No | 0.15 or 0 |
| Technical requirements | 20% | Yes/No | 0.20 or 0 |
| Data model | 15% | Yes/No | 0.15 or 0 |
| API contracts | 15% | Yes/No | 0.15 or 0 |
| Acceptance criteria | 20% | Yes/No | 0.20 or 0 |

**Total**: Sum of scores = Spec Completeness (0.0-1.0)

**Scoring Examples**:

| Completeness | Clarity | Calculation | Score | Category |
|--------------|---------|-------------|-------|----------|
| 100% | Clear (1.0) | 1.0 - (1.0 * 1.0) | 0.00 | Very Low |
| 70% | Some ambiguity (0.7) | 1.0 - (0.7 * 0.7) | 0.51 | Moderate |
| 40% | Many unknowns (0.4) | 1.0 - (0.4 * 0.4) | 0.84 | High |
| 20% | Vague (0.2) | 1.0 - (0.2 * 0.2) | 0.96 | Critical |

### 6. Technical Debt (Weight: 10%)

**What It Measures**:
- Legacy code ratio (old code / total code)
- Deprecated dependency count
- Incompatible framework versions
- Security vulnerability count
- Code quality issues (linting, formatting)

**Scoring Formula**:
```python
tech_debt_score = min(1.0,
    (legacy_files / total_files) * 0.6 +
    (deprecated_deps / total_deps) * 0.4
)
```

**Legacy Code Definition**:
- Code >3 years old without updates
- Using deprecated APIs
- Missing tests
- No documentation
- Security vulnerabilities

**Scoring Examples**:

| Legacy % | Deprecated Deps | Calculation | Score | Category |
|----------|-----------------|-------------|-------|----------|
| 0% (greenfield) | 0 | 0*0.6 + 0*0.4 | 0.00 | None |
| 20% | 2/10 | 0.2*0.6 + 0.2*0.4 | 0.20 | Low |
| 50% | 5/10 | 0.5*0.6 + 0.5*0.4 | 0.50 | Moderate |
| 80% | 8/10 | 0.8*0.6 + 0.8*0.4 | 0.80 | High |

---

## Overall Complexity Score

### Calculation

```python
def calculate_overall_complexity(
    structure: float,
    logic: float,
    integration: float,
    scale: float,
    uncertainty: float,
    technical_debt: float
) -> float:
    return (
        structure * 0.20 +
        logic * 0.25 +
        integration * 0.20 +
        scale * 0.15 +
        uncertainty * 0.10 +
        technical_debt * 0.10
    )
```

### Example Calculation

**Project**: REST API with authentication and rate limiting

**Dimension Scores**:
- Structure: 0.42 (20 files, 3 levels)
- Logic: 0.55 (11 business rules, 22 branches)
- Integration: 0.45 (DB, 2 APIs, JWT auth)
- Scale: 0.25 (1000 users, 10GB data)
- Uncertainty: 0.35 (70% spec complete, some ambiguity)
- Technical Debt: 0.00 (greenfield)

**Overall**:
```
0.42*0.20 + 0.55*0.25 + 0.45*0.20 + 0.25*0.15 + 0.35*0.10 + 0.00*0.10
= 0.084 + 0.138 + 0.090 + 0.038 + 0.035 + 0.000
= 0.385
```

**Result**: 0.39 (SIMPLE)

---

## Complexity Categories

### Category Definitions

| Score Range | Category | Characteristics | Typical Projects |
|-------------|----------|-----------------|------------------|
| 0.00 - 0.20 | TRIVIAL | Single-file scripts, utilities | CLI tools, scripts |
| 0.20 - 0.40 | SIMPLE | Basic apps, limited integrations | Todo apps, blogs |
| 0.40 - 0.60 | MODERATE | Multi-layer, some integrations | E-commerce, dashboards |
| 0.60 - 0.75 | COMPLEX | Distributed, many integrations | Social platforms, marketplaces |
| 0.75 - 0.90 | VERY COMPLEX | Large scale, high uncertainty | Enterprise systems, SaaS platforms |
| 0.90 - 1.00 | CRITICAL | Mission-critical, regulated | Banking, healthcare, aerospace |

### Phase Count by Category

| Category | Phase Count | Rationale |
|----------|-------------|-----------|
| TRIVIAL | 3 | Setup, Implementation, Validation |
| SIMPLE | 3 | Setup, Core, Testing |
| MODERATE | 4 | Setup, Core, Features, Integration |
| COMPLEX | 5 | Setup, Foundation, Core, Features, Integration |
| VERY COMPLEX | 5-6 | + Extended validation or risk mitigation |
| CRITICAL | 6 | + Dedicated risk mitigation phase |

### Timeline Estimates

| Category | Duration | Team Size | Risk Level |
|----------|----------|-----------|------------|
| TRIVIAL | 2-6 hours | 1 | Very Low |
| SIMPLE | 1-3 days | 1-2 | Low |
| MODERATE | 3-7 days | 2-3 | Moderate |
| COMPLEX | 1-3 weeks | 3-5 | Moderate-High |
| VERY COMPLEX | 3-8 weeks | 5-8 | High |
| CRITICAL | 8-16 weeks | 8-15 | Very High |

---

## Phase Planning Integration

### 3-Phase Distribution (TRIVIAL, SIMPLE)

```
Phase 1: Setup & Core (25%)
- Project structure
- Core functionality
- Basic validation

Phase 2: Features & Integration (50%)
- Feature implementation
- External integrations
- Primary testing

Phase 3: Testing & Validation (25%)
- Comprehensive testing
- Performance validation
- Documentation
```

### 4-Phase Distribution (MODERATE)

```
Phase 1: Setup (20%)
- Project structure
- Database schema
- Configuration

Phase 2: Core (35%)
- Core business logic
- Primary APIs
- Unit tests

Phase 3: Features (25%)
- Additional features
- Integrations
- Integration tests

Phase 4: Validation (20%)
- End-to-end testing
- Performance tuning
- Documentation
```

### 5-Phase Distribution (COMPLEX, VERY COMPLEX)

```
Phase 1: Foundation (15%)
- Architecture
- Infrastructure
- Setup

Phase 2: Core (35%)
- Core business logic
- Primary features
- Core tests

Phase 3: Features (25%)
- Additional features
- Integrations
- Feature tests

Phase 4: Integration (20%)
- System integration
- Performance optimization
- Integration tests

Phase 5: Validation (5%)
- Final validation
- Security audit
- Documentation
```

### 6-Phase Distribution (CRITICAL)

```
Phase 1: Analysis & Setup (12%)
- Requirements analysis
- Risk assessment
- Architecture planning

Phase 2: Foundation (20%)
- Infrastructure
- Core frameworks
- Security foundation

Phase 3: Core Features (25%)
- Primary business logic
- Core APIs
- Core tests

Phase 4: Advanced Features (20%)
- Complex features
- Advanced integrations
- Feature tests

Phase 5: Integration & Testing (18%)
- System integration
- Performance testing
- Security testing

Phase 6: Validation & Risk Mitigation (5%)
- Final validation
- Risk mitigation
- Compliance verification
```

---

## Adjustment Factors

### Integration Adjustment

**If** `integration_score > 0.7`:
- **Action**: Add 5% to Phase 4 (Integration)
- **Source**: Subtract 2% from Phase 2, 3% from Phase 3

**Rationale**: High integration complexity requires dedicated integration effort.

### Uncertainty Adjustment

**If** `uncertainty > 0.6`:
- **Action**: Add 5% to Phase 1 (Setup/Analysis)
- **Source**: Subtract 5% from Phase 2

**Rationale**: High uncertainty requires more upfront analysis and planning.

### Scale Adjustment

**If** `scale > 0.7`:
- **Action**: Add 5% to Phase 3 (Features)
- **Source**: Subtract 5% from Phase 2

**Rationale**: High scale requires more feature development time for performance optimization.

### Technical Debt Adjustment

**If** `technical_debt > 0.6`:
- **Action**: Add 10% to Phase 1 (Analysis/Refactoring)
- **Source**: Subtract 5% from Phase 2, 5% from Phase 3

**Rationale**: High technical debt requires upfront refactoring and analysis.

---

## Output Format

### Complexity Analysis Report

```json
{
  "overall_score": 0.385,
  "category": "SIMPLE",
  "dimensions": {
    "structure": {"score": 0.42, "details": "20 files, 3 levels"},
    "logic": {"score": 0.55, "details": "11 business rules, 22 branches"},
    "integration": {"score": 0.45, "details": "DB + 2 APIs + JWT"},
    "scale": {"score": 0.25, "details": "1K users, 10GB data"},
    "uncertainty": {"score": 0.35, "details": "70% complete, some ambiguity"},
    "technical_debt": {"score": 0.00, "details": "Greenfield"}
  },
  "phase_plan": {
    "count": 3,
    "distribution": {
      "phase_1": {"percentage": 25, "duration_hours": 4},
      "phase_2": {"percentage": 50, "duration_hours": 8},
      "phase_3": {"percentage": 25, "duration_hours": 4}
    },
    "total_duration_hours": 16,
    "total_duration_days": 2
  },
  "risk_level": "Low",
  "recommended_team_size": "1-2",
  "confidence": 0.85
}
```

---

## Usage in Commands

### `/ccb:init`

1. Parse specification text
2. Calculate 6D complexity scores
3. Determine phase count algorithmically
4. Calculate timeline distribution
5. Generate phase plan with validation gates
6. Save to `.serena/ccb/complexity_analysis.json`

### `/ccb:analyze`

1. Calculate complexity scores only (no phase planning)
2. Display dimension breakdown
3. Optionally save results (`--save` flag)
4. Optionally recommend MCPs (`--mcps` flag)

### `/ccb:status`

- Display current complexity score
- Show phase progress relative to complexity-based timeline
- Highlight if project is trending over/under complexity estimate

---

## References

- **Shannon Framework 8D Scoring**: [shannon-framework/skills/spec-analysis](https://github.com/krzemienski/shannon-framework)
- **CCB Principles**: `.claude/core/ccb-principles.md`
- **Phase Planning**: `.claude/core/phase-planning.md`

---

**End of Complexity Analysis**

**Next**: Load `phase-planning.md` for timeline distribution algorithms.
