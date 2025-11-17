---
name: test-coverage
skill-type: QUANTITATIVE
enforcement: 80
---

# Test Coverage: 80%+ Target

**Enforcement**: QUANTITATIVE (80%)

## Target

≥80% test coverage (configurable)

## Measurement

- Python: pytest-cov
- JavaScript: vitest --coverage
- Go: go test -cover
- Rust: cargo tarpaulin

## Enforcement

- Phase completion BLOCKED if coverage <80%
- `/ccb:test` displays coverage
- Validation gate: "Coverage ≥80%"

## References

- `.claude/core/testing-philosophy.md`
