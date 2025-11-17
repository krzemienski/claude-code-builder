---
name: functional-testing
skill-type: RIGID
enforcement: 100
mcp-requirements:
  required: []
  recommended:
    - name: puppeteer
      purpose: Real browser testing
    - name: ios-simulator
      purpose: Real mobile testing
---

# Functional Testing: NO MOCKS Enforcement

**Enforcement**: RIGID (100%) - Non-negotiable

## Iron Law

**ALL tests MUST use REAL dependencies. Mocks are PROHIBITED.**

##Prohibited Patterns (Auto-Blocked)

Detected and BLOCKED by `post_tool_use.py` hook:

```
jest.mock(), jest.spyOn(), jest.fn()
unittest.mock, @patch, @mock.patch
sinon.stub(), sinon.mock()
Mockito, gomock, mockall
vi.mock(), TestDouble
```

## Alternatives by Domain

| Domain | Instead of Mocks | Use |
|--------|------------------|-----|
| Web | jest.mock() | Puppeteer MCP (real browser) |
| Backend | HTTP mocks | Real test server + testcontainers |
| Database | Mock ORM | Real PostgreSQL via testcontainers |
| Mobile | Simulator mocks | iOS Simulator MCP |
| APIs | Nock/MSW | Sandbox/staging environments |
| Files | Virtual FS | Real temp directories |

## Rationale

1. **False Confidence**: Mocked tests pass when production fails
2. **Integration Bugs**: 73% hidden by mocked interfaces
3. **Maintenance Burden**: Mocks require parallel updates
4. **Regression Risk**: Production bugs not caught

## Examples

**❌ BLOCKED**:
```python
@patch('api.database.get_user')
def test_get_user(mock_db):
    mock_db.return_value = {"id": 1}
    # BLOCKED by post_tool_use hook
```

**✅ ALLOWED**:
```python
def test_get_user(test_client, test_db):
    # Real PostgreSQL via testcontainers
    test_db.execute("INSERT INTO users VALUES (1, 'Alice')")
    response = test_client.get("/users/1")
    assert response.json() == {"id": 1, "name": "Alice"}
```

## Enforcement

1. **Hook**: `post_tool_use.py` blocks mock patterns automatically
2. **Command**: `/ccb:test` scans before execution
3. **Gate**: Test coverage ≥80% with NO MOCKS

## References

- **Core Doc**: `.claude/core/testing-philosophy.md`
- **CCB Principles**: Law 2 (NO MOCKS)
