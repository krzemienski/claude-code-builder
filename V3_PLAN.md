# Claude Code Builder v3 - Skills-Powered Architecture

> **Revolutionary Evolution**: From specification to production with intelligent, reusable Skills

## Executive Summary

v3 transforms Claude Code Builder into a **Skills-powered development platform** that combines the proven v2 architecture with Claude's Agent Skills system. This integration enables:

- **Modular, reusable expertise** via custom CCB Skills
- **Progressive disclosure** for massive specification handling (500K+ tokens)
- **Domain-specific intelligence** loaded only when needed
- **Community-driven skill marketplace** for shared best practices
- **Adaptive builds** that learn from project patterns

## Research: Claude Skills Deep Dive

### What Are Skills?

Skills are **filesystem-based capability packages** that extend Claude's functionality through:
- `SKILL.md` with YAML frontmatter (metadata + instructions)
- Optional Python scripts, templates, and reference materials
- Progressive disclosure: metadata loads always (~100 tokens), instructions load when triggered (<5K tokens), resources accessed on-demand

### How Skills Work

```
User Request → Claude evaluates skill descriptions → Matches relevant skill →
Loads SKILL.md instructions → Accesses bundled resources as needed → Executes
```

**Key Advantages:**
- **Zero upfront token cost** for resources until needed
- **Filesystem execution** - scripts run without loading code into context
- **Automatic discovery** - Claude decides when to use each skill
- **Workspace-wide sharing** via Claude API

### Skills Structure

```
my-skill/
├── SKILL.md              # Required: metadata + instructions
├── templates/            # Optional: reusable templates
├── scripts/              # Optional: Python utilities
├── examples/             # Optional: reference examples
└── resources/            # Optional: documentation, data
```

## v3 Architecture: Skills-First Design

### Core Philosophy

**v2**: Monolithic agents with embedded domain knowledge
**v3**: Lightweight orchestrator + Skills ecosystem

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Builder v3                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Skill-Aware Build Orchestrator              │  │
│  │  - Analyzes spec requirements                        │  │
│  │  - Discovers relevant skills                         │  │
│  │  - Composes multi-skill workflows                    │  │
│  │  - Progressive context management                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Skill Registry & Manager                │  │
│  │  - Built-in CCB Skills                              │  │
│  │  - User-installed Skills                            │  │
│  │  - Marketplace Skills                               │  │
│  │  - Version management                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────────┐  │
│  │ Project │ Testing │  Arch   │  Docs   │ Deployment  │  │
│  │Template │Strategy │ Pattern │ Style   │  Pipeline   │  │
│  │ Skills  │ Skills  │ Skills  │ Skills  │   Skills    │  │
│  └─────────┴─────────┴─────────┴─────────┴─────────────┘  │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Claude Agent SDK Integration                │  │
│  │  - Real SDK (no mocks)                               │  │
│  │  - Skills API (code-execution + skills betas)        │  │
│  │  - MCP servers                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 5 Core New Features

### Feature 1: Intelligent Project Templates with Skills

**Problem**: Every Python FastAPI project needs similar setup, structure, dependencies, testing config
**Solution**: Pre-built Skills that package complete project scaffolds

**How It Works:**
```bash
claude-code-builder init --template fastapi-microservice spec.md
```

The orchestrator:
1. Analyzes spec: "Build a REST API for user management"
2. Loads `python-fastapi-builder` skill
3. Skill provides: FastAPI structure, Pydantic models, SQLAlchemy setup, pytest config, Docker, OpenAPI docs
4. Generates complete, production-ready scaffold
5. Customizes based on spec requirements

**Skills Included:**
- `python-fastapi-builder` - REST APIs with FastAPI
- `python-cli-builder` - Click-based CLI tools
- `react-nextjs-builder` - Next.js web applications
- `nodejs-express-builder` - Express.js backends
- `rust-cli-builder` - Performant Rust CLIs
- `go-microservice-builder` - Go microservices
- `python-ml-builder` - ML/data science projects

**Value:**
- **10x faster scaffolding** - minutes instead of hours
- **Best practices baked in** - testing, linting, CI/CD from day 1
- **Consistent structure** - all projects follow proven patterns
- **Community contributions** - skill marketplace for templates

---

### Feature 2: Adaptive Testing Framework

**Problem**: Different projects need different testing strategies (unit, integration, E2E, performance, etc.)
**Solution**: Testing Strategy Skills that provide specialized test generation

**How It Works:**
```bash
claude-code-builder test --strategy comprehensive spec.md
```

The orchestrator:
1. Analyzes project type (API, CLI, web app, library, etc.)
2. Loads relevant testing skills:
   - `api-testing-strategy` for REST APIs
   - `ui-testing-strategy` for web UIs
   - `cli-testing-strategy` for CLI tools
   - `performance-testing-strategy` for load testing
3. Each skill provides specialized test templates
4. Generates complete test suite with real test data

**Skills Included:**
- `api-testing-strategy` - REST API tests (pytest, requests)
- `ui-testing-strategy` - Playwright E2E tests
- `cli-testing-strategy` - subprocess-based CLI tests
- `performance-testing-strategy` - Locust/K6 load tests
- `security-testing-strategy` - OWASP vulnerability tests
- `contract-testing-strategy` - Pact consumer/provider tests
- `mutation-testing-strategy` - Code coverage validation

**Value:**
- **Comprehensive coverage** - all testing levels automated
- **Real test data** - Skills include realistic fixtures
- **CI/CD ready** - Tests work in GitHub Actions, GitLab CI
- **NO MOCKS** - Real integration tests using test containers

---

### Feature 3: Architecture Decision Engine

**Problem**: Choosing between monolith, microservices, serverless, event-driven is complex
**Solution**: Architecture Pattern Skills that guide structural decisions

**How It Works:**
```bash
claude-code-builder analyze --architecture spec.md
```

The orchestrator:
1. Analyzes requirements: scale, team size, complexity, deployment
2. Loads architecture skills to evaluate options
3. Skills score fitness for each pattern
4. Recommends optimal architecture with trade-offs
5. Generates architecture decision record (ADR)
6. Applies chosen pattern skill to build structure

**Skills Included:**
- `microservices-architect` - Service decomposition, API gateway, service mesh
- `monolith-architect` - Modular monolith with clear boundaries
- `serverless-architect` - Lambda/Cloud Functions, event-driven
- `event-driven-architect` - Kafka/RabbitMQ, CQRS, event sourcing
- `hexagonal-architect` - Ports & adapters, DDD
- `clean-architect` - Clean architecture layers
- `jamstack-architect` - Static site, API backend

**Value:**
- **Data-driven decisions** - Skills evaluate based on proven heuristics
- **Trade-off analysis** - Clear pros/cons for each pattern
- **ADR generation** - Documented architectural decisions
- **Pattern enforcement** - Structure matches chosen architecture

---

### Feature 4: Multi-Stage Build Pipeline with Skill Injection

**Problem**: v2 builds are linear; real projects need iterative refinement
**Solution**: Multi-stage pipeline where Skills can be injected at any phase

**How It Works:**
```bash
claude-code-builder build spec.md \
  --pipeline "scaffold → test → security → optimize → deploy"
```

The orchestrator:
1. Parses pipeline stages
2. At each stage, evaluates which skills to load
3. Skills can be chained (output of one → input to next)
4. Checkpointing between stages
5. Human-in-the-loop review gates

**Pipeline Stages:**

```
┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Scaffold   │ -> │   Test   │ -> │ Security │ -> │ Optimize │
│   Skills    │    │  Skills  │    │  Skills  │    │  Skills  │
└─────────────┘    └──────────┘    └──────────┘    └──────────┘
                                                           ↓
┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Deploy    │ <- │   Docs   │ <- │ Validate │ <- │  Review  │
│   Skills    │    │  Skills  │    │  Skills  │    │  Skills  │
└─────────────┘    └──────────┘    └──────────┘    └──────────┘
```

**Skills by Stage:**
- **Scaffold**: Project template skills
- **Test**: Testing strategy skills
- **Security**: OWASP, dependency scanning, secrets detection
- **Optimize**: Performance profiling, bundle size, database queries
- **Review**: Code quality, complexity analysis, best practices
- **Validate**: Contract validation, API compatibility
- **Docs**: API docs, user guides, architecture diagrams
- **Deploy**: Deployment pipeline skills

**Value:**
- **Iterative refinement** - Each stage improves the previous
- **Quality gates** - Automated checks at each stage
- **Flexible workflows** - Custom pipelines per project type
- **Parallel execution** - Independent stages run concurrently

---

### Feature 5: Live Code Review & Refactoring Agent

**Problem**: Generated code needs continuous improvement as requirements evolve
**Solution**: Persistent review agent using Skills for domain-specific best practices

**How It Works:**
```bash
# Start review agent (watches project directory)
claude-code-builder review --watch ./my-project --continuous

# Or one-time review
claude-code-builder review ./my-project --skill python-code-quality
```

The orchestrator:
1. Monitors project directory for changes (or runs once)
2. On file change, loads relevant review skills
3. Skills provide language-specific, framework-specific checks
4. Generates refactoring suggestions with diffs
5. Can auto-apply with `--auto-fix` flag

**Review Skills:**
- `python-code-quality` - PEP 8, type hints, docstrings
- `python-fastapi-best-practices` - FastAPI-specific patterns
- `react-best-practices` - React hooks, component patterns
- `typescript-code-quality` - TS best practices, type safety
- `security-code-review` - Vulnerability detection
- `performance-code-review` - N+1 queries, inefficient algorithms
- `accessibility-review` - WCAG compliance for UIs

**Value:**
- **Continuous improvement** - Code evolves with the project
- **Domain expertise** - Skills encode framework-specific knowledge
- **Learning tool** - Explains why each suggestion improves code
- **Safe refactoring** - Suggests changes with test validation

---

## Custom Skills for v3

### 1. python-fastapi-builder

**File**: `~/.claude/skills/ccb-python-fastapi-builder/SKILL.md`

```markdown
---
name: ccb-python-fastapi-builder
description: Generate production-ready FastAPI REST API projects with SQLAlchemy, Pydantic, pytest, Docker, and OpenAPI documentation. Use when user requests a Python REST API, web API, or HTTP service.
---

# CCB Python FastAPI Builder

This skill generates complete FastAPI projects following best practices.

## Project Structure

```
{project_name}/
├── src/
│   └── {project_name}/
│       ├── __init__.py
│       ├── main.py              # FastAPI app
│       ├── models.py            # SQLAlchemy models
│       ├── schemas.py           # Pydantic schemas
│       ├── routers/             # API routers
│       │   ├── __init__.py
│       │   └── users.py
│       ├── services/            # Business logic
│       │   ├── __init__.py
│       │   └── user_service.py
│       ├── database.py          # DB connection
│       └── config.py            # Settings
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_api/
│   │   └── test_users.py
│   └── test_services/
│       └── test_user_service.py
├── alembic/                     # DB migrations
│   ├── versions/
│   └── env.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

## Core Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = "^2.0.25"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
alembic = "^1.13.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.4"
pytest-asyncio = "^0.23.3"
httpx = "^0.26.0"
faker = "^22.0.0"
```

## Key Patterns

### 1. Three-Layer Architecture
- **Routers**: HTTP endpoint definitions (request/response)
- **Services**: Business logic (reusable across routers)
- **Models**: Database entities (SQLAlchemy ORM)

### 2. Dependency Injection
```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id)
```

### 3. Pydantic Schemas for Validation
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### 4. Environment-Based Configuration
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")
```

### 5. Database Migrations with Alembic
- Auto-generate migrations from model changes
- Version control for schema evolution

### 6. Docker Support
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7. Comprehensive Testing
- **Unit tests**: Service layer with mocked DB
- **Integration tests**: Real DB with test containers
- **API tests**: Full request/response cycle with TestClient

## Security Best Practices

1. **Password hashing**: bcrypt via passlib
2. **JWT authentication**: python-jose for tokens
3. **Input validation**: Pydantic schemas catch malicious input
4. **SQL injection prevention**: SQLAlchemy ORM (no raw SQL)
5. **CORS configuration**: Explicit allowed origins
6. **Rate limiting**: slowapi integration
7. **Secrets management**: Environment variables, never hardcoded

## OpenAPI Documentation

FastAPI auto-generates:
- Interactive docs at `/docs` (Swagger UI)
- Alternative docs at `/redoc` (ReDoc)
- OpenAPI schema at `/openapi.json`

## When to Use This Skill

- User requests a "REST API", "web API", "HTTP service"
- Specification mentions FastAPI, Python web service
- Requirements include CRUD operations, database, authentication
- Need rapid prototyping of Python backend

## When NOT to Use

- User wants GraphQL (use `python-graphql-builder`)
- User wants CLI tool (use `python-cli-builder`)
- User wants async task processing (use `python-celery-builder`)
- User prefers Django (use `python-django-builder`)

## Generated Files Checklist

- [ ] `src/{project_name}/main.py` - FastAPI app with routers
- [ ] `src/{project_name}/models.py` - SQLAlchemy models
- [ ] `src/{project_name}/schemas.py` - Pydantic schemas
- [ ] `src/{project_name}/database.py` - DB connection
- [ ] `src/{project_name}/config.py` - Settings management
- [ ] `src/{project_name}/routers/` - API endpoints
- [ ] `src/{project_name}/services/` - Business logic
- [ ] `tests/conftest.py` - Pytest fixtures
- [ ] `tests/test_api/` - API integration tests
- [ ] `tests/test_services/` - Service unit tests
- [ ] `alembic/versions/` - Initial migration
- [ ] `Dockerfile` - Container definition
- [ ] `docker-compose.yml` - Local development
- [ ] `pyproject.toml` - Dependencies
- [ ] `.env.example` - Environment variables template
- [ ] `README.md` - Project documentation
```

### 2. react-nextjs-builder

**File**: `~/.claude/skills/ccb-react-nextjs-builder/SKILL.md`

```markdown
---
name: ccb-react-nextjs-builder
description: Generate production-ready Next.js applications with TypeScript, Tailwind CSS, React Query, Zustand state management, and comprehensive testing. Use when user requests a React web app, Next.js site, or modern frontend.
---

# CCB React Next.js Builder

This skill generates modern Next.js 14+ applications with App Router and best practices.

## Project Structure

```
{project_name}/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Home page
│   │   ├── globals.css          # Global styles
│   │   └── api/                 # API routes
│   │       └── [...]/route.ts
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   ├── features/            # Feature components
│   │   └── layout/              # Layout components
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   ├── utils.ts             # Utilities
│   │   └── hooks.ts             # Custom hooks
│   ├── stores/
│   │   └── useStore.ts          # Zustand stores
│   └── types/
│       └── index.ts             # TypeScript types
├── tests/
│   ├── unit/
│   │   └── components/
│   ├── integration/
│   │   └── api/
│   └── e2e/
│       └── playwright/
├── public/
│   ├── images/
│   └── fonts/
├── .env.local.example
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

## Core Dependencies

```json
{
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.5",
    "zod": "^3.22.4",
    "tailwindcss": "^3.4.1",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.309.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "typescript": "^5",
    "@playwright/test": "^1.41.0",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.2.0",
    "vitest": "^1.2.0",
    "eslint": "^8",
    "prettier": "^3.1.1"
  }
}
```

## Key Patterns

### 1. App Router with Server Components
```tsx
// app/page.tsx - Server Component by default
export default async function HomePage() {
  const data = await fetch('https://api.example.com/data')
  return <div>{/* Render data */}</div>
}
```

### 2. Client Components for Interactivity
```tsx
'use client'
import { useState } from 'react'

export function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

### 3. TypeScript for Type Safety
```tsx
interface User {
  id: string
  name: string
  email: string
}

interface UserCardProps {
  user: User
  onDelete?: (id: string) => void
}

export function UserCard({ user, onDelete }: UserCardProps) {
  // Component implementation
}
```

### 4. Zustand for State Management
```tsx
// stores/useAuthStore.ts
import { create } from 'zustand'

interface AuthState {
  user: User | null
  login: (user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  login: (user) => set({ user }),
  logout: () => set({ user: null }),
}))
```

### 5. React Query for Server State
```tsx
import { useQuery } from '@tanstack/react-query'

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await fetch('/api/users')
      return response.json()
    },
  })
}
```

### 6. Tailwind CSS + CVA for Styling
```tsx
import { cva } from 'class-variance-authority'

const buttonVariants = cva(
  'rounded-md font-medium transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
      },
    },
  }
)
```

### 7. Zod for Validation
```tsx
import { z } from 'zod'

const userSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().min(18),
})

type User = z.infer<typeof userSchema>
```

## Testing Strategy

### Unit Tests (Vitest + Testing Library)
```tsx
import { render, screen } from '@testing-library/react'
import { UserCard } from './UserCard'

test('renders user information', () => {
  const user = { id: '1', name: 'Alice', email: 'alice@example.com' }
  render(<UserCard user={user} />)
  expect(screen.getByText('Alice')).toBeInTheDocument()
})
```

### E2E Tests (Playwright)
```tsx
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  await page.goto('/')
  await page.click('text=Login')
  await page.fill('[name=email]', 'test@example.com')
  await page.fill('[name=password]', 'password123')
  await page.click('button[type=submit]')
  await expect(page).toHaveURL('/dashboard')
})
```

## Performance Optimizations

1. **Image Optimization**: Next.js Image component
2. **Font Optimization**: next/font with local fonts
3. **Code Splitting**: Automatic with Next.js
4. **Server Components**: Reduce client bundle size
5. **Static Generation**: ISR for dynamic content

## When to Use

- User requests React web app, Next.js site, modern frontend
- Requirements include SSR, SEO, performance
- Need TypeScript, type-safe development
- Complex state management requirements

## Generated Files Checklist

- [ ] `src/app/layout.tsx` - Root layout with providers
- [ ] `src/app/page.tsx` - Home page
- [ ] `src/components/ui/` - shadcn/ui components
- [ ] `src/lib/api.ts` - API client with Axios
- [ ] `src/stores/` - Zustand stores
- [ ] `src/types/` - TypeScript type definitions
- [ ] `tests/e2e/` - Playwright tests
- [ ] `tailwind.config.ts` - Tailwind configuration
- [ ] `next.config.js` - Next.js configuration
- [ ] `package.json` - Dependencies
- [ ] `.env.local.example` - Environment variables
- [ ] `README.md` - Documentation
```

### 3. microservices-architect

**File**: `~/.claude/skills/ccb-microservices-architect/SKILL.md`

```markdown
---
name: ccb-microservices-architect
description: Design and scaffold microservices architectures with service decomposition, API gateway, service mesh, event-driven communication, and observability. Use when requirements indicate high scale, team autonomy, or polyglot needs.
---

# CCB Microservices Architect

This skill provides guidance and scaffolding for microservices architectures.

## When to Choose Microservices

### Good Fit (Score 8+)
- **Scale**: >1M users, high traffic variance
- **Team**: 3+ autonomous teams
- **Domain**: Clear bounded contexts (DDD)
- **Technology**: Need for polyglot (different languages/frameworks)
- **Deployment**: Frequent, independent releases
- **Resilience**: Fault isolation required

### Poor Fit (Score <5)
- **Scale**: <10K users, predictable traffic
- **Team**: <5 developers
- **Domain**: Tightly coupled features
- **Technology**: Single language/framework preference
- **Deployment**: Coordinated releases acceptable
- **Complexity**: Simple CRUD application

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                      API Gateway                         │
│  (Kong, AWS API Gateway, or custom)                     │
│  - Authentication                                        │
│  - Rate limiting                                         │
│  - Request routing                                       │
└───────────┬─────────────────────────────────┬───────────┘
            │                                 │
┌───────────▼──────────┐         ┌───────────▼──────────┐
│  User Service        │         │  Product Service     │
│  - User management   │         │  - Catalog           │
│  - Authentication    │         │  - Inventory         │
│  - PostgreSQL        │         │  - PostgreSQL        │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                │
           └────────────┬───────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                Message Broker (Kafka/RabbitMQ)          │
│  - Event streaming                                       │
│  - Async communication                                   │
│  - Event sourcing (optional)                            │
└───────────┬─────────────────────────────────┬───────────┘
            │                                 │
┌───────────▼──────────┐         ┌───────────▼──────────┐
│  Order Service       │         │  Payment Service     │
│  - Order processing  │         │  - Transactions      │
│  - PostgreSQL        │         │  - PCI compliance    │
└──────────────────────┘         └──────────────────────┘
```

## Service Decomposition Strategy

### 1. Domain-Driven Design
Identify bounded contexts:
- **User Context**: Authentication, profiles, preferences
- **Product Context**: Catalog, inventory, search
- **Order Context**: Cart, checkout, fulfillment
- **Payment Context**: Transactions, refunds, billing

### 2. Service Boundaries
Each service owns:
- **Data**: Private database (database per service pattern)
- **Business Logic**: Domain rules
- **API**: RESTful or gRPC endpoints
- **Events**: Published domain events

### 3. Communication Patterns

#### Synchronous (Request/Response)
- **REST**: Simple, HTTP-based, wide tooling
- **gRPC**: High performance, strong typing, bi-directional streaming

#### Asynchronous (Event-Driven)
- **Publish/Subscribe**: Kafka, RabbitMQ for events
- **Message Queues**: SQS, RabbitMQ for commands
- **Event Sourcing**: Immutable event log as source of truth

## Infrastructure Components

### API Gateway
```yaml
# Kong configuration example
services:
  - name: user-service
    url: http://user-service:8000
    routes:
      - name: user-routes
        paths:
          - /api/users

plugins:
  - name: rate-limiting
    config:
      minute: 100
  - name: jwt
    config:
      secret_is_base64: false
```

### Service Discovery
- **Kubernetes**: Built-in service discovery with DNS
- **Consul**: Service mesh with health checks
- **Eureka**: Netflix OSS service registry

### Load Balancing
- **Client-side**: Ribbon, Spring Cloud LoadBalancer
- **Server-side**: Nginx, HAProxy, AWS ALB

### Circuit Breaker
```python
# Resilience4j-style pattern
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
def call_product_service(product_id):
    response = requests.get(f'{PRODUCT_SERVICE_URL}/products/{product_id}')
    return response.json()
```

## Observability

### 1. Logging
- **Structured Logging**: JSON format
- **Correlation IDs**: Trace requests across services
- **Centralized**: ELK Stack, Datadog, CloudWatch

```python
import structlog

log = structlog.get_logger()
log.info('order_created', order_id=order_id, user_id=user_id, correlation_id=correlation_id)
```

### 2. Metrics
- **RED Metrics**: Rate, Errors, Duration
- **Tools**: Prometheus, Grafana, Datadog

```python
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests', ['service', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['service', 'endpoint'])
```

### 3. Tracing
- **Distributed Tracing**: Jaeger, Zipkin, AWS X-Ray
- **OpenTelemetry**: Vendor-neutral instrumentation

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_order"):
    # Order processing logic
    pass
```

## Data Management Patterns

### 1. Database Per Service
- Each service has its own database
- No direct database access between services
- Data consistency via sagas or eventual consistency

### 2. Shared Database (Anti-pattern)
- ❌ Multiple services accessing same database
- ❌ Tight coupling, hard to evolve independently

### 3. Event Sourcing
- Store events, not current state
- Replay events to rebuild state
- Audit log built-in

### 4. CQRS (Command Query Responsibility Segregation)
- Separate read and write models
- Optimize each for its use case

## Deployment Strategy

### Docker Compose (Development)
```yaml
version: '3.8'
services:
  user-service:
    build: ./user-service
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - KAFKA_BROKER=kafka:9092

  product-service:
    build: ./product-service
    ports:
      - "8002:8000"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    ports:
      - "9092:9092"
```

### Kubernetes (Production)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
```

## Testing Strategy

### 1. Unit Tests
- Test individual service logic
- Mock external dependencies

### 2. Integration Tests
- Test service with real database
- Use test containers

### 3. Contract Tests (Pact)
- Verify service interactions
- Consumer-driven contracts

### 4. E2E Tests
- Test full workflows across services
- Use staging environment

## Security

### 1. Authentication
- **JWT tokens** from API gateway
- **OAuth 2.0** for third-party integrations

### 2. Authorization
- **Service-to-service**: Mutual TLS, service mesh
- **User-to-service**: RBAC, attribute-based access control

### 3. Secrets Management
- **Vault**, **AWS Secrets Manager**, **Kubernetes Secrets**

## Generated Artifacts

- [ ] Service scaffolds for each bounded context
- [ ] API Gateway configuration (Kong, AWS, custom)
- [ ] Docker Compose for local development
- [ ] Kubernetes manifests for production
- [ ] Kafka topics and consumer groups
- [ ] Prometheus metrics and Grafana dashboards
- [ ] Jaeger tracing configuration
- [ ] CI/CD pipelines per service
- [ ] Architecture Decision Records (ADRs)
- [ ] Service dependency diagram
```

### 4. test-strategy-selector

**File**: `~/.claude/skills/ccb-test-strategy-selector/SKILL.md`

```markdown
---
name: ccb-test-strategy-selector
description: Analyze project requirements and recommend comprehensive testing strategies including unit, integration, E2E, performance, and security testing. Use when generating test suites or user requests testing guidance.
---

# CCB Test Strategy Selector

This skill analyzes projects and recommends appropriate testing strategies.

## Testing Pyramid

```
        /\          E2E Tests (Few)
       /  \         - Slow, expensive, brittle
      /____\        - Full user workflows
     /      \       
    / Integ  \      Integration Tests (Some)
   /  Tests   \     - Medium speed, moderate cost
  /____________\    - Service interactions
 /              \   
/  Unit  Tests  \   Unit Tests (Many)
/________________\  - Fast, cheap, focused
                    - Pure logic
```

## Project Type Analysis

### Web API / REST Service
**Primary Focus**: Integration > Unit > E2E
**Test Strategy**:
- **Unit Tests** (60%): Business logic, validation, utilities
- **Integration Tests** (30%): Database operations, API endpoints
- **E2E Tests** (10%): Critical workflows (auth, core features)

**Recommended Tools**:
- **Python**: pytest, pytest-asyncio, httpx, Faker
- **Node.js**: Jest, Supertest, Faker.js
- **Database**: pytest-postgresql, Testcontainers
- **Mocking**: unittest.mock (minimal), prefer real dependencies

**Example Structure**:
```
tests/
├── unit/
│   ├── test_services/
│   ├── test_models/
│   └── test_utils/
├── integration/
│   ├── test_api/
│   ├── test_database/
│   └── conftest.py       # Fixtures
└── e2e/
    └── test_workflows/
```

### CLI Application
**Primary Focus**: Functional > Unit > Integration
**Test Strategy**:
- **Unit Tests** (50%): Command logic, parsers, formatters
- **Functional Tests** (40%): Command execution, output validation
- **Integration Tests** (10%): File I/O, external APIs

**Recommended Tools**:
- **Python**: pytest, click.testing.CliRunner
- **subprocess**: Test actual CLI invocation
- **Golden files**: Compare output snapshots

**Example**:
```python
from click.testing import CliRunner
from myapp.cli import cli

def test_version_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert 'version 1.0.0' in result.output
```

### Web Frontend (React/Next.js)
**Primary Focus**: Component > E2E > Integration
**Test Strategy**:
- **Component Tests** (50%): Rendering, interactions, state
- **E2E Tests** (30%): User workflows, navigation
- **Integration Tests** (20%): API calls, data fetching

**Recommended Tools**:
- **Component**: Vitest, Testing Library, MSW
- **E2E**: Playwright, Cypress
- **Visual**: Percy, Chromatic for visual regression

**Example**:
```tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Counter } from './Counter'

test('increments counter', () => {
  render(<Counter />)
  const button = screen.getByRole('button')
  fireEvent.click(button)
  expect(screen.getByText('1')).toBeInTheDocument()
})
```

### Microservices
**Primary Focus**: Contract > Integration > E2E
**Test Strategy**:
- **Unit Tests** (40%): Service logic
- **Integration Tests** (30%): Database, message brokers
- **Contract Tests** (20%): Pact for service interactions
- **E2E Tests** (10%): Critical cross-service workflows

**Recommended Tools**:
- **Contract**: Pact, Spring Cloud Contract
- **Integration**: Testcontainers for dependencies
- **E2E**: Postman, K6 for API testing

### Library / SDK
**Primary Focus**: Unit > Integration > Examples
**Test Strategy**:
- **Unit Tests** (70%): Public API, edge cases
- **Integration Tests** (20%): Real usage scenarios
- **Example Tests** (10%): Documentation examples work

**Recommended Tools**:
- **Property-based**: Hypothesis (Python), fast-check (TS)
- **Coverage**: Aim for >90% for public APIs

## Testing Anti-Patterns to Avoid

### ❌ Over-Mocking
**Problem**: Mocking everything means tests pass but code breaks
**Solution**: Use real dependencies via Testcontainers

### ❌ Testing Implementation Details
**Problem**: Tests break on refactoring, not behavior changes
**Solution**: Test public API, not internal methods

### ❌ Flaky Tests
**Problem**: Tests pass/fail randomly
**Solution**: Avoid sleeps, use deterministic waits, isolate tests

### ❌ Slow Test Suites
**Problem**: >10 min test runs block development
**Solution**: Parallelize, optimize DB setup, use in-memory DBs

## Test Data Management

### Fixtures (pytest)
```python
import pytest
from faker import Faker

fake = Faker()

@pytest.fixture
def user():
    return {
        'id': fake.uuid4(),
        'name': fake.name(),
        'email': fake.email(),
    }

def test_user_creation(user):
    # Test using realistic data
    pass
```

### Factory Pattern
```python
from faker import Faker

class UserFactory:
    def __init__(self):
        self.fake = Faker()
    
    def create_user(self, **overrides):
        defaults = {
            'name': self.fake.name(),
            'email': self.fake.email(),
            'age': self.fake.random_int(18, 80),
        }
        return {**defaults, **overrides}
```

## Performance Testing

### Load Testing (K6)
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Steady state
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests < 500ms
  },
};

export default function () {
  let response = http.get('https://api.example.com/users');
  check(response, {
    'status is 200': (r) => r.status === 200,
  });
}
```

## Security Testing

### OWASP Dependency Check
```bash
# Check for vulnerable dependencies
safety check
npm audit
pip-audit
```

### SQL Injection Prevention
```python
# ❌ Vulnerable
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ Safe (ORM)
user = db.query(User).filter(User.email == email).first()

# ✅ Safe (parameterized)
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Coverage Goals

| Project Type | Target Coverage | Critical Paths |
|--------------|----------------|----------------|
| Library/SDK  | >90%           | Public API 100% |
| Web API      | >80%           | Auth/Payment 100% |
| CLI Tool     | >75%           | Core commands 90% |
| Frontend     | >70%           | Critical flows 90% |
| Microservice | >80%           | Integration 100% |

## When to Use This Skill

- User requests testing strategy or test generation
- Building test suite for new project
- Evaluating existing test coverage
- Migrating from one testing approach to another

## Output Checklist

- [ ] Test strategy recommendation with rationale
- [ ] Test pyramid distribution (unit/integration/E2E %)
- [ ] Recommended tools and frameworks
- [ ] Test file structure
- [ ] CI/CD integration examples
- [ ] Coverage goals and critical paths
- [ ] Common pitfalls to avoid for this project type
```

### 5. deployment-pipeline-generator

**File**: `~/.claude/skills/ccb-deployment-pipeline-generator/SKILL.md`

```markdown
---
name: ccb-deployment-pipeline-generator
description: Generate complete CI/CD pipelines for GitHub Actions, GitLab CI, AWS, GCP, Azure, Docker, and Kubernetes. Includes build, test, security scanning, and multi-environment deployment. Use when deploying projects or setting up automation.
---

# CCB Deployment Pipeline Generator

This skill generates production-ready deployment pipelines.

## Pipeline Stages

```
┌─────────┐   ┌──────┐   ┌──────────┐   ┌─────┐   ┌────────┐
│ Trigger │ → │ Build│ → │   Test   │ → │Scan │ → │ Deploy │
│(push/PR)│   │      │   │Unit/Int/ │   │Sec/ │   │Dev/Stg/│
│         │   │      │   │   E2E    │   │Lint │   │  Prod  │
└─────────┘   └──────┘   └──────────┘   └─────┘   └────────┘
```

## GitHub Actions Pipeline

### Python FastAPI Project

**File**: `.github/workflows/deploy.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ─────────────────────────────────────────────────────────
  # Job 1: Code Quality & Security
  # ─────────────────────────────────────────────────────────
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Lint with Ruff
        run: poetry run ruff check .
      
      - name: Format check with Black
        run: poetry run black --check .
      
      - name: Type check with MyPy
        run: poetry run mypy src/
      
      - name: Security scan with Bandit
        run: poetry run bandit -r src/
      
      - name: Dependency vulnerability check
        run: poetry run safety check

  # ─────────────────────────────────────────────────────────
  # Job 2: Tests
  # ─────────────────────────────────────────────────────────
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run unit tests
        run: poetry run pytest tests/unit -v
      
      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
        run: poetry run pytest tests/integration -v
      
      - name: Run E2E tests
        run: poetry run pytest tests/e2e -v
      
      - name: Generate coverage report
        run: |
          poetry run pytest --cov=src --cov-report=xml --cov-report=html
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  # ─────────────────────────────────────────────────────────
  # Job 3: Build Docker Image
  # ─────────────────────────────────────────────────────────
  build:
    needs: [quality, test]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ─────────────────────────────────────────────────────────
  # Job 4: Deploy to Development
  # ─────────────────────────────────────────────────────────
  deploy-dev:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment:
      name: development
      url: https://dev.example.com
    
    steps:
      - name: Deploy to Kubernetes (Dev)
        run: |
          # Set up kubectl
          echo "${{ secrets.KUBECONFIG_DEV }}" > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml
          
          # Update deployment
          kubectl set image deployment/myapp \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:develop
          
          # Wait for rollout
          kubectl rollout status deployment/myapp
      
      - name: Run smoke tests
        run: |
          curl -f https://dev.example.com/health || exit 1

  # ─────────────────────────────────────────────────────────
  # Job 5: Deploy to Staging
  # ─────────────────────────────────────────────────────────
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    
    steps:
      - name: Deploy to Kubernetes (Staging)
        run: |
          echo "${{ secrets.KUBECONFIG_STAGING }}" > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml
          kubectl set image deployment/myapp \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:main
          kubectl rollout status deployment/myapp
      
      - name: Run integration tests against staging
        run: |
          # Run full test suite against staging
          pytest tests/e2e --base-url=https://staging.example.com

  # ─────────────────────────────────────────────────────────
  # Job 6: Deploy to Production (Manual Approval)
  # ─────────────────────────────────────────────────────────
  deploy-prod:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    
    steps:
      - name: Deploy to Kubernetes (Production)
        run: |
          echo "${{ secrets.KUBECONFIG_PROD }}" > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml
          
          # Blue-green deployment
          kubectl set image deployment/myapp-blue \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:main
          kubectl rollout status deployment/myapp-blue
          
          # Switch traffic
          kubectl patch service myapp -p '{"spec":{"selector":{"version":"blue"}}}'
      
      - name: Verify deployment
        run: |
          curl -f https://example.com/health || exit 1
      
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Production deployment successful! 🚀"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Docker Configuration

### Multi-Stage Dockerfile

```dockerfile
# ═══════════════════════════════════════════════════════════
# Stage 1: Builder
# ═══════════════════════════════════════════════════════════
FROM python:3.11-slim as builder

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (no dev dependencies)
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-dev --no-interaction --no-ansi

# ═══════════════════════════════════════════════════════════
# Stage 2: Runtime
# ═══════════════════════════════════════════════════════════
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Add virtualenv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml (Local Development)

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./src:/app/src  # Hot reload
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=myapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Kubernetes Deployment

### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: ghcr.io/myorg/myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## AWS Deployment (Terraform)

### main.tf

```hcl
# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "myapp-cluster"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "myapp"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([{
    name  = "myapp"
    image = "ghcr.io/myorg/myapp:latest"
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    environment = [
      {
        name  = "DATABASE_URL"
        value = var.database_url
      }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/myapp"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# ECS Service
resource "aws_ecs_service" "main" {
  name            = "myapp-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 3
  launch_type     = "FARGATE"

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "myapp"
    container_port   = 8000
  }

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.ecs_tasks.id]
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "myapp-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids
}

resource "aws_lb_target_group" "app" {
  name     = "myapp-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 10
  }
}
```

## Platform-Specific Pipelines

### GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install poetry
    - poetry install
    - poetry run pytest

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/myapp myapp=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### Azure DevOps
```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: Test
  jobs:
  - job: RunTests
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.11'
    - script: |
        pip install poetry
        poetry install
        poetry run pytest

- stage: Build
  jobs:
  - job: BuildDocker
    steps:
    - task: Docker@2
      inputs:
        command: buildAndPush
        repository: myapp
        containerRegistry: $(dockerRegistryServiceConnection)
```

## Security Scanning

### Trivy (Container Scanning)
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload Trivy results to GitHub Security
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: 'trivy-results.sarif'
```

## Monitoring & Observability

### DataDog Integration
```yaml
- name: Deploy with DataDog APM
  run: |
    kubectl set env deployment/myapp \
      DD_AGENT_HOST=datadog-agent \
      DD_SERVICE=myapp \
      DD_ENV=production \
      DD_VERSION=${{ github.sha }}
```

## Generated Artifacts Checklist

- [ ] GitHub Actions workflow (multi-environment)
- [ ] Dockerfile (multi-stage, optimized)
- [ ] docker-compose.yml (local development)
- [ ] Kubernetes manifests (deployment, service, HPA)
- [ ] Terraform configuration (cloud infrastructure)
- [ ] Security scanning integration
- [ ] Monitoring/observability setup
- [ ] Rollback procedures
- [ ] Environment-specific configurations
- [ ] Secrets management setup
```

## Impact Analysis: How Skills + 5 Features Transform CCB

### 1. Development Speed: 5-10x Faster

**Before v3**:
- Specification → Code: 2-4 hours per module
- Manual decisions at each step
- Regenerating common patterns repeatedly

**After v3**:
- Specification → Production scaffold: 10-20 minutes
- Skills provide instant expertise
- Templates eliminate repetitive generation

**Example**:
```bash
# v2: Manual spec writing, iterative generation
claude-code-builder build api-spec.md --output-dir ./api
# Result: 3 hours for basic FastAPI scaffold

# v3: Skills-powered instant scaffolding
claude-code-builder init --template fastapi-microservice "Build user management API" --output-dir ./api
# Result: 15 minutes for production-ready API with tests, Docker, K8s, CI/CD
```

### 2. Quality: Production-Ready from Day 1

**Before v3**:
- Testing strategies ad-hoc
- Security as afterthought
- Deployment pipelines added later

**After v3**:
- Skills encode best practices
- Security baked in (OWASP, dependency scanning)
- Full CI/CD from first commit

**Example**:
```bash
# v3 automatically includes:
✓ pytest with 80%+ coverage
✓ Docker multi-stage builds (security)
✓ Kubernetes deployment with HPA
✓ GitHub Actions with security scanning
✓ Secrets management with Vault/K8s Secrets
✓ Observability (Prometheus, Datadog)
```

### 3. Context Efficiency: 500K+ Token Specifications

**Before v3 (v2 limitations)**:
- Context: ~150K tokens (Opus 4 extended)
- Large specs need manual chunking
- Context overflow on complex projects

**After v3 (Skills progressive disclosure)**:
- Metadata: ~100 tokens per skill (always loaded)
- Instructions: <5K tokens per skill (when triggered)
- Resources: 0 tokens (filesystem access)
- **Effective capacity: 500K+ tokens**

**Example**:
```
User: "Build a complete e-commerce platform"

v2: Loads entire architecture knowledge into context (80K tokens)
    CONTEXT OVERFLOW after 2-3 agents

v3: Loads skill metadata (2K tokens)
    When needed, loads:
    - python-fastapi-builder instructions (3K tokens)
    - microservices-architect instructions (4K tokens)
    - deployment-pipeline-generator instructions (3K tokens)
    Total: 12K tokens, resources accessed on-demand
    NO CONTEXT OVERFLOW, handles massive specs
```

### 4. Customization: Community Marketplace

**Before v3**:
- Monolithic agents
- Customization requires forking CCB
- No sharing of domain expertise

**After v3**:
- Skills marketplace
- Users create/share/install skills
- Domain experts package their knowledge

**Example Marketplace**:
```
Community Skills:
├── Healthcare
│   ├── hipaa-compliant-api (HIPAA regulations built-in)
│   ├── hl7-fhir-builder (Healthcare data formats)
│   └── medical-device-software (FDA guidelines)
├── Finance
│   ├── pci-dss-compliant-api (Payment card security)
│   ├── sox-compliance-builder (Sarbanes-Oxley)
│   └── fintech-blockchain (Crypto/blockchain patterns)
└── Gaming
    ├── unity-game-builder (C# Unity projects)
    ├── unreal-cpp-builder (C++ Unreal projects)
    └── multiplayer-netcode (Networking patterns)

Install with:
$ claude-code-builder skills install hipaa-compliant-api
$ claude-code-builder build medical-app-spec.md --skills hipaa-compliant-api
```

### 5. Learning & Documentation: Self-Improving System

**Before v3**:
- Static documentation
- No learning from builds
- Patterns not captured

**After v3**:
- Skills document "why" not just "how"
- Builds generate ADRs (Architecture Decision Records)
- Skills version controlled and evolve

**Example**: Architecture Decision Record (Auto-Generated)

```markdown
# ADR 001: Microservices Architecture

## Status
Accepted

## Context
Requirements indicate:
- Expected scale: 1M+ users
- Team structure: 4 independent teams
- Domain: E-commerce with clear bounded contexts (User, Product, Order, Payment)

**Microservices Fitness Score**: 9/10
- Scale: 10/10 (high traffic, need horizontal scaling)
- Team: 9/10 (multiple teams, benefit from autonomy)
- Domain: 10/10 (clear bounded contexts)
- Complexity: 7/10 (added operational complexity acceptable for scale)

## Decision
Use **microservices architecture** based on ccb-microservices-architect skill.

Architecture:
- User Service (FastAPI, PostgreSQL)
- Product Service (FastAPI, PostgreSQL)
- Order Service (FastAPI, PostgreSQL, Kafka)
- Payment Service (FastAPI, PostgreSQL, Kafka, PCI-DSS)

Communication:
- Synchronous: REST for read operations
- Asynchronous: Kafka for domain events

## Consequences
**Positive**:
- Independent scaling per service
- Team autonomy (deploy independently)
- Fault isolation
- Polyglot possible (but starting with Python)

**Negative**:
- Increased operational complexity
- Distributed data management
- Network latency between services

**Mitigations**:
- Kubernetes for orchestration
- API Gateway for routing
- Observability (Jaeger tracing, Prometheus metrics)
- Contract testing (Pact) for service interactions

## Generated By
CCB v3 microservices-architect skill (v1.2.0)
```

### 6. Cost Optimization: Pay for Results, Not Exploration

**Before v3**:
- Every build explores patterns from scratch
- High API costs for repetitive tasks
- Token waste on common patterns

**After v3**:
- Skills cache expertise
- Progressive disclosure minimizes token usage
- Focus API calls on customization, not boilerplate

**Cost Comparison**:
```
Build "Python FastAPI API with auth, DB, tests, Docker, K8s, CI/CD"

v2:
- Spec analysis: 50K tokens ($0.75)
- Architecture exploration: 80K tokens ($1.20)
- Code generation: 200K tokens ($3.00)
- Testing strategy: 40K tokens ($0.60)
- Deployment setup: 60K tokens ($0.90)
TOTAL: 430K tokens, $6.45

v3:
- Skill discovery: 2K tokens ($0.03)
- python-fastapi-builder: 3K tokens ($0.045)
- test-strategy-selector: 2K tokens ($0.03)
- deployment-pipeline-generator: 3K tokens ($0.045)
- Customization: 20K tokens ($0.30)
TOTAL: 30K tokens, $0.45

SAVINGS: 93% cost reduction, 14x cheaper
```

## v3 CLI Usage Examples

### Quick Start
```bash
# Install v3
pip install claude-code-builder --upgrade

# List available templates
claude-code-builder skills list --category templates

# Generate FastAPI project
claude-code-builder init \
  --template fastapi-microservice \
  "Build a REST API for task management with auth" \
  --output-dir ./task-api

# Result:
✓ Project scaffolded (15s)
✓ Tests generated (pytest, 85% coverage)
✓ Docker + K8s configs generated
✓ CI/CD pipeline (GitHub Actions)
✓ Documentation (README, API docs, ADRs)

# Analyze architecture fitness
claude-code-builder analyze --architecture ecommerce-spec.md
# Output: Recommends microservices (score: 9/10) with rationale

# Multi-stage build with custom pipeline
claude-code-builder build spec.md \
  --pipeline "scaffold → test → security → optimize → deploy" \
  --stages.security.skills owasp-scanner,secrets-detector \
  --stages.optimize.skills bundle-analyzer,db-query-optimizer

# Live code review (continuous)
claude-code-builder review --watch ./my-project --continuous \
  --skills python-code-quality,fastapi-best-practices,security-code-review

# Install community skill
claude-code-builder skills install hipaa-compliant-api --marketplace

# Create custom skill
claude-code-builder skills create \
  --name my-company-django-builder \
  --description "Our company's Django project template with custom auth" \
  --template company-template
```

## Conclusion: v3 Vision

Claude Code Builder v3 transforms from a **code generator** to a **knowledge-powered development platform**:

### Key Innovations
1. **Skills Marketplace**: Community expertise, packaged and reusable
2. **Progressive Disclosure**: Massive specifications (500K+) via intelligent loading
3. **Production-First**: Security, testing, deployment from day 1
4. **Adaptive Pipelines**: Custom workflows per project type
5. **Continuous Improvement**: Live review agent, ADR generation

### Impact
- **10x faster development**: Minutes instead of hours for scaffolds
- **Higher quality**: Best practices encoded in skills
- **Lower costs**: 93% cost reduction via skills caching
- **Community-driven**: Share expertise via marketplace
- **Self-improving**: Skills version controlled and evolve

### Next Steps for v3 Implementation
1. **Phase 1** (Months 1-2): Skills infrastructure and registry
2. **Phase 2** (Months 2-3): Core 5 skills (FastAPI, Next.js, microservices, testing, deployment)
3. **Phase 3** (Months 3-4): Multi-stage pipeline orchestrator
4. **Phase 4** (Months 4-5): Live review agent
5. **Phase 5** (Months 5-6): Skills marketplace and community

**v3 makes the promise real**: *From specification to production with minimal human intervention.*
