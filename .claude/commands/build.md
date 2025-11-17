# /ccb:build

Execute current phase with validation gates.

**Usage**: `/ccb:build [--phase N] [--auto]`

**Workflow**:
1. Load phase plan
2. Display objectives and gates
3. Execute phase tasks
4. Run functional tests (NO MOCKS)
5. Measure coverage
6. Check validation gates
7. If all pass: checkpoint, advance phase
8. If any fail: mark incomplete, BLOCK

**Options**:
- `--phase N`: Execute specific phase
- `--auto`: Skip confirmations

**Skills**: @skill phase-execution, @skill validation-gates, @skill functional-testing

**Enforcement**: Gates must pass to proceed
