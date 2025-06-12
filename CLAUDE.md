# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code Builder (CCB) is an AI-powered Python CLI tool that automates the complete software development lifecycle. It transforms project specifications into production-ready applications through intelligent task decomposition, custom AI instruction generation, and systematic phase-based execution.

## 🚨 CRITICAL: MCP Server Usage is MANDATORY

Every operation MUST use the appropriate MCP server:
- **context7**: Before implementing ANY library or framework
- **memory**: After completing each task/module
- **sequential-thinking**: For complex problem decomposition
- **filesystem**: For ALL file operations (NEVER use Python's open())
- **git**: For version control after each phase

## Key Development Commands

```bash
# Install dependencies
poetry install

# Run the CLI
poetry run claude-code-builder --help
poetry run claude-code-builder init spec.md --output-dir ./project
poetry run claude-code-builder resume ./project
poetry run claude-code-builder status ./project
poetry run claude-code-builder logs ./project --tail

# Development tools
poetry run ruff check .
poetry run ruff format .
poetry run mypy src/claude_code_builder/
poetry run black .

# Build and test
poetry build
pip install dist/*.whl
claude-code-builder --version

# Functional testing (NO UNIT TESTS)
python validate_build.py ./test_output
```

## Architecture Overview

### Multi-Agent System
```
src/claude_code_builder/
├── agents/
│   ├── spec_analyzer.py      # Analyzes specifications
│   ├── task_generator.py     # Creates task breakdowns
│   ├── instruction_builder.py # Generates AI instructions
│   ├── acceptance_generator.py # Creates test criteria
│   ├── documentation_agent.py  # Generates docs
│   └── executor.py           # Claude Code SDK execution
├── core/
│   ├── models.py            # Pydantic v2 models
│   ├── logging_system.py    # Multi-stream logging
│   ├── context_manager.py   # 150K+ token handling
│   ├── mcp_orchestrator.py  # MCP enforcement
│   ├── output_manager.py    # Project directories
│   └── project_manager.py   # State management
├── builders/
│   ├── claude_md_builder.py
│   ├── command_builder.py
│   └── documentation_builder.py
├── testing/
│   ├── acceptance_runner.py  # Real-world tests only
│   └── production_validator.py
└── cli/
    └── main.py              # Click CLI entry
```

## Implementation Requirements

### 1. Async Throughout
```python
# EVERY operation must be async
async def analyze_spec(self, spec: str) -> SpecAnalysis:
    async with self.client as client:
        response = await client.messages.create_async(...)
```

### 2. Comprehensive Logging
```python
# Log EVERYTHING with structured logging
logger.info("api_call",
    model=model,
    tokens_in=tokens_in,
    tokens_out=tokens_out,
    latency_ms=latency,
    phase=current_phase,
    agent="spec_analyzer"
)
```

### 3. Error Recovery
```python
try:
    result = await self.execute_phase(phase)
except ContextOverflowError:
    # Intelligent recovery
    optimized = await self.optimize_context()
    result = await self.retry_with_context(optimized)
```

### 4. NO Mock Testing
- Test by running the actual built CLI
- Use real specifications as input
- Validate outputs and logs
- Check generated artifacts

## Implementation Phases

**Current Phase Tracking**: Check memory MCP for `ccb_phase_*`

1. **Phase 1**: Initialize project, MCP config, research
2. **Phase 2**: Poetry setup, directory structure
3. **Phase 3**: Pydantic models, type system
4. **Phase 4**: Logging system with Rich
5. **Phase 5**: Context management (150K tokens)
6. **Phase 6**: MCP orchestration
7. **Phase 7**: SpecAnalyzer agent
8. **Phase 8**: Task/Instruction generators
9. **Phase 9**: Claude Code executor
10. **Phase 10**: CLI implementation
11. **Phase 11**: Documentation system
12. **Phase 12**: Build validation
13. **Phase 13**: Functional testing
14. **Phase 14**: Advanced testing
15. **Phase 15**: Release preparation

## Memory MCP Pattern

```python
# ALWAYS check memory before redundant work
existing = await memory.search_nodes("ccb_phase_4_complete")
if existing:
    # Skip to next phase
    return

# Store after completion
await memory.create_entity(
    name="ccb_phase_4_complete",
    observations=["Logging system implemented", "API tracking active"]
)
```

## Critical Patterns

### Agent Pattern
```python
class SpecAnalyzer:
    def __init__(self, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic()
        self.tools = self._define_tools()
        
    async def analyze(self, spec: str) -> SpecAnalysis:
        # Always async, always logged
```

### Context Management
```python
class ContextManager:
    def __init__(self, max_tokens: int = 150000):
        # Opus 4 extended context
        self.max_tokens = max_tokens
```

### CLI Pattern
```python
@click.command()
@click.option('--verbose', '-v', count=True)
async def init(spec_file: str, verbose: int):
    with console.status("[cyan]Analyzing..."):
        result = await analyzer.analyze(spec)
```

## Testing Strategy

**Functional Validation Only**:
```bash
# Build and install
poetry build
pip install dist/*.whl

# Execute
claude-code-builder init test_spec.md --output-dir test_output

# Validate
python validate_build.py test_output
```

## Common Pitfalls

1. **DON'T** use synchronous code
2. **DON'T** skip MCP usage
3. **DON'T** write unit tests
4. **DON'T** use mocks
5. **DON'T** forget logging
6. **DON'T** use Python's open()
7. **DON'T** skip git commits

## Success Criteria

- Handles 200K+ token specifications
- Logs every API call completely
- Resumes from any interruption
- Beautiful Rich CLI output
- MCP compliance 100%
- Zero placeholder code