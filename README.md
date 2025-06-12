# Claude Code Builder

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/dependency%20management-poetry-blueviolet)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-orange)](https://github.com/astral-sh/ruff)

An AI-powered Python CLI tool that automates the complete software development lifecycle using Claude Code SDK and Anthropic's agent system.

## 🚀 Overview

Claude Code Builder transforms project specifications of any size into fully implemented, production-ready applications through:

- **Intelligent Task Decomposition**: Breaks down complex specifications into manageable phases
- **Custom AI Instruction Generation**: Creates tailored instructions for each development phase
- **Systematic Phase-Based Execution**: Implements projects step-by-step with full transparency
- **Comprehensive Documentation**: Generates complete documentation alongside code

## ✨ Key Features

- **Large Specification Support**: Handles specs exceeding 150K+ tokens through intelligent chunking
- **Production-Only Testing**: Enforces real-world functional testing (no mocks allowed)
- **MCP-First Development**: Mandates use of Model Context Protocol servers for consistency
- **Complete Audit Trail**: Streams and persists all logs, code generation, and API interactions
- **Intelligent Resume**: Pick up exactly where you left off with checkpoint-based state management
- **Beautiful CLI**: Rich terminal output with progress tracking and status displays

## 📋 Requirements

- Python 3.11 or higher
- Poetry for dependency management
- Active Anthropic API key
- Git for version control

## 🛠️ Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-code-builder.git
cd claude-code-builder

# Install dependencies with Poetry
poetry install

# Run the CLI
poetry run claude-code-builder --help
```

### From Package

```bash
# Install from PyPI (coming soon)
pip install claude-code-builder

# Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Run the CLI
claude-code-builder --help
```

## 🚦 Quick Start

### Initialize a New Project

```bash
# Basic usage
claude-code-builder init spec.md --output-dir ./my-project

# With options
claude-code-builder init spec.md \
  --output-dir ./my-project \
  --model claude-opus-4-20250514 \
  --max-cost 50.0 \
  --verbose
```

### Resume an Interrupted Build

```bash
# Resume from last checkpoint
claude-code-builder resume ./my-project

# Resume from specific phase
claude-code-builder resume ./my-project --from-phase 7
```

### Monitor Progress

```bash
# Check project status
claude-code-builder status ./my-project

# View real-time logs
claude-code-builder logs ./my-project --tail

# Export project artifacts
claude-code-builder export ./my-project
```

## 🏗️ Architecture

Claude Code Builder uses a multi-agent architecture:

- **SpecAnalyzer**: Analyzes project specifications and identifies requirements
- **TaskGenerator**: Creates phase-based task breakdowns
- **InstructionBuilder**: Generates custom AI instructions for each phase
- **AcceptanceCriteriaGenerator**: Creates measurable test criteria
- **DocumentationAgent**: Generates comprehensive documentation
- **ClaudeCodeExecutor**: Manages Claude Code SDK execution

## 🧪 Testing Philosophy

Claude Code Builder enforces production-only testing:
- No unit tests or mocks
- All validation through functional testing
- Real-world execution with actual specifications
- Complete output validation

## 📝 Example Specification

```markdown
# Task Management API

Build a RESTful API with:
- FastAPI backend
- PostgreSQL database
- JWT authentication
- CRUD operations for tasks
- Real-time updates via WebSockets
- Docker deployment

## Requirements
- Users can register and authenticate
- Tasks support title, description, status, priority
- Real-time updates when tasks change
- API documentation with OpenAPI
- Rate limiting and security headers
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Anthropic's Claude API](https://www.anthropic.com)
- Uses [Claude Code SDK](https://docs.anthropic.com/en/docs/claude-code/sdk)
- Terminal UI powered by [Rich](https://github.com/Textualize/rich)
- CLI framework by [Click](https://click.palletsprojects.com/)