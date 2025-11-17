# /ccb:test

Run functional tests with NO MOCKS enforcement.

**Usage**: `/ccb:test [--coverage] [--functional-only]`

**Process**:
1. Discover test files
2. Scan for mock patterns (BLOCK if found)
3. Run tests with coverage
4. Display results and coverage %
5. Check ≥80% threshold
6. Save to `.serena/ccb/test_results.json`

**Options**:
- `--coverage`: Show detailed coverage
- `--functional-only`: Skip unit tests

**Skills**: @skill functional-testing, @skill test-coverage

**Enforcement**: Mocks BLOCKED, coverage enforced
