# /ccb:do

Execute task on existing codebase.

**Usage**: `/ccb:do "<task_description>"`

**Workflow**:
1. Check for PROJECT_INDEX.md (generate if missing)
2. Analyze task against index (3K tokens)
3. Identify affected modules (0 tokens, index lookup)
4. Load only affected files (500-2K tokens)
5. Execute with functional tests
6. Validate existing tests still pass

**Use Cases**:
- Add feature to existing app
- Refactor existing code
- Fix bugs
- Update dependencies

**Skills**: @skill project-indexing, @skill incremental-enhancement, @skill functional-testing

**Example**: `/ccb:do "add user authentication with JWT"`
