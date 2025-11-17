# Claude Code Builder v3

> **Shannon-Aligned Specification-Driven Development Framework**
>
> A hook-driven behavioral framework that guides Claude through specification-first development using quantitative complexity analysis, automatic NO MOCKS enforcement, and cross-session state persistence.

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/krzemienski/claude-code-builder)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/inspired_by-Shannon_Framework-purple.svg)](https://github.com/krzemienski/shannon-framework)

## What is Claude Code Builder v3?

Claude Code Builder v3 is **NOT a code generator**. It is a **behavioral enforcement system** that guides Claude through specification-driven development using:

- **Auto-Activated Skills**: Behavioral guidance that activates automatically via lifecycle hooks
- **Slash Commands**: Workflow orchestration for init, build, test, and deployment
- **Quantitative Analysis**: 6D complexity scoring (0.0-1.0) for objective decision-making
- **NO MOCKS Enforcement**: 13 mock patterns blocked automatically via hooks
- **State Persistence**: Cross-session continuity via Serena MCP
- **Project Indexing**: 94% token reduction (58K → 3K) for existing codebases

## Table of Contents

- [Core Philosophy](#core-philosophy)
- [Quick Start](#quick-start)
- [Framework Architecture](#framework-architecture)
- [Slash Commands](#slash-commands)
- [Skills System](#skills-system)
- [Iron Laws](#iron-laws)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [For Project Maintainers](#for-project-maintainers)
- [Contributing](#contributing)

## Core Philosophy

### Quantitative Over Qualitative

Every decision must be **measurable and algorithmic**, not subjective:

- ❌ "This looks simple" → ✅ Complexity score: 0.23 (SIMPLE)
- ❌ "We need some tests" → ✅ Test coverage: 87% (TARGET: 80%)
- ❌ "Let's split this up" → ✅ 4 phases, 35% → 25% → 25% → 15%
- ❌ "I'll use mocks" → ✅ BLOCKED - Functional tests only

### Hook-Driven Enforcement

Skills are **automatically activated** through lifecycle hooks:

- **SessionStart**: Load ccb-principles on every session
- **UserPromptSubmit**: Inject build goal and phase context on EVERY prompt
- **PostToolUse**: Block test file mocks, enforce coverage requirements
- **PreCompact**: Checkpoint build state (MUST succeed before compression)
- **Stop**: Validate phase completion before session end

### Command-Orchestrated Workflows

Users interact through **slash commands** that orchestrate multi-stage workflows:

```bash
/ccb:init spec.md          # Analyze → Plan → Checkpoint
/ccb:build                 # Execute → Test → Validate → Save
/ccb:do "add auth"         # Analyze existing code → Implement → Test
```

## Quick Start

### 1. Copy Framework to Your Project

```bash
# Clone repository
git clone https://github.com/krzemienski/claude-code-builder.git

# Copy .claude framework to your project
cp -r claude-code-builder/.claude /path/to/your/project/
cp claude-code-builder/.claude-plugin /path/to/your/project/

cd /path/to/your/project
```

### 2. Install Serena MCP (Required)

```bash
# Install Serena MCP for state persistence
npx -y @modelcontextprotocol/server-memory

# Configure in Claude Code settings
# Add to your MCP configuration:
{
  "mcps": {
    "serena": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

### 3. Create Your Specification

```markdown
# My API Service

## Overview
A REST API for managing user accounts with authentication.

## Requirements
- User registration and login
- JWT token-based authentication
- Password hashing with bcrypt
- Input validation
- 80%+ test coverage

## Technology Stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- pytest (functional tests only)

## Success Criteria
1. All endpoints functional
2. Authentication secure
3. Tests passing (NO MOCKS)
```

### 4. Initialize and Build

```bash
# Initialize from specification
/ccb:init spec.md

# Check status
/ccb:status

# Execute current phase
/ccb:build

# Run functional tests
/ccb:test

# Gap assessment
/ccb:reflect
```

## Framework Architecture

### 4-Layer Enforcement Pyramid

```
┌─────────────────────────────────────────┐
│  Layer 4: COMMANDS (Slash Commands)    │  ← User interaction
│  /ccb:init, /ccb:build, /ccb:test      │
├─────────────────────────────────────────┤
│  Layer 3: SKILLS (Behavioral Guidance)  │  ← Auto-activated
│  12 skills (RIGID/PROTOCOL/QUANTITATIVE)│
├─────────────────────────────────────────┤
│  Layer 2: HOOKS (Auto-Activation)       │  ← Lifecycle events
│  SessionStart, PostToolUse, PreCompact  │
├─────────────────────────────────────────┤
│  Layer 1: CORE DOCS (Foundational Laws) │  ← Iron Laws
│  ccb-principles.md, complexity-analysis │
└─────────────────────────────────────────┘
```

### Directory Structure

```
your-project/
├── .claude/
│   ├── core/                           # 6 reference documents
│   │   ├── ccb-principles.md           # Iron Laws & foundations
│   │   ├── complexity-analysis.md      # 6D quantitative scoring
│   │   ├── phase-planning.md           # Algorithmic phase planning
│   │   ├── testing-philosophy.md       # NO MOCKS enforcement
│   │   ├── state-management.md         # Serena MCP integration
│   │   └── project-indexing.md         # 94% token reduction
│   │
│   ├── hooks/                          # 5 lifecycle hooks
│   │   ├── hooks.json                  # Hook configuration
│   │   ├── session_start.sh            # Load principles
│   │   ├── user_prompt_submit.py       # Context injection
│   │   ├── post_tool_use.py            # Mock blocking
│   │   ├── precompact.py               # Checkpoint creation
│   │   └── stop.py                     # Phase validation
│   │
│   ├── skills/                         # 12 behavioral skills
│   │   ├── ccb-principles/             # RIGID (100%)
│   │   ├── functional-testing/         # RIGID (100%)
│   │   ├── spec-driven-building/       # PROTOCOL (90%)
│   │   ├── phase-execution/            # PROTOCOL (90%)
│   │   ├── checkpoint-preservation/    # PROTOCOL (90%)
│   │   ├── project-indexing/           # PROTOCOL (90%)
│   │   ├── complexity-analysis/        # QUANTITATIVE (80%)
│   │   ├── validation-gates/           # QUANTITATIVE (80%)
│   │   ├── test-coverage/              # QUANTITATIVE (80%)
│   │   ├── mcp-augmented-research/     # FLEXIBLE (70%)
│   │   ├── honest-assessment/          # FLEXIBLE (70%)
│   │   └── incremental-enhancement/    # FLEXIBLE (70%)
│   │
│   └── commands/                       # 10 slash commands
│       ├── init.md                     # Initialize from spec
│       ├── status.md                   # Show progress
│       ├── checkpoint.md               # Manual save
│       ├── resume.md                   # Auto-resume
│       ├── analyze.md                  # Complexity only
│       ├── index.md                    # Generate PROJECT_INDEX
│       ├── build.md                    # Execute phase
│       ├── do.md                       # Brownfield support
│       ├── test.md                     # Functional tests
│       └── reflect.md                  # Gap assessment
│
├── .claude-plugin/
│   └── manifest.json                   # Plugin metadata
│
└── .serena/                            # State persistence
    └── ccb/
        ├── build_goal.txt
        ├── current_phase.txt
        ├── complexity_analysis.json
        └── checkpoints/
```

## Slash Commands

### Session Management

| Command | Description | Usage |
|---------|-------------|-------|
| `/ccb:init` | Initialize build from spec | `/ccb:init spec.md` |
| `/ccb:status` | Show build progress | `/ccb:status` |
| `/ccb:checkpoint` | Manual state save | `/ccb:checkpoint` |
| `/ccb:resume` | Auto-resume from checkpoint | `/ccb:resume` |

### Analysis & Planning

| Command | Description | Usage |
|---------|-------------|-------|
| `/ccb:analyze` | 6D complexity analysis only | `/ccb:analyze spec.md` |
| `/ccb:index` | Generate PROJECT_INDEX (94% reduction) | `/ccb:index` |

### Execution

| Command | Description | Usage |
|---------|-------------|-------|
| `/ccb:build` | Execute current phase | `/ccb:build` |
| `/ccb:do` | Operate on existing codebase | `/ccb:do "add user auth"` |

### Quality & Testing

| Command | Description | Usage |
|---------|-------------|-------|
| `/ccb:test` | Functional tests (NO MOCKS) | `/ccb:test` |
| `/ccb:reflect` | Honest gap assessment | `/ccb:reflect` |

## Skills System

Skills define **HOW to build**, not what to build. They are automatically activated via hooks.

### RIGID Skills (100% Enforcement)

- **ccb-principles**: Meta-skill for Iron Law enforcement
- **functional-testing**: NO MOCKS enforcement with alternatives

### PROTOCOL Skills (90% Enforcement)

- **spec-driven-building**: Enforce specification analysis first
- **phase-execution**: Sequential phase execution with gates
- **checkpoint-preservation**: Cross-session continuity
- **project-indexing**: 94% token reduction for existing codebases

### QUANTITATIVE Skills (80% Enforcement)

- **complexity-analysis**: 6D quantitative scoring (0.0-1.0)
- **validation-gates**: ≥3 measurable gates per phase
- **test-coverage**: 80%+ coverage enforcement

### FLEXIBLE Skills (70% Enforcement)

- **mcp-augmented-research**: Framework docs via context7 MCP
- **honest-assessment**: Gap analysis and quality grading
- **incremental-enhancement**: Brownfield/existing codebase support

## Iron Laws

### Law 1: Specification-First

**No implementation without specification analysis.**

- Minimum 50 words
- Clear acceptance criteria
- Technology stack defined

### Law 2: NO MOCKS

**13 mock patterns automatically blocked.**

Prohibited patterns:
- `jest.mock()`
- `unittest.mock`
- `sinon.mock()`
- `Mockito.mock()`
- `gomock`
- And 8 more...

**Alternatives by domain:**
- Web: Puppeteer MCP (real browser)
- Mobile: iOS Simulator MCP (real simulator)
- APIs: Test instances, Docker containers
- Databases: Test databases, transactions

### Law 3: Quantitative Decisions

**All decisions must be measurable (0.0-1.0 scale).**

6D Complexity Formula:
```python
complexity = (
    structure * 0.20 +      # File count, nesting depth
    logic * 0.25 +          # Conditional complexity
    integration * 0.20 +    # External dependencies
    scale * 0.15 +          # Lines of code, data volume
    uncertainty * 0.10 +    # Ambiguity in requirements
    technical_debt * 0.10   # Legacy code quality
)
```

Categories:
- 0.00-0.30: SIMPLE (3 phases)
- 0.30-0.50: MODERATE (3-4 phases)
- 0.50-0.70: COMPLEX (5 phases)
- 0.70-0.85: VERY COMPLEX (5 phases + extended validation)
- 0.85-1.00: EXTREME (6 phases)

### Law 4: State Persistence

**Serena MCP for cross-session continuity.**

Storage structure:
```
.serena/ccb/
├── build_goal.txt
├── current_phase.txt
├── phase_completion.json
├── complexity_analysis.json
├── validation_gates.json
└── checkpoints/
    ├── ckpt_20250117_143022.tar.gz
    └── ckpt_20250117_153045.tar.gz
```

### Law 5: Validation Gates

**≥3 measurable gates per phase.**

Example gates:
```yaml
phase_2_core:
  gates:
    - metric: "Files created"
      target: "≥5"
      actual: 7
      status: PASS
    - metric: "Test coverage"
      target: "≥80%"
      actual: "87%"
      status: PASS
    - metric: "Build successful"
      target: "exit_code=0"
      actual: 0
      status: PASS
```

## Installation

### Prerequisites

- **Claude Code** with MCP support
- **Node.js** 18+ (for MCP servers)
- **Python** 3.9+ (optional, for hook scripts)

### Step 1: Install Framework

```bash
# Clone repository
git clone https://github.com/krzemienski/claude-code-builder.git

# Copy to your project
cp -r claude-code-builder/.claude /your/project/
cp -r claude-code-builder/.claude-plugin /your/project/

cd /your/project
```

### Step 2: Install Serena MCP (Required)

```bash
npx -y @modelcontextprotocol/server-memory
```

Add to Claude Code MCP configuration:

```json
{
  "mcps": {
    "serena": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

### Step 3: Install Optional MCPs

```bash
# Framework documentation
npx -y @modelcontextprotocol/server-context7

# Web testing (NO MOCKS)
npx -y @modelcontextprotocol/server-puppeteer

# iOS testing (NO MOCKS)
npx -y @modelcontextprotocol/server-ios-simulator

# Deep reasoning
npx -y @modelcontextprotocol/server-sequential-thinking
```

### Step 4: Verify Installation

The framework will auto-activate on session start. You should see:

```
🏗️  Claude Code Builder v3 Loaded
```

Test with:
```bash
/ccb:status
```

## Usage Examples

### Example 1: Greenfield Project

```bash
# Create specification
cat > spec.md <<EOF
# Todo API
## Overview
REST API for managing todos with user authentication.
## Requirements
- User registration/login
- CRUD operations for todos
- JWT authentication
- 80%+ test coverage
## Tech Stack
- Python 3.11, FastAPI, SQLAlchemy, pytest
EOF

# Initialize
/ccb:init spec.md

# Output shows:
# - Complexity: 0.42 (MODERATE)
# - Phase count: 4
# - Estimated timeline: 8-12 hours

# Execute phases
/ccb:build    # Phase 1: Foundation
/ccb:build    # Phase 2: Core features
/ccb:build    # Phase 3: Authentication
/ccb:build    # Phase 4: Testing & docs

# Validate
/ccb:test     # All functional tests
/ccb:reflect  # Gap assessment
```

### Example 2: Brownfield Enhancement

```bash
# Generate project index (94% token reduction)
/ccb:index

# Execute task on existing codebase
/ccb:do "add rate limiting middleware to all API endpoints"

# Output shows:
# - Analyzed 47 files (58K tokens → 3K tokens via PROJECT_INDEX)
# - Identified 12 endpoints
# - Created rate_limiter.py
# - Updated all endpoint decorators
# - Added functional tests (NO MOCKS)
# - Updated documentation

# Validate
/ccb:test
```

### Example 3: Complex Enterprise System

```bash
# Analyze first
/ccb:analyze enterprise-spec.md

# Output:
# Complexity: 0.78 (VERY COMPLEX)
# Dimensions:
#   - Structure: 0.85 (15+ components)
#   - Logic: 0.80 (high conditional complexity)
#   - Integration: 0.90 (6 external services)
#   - Scale: 0.70 (50K+ LOC)
#   - Uncertainty: 0.65 (ambiguous requirements)
#   - Technical Debt: 0.60 (legacy migration)
# Phase count: 5 + extended validation
# Estimated cost: $150-300

# Initialize with budget
/ccb:init enterprise-spec.md

# Execute with checkpoints
/ccb:build    # Auto-checkpoints before each phase
/ccb:status   # Monitor progress
/ccb:build    # Resume after interruption
```

## Configuration

### Plugin Manifest (`.claude-plugin/manifest.json`)

```json
{
  "name": "claude-code-builder",
  "version": "3.0.0",
  "mcps": {
    "serena": {
      "required": true,
      "description": "State persistence"
    },
    "context7": {
      "required": false,
      "description": "Framework documentation"
    }
  },
  "enforcement": {
    "no_mocks": {
      "enabled": true,
      "level": "blocking"
    },
    "specification_first": {
      "enabled": true,
      "minimum_spec_words": 50
    }
  }
}
```

### Hook Configuration (`.claude/hooks/hooks.json`)

```json
{
  "SessionStart": {
    "command": ["bash", "${CLAUDE_PLUGIN_ROOT}/hooks/session_start.sh"],
    "timeout": 5000
  },
  "PostToolUse": {
    "command": ["python3", "${CLAUDE_PLUGIN_ROOT}/hooks/post_tool_use.py"],
    "timeout": 3000,
    "toolPattern": ["Write", "Edit", "MultiEdit"]
  },
  "PreCompact": {
    "command": ["python3", "${CLAUDE_PLUGIN_ROOT}/hooks/precompact.py"],
    "timeout": 15000,
    "continueOnError": false
  }
}
```

## For Project Maintainers

### Adding to Existing Projects

```bash
# Add framework to existing repo
cd /your/existing/project
git clone https://github.com/krzemienski/claude-code-builder.git /tmp/ccb
cp -r /tmp/ccb/.claude .
cp -r /tmp/ccb/.claude-plugin .

# Generate index for token efficiency
/ccb:index

# Use /ccb:do for enhancements
/ccb:do "add feature X"
```

### Customizing Skills

Skills can be adjusted per-project by modifying YAML frontmatter:

```yaml
---
name: functional-testing
enforcement: 100  # Change to 90 for warnings instead of blocking
---
```

### Checkpoint Management

```bash
# Checkpoints stored in .serena/ccb/checkpoints/
ls .serena/ccb/checkpoints/

# Manual checkpoint
/ccb:checkpoint

# Resume from specific checkpoint
/ccb:resume --checkpoint ckpt_20250117_143022
```

## Key Features Summary

| Feature | Description | Impact |
|---------|-------------|--------|
| **Quantitative Analysis** | 6D complexity scoring (0.0-1.0) | Objective decision-making |
| **NO MOCKS Enforcement** | 13 patterns blocked automatically | Real functional tests only |
| **State Persistence** | Cross-session via Serena MCP | Auto-resume within 24h |
| **Project Indexing** | Hierarchical summarization | 94% token reduction |
| **Hook-Driven** | Auto-activation via lifecycle | No manual skill invocation |
| **Validation Gates** | ≥3 measurable gates per phase | Quality enforcement |
| **Brownfield Support** | /ccb:do for existing codebases | Incremental enhancement |
| **Specification-First** | No code without spec analysis | Prevents scope creep |

## Troubleshooting

### Framework Not Loading

```bash
# Check .claude directory exists
ls -la .claude/

# Verify hooks are executable
chmod +x .claude/hooks/*.sh
chmod +x .claude/hooks/*.py

# Check session start message
# Should see: "🏗️  Claude Code Builder v3 Loaded"
```

### Serena MCP Not Working

```bash
# Verify MCP is installed
npx -y @modelcontextprotocol/server-memory

# Check MCP configuration
# Must be in Claude Code settings under MCP section

# Test state persistence
/ccb:checkpoint
ls .serena/ccb/
```

### Mock Patterns Not Blocked

```bash
# Verify post_tool_use.py hook is configured
cat .claude/hooks/hooks.json | grep PostToolUse

# Test by trying to write mock code
# Should be blocked with clear message
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/krzemienski/claude-code-builder.git
cd claude-code-builder

# Test framework
cp -r .claude /path/to/test/project/
cd /path/to/test/project
/ccb:init test-spec.md
```

## Inspiration

Claude Code Builder v3 is inspired by the [Shannon Framework](https://github.com/krzemienski/shannon-framework), which pioneered hook-driven auto-activation and behavioral skill enforcement in Claude Code.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **GitHub Issues**: [Report bugs](https://github.com/krzemienski/claude-code-builder/issues)
- **Discussions**: [Ask questions](https://github.com/krzemienski/claude-code-builder/discussions)
- **Documentation**: See `.claude/core/*.md` for detailed reference

---

**Claude Code Builder v3.0.0** - Shannon-Aligned Specification-Driven Development Framework
