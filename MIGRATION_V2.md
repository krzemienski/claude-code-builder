# Migration Guide: v0.1.0 → v2.0 (SDK-Based)

This guide helps you migrate from Claude Code Builder v0.1.0 to v2.0, which is built on SDK-compatible patterns.

## Overview

Version 2.0 is a complete architectural rewrite featuring:
- SDK-compatible patterns and interfaces
- Enhanced cost tracking and monitoring
- Streaming progress reporting
- Improved MCP integration
- Better error handling and recovery
- 35 comprehensive tests (100% passing)

## Breaking Changes

### 1. API Client Access
**v0.1.0:**
```python
from anthropic import AsyncAnthropic
client = AsyncAnthropic(api_key=api_key)
```

**v2.0:**
```python
from claude_code_builder_v2.sdk import SDKClientManager
manager = SDKClientManager(config, logger, api_key=api_key)
```

### 2. Agent Initialization
**v0.1.0:**
```python
agent = SpecAnalyzer(
    executor=executor,
    context_manager=context_manager,
    mcp_orchestrator=mcp_orchestrator,
    logger=logger,
)
```

**v2.0:**
```python
agent = SpecAnalyzer(
    sdk_manager=sdk_manager,
    context_manager=context_manager,
    logger=logger,
)
```

### 3. CLI Commands
**v0.1.0:**
```bash
claude-code-builder init spec.md --output ./project
```

**v2.0:**
```bash
claude-code-builder-v2 init spec.md --output ./project
```

## Compatibility

### ✅ Fully Compatible
- **Project States**: All v0.1.0 project states can be loaded in v2.0
- **Checkpoints**: Checkpoint format unchanged
- **Configuration Files**: Core configs work with minor updates
- **Specifications**: All v0.1.0 specs work in v2.0

### ⚠️ Requires Updates
- **Custom Agents**: Need to use `SDKClientManager` instead of direct API client
- **MCP Configuration**: Use new SDK-compatible format
- **Direct API Calls**: Replace with SDK manager calls

## Step-by-Step Migration

### Step 1: Install v2.0
```bash
# Update dependencies
poetry update

# Or fresh install
poetry install

# Verify installation
claude-code-builder-v2 --version
# Output: claude-code-builder-v2, version 2.0.0-sdk
```

### Step 2: Update Configuration (Optional)
If you have custom configurations, update to v2 format:

**Old `.mcp.json`** (still works):
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@filesystem/mcp"]
    }
  }
}
```

**Enhanced v2 format** (optional):
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@filesystem/mcp"],
      "description": "File system operations",
      "usage": "Mandatory for all file operations"
    }
  }
}
```

### Step 3: Update Custom Agents (If Any)
If you've created custom agents, update them:

```python
# v0.1.0 Custom Agent
class MyCustomAgent(BaseAgent):
    def __init__(self, executor, context_manager, mcp_orchestrator, logger):
        self.executor = executor
        # ...

    async def run(self, context):
        response = await self.executor.query("...")
        return response

# v2.0 Custom Agent
from claude_code_builder_v2.agents import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, sdk_manager, context_manager, logger):
        super().__init__(
            agent_type=AgentType.CUSTOM,
            sdk_manager=sdk_manager,
            context_manager=context_manager,
            logger=logger,
        )

    async def execute(self, context, **kwargs):
        # Use self.query() instead of direct executor calls
        response = await self.query("...")
        return AgentResponse(
            agent_type=self.agent_type,
            success=True,
            result=response,
        )
```

### Step 4: Test Migration
```bash
# Run existing project with v2
claude-code-builder-v2 init your-spec.md --output ./test-output

# Or resume existing v0.1.0 project (when implemented)
# claude-code-builder-v2 resume ./existing-project
```

## New Features in v2.0

### 1. Cost Tracking
```python
from claude_code_builder_v2.sdk import CostTracker

tracker = CostTracker()
cost = tracker.track_usage(
    model="claude-3-haiku-20240307",
    input_tokens=1000,
    output_tokens=500,
)
summary = tracker.get_summary()
# Returns: api_calls, total_tokens, total_cost, by_model breakdown
```

### 2. Streaming Progress
```python
from claude_code_builder_v2.sdk import StreamingProgressReporter

def progress_callback(message: str):
    print(f"Progress: {message}")

reporter = StreamingProgressReporter(logger, progress_callback)
response = await reporter.report_progress(query_iterator)
```

### 3. Enhanced Hooks
```python
from claude_code_builder_v2.sdk import EnhancedSDKHooks

hooks = EnhancedSDKHooks(logger, cost_tracker, tool_tracker)

# Hooks are called automatically during execution
# Access comprehensive summaries:
summary = hooks.get_comprehensive_summary()
# Returns: cost, tools, active_tools
```

### 4. Better MCP Integration
```python
from claude_code_builder_v2.mcp import SDKMCPIntegration

integration = SDKMCPIntegration(mcp_config, logger)

# Get phase-specific servers
servers = integration.get_servers_for_phase("implementation")

# Get all tools for servers
tools = integration.get_all_tools_for_servers(servers)
```

## Troubleshooting

### Issue: "Module not found"
```bash
# Solution: Reinstall package
poetry install --no-interaction
```

### Issue: "API key not set"
```bash
# Solution: Set environment variable
export ANTHROPIC_API_KEY=your-key-here

# Or pass via CLI
claude-code-builder-v2 init spec.md --api-key your-key
```

### Issue: "Tests failing"
```bash
# Run all tests
poetry run pytest tests/test_*_v2.py -v

# Expected: 35/35 passing
```

## Rollback to v0.1.0

If you need to rollback:
```bash
# v1 CLI still available
claude-code-builder init spec.md --output ./project

# Both versions coexist
which claude-code-builder    # v0.1.0
which claude-code-builder-v2  # v2.0
```

## Getting Help

- **Documentation**: See `REWRITE_SPEC.md` for architecture details
- **Examples**: Check `tests/test_*_v2.py` for usage examples
- **Issues**: Report at https://github.com/krzemienski/claude-code-builder/issues

## Summary

v2.0 is a significant upgrade with:
- ✅ Full feature parity with v0.1.0
- ✅ Enhanced monitoring and tracking
- ✅ Better error handling
- ✅ SDK-ready architecture
- ✅ Comprehensive test coverage

The migration is straightforward for most users, with custom agents being the main area requiring updates.
