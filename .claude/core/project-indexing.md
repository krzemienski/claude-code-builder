# Project Indexing: 94% Token Reduction for Existing Codebases

**Framework**: Claude Code Builder v3
**Purpose**: Compress large codebases into structured summaries
**Achievement**: 58,000 tokens → 3,000 tokens (94.8% reduction)
**ROI**: 16.6x token savings on follow-up operations

---

## The Problem

**Reading raw codebases is expensive**:
- Average file: 400 tokens
- 100-file project: 40,000 tokens
- 500-file project: 200,000 tokens (exceeds context window)

**Naive approach multiplies costs**:
- Analyze architecture: Load all files (40K tokens)
- Find module: Load all files (40K tokens)
- Add feature: Load all files (40K tokens)
- **Total**: 120K tokens for 3 operations

---

## The Solution: PROJECT_INDEX.md

**Hierarchical summarization** achieves 94% reduction:

**Input**: 127 files, 18,432 lines, 58,000 tokens
**Output**: PROJECT_INDEX.md, 3,100 tokens
**Reduction**: 94.6%

**Subsequent operations**:
- Analyze architecture: 3,100 tokens (index) + 0 tokens (no files)
- Find module: 3,100 tokens (index) + 500 tokens (1 specific file)
- Add feature: 3,100 tokens (index) + 1,500 tokens (3 specific files)
- **Total**: 11,200 tokens (vs 120,000 without indexing)
- **Savings**: 90.7%

---

## When to Index

### Mandatory Indexing

**`/ccb:do` command** (operate on existing codebase):
- ALWAYS indexes before modification
- Ensures understanding of existing architecture
- Prevents breaking existing functionality

### Recommended Indexing

1. **Beginning any project analysis**
2. **Onboarding new agents/sessions**
3. **Multi-agent workflows** (each agent needs context)
4. **Switching between projects**
5. **Context window efficiency critical**

### Anti-Rationalization

**Rationalization**: "I can just read the files directly, indexing is unnecessary"

**Counter**:
- Token cost multiplication: N operations × 40,000 tokens
- Index generation: 3,100 tokens (one-time)
- Subsequent queries: 50 tokens (index lookup) vs 5,000 tokens (file reads)
- ROI: 16.6x savings
- Time savings: 99% on follow-up operations

**Action**: BLOCKED - Run `/ccb:index` before operating on existing codebase

---

## Generation Process

### Phase 1: Discovery (800 tokens)

**Scan directory structure**:
```python
def discover_project() -> ProjectStructure:
    """
    Discover project files and structure.

    Returns:
        ProjectStructure with files, directories, sizes
    """
    structure = {
        "root": Path.cwd(),
        "files": [],
        "directories": [],
        "total_lines": 0,
        "total_size_bytes": 0,
    }

    for file in Path.cwd().rglob("*"):
        if should_skip(file):  # Skip node_modules, .git, etc.
            continue

        if file.is_file():
            structure["files"].append({
                "path": str(file),
                "size": file.stat().st_size,
                "lines": count_lines(file),
                "extension": file.suffix,
            })
            structure["total_lines"] += count_lines(file)
            structure["total_size_bytes"] += file.stat().st_size

    return structure
```

**Output**: File list, sizes, extensions, line counts

### Phase 2: Tech Stack Analysis (1,200 tokens)

**Detect languages and frameworks**:
```python
def analyze_tech_stack(files: List[Path]) -> TechStack:
    """
    Detect languages, frameworks, and tools.

    Returns:
        TechStack with languages, frameworks, tools, versions
    """
    stack = {
        "languages": {},  # Extension -> percentage
        "frameworks": [],
        "databases": [],
        "tools": [],
    }

    # Language detection
    for file in files:
        ext = file.suffix
        if ext in LANGUAGE_MAP:
            stack["languages"][LANGUAGE_MAP[ext]] = \
                stack["languages"].get(LANGUAGE_MAP[ext], 0) + 1

    # Framework detection (parse package files)
    if "package.json" in files:
        package_json = json.load(open("package.json"))
        stack["frameworks"].extend(detect_js_frameworks(package_json))

    if "requirements.txt" in files:
        requirements = open("requirements.txt").readlines()
        stack["frameworks"].extend(detect_python_frameworks(requirements))

    if "Cargo.toml" in files:
        cargo = toml.load(open("Cargo.toml"))
        stack["frameworks"].extend(detect_rust_frameworks(cargo))

    return stack
```

**Output**: Language percentages, framework versions, tools

### Phase 3: Architecture Identification (600 tokens)

**Identify patterns and structure**:
```python
def identify_architecture(files: List[Path], tech_stack: TechStack) -> Architecture:
    """
    Identify architectural patterns.

    Returns:
        Architecture with pattern, layers, module boundaries
    """
    patterns = []

    # MVC detection
    if has_directories(["models", "views", "controllers"]):
        patterns.append("MVC")

    # Microservices detection
    if has_multiple_services() and has_file("docker-compose.yml"):
        patterns.append("Microservices")

    # Layered architecture
    if has_directories(["api", "services", "models"]):
        patterns.append("3-Layer (API -> Services -> Models)")

    # Monolith detection
    if len(get_entry_points()) == 1:
        patterns.append("Monolith")

    return {
        "patterns": patterns,
        "entry_points": find_entry_points(),
        "core_modules": identify_core_modules(),
        "dependencies": parse_dependencies(),
    }
```

**Output**: Architectural patterns, entry points, modules, dependencies

### Phase 4: Pattern Extraction (300 tokens)

**Extract common coding patterns**:
```python
def extract_patterns(files: List[Path]) -> List[Pattern]:
    """
    Extract common coding patterns and conventions.

    Returns:
        List of Pattern objects (naming, testing, error handling)
    """
    patterns = []

    # Naming conventions
    patterns.append(detect_naming_convention(files))

    # Testing approach
    if has_tests:
        patterns.append({
            "type": "testing",
            "framework": detect_test_framework(),
            "coverage": calculate_test_coverage(),
            "mocks_present": detect_mocks(),  # Flag for NO MOCKS enforcement
        })

    # Error handling
    patterns.append(analyze_error_handling(files))

    # Authentication
    if auth_files := find_auth_files():
        patterns.append(analyze_auth_pattern(auth_files))

    return patterns
```

**Output**: Naming conventions, testing approach, error handling, auth patterns

### Phase 5: Index Generation (100 tokens)

**Generate PROJECT_INDEX.md**:
```markdown
# Project Index

**Generated**: 2025-01-17 14:30:22
**Total Files**: 127
**Total Lines**: 18,432
**Total Size**: 2.4 MB

## Quick Stats

- **Languages**: Python (78%), TypeScript (18%), SQL (4%)
- **Frameworks**: FastAPI, React, PostgreSQL
- **Test Coverage**: 87%
- **Dependencies**: 42 total (3 outdated)
- **Architecture**: 3-Layer (API → Services → Models)

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
- **NO MOCKS** (functional tests only)

## Core Modules

### API Layer (`src/api/`)
- `server.py`: FastAPI app, middleware, CORS
- `routes/`: REST endpoints (auth, users, posts)
- `dependencies.py`: Dependency injection

### Business Logic (`src/services/`)
- `auth_service.py`: JWT auth, password hashing (bcrypt)
- `user_service.py`: User CRUD operations
- `post_service.py`: Post creation, retrieval, search

### Data Layer (`src/models/`)
- `user.py`: User SQLAlchemy model
- `post.py`: Post model with relationships
- `database.py`: DB connection, session management

### Frontend (`frontend/src/`)
- `App.tsx`: Root component, routing (React Router)
- `pages/`: Page components (Home, Profile, Post)
- `components/`: Reusable UI (Button, Card, Input)
- `hooks/`: Custom hooks (useAuth, usePosts)
- `api/`: API client (axios)

## Dependencies

**Production**: 28
**Development**: 14

**Outdated** (3):
- FastAPI 0.109.0 → 0.110.0 (security fix available)
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
- pytest for backend (87% coverage)
- Playwright for frontend (E2E tests)
- **NO MOCKS** (functional tests with testcontainers)

### Error Handling
- Custom exception hierarchy (`AppException`, `ValidationError`, `NotFoundError`)
- Global exception handlers in FastAPI
- Structured logging with loguru

### API Design
- RESTful endpoints
- JSON request/response
- Pagination (limit/offset)
- Filtering via query params
- Versioning (`/api/v1/`)

## Entry Points

- **Backend**: `src/api/server.py` (FastAPI app)
- **Frontend**: `frontend/src/main.tsx` (React root)
- **CLI**: `src/cli/main.py` (Click commands)

## Recent Changes

- 2025-01-15: Added JWT refresh token endpoint
- 2025-01-14: Implemented rate limiting (100 req/min)
- 2025-01-13: Migrated from MySQL to PostgreSQL
- 2025-01-12: Added E2E tests with Playwright

## Notes

- Database migrations managed via Alembic
- Docker Compose for local development
- CI/CD via GitHub Actions
- Deployed on AWS (ECS + RDS)
```

---

## Index Structure Specification

### Required Sections

Every PROJECT_INDEX.md MUST include:

1. **Header** (metadata)
   - Generation timestamp
   - File/line/size counts

2. **Quick Stats** (high-level overview)
   - Language breakdown
   - Frameworks
   - Test coverage
   - Dependencies count
   - Architecture type

3. **Tech Stack** (detailed versions)
   - Backend frameworks and versions
   - Frontend frameworks and versions
   - Databases and tools
   - Testing frameworks

4. **Core Modules** (hierarchical structure)
   - Module paths
   - File descriptions (1-2 sentences each)
   - Responsibilities

5. **Dependencies** (production + development)
   - Counts
   - Outdated dependencies with available versions

6. **Key Patterns** (conventions)
   - Architecture pattern
   - Authentication approach
   - Testing strategy (**NO MOCKS flag**)
   - Error handling
   - API design

7. **Entry Points** (where execution starts)
   - Backend entry
   - Frontend entry
   - CLI entry (if applicable)

### Optional Sections

- **Recent Changes**: Git log summary
- **Known Issues**: TODO comments or GitHub issues
- **Performance**: Benchmarks or profiling notes
- **Security**: Security audit notes

---

## Token Accounting

### Generation Costs

| Phase | Operation | Tokens |
|-------|-----------|--------|
| 1 | Discovery | 800 |
| 2 | Tech Stack Analysis | 1,200 |
| 3 | Architecture Identification | 600 |
| 4 | Pattern Extraction | 300 |
| 5 | Index Generation | 100 |
| **Total** | **Generation** | **3,000** |

### Usage Costs

| Operation | Without Index | With Index | Savings |
|-----------|---------------|------------|---------|
| First analysis | 0 (generate index) | 3,000 | -3,000 (one-time cost) |
| Architecture query | 40,000 (load all files) | 3,100 (read index) | 36,900 (92.3%) |
| Find module | 40,000 | 3,600 (index + 1 file) | 36,400 (91.0%) |
| Add feature | 40,000 | 4,600 (index + 3 files) | 35,400 (88.5%) |
| Refactor | 40,000 | 5,100 (index + 5 files) | 34,900 (87.3%) |

**3 operations without index**: 120,000 tokens
**3 operations with index**: 14,300 tokens
**Savings**: 105,700 tokens (88.1%)
**ROI**: 8.4x after 3 operations, 16.6x after 6 operations

---

## Compressed Representation

### Hierarchical Summarization

**Level 1: Quick Stats** (50 tokens)
- Languages, frameworks, test coverage
- Loaded ALWAYS

**Level 2: Core Modules** (500 tokens)
- Module paths and responsibilities
- Loaded when needed

**Level 3: Detailed Files** (full source)
- Specific file contents
- Loaded on-demand via filesystem

**Token Progressive Disclosure**:
- Initial: 50 tokens (Quick Stats)
- Deep dive: +500 tokens (Core Modules)
- Specific file: +400 tokens per file

### Structural Deduplication

**Identify repeating patterns**:
```markdown
## Core Modules

### API Routes (`src/api/routes/`)
**Pattern**: REST endpoints following FastAPI conventions
- `auth.py`: Login, register, refresh token
- `users.py`: User CRUD (GET, POST, PUT, DELETE)
- `posts.py`: Post CRUD + search
- `comments.py`: Comment CRUD
- `likes.py`: Like creation/deletion

**All files follow**:
- Pydantic request/response models
- Dependency injection for auth
- 200/201/400/401/404 status codes
- Docstrings with examples
```

**Instead of**:
```markdown
- auth.py: FastAPI endpoint for login with Pydantic models, uses dependency injection, returns 200/401, has docstrings
- users.py: FastAPI endpoint for users with Pydantic models, uses dependency injection, returns 200/404, has docstrings
... (repeat 5 times)
```

**Token savings**: 200 tokens → 80 tokens (60% reduction)

### Pattern Abstraction

**Abstract common implementations**:
```markdown
## Testing Strategy

**Framework**: pytest + Playwright
**Coverage**: 87%
**Approach**: Functional tests with REAL dependencies (NO MOCKS)

**Backend tests** (pytest):
- Real PostgreSQL via testcontainers
- Real FastAPI TestClient
- Database migrations run before each test suite
- Pattern: Arrange (insert test data) → Act (API call) → Assert (check DB + response)

**Frontend tests** (Playwright):
- Real browser (Chrome/Firefox)
- Real API server (localhost:8000)
- Pattern: Navigate → Interact → Assert (page state)

**Test file naming**: `test_*.py`, `*.test.ts`
**Test location**: `tests/` (Python), `__tests__/` (TypeScript)
```

---

## Usage in Commands

### `/ccb:index [directory]`

**Workflow**:
1. Check if PROJECT_INDEX.md exists and is recent (<24 hours)
2. If exists and recent: Skip generation, use existing
3. If not: Generate new index
4. Display Quick Stats to user
5. Save to `PROJECT_INDEX.md` and `.serena/ccb/indices/PROJECT_INDEX.md`

**Example**:
```bash
/ccb:index

# Output:
Generating project index...

Discovered:
- 127 files (18,432 lines)
- Python 78%, TypeScript 18%, SQL 4%
- FastAPI + React stack
- 87% test coverage

✅ PROJECT_INDEX.md created (3,102 tokens vs 58,000 raw)

Token reduction: 94.6%
Savings on next operation: 36,900 tokens (92.3%)
```

### `/ccb:do "<task>"`

**Workflow**:
1. Check for PROJECT_INDEX.md
2. If missing: Generate automatically
3. Load index (3,100 tokens)
4. Analyze task against index
5. Identify affected modules (0 tokens, just index lookup)
6. Load only affected files (500-2,000 tokens)
7. Execute task
8. Test existing functionality (ensure no breakage)

**Example**:
```bash
/ccb:do "add user profile image upload with S3"

# Workflow:
# 1. Load PROJECT_INDEX.md (3,100 tokens)
# 2. Identify affected modules from index:
#    - src/models/user.py (add image_url field)
#    - src/api/routes/users.py (add upload endpoint)
#    - NEW: src/services/storage_service.py
# 3. Load ONLY those 2 files (800 tokens)
# 4. Implement changes
# 5. Test (functional, NO MOCKS)
# Total tokens: 3,900 (vs 58,000 without index)
```

---

## Success Criteria

**Index Quality**:
- ✅ All required sections present
- ✅ Quick Stats accurate
- ✅ Core Modules cover ≥80% of codebase
- ✅ Key Patterns identified correctly
- ✅ NO MOCKS flag present in Testing section

**Token Efficiency**:
- Token reduction: ≥90% (target: 94%)
- Generation cost: ≤5,000 tokens
- Subsequent operation savings: ≥85%
- ROI: ≥10x after 5 operations

**Accuracy**:
- Tech stack detection: ≥95% accuracy
- Module identification: ≥90% coverage
- Pattern extraction: ≥85% relevant patterns
- Dependency versions: 100% accurate

---

## References

- **Shannon Project Indexing**: [shannon-framework/skills/project-indexing](https://github.com/krzemienski/shannon-framework)
- **CCB Principles**: `.claude/core/ccb-principles.md`
- **Incremental Enhancement Skill**: `.claude/skills/incremental-enhancement/SKILL.md`

---

**End of Project Indexing**

**This completes the 6 core reference documents.**

**Next**: Implement hooks (session_start.sh, user_prompt_submit.py, post_tool_use.py, precompact.py, stop.py)
