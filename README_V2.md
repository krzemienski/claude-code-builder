# Claude Code Builder v2.0 (SDK-Based)

**AI-Powered Software Development Automation with Claude Agent SDK Patterns**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-35%2F35%20passing-brightgreen)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Transform project specifications into production-ready code using Claude's advanced AI capabilities and SDK-compatible architecture.

## 🚀 What's New in v2.0

- **SDK-Compatible Architecture**: Built with patterns ready for the Claude Agent SDK
- **Enhanced Cost Tracking**: Real-time API cost monitoring per model
- **Streaming Progress**: Live progress reporting during builds
- **Improved MCP Integration**: Phase-specific MCP server configuration
- **Comprehensive Testing**: 35 tests with 100% pass rate
- **Better Error Handling**: Enhanced recovery and retry logic

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [v1 vs v2](#v1-vs-v2)
- [Migration Guide](#migration-guide)
- [Testing](#testing)
- [Contributing](#contributing)

## Quick Start

```bash
# Install
poetry install

# Run v2 CLI
export ANTHROPIC_API_KEY=your-key-here
poetry run claude-code-builder-v2 init my-spec.md --output ./my-project

# Check version
poetry run claude-code-builder-v2 --version
# Output: claude-code-builder-v2, version 2.0.0-sdk
```

## Installation

### Prerequisites
- Python 3.11+
- Poetry 1.7+
- Anthropic API key

### Install Dependencies
```bash
# Clone repository
git clone https://github.com/krzemienski/claude-code-builder
cd claude-code-builder

# Install with Poetry
poetry install

# Verify installation
poetry run claude-code-builder-v2 --help
```

## Usage

### Initialize a New Project
```bash
claude-code-builder-v2 init specification.md \
  --output ./my-project \
  --model claude-3-haiku-20240307 \
  --max-cost 10.0
```

### CLI Options
```
--output, -o          Output directory
--model               Claude model (default: claude-3-haiku-20240307)
--api-key             API key (or set ANTHROPIC_API_KEY)
--max-cost            Maximum cost limit in USD (default: 100.0)
--max-tokens          Max tokens per request (default: 4096)
--temperature         Model temperature 0.0-1.0 (default: 0.3)
--verbose, -v         Increase verbosity (-v, -vv for DEBUG)
```

### Example Specification

```markdown
# Simple REST API

Build a Python REST API with the following requirements:

## Features
- User authentication (JWT)
- CRUD operations for "tasks"
- PostgreSQL database
- Docker deployment

## Technical Stack
- FastAPI framework
- SQLAlchemy ORM
- Alembic migrations
- pytest for testing

## Acceptance Criteria
- All endpoints have tests
- API documentation via Swagger
- Docker Compose setup included
```

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer (Click + Rich)                 │
├─────────────────────────────────────────────────────────────┤
│                  SDKBuildOrchestrator                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           SDKPhaseExecutor                           │   │
│  │  ┌────────────────────────────────────────────┐    │   │
│  │  │     8 Specialized Agents                    │    │   │
│  │  │  • SpecAnalyzer  • TaskGenerator           │    │   │
│  │  │  • InstructionBuilder • CodeGenerator       │    │   │
│  │  │  • TestGenerator • AcceptanceGenerator     │    │   │
│  │  │  • ErrorHandler  • DocumentationAgent      │    │   │
│  │  └────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
├──────────────────────────┬──────────────────────────────────┤
│    SDKClientManager      │      MCP Integration             │
│  - Session Management    │  - Filesystem                    │
│  - Query Routing         │  - Memory                        │
│  - Tool Registry         │  - Context7                      │
│  - Hook System           │  - Git                           │
├──────────────────────────┴──────────────────────────────────┤
│              AsyncAnthropic (API Client)                     │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

**SDK Layer** (`src/claude_code_builder_v2/sdk/`)
- `SDKClientManager`: Central SDK client lifecycle management
- `ToolRegistry`: Type-safe tool definitions with `@tool` decorator
- `HookRegistry`: Event hooks for monitoring
- `StreamingProgressReporter`: Real-time progress updates
- `EnhancedSDKHooks`: Cost and tool usage tracking

**Agent System** (`src/claude_code_builder_v2/agents/`)
- `BaseAgent`: SDK-integrated base class with session management
- 8 specialized agents for different build phases
- Automatic agent selection based on task type

**Executor System** (`src/claude_code_builder_v2/executor/`)
- `SDKPhaseExecutor`: Phase-level execution with dependency management
- `SDKBuildOrchestrator`: Complete build lifecycle orchestration

**MCP Integration** (`src/claude_code_builder_v2/mcp/`)
- `SDKMCPIntegration`: Configuration for 5 MCP server types
- Phase-specific server selection
- Tool listing and validation

## v1 vs v2

| Feature | v0.1.0 | v2.0 |
|---------|--------|------|
| Architecture | Direct API calls | SDK-compatible patterns |
| Cost Tracking | Basic | Per-model, comprehensive |
| Progress Reporting | Logs only | Streaming + callbacks |
| MCP Integration | Subprocess-based | SDK-compatible config |
| Testing | Scattered | 35 comprehensive tests |
| Error Handling | Basic | Enhanced with recovery |
| Session Management | Manual | Automatic via SDK |
| Tool Definitions | Manual schemas | @tool decorator |
| Hooks | None | Pre/post hooks for all operations |

## Migration Guide

See [MIGRATION_V2.md](MIGRATION_V2.md) for detailed migration instructions.

**Quick Migration:**
```bash
# v0.1.0
claude-code-builder init spec.md

# v2.0
claude-code-builder-v2 init spec.md

# Both CLIs coexist!
```

## Testing

```bash
# Run all v2 tests
poetry run pytest tests/test_*_v2.py -v

# Expected output:
# tests/test_sdk_v2.py::12 passed
# tests/test_agents_v2.py::14 passed
# tests/test_executor_v2.py::9 passed
# Total: 35/35 passing (100%)

# Run with coverage
poetry run pytest tests/test_*_v2.py --cov=claude_code_builder_v2

# Run integration tests (requires API key)
export ANTHROPIC_API_KEY=your-key
poetry run pytest tests/test_integration_v2.py -v -m integration
```

### Test Organization
- `test_sdk_v2.py`: SDK layer (client manager, tools, hooks)
- `test_agents_v2.py`: All 8 specialized agents
- `test_executor_v2.py`: Phase and build orchestration
- `test_integration_v2.py`: End-to-end integration

## Cost Estimation

Typical costs for building projects:

| Project Size | Model | Estimated Cost |
|--------------|-------|----------------|
| Simple CLI (50 LOC) | Haiku | $0.05-0.15 |
| REST API (500 LOC) | Haiku | $0.50-1.50 |
| Web App (2000 LOC) | Sonnet | $5.00-15.00 |
| Complex System (10k+ LOC) | Opus | $50.00-150.00 |

Use `--max-cost` to set hard limits.

## Configuration

### Environment Variables
```bash
export ANTHROPIC_API_KEY=your-key-here
export CCB_BASE_OUTPUT_DIR=./builds
export CCB_MAX_CONCURRENT_API_CALLS=5
```

### MCP Configuration (`.mcp.json`)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@filesystem/mcp"],
      "description": "File system operations"
    },
    "memory": {
      "command": "npx",
      "args": ["@memory/mcp"],
      "description": "Context persistence"
    }
  }
}
```

## Troubleshooting

### Common Issues

**"ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY=your-key-here
# Or pass via CLI
claude-code-builder-v2 init spec.md --api-key your-key
```

**"ModuleNotFoundError"**
```bash
poetry install --no-interaction
```

**Tests failing**
```bash
# Ensure you're in the project root
cd claude-code-builder
poetry run pytest tests/test_*_v2.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`poetry run pytest tests/test_*_v2.py -v`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup
```bash
# Install dev dependencies
poetry install

# Run linters
poetry run ruff check .
poetry run mypy src/claude_code_builder_v2/

# Format code
poetry run ruff format .
```

## Roadmap

- [ ] Resume functionality for v2
- [ ] Status command for v2
- [ ] Real Claude Agent SDK integration (when available)
- [ ] Enhanced streaming with progress bars
- [ ] Project templates
- [ ] Plugin system for custom agents

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [Claude](https://anthropic.com/claude) by Anthropic
- Inspired by the vision of AI-powered development automation
- Thanks to the open-source community

## Support

- **Documentation**: [REWRITE_SPEC.md](REWRITE_SPEC.md), [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Issues**: https://github.com/krzemienski/claude-code-builder/issues
- **Discussions**: https://github.com/krzemienski/claude-code-builder/discussions

---

**Note**: v2.0 is SDK-compatible but uses `AsyncAnthropic` as the underlying client since the official Claude Agent SDK for Python is not yet publicly available. The architecture and patterns are designed to make switching to the real SDK straightforward when it's released.
