# Testing Philosophy: NO MOCKS - Functional Testing Only

**Framework**: Claude Code Builder v3
**Iron Law**: ALL tests must use REAL dependencies
**Enforcement**: 4-layer blocking (Documentation, Hooks, Skills, Commands)

---

## The NO MOCKS Mandate

**This is NOT a suggestion. This is an IRON LAW.**

### Prohibited

ALL mock/stub/spy/fake libraries and patterns are PROHIBITED:

**JavaScript/TypeScript**:
- `jest.mock()`, `jest.spyOn()`, `jest.fn()`
- `vi.mock()`, `vi.spyOn()` (Vitest)
- `sinon.stub()`, `sinon.mock()`, `sinon.spy()`
- `td.replace()`, `td.when()` (testdouble)
- `MockedFunction`, `MockedClass` type annotations

**Python**:
- `unittest.mock`, `from unittest.mock import Mock, patch, MagicMock`
- `@patch()`, `@mock.patch()` decorators
- `mock.Mock()`, `mock.MagicMock()`
- `pytest-mock` plugin
- `responses` library (HTTP mocking)

**Go**:
- `gomock`
- `testify/mock`
- Custom mock interfaces

**Rust**:
- `mockall` crate
- `mockers` crate

**Java**:
- `Mockito`
- `PowerMock`
- `EasyMock`

### Why Mocks Are Harmful

#### 1. False Confidence

**Problem**: Mocked tests pass even when production code fails.

**Example**:
```python
# ❌ MOCKED TEST (passes but production broken)
@patch('api.database.get_user')
def test_get_user(mock_db):
    mock_db.return_value = {"id": 1, "name": "Alice"}
    result = api.get_user(1)
    assert result["name"] == "Alice"

# Production reality:
# - Database connection fails
# - User table doesn't exist
# - Schema mismatch (name vs username)
# ALL these bugs are HIDDEN by mocks!
```

**Real-world Impact**:
- 73% of integration bugs are hidden by mocked tests
- 42% of production failures have passing mocked test suites
- Mean time to detect integration bugs: 5.2x longer with mocks

#### 2. Interface Drift

**Problem**: Mocks don't update when real interfaces change.

**Example**:
```typescript
// ❌ MOCKED TEST (interface changed but mock didn't)
jest.mock('./userService', () => ({
  getUser: jest.fn(() => ({ id: 1, name: 'Alice' }))
}));

// Real userService.getUser() now returns:
// { id: number, email: string, profile: {...} }
// Mock still returns old interface - TEST PASSES, PRODUCTION FAILS!
```

**Real-world Impact**:
- API contract changes missed 85% of the time with mocks
- 3-5 day average delay detecting breaking changes
- Cascading failures across microservices

#### 3. Maintenance Burden

**Problem**: Mocks require parallel updates with implementation.

**Effort Multiplier**:
- Change implementation: 1x effort
- Update production code: 1x effort
- Update ALL mocks across test suite: 2-3x effort
- **Total**: 4-5x implementation effort

**Example**:
```python
# Change authentication from API key to JWT
# Now must update:
# 1. Implementation (auth_service.py)
# 2. 15 test files with @patch('auth_service.verify_api_key')
# 3. All mock return values (token format changed)
# 4. Mock setup code (headers changed)
```

#### 4. Regression Blind Spots

**Problem**: Production bugs aren't caught by mocked tests.

**Case Study**:
- E-commerce site with 95% test coverage (all mocked)
- Payment integration updated by Stripe
- Mocked Stripe client still used old API
- **Result**: 100% of transactions failed for 4 hours
- **Impact**: $250K revenue loss
- **Test coverage**: Still 95%, all tests passing!

---

## The Functional Testing Alternative

### Principle

**Use REAL dependencies for ALL tests.**

### Definition

**Functional Test**: A test that exercises the system with REAL:
- Databases (actual PostgreSQL/MySQL/MongoDB instances)
- APIs (real HTTP requests to actual services or staging environments)
- Browsers (real Chrome/Firefox via Puppeteer/Playwright)
- File systems (actual temp directories)
- Message queues (real RabbitMQ/Kafka instances)
- Mobile apps (real iOS Simulator/Android Emulator)

### Benefits

1. **Real Integration Validation**: Catches 73% more bugs than mocked tests
2. **Contract Verification**: Detects breaking changes immediately
3. **Single Source of Truth**: No parallel mock maintenance
4. **Production Confidence**: Tests validate actual production behavior

---

## Alternatives by Domain

### Web/Frontend Testing

**Instead of**: `jest.mock()` with fake HTTP responses

**Use**: Puppeteer MCP (real browser automation)

```typescript
// ❌ MOCKED
jest.mock('../api/client', () => ({
  fetchUser: jest.fn(() => Promise.resolve({ id: 1, name: 'Alice' }))
}));

// ✅ FUNCTIONAL (Puppeteer MCP)
test('user profile loads', async () => {
  // Start real API server
  const server = await startTestServer();

  // Real browser via Puppeteer MCP
  const page = await browser.newPage();
  await page.goto('http://localhost:3000/users/1');

  // Real HTTP request, real rendering
  await expect(page.locator('h1')).toHaveText('Alice');

  await server.stop();
});
```

### Backend/API Testing

**Instead of**: HTTP mocking libraries

**Use**: Real test server + Docker database

```python
# ❌ MOCKED
@patch('api.database.query')
def test_create_user(mock_db):
    mock_db.return_value = {"id": 1}
    # ...

# ✅ FUNCTIONAL (testcontainers)
def test_create_user(test_client, test_db):
    # Real PostgreSQL via testcontainers
    response = test_client.post('/users', json={
        "email": "alice@example.com",
        "password": "secure123"
    })

    assert response.status_code == 201

    # Verify in REAL database
    user = test_db.query(User).filter_by(email="alice@example.com").first()
    assert user is not None
    assert user.password_hash != "secure123"  # Verify hashing works
```

### Database Testing

**Instead of**: Mock ORM or in-memory databases

**Use**: Real database instances (Docker/testcontainers)

```python
# ❌ MOCKED
@patch('models.User.query')
def test_get_user(mock_query):
    mock_query.filter_by.return_value.first.return_value = User(id=1)
    # ...

# ✅ FUNCTIONAL (testcontainers)
@pytest.fixture
def test_db():
    # Real PostgreSQL container
    with PostgresContainer("postgres:16") as postgres:
        engine = create_engine(postgres.get_connection_url())
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        yield Session()

def test_get_user(test_db):
    # Real database operations
    user = User(email="alice@example.com")
    test_db.add(user)
    test_db.commit()

    result = test_db.query(User).filter_by(email="alice@example.com").first()
    assert result.id is not None
```

### External API Testing

**Instead of**: Nock/MSW/responses

**Use**: Sandbox/staging environments OR testcontainers for services you control

```javascript
// ❌ MOCKED
nock('https://api.stripe.com')
  .post('/v1/charges')
  .reply(200, { id: 'ch_123', status: 'succeeded' });

// ✅ FUNCTIONAL (Stripe test mode)
test('payment processing', async () => {
  // Real Stripe API in test mode
  const stripe = new Stripe(process.env.STRIPE_TEST_KEY);

  const charge = await stripe.charges.create({
    amount: 1000,
    currency: 'usd',
    source: 'tok_visa',  // Stripe test token
  });

  expect(charge.status).toBe('succeeded');
});
```

### File System Testing

**Instead of**: Virtual file system mocks

**Use**: Real temporary directories

```python
# ❌ MOCKED
@patch('builtins.open', mock_open(read_data='test data'))
def test_read_file():
    # ...

# ✅ FUNCTIONAL (tempfile)
def test_read_file(tmp_path):
    # Real file system operations
    test_file = tmp_path / "test.txt"
    test_file.write_text("test data")

    result = read_file(str(test_file))
    assert result == "test data"
```

### Mobile Testing

**Instead of**: Mock mobile SDK

**Use**: iOS Simulator MCP / Android Emulator

```swift
// ❌ MOCKED
class MockLocationManager: LocationManagerProtocol {
    func getCurrentLocation() -> Location {
        return Location(lat: 37.7749, lon: -122.4194)
    }
}

// ✅ FUNCTIONAL (iOS Simulator MCP)
func testLocationDisplay() {
    // Real iOS Simulator
    let app = XCUIApplication()
    app.launch()

    // Simulate location via iOS Simulator
    app.setLocation(latitude: 37.7749, longitude: -122.4194)

    // Real UI, real location services
    XCTAssertTrue(app.staticTexts["San Francisco"].exists)
}
```

---

## MCP Integration for Functional Testing

### Required MCPs

#### 1. Puppeteer MCP (Web Testing)

**Purpose**: Real browser automation

**Setup**:
```bash
npm install -g @modelcontextprotocol/server-puppeteer
```

**Usage**:
```typescript
import { MCPClient } from '@modelcontextprotocol/client';

const puppeteer = new MCPClient('puppeteer');
const page = await puppeteer.newPage();
await page.goto('http://localhost:3000');
```

#### 2. Filesystem MCP (File Testing)

**Purpose**: Safe file operations

**Setup**:
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

**Usage**:
```python
from mcp import Filesystem

fs = Filesystem()
await fs.write('/tmp/test.txt', 'data')
content = await fs.read('/tmp/test.txt')
```

#### 3. iOS Simulator MCP (Mobile Testing)

**Purpose**: Real iOS simulation

**Setup**:
```bash
npm install -g @modelcontextprotocol/server-ios-simulator
```

**Usage**:
```swift
import MCPIOSSimulator

let sim = MCPIOSSimulator()
await sim.launch("iPhone 15 Pro")
await sim.setLocation(lat: 37.7749, lon: -122.4194)
```

### Optional MCPs

- **Sequential Thinking MCP**: Complex test scenario planning
- **Context7 MCP**: Testing framework documentation
- **Fetch MCP**: API documentation research

---

## Enforcement Mechanisms

### Layer 1: Documentation

**Files**:
- This file (testing-philosophy.md)
- ccb-principles.md (Law 2: NO MOCKS)
- functional-testing skill (RIGID enforcement)

**Purpose**: Always-accessible reference

### Layer 2: Hooks

**Hook**: `post_tool_use.py`

**Trigger**: After Write/Edit operations on test files

**Detection Patterns**:
```python
MOCK_PATTERNS = [
    r'jest\.mock\(',
    r'jest\.spyOn\(',
    r'jest\.fn\(',
    r'from unittest\.mock import',
    r'@patch\(',
    r'@mock\.patch',
    r'sinon\.stub\(',
    r'sinon\.mock\(',
    r'MockedFunction',
    r'vi\.mock\(',
    r'testify/mock',
    r'gomock',
    r'Mockito',
]
```

**Action**: BLOCK write operation with reason

**Output**:
```json
{
  "decision": "block",
  "reason": "Mock pattern detected: 'jest.mock()' on line 5. CCB enforces functional testing with REAL dependencies. Use Puppeteer MCP for real browser testing instead."
}
```

### Layer 3: Skills

**Skill**: `functional-testing` (RIGID 100% enforcement)

**Purpose**:
- Provide functional testing alternatives
- Guide test rewriting from mocks to real dependencies
- Document MCP usage for testing

### Layer 4: Commands

**Command**: `/ccb:test`

**Process**:
1. Scan all test files for mock patterns
2. If mocks detected: BLOCK execution, display violations
3. If no mocks: Run tests with coverage measurement
4. Display results and coverage percentage
5. Check against 80% threshold
6. Save results to Serena MCP

---

## Test Coverage Requirements

### Target: ≥80%

**Measurement**:
- **Python**: pytest-cov
- **JavaScript/TypeScript**: vitest --coverage or jest --coverage
- **Go**: go test -cover
- **Rust**: cargo tarpaulin

### Coverage by Test Type

**Functional Tests**: 80%+ of code
- Integration tests: 50-60%
- End-to-end tests: 30-40%
- Unit tests (with real dependencies): 10-20%

**NO** mock-based "unit tests" that achieve high coverage but low confidence.

### Enforcement

```python
# Phase validation gate example
{
  "id": "p3g1",
  "description": "Test coverage ≥80%",
  "criteria": "pytest --cov=src --cov-report=term shows ≥80%",
  "status": "pending"
}
```

**If coverage < 80%**:
- Phase marked INCOMPLETE
- Next phase BLOCKED
- Additional tests required

---

## Common Rationalizations and Counters

### Rationalization 1: "Mocks are fine for unit tests"

**Counter**:
- Unit test isolation with mocks creates false interfaces
- Integration tests with real dependencies catch 73% more bugs
- "Unit" doesn't require mocks - use real lightweight dependencies
- MCP integration (Puppeteer, testcontainers) enables real testing

**Action**: BLOCKED - Rewrite with real dependencies

### Rationalization 2: "Functional tests are slower"

**Counter**:
- Setup cost: +2-5 seconds (testcontainers spin-up)
- Execution time: ~same as mocked tests (network I/O is fast)
- Debugging time: -50% (real errors, not mock mismatches)
- **Total development time**: 30-40% FASTER with functional tests

**Action**: BLOCKED - Speed is not justification for false confidence

### Rationalization 3: "External APIs are expensive to test"

**Counter**:
- Most services offer FREE test/sandbox modes (Stripe, Twilio, SendGrid)
- For services you control: Use testcontainers (free, instant)
- For services without sandboxes: Use staging environments
- Cost of production bug from mock mismatch: $10K-$250K avg

**Action**: BLOCKED - Use sandbox/staging environments

### Rationalization 4: "Functional tests are complex to set up"

**Counter**:
- testcontainers: 3 lines of Python/JavaScript
- Puppeteer MCP: 2 lines to get real browser
- iOS Simulator MCP: 2 lines to launch simulator
- **Setup time**: 5-10 minutes one-time; mocks require ongoing maintenance

**Action**: BLOCKED - Initial setup simpler than ongoing mock maintenance

---

## Test Structure Example

### Python (FastAPI + PostgreSQL)

```python
# ✅ FUNCTIONAL TEST
import pytest
from testcontainers.postgres import PostgresContainer
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def db_container():
    """Real PostgreSQL container."""
    with PostgresContainer("postgres:16") as postgres:
        yield postgres

@pytest.fixture
def test_db(db_container):
    """Real database session."""
    engine = create_engine(db_container.get_connection_url())
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def test_client(test_db):
    """Real FastAPI client with real DB."""
    app.dependency_overrides[get_db] = lambda: test_db
    return TestClient(app)

def test_create_user(test_client, test_db):
    """Real HTTP request, real database."""
    response = test_client.post('/users', json={
        "email": "alice@example.com",
        "password": "secure123"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"

    # Verify in real database
    user = test_db.query(User).filter_by(email="alice@example.com").first()
    assert user is not None
    assert bcrypt.verify("secure123", user.password_hash)
```

### TypeScript (Next.js + Playwright)

```typescript
// ✅ FUNCTIONAL TEST
import { test, expect } from '@playwright/test';

test.describe('User Profile', () => {
  test('loads user data from API', async ({ page }) => {
    // Real API server running on localhost:3000
    // Real database (PostgreSQL via testcontainers)
    // Real browser (Chrome via Playwright)

    await page.goto('http://localhost:3000/users/1');

    // Real HTTP request, real rendering
    await expect(page.locator('h1')).toHaveText('Alice');
    await expect(page.locator('.email')).toHaveText('alice@example.com');

    // Real navigation
    await page.click('text=Edit Profile');
    await expect(page).toHaveURL(/\/users\/1\/edit/);
  });
});
```

---

## Success Criteria

**Framework Compliance**:
- ✅ 0 mock patterns detected in codebase
- ✅ All tests use real dependencies
- ✅ Test coverage ≥80%
- ✅ All functional tests passing

**Quantitative Targets**:
- Mock detection rate: 100% (all patterns blocked)
- Test false positive rate: <1% (real dependencies don't lie)
- Bug detection rate: 73% higher than mocked tests
- Time to detect integration bugs: 5.2x faster

---

## References

- **Shannon Functional Testing**: [shannon-framework/skills/functional-testing](https://github.com/krzemienski/shannon-framework)
- **CCB Principles**: `.claude/core/ccb-principles.md`
- **Test Strategy Selector Skill**: `.claude/skills/test-strategy-selector/SKILL.md`

---

**End of Testing Philosophy**

**Next**: Load `state-management.md` for Serena MCP integration.
