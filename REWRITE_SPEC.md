# Claude Code Builder v2.0: Agent SDK Rewrite Specification

**Document Version:** 1.0
**Date:** 2025-11-15
**Status:** Comprehensive Design & Implementation Plan

---

## Executive Summary

This document provides a complete specification for rewriting Claude Code Builder (CCB) v0.1.0 to leverage the **Claude Agent SDK for Python**. The rewrite maintains 100% feature parity with the current implementation while introducing significant architectural improvements, better maintainability, and enhanced capabilities through native SDK integration.

### Key Objectives

1. **Complete Rewrite**: Replace custom API client with Claude Agent SDK
2. **Feature Parity**: Maintain all existing functionality
3. **Enhanced Capabilities**: Leverage SDK-native features (streaming, hooks, subagents)
4. **Better Architecture**: Simplify codebase by using SDK patterns
5. **Improved MCP Integration**: Use SDK's built-in MCP support
6. **Developer Experience**: Better debugging, testing, and extensibility

---

## Table of Contents

1. [Current System Analysis](#current-system-analysis)
2. [Claude Agent SDK Capabilities](#claude-agent-sdk-capabilities)
3. [Architecture Design](#architecture-design)
4. [Component Mapping](#component-mapping)
5. [Data Models](#data-models)
6. [Implementation Plan](#implementation-plan)
7. [Migration Strategy](#migration-strategy)
8. [Testing Strategy](#testing-strategy)
9. [Success Criteria](#success-criteria)

---

## 1. Current System Analysis

### 1.1 Current Architecture Overview

**Total Codebase:** 11,929 lines of Python
**Core Components:** 43+ modules
**Agents:** 8 specialized agents
**Data Models:** 30+ Pydantic models
**CLI Commands:** 7 main commands

```
claude-code-builder (v0.1.0)
├── CLI Layer (Click + Rich)
├── Build Orchestrator
│   ├── Phase Executor
│   ├── Checkpoint Manager
│   └── Cost Tracker
├── Multi-Agent System
│   ├── SpecAnalyzer
│   ├── TaskGenerator
│   ├── InstructionBuilder
│   ├── CodeGenerator
│   ├── TestGenerator
│   ├── ReviewAgent
│   ├── ErrorHandler
│   └── DocumentationAgent
├── Core Infrastructure
│   ├── Context Manager (150K+ tokens)
│   ├── Logging System (structured + JSON)
│   ├── MCP Orchestrator
│   └── Output Manager
├── Executor (AsyncAnthropic)
│   ├── Tool definitions (hardcoded)
│   ├── Manual streaming
│   └── Custom tool execution
└── MCP Integration (External)
    ├── Filesystem (npx)
    ├── Memory (npx)
    ├── Context7 (npx)
    ├── Git (npx)
    └── Sequential-thinking (npx)
```

### 1.2 Current Strengths

✅ Comprehensive logging and tracking
✅ Advanced context management for large specs
✅ Robust checkpoint/resume system
✅ Rich CLI interface with progress tracking
✅ Well-defined data models with Pydantic v2
✅ Multi-agent architecture with clear responsibilities
✅ Cost tracking and budget enforcement
✅ MCP server orchestration

### 1.3 Current Limitations

❌ Custom API client reimplements SDK features
❌ Manual tool definition and execution
❌ Complex MCP server management (subprocess handling)
❌ No native streaming support
❌ Limited error recovery patterns
❌ Agent communication requires custom coordination
❌ Testing requires full system integration
❌ No built-in permission system
❌ Manual session management

### 1.4 Key Components to Preserve

**Must Keep:**
- All 30+ Pydantic data models
- Comprehensive logging system
- Context management for large specifications
- Checkpoint and resume functionality
- Cost tracking and budget enforcement
- CLI interface and UX
- Build orchestration logic
- Agent system prompt templates
- MCP validation and compliance checking

---

## 2. Claude Agent SDK Capabilities

### 2.1 Core SDK Features

#### 2.1.1 Dual Interaction Modes

**`query()` Function:**
- Stateless, session-per-call
- Async iterator support
- Perfect for one-off agent tasks
- Auto cleanup

**`ClaudeSDKClient` Class:**
- Stateful, persistent sessions
- Multi-turn conversations
- Context preservation across queries
- Explicit lifecycle management
- Interrupt capability

#### 2.1.2 Tool Integration

**`@tool()` Decorator:**
```python
@tool()
def analyze_spec(content: str) -> dict:
    """Analyze specification content."""
    # Type-safe, auto-validated
    return {"analysis": "..."}
```

**`create_sdk_mcp_server()`:**
- In-process MCP servers
- No subprocess management
- Native SDK integration
- Automatic tool namespacing

#### 2.1.3 Configuration System

**`ClaudeAgentOptions`:**
- Tool permissions (allowed/disallowed)
- System prompts (with presets)
- MCP server registration
- Permission modes
- Custom hooks
- Subagent definitions

#### 2.1.4 Advanced Features

**Streaming:**
- Native async iteration
- Real-time progress monitoring
- Tool call observation
- Thinking block visibility

**Hooks:**
- PreToolUse / PostToolUse
- UserPromptSubmit
- Stop / SubagentStop
- PreCompact

**Subagents:**
- Programmatic delegation
- Isolated tool access
- Model selection per agent
- Custom system prompts

**Permission System:**
- Declaration-based filtering
- Dynamic callbacks
- Input modification
- Execution blocking

### 2.2 SDK Advantages for CCB

1. **Simplified Codebase**: Remove ~2,000 lines of custom client code
2. **Better Tool Management**: No manual tool definitions
3. **Native MCP**: In-process servers, no subprocess hell
4. **Streaming by Default**: Real-time progress without custom code
5. **Error Handling**: SDK handles retries and failures
6. **Session Management**: Built-in conversation state
7. **Testing**: Mock SDK client instead of API calls
8. **Security**: Built-in permission system
9. **Maintenance**: SDK updates bring new features

---

## 3. Architecture Design

### 3.1 New System Architecture

```
claude-code-builder-v2 (SDK-based)
├── CLI Layer (Click + Rich) [PRESERVED]
├── SDK Integration Layer [NEW]
│   ├── SDKClientManager
│   │   ├── Session lifecycle
│   │   ├── Configuration management
│   │   └── Hook registration
│   ├── ToolRegistry [NEW]
│   │   ├── Custom @tool decorators
│   │   ├── MCP server creation
│   │   └── Permission management
│   └── SubagentFactory [NEW]
│       ├── Agent definitions
│       ├── Isolated contexts
│       └── Model selection
├── Build Orchestrator [ENHANCED]
│   ├── SDKPhaseExecutor [REFACTORED]
│   ├── Checkpoint Manager [PRESERVED]
│   └── Cost Tracker [ENHANCED]
├── Agent System [REFACTORED]
│   ├── SDK-based agents using query()/client
│   ├── Subagent delegation patterns
│   ├── Streaming progress reporting
│   └── Hook-based coordination
├── Core Infrastructure [PRESERVED]
│   ├── Context Manager [PRESERVED]
│   ├── Logging System [ENHANCED with SDK events]
│   ├── Data Models [PRESERVED]
│   └── Output Manager [PRESERVED]
├── MCP Integration [SIMPLIFIED]
│   ├── In-process MCP servers via SDK
│   ├── Native tool registration
│   └── No subprocess management
└── Testing Framework [NEW]
    ├── SDK client mocking
    ├── Agent unit tests
    └── Integration test harness
```

### 3.2 Component Interaction Flow

```
User Request (CLI)
    ↓
[Click Handler]
    ↓
[SDKClientManager] ← Creates configured client
    ↓
[BuildOrchestrator] ← Receives SDK client
    ↓
[SDKPhaseExecutor] ← Manages phase execution
    ↓
[Agent (via SDK query/client)]
    ├── Uses @tool functions
    ├── Leverages SDK streaming
    ├── Delegates to subagents
    └── Emits hook events
    ↓
[ToolRegistry] ← Executes tools
    ↓
[MCP Servers (in-process)]
    ↓
[Results] → [Checkpoint] → [Logging] → [CLI Output]
```

---

## 4. Component Mapping

### 4.1 Current → SDK Mapping

| Current Component | SDK Replacement | Changes |
|-------------------|----------------|---------|
| `ClaudeCodeExecutor` | `ClaudeSDKClient` + `query()` | Complete replacement, simplified |
| `BaseAgent.call_claude()` | `await query()` or `client.query()` | Use SDK methods directly |
| Tool definitions (dict) | `@tool()` decorator | Type-safe, auto-validated |
| `MCPOrchestrator` | `create_sdk_mcp_server()` | In-process, no subprocess |
| Manual streaming | SDK async iteration | Native support |
| Custom tool execution | SDK tool handler | Automatic |
| Agent coordination | Subagent delegation | Built-in SDK feature |
| Permission checking | SDK permission system | Native callbacks |
| Message history | SDK session state | Automatic management |
| Error handling | SDK error types | Structured exceptions |

### 4.2 Preserved Components

**Unchanged (Copy Forward):**
- All Pydantic models (`src/claude_code_builder/core/models.py`)
- All enums (`src/claude_code_builder/core/enums.py`)
- Base model hierarchy (`src/claude_code_builder/core/base_model.py`)
- Type definitions (`src/claude_code_builder/core/types.py`)
- Exception classes (`src/claude_code_builder/core/exceptions.py`)
- Configuration system (`src/claude_code_builder/core/config.py`)
- Output manager (`src/claude_code_builder/core/output_manager.py`)
- CLI commands structure (`src/claude_code_builder/cli/`)

**Enhanced (Adapt to SDK):**
- Logging system (add SDK event logging)
- Context manager (integrate with SDK session)
- Checkpoint system (track SDK session state)
- Cost tracking (parse SDK usage data)

**Refactored (Rewrite with SDK):**
- All agents (`src/claude_code_builder/agents/`)
- Phase executor (`src/claude_code_builder/executor/`)
- Build orchestrator (`src/claude_code_builder/executor/build_orchestrator.py`)
- MCP clients (`src/claude_code_builder/mcp/clients.py`)

**Deleted (SDK Provides):**
- `ClaudeCodeExecutor` class
- Manual tool definitions
- Subprocess MCP management
- Custom streaming logic

---

## 5. Data Models

### 5.1 Preserved Models (No Changes)

All existing Pydantic v2 models remain unchanged:

```python
# Core Models (30+)
- SpecAnalysis
- Task, Phase, TaskBreakdown
- ExecutionContext
- APICall (adapt to SDK format)
- ProjectMetadata, ProjectState
- AcceptanceCriteria, TestResult
- MCPValidation, MCPViolation
- RecoveryStrategy, RecoveryResult
- BuildMetrics, ResourceUsage
- Documentation, DocumentationSection
```

### 5.2 New SDK-Specific Models

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class SDKSessionContext(BaseModel):
    """Context for an SDK client session."""
    session_id: str
    client: ClaudeSDKClient  # Active SDK client
    options: ClaudeAgentOptions  # SDK configuration
    conversation_history: List[Dict[str, Any]]
    active_tools: List[str]
    current_cost: float
    started_at: datetime

class SDKAgentConfig(BaseModel):
    """Configuration for SDK-based agent."""
    agent_type: AgentType
    system_prompt: str
    allowed_tools: List[str]
    subagent_definitions: List[AgentDefinition]
    permission_mode: str = "default"
    enable_thinking: bool = True
    max_iterations: int = 10

class SDKToolCall(BaseModel):
    """SDK tool call record."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None
    timestamp: datetime

class SDKStreamChunk(BaseModel):
    """Streaming chunk from SDK."""
    chunk_type: str  # text, tool_use, tool_result, thinking
    content: Any
    timestamp: datetime
```

### 5.3 Modified Models

**APICall (Enhanced for SDK):**
```python
class APICall(TimestampedModel):
    """Record of an API call via SDK."""
    # Existing fields preserved
    # Add SDK-specific fields:
    sdk_session_id: Optional[str] = None
    stream_chunks: List[SDKStreamChunk] = Field(default_factory=list)
    thinking_blocks: List[str] = Field(default_factory=list)
    subagent_calls: List[UUID] = Field(default_factory=list)
    hook_events: List[str] = Field(default_factory=list)
```

**AgentResponse (Enhanced):**
```python
class AgentResponse(BaseModel):
    """Response from SDK-based agent execution."""
    # Existing fields preserved
    # Add SDK-specific:
    sdk_session_id: str
    stream_events: List[SDKStreamChunk]
    final_message: Dict[str, Any]  # SDK message format
    interrupted: bool = False
```

---

## 6. Implementation Plan

### 6.1 Phase 1: Foundation (Week 1)

**1.1 Project Setup**
- [ ] Create new branch: `rewrite/agent-sdk-v2`
- [ ] Update pyproject.toml dependencies
  ```toml
  [tool.poetry.dependencies]
  anthropic = "^0.40.0"  # Latest with SDK
  claude-agent-sdk = "^0.2.0"  # NEW
  # Remove: manual subprocess management libs
  ```
- [ ] Set up new module structure:
  ```
  src/claude_code_builder_v2/
  ├── sdk/           # NEW: SDK integration layer
  ├── agents/        # REFACTORED
  ├── core/          # PRESERVED (copy from v1)
  ├── executor/      # REFACTORED
  ├── mcp/           # SIMPLIFIED
  ├── cli/           # PRESERVED (minor updates)
  └── utils/         # PRESERVED
  ```

**1.2 SDK Integration Layer**
- [ ] Implement `SDKClientManager` class
  ```python
  class SDKClientManager:
      """Manages Claude SDK client lifecycle."""

      async def create_client(
          self,
          config: ExecutorConfig,
          mcp_servers: List[MCPServerConfig],
      ) -> ClaudeSDKClient:
          """Create configured SDK client with MCP servers."""

      async def create_stateless_query(
          self,
          prompt: str,
          tools: List[str],
          system_prompt: str,
      ) -> AsyncIterator:
          """Execute stateless query."""

      def register_hooks(self, client: ClaudeSDKClient) -> None:
          """Register SDK hooks for logging and tracking."""
  ```

- [ ] Implement `ToolRegistry` class
  ```python
  class ToolRegistry:
      """Registry for SDK tools and MCP servers."""

      def register_tool(self, func: Callable) -> None:
          """Register a @tool decorated function."""

      async def create_mcp_servers(
          self,
          configs: List[MCPServerConfig],
      ) -> List[Any]:
          """Create in-process MCP servers."""

      def get_tool_definitions(self) -> List[ToolDefinition]:
          """Get all registered tool definitions."""
  ```

- [ ] Implement `SubagentFactory` class
  ```python
  class SubagentFactory:
      """Factory for creating SDK subagent definitions."""

      def create_agent_definition(
          self,
          agent_type: AgentType,
          system_prompt: str,
          allowed_tools: List[str],
      ) -> AgentDefinition:
          """Create subagent definition for SDK."""
  ```

**1.3 Copy Preserved Components**
- [ ] Copy all models from v1 to v2 (no changes)
- [ ] Copy enums (no changes)
- [ ] Copy base models (no changes)
- [ ] Copy types (no changes)
- [ ] Copy exceptions (add SDK-specific exceptions)
- [ ] Copy config system (enhance with SDK options)

### 6.2 Phase 2: Agent System Rewrite (Week 2)

**2.1 New BaseAgent (SDK-based)**
```python
from claude_agent_sdk import query, ClaudeSDKClient
from typing import AsyncIterator

class BaseAgent(ABC):
    """Base agent using Claude Agent SDK."""

    def __init__(
        self,
        agent_type: AgentType,
        sdk_manager: SDKClientManager,
        context_manager: ContextManager,
        logger: ComprehensiveLogger,
        config: Optional[ExecutorConfig] = None,
    ) -> None:
        self.agent_type = agent_type
        self.sdk_manager = sdk_manager
        self.context_manager = context_manager
        self.logger = logger
        self.config = config or ExecutorConfig()

    @abstractmethod
    async def execute(
        self,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute agent task using SDK."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        pass

    @abstractmethod
    def get_allowed_tools(self) -> List[str]:
        """Get allowed tools for this agent."""
        pass

    async def run(
        self,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> AgentResponse:
        """Run agent with SDK integration."""
        start_time = time.time()

        # Create SDK client for this agent
        client = await self.sdk_manager.create_client(
            config=self.config,
            mcp_servers=self._get_required_mcp_servers(),
        )

        # Configure agent-specific options
        options = ClaudeAgentOptions(
            system_prompt=self.get_system_prompt(),
            allowed_tools=self.get_allowed_tools(),
            permission_mode="default",
        )

        try:
            # Execute with SDK
            response = await self.execute(context, client=client, **kwargs)

            # Track metrics
            response.duration_seconds = time.time() - start_time

            # Log completion
            self.logger.logger.info(
                "agent_completed",
                agent_type=self.agent_type.value,
                success=response.success,
            )

            return response

        except Exception as e:
            # Error handling with SDK exceptions
            self.logger.logger.error(
                "agent_failed",
                agent_type=self.agent_type.value,
                error=str(e),
            )
            raise
        finally:
            # Cleanup SDK client
            await client.disconnect()
```

**2.2 Rewrite Each Agent**

For each agent (8 total):

**Example: SpecAnalyzer**
```python
class SpecAnalyzer(BaseAgent):
    """Analyzes specifications using Claude SDK."""

    def get_system_prompt(self) -> str:
        return """You are a specification analysis expert.
        Analyze the provided specification and extract:
        - Project type and complexity
        - Key features and requirements
        - Technical requirements
        - Identified risks
        """

    def get_allowed_tools(self) -> List[str]:
        return [
            "mcp__memory__create_entities",
            "mcp__memory__search_nodes",
            "mcp__sequential_thinking__solve_problem",
        ]

    async def execute(
        self,
        context: ExecutionContext,
        client: ClaudeSDKClient,
        specification: str,
        **kwargs,
    ) -> AgentResponse:
        """Execute specification analysis using SDK."""

        # Prepare prompt
        prompt = f"""Analyze this specification:

{specification}

Provide a structured analysis including:
1. Project type
2. Complexity assessment
3. Key features
4. Technical requirements
5. Identified risks
"""

        # Use SDK to query
        response_text = ""
        tool_calls = []

        async for chunk in await query(
            prompt=prompt,
            system=self.get_system_prompt(),
            tools=self.get_allowed_tools(),
            model=self.config.model,
        ):
            if chunk.type == "text":
                response_text += chunk.content
            elif chunk.type == "tool_use":
                tool_calls.append(chunk)

        # Parse response into SpecAnalysis model
        analysis = self._parse_analysis(response_text)

        return AgentResponse(
            agent_type=self.agent_type,
            success=True,
            result=analysis,
            sdk_session_id=client.session_id if client else "stateless",
        )
```

**Agents to Rewrite:**
1. [ ] SpecAnalyzer
2. [ ] TaskGenerator
3. [ ] InstructionBuilder
4. [ ] CodeGenerator
5. [ ] TestGenerator
6. [ ] ReviewAgent
7. [ ] ErrorHandler
8. [ ] DocumentationAgent

### 6.3 Phase 3: Executor System (Week 3)

**3.1 SDK Phase Executor**
```python
class SDKPhaseExecutor:
    """Executes build phases using SDK agents."""

    def __init__(
        self,
        sdk_manager: SDKClientManager,
        context_manager: ContextManager,
        checkpoint_manager: CheckpointManager,
        logger: ComprehensiveLogger,
    ) -> None:
        self.sdk_manager = sdk_manager
        self.context_manager = context_manager
        self.checkpoint_manager = checkpoint_manager
        self.logger = logger

        # Initialize agents with SDK
        self._init_agents()

    def _init_agents(self) -> None:
        """Initialize all SDK-based agents."""
        self.agents = {
            AgentType.SPEC_ANALYZER: SpecAnalyzer(
                AgentType.SPEC_ANALYZER,
                self.sdk_manager,
                self.context_manager,
                self.logger,
            ),
            # ... other agents
        }

    async def execute_phase(
        self,
        phase: Phase,
        context: ExecutionContext,
    ) -> PhaseResult:
        """Execute a single phase with SDK."""

        self.logger.print_info(f"Executing phase: {phase.name}")

        # Create persistent SDK client for phase
        client = await self.sdk_manager.create_client(
            config=self.executor_config,
            mcp_servers=self._get_phase_mcp_servers(phase),
        )

        try:
            results = []

            for task in phase.tasks:
                # Get agent for task
                agent = self.agents.get(task.assigned_agent)

                if not agent:
                    raise ValueError(f"No agent for {task.assigned_agent}")

                # Execute task with SDK
                result = await agent.run(context, client=client)
                results.append(result)

                # Checkpoint after each task
                await self.checkpoint_manager.save_checkpoint(
                    phase=phase,
                    task=task,
                    result=result,
                )

            return PhaseResult(
                phase_id=phase.id,
                success=all(r.success for r in results),
                results=results,
            )

        finally:
            # Cleanup
            await client.disconnect()
```

**3.2 Build Orchestrator (Enhanced)**
```python
class BuildOrchestrator:
    """Orchestrates complete build using SDK."""

    async def build(
        self,
        specification: str,
        config: BuildConfig,
    ) -> BuildResult:
        """Execute complete build process."""

        # Initialize SDK components
        self.sdk_manager = SDKClientManager(config)
        self.phase_executor = SDKPhaseExecutor(
            self.sdk_manager,
            self.context_manager,
            self.checkpoint_manager,
            self.logger,
        )

        # Setup MCP servers (in-process via SDK)
        await self.sdk_manager.setup_mcp_servers(config.mcp_servers)

        try:
            # Execute build phases
            results = await self._execute_all_phases(specification, config)

            return BuildResult(
                success=all(r.success for r in results),
                phases=results,
                metrics=self._collect_metrics(),
            )

        finally:
            # Cleanup SDK resources
            await self.sdk_manager.shutdown()
```

### 6.4 Phase 4: MCP Integration (Week 3)

**4.1 In-Process MCP Servers**
```python
from claude_agent_sdk import create_sdk_mcp_server

class SDKMCPIntegration:
    """Manages in-process MCP servers via SDK."""

    async def create_servers(
        self,
        configs: List[MCPServerConfig],
    ) -> Dict[str, Any]:
        """Create all MCP servers in-process."""

        servers = {}

        for config in configs:
            if config.server_type == MCPServer.FILESYSTEM:
                servers['filesystem'] = await self._create_filesystem_server(config)
            elif config.server_type == MCPServer.MEMORY:
                servers['memory'] = await self._create_memory_server(config)
            # ... other servers

        return servers

    async def _create_filesystem_server(
        self,
        config: MCPServerConfig,
    ) -> Any:
        """Create in-process filesystem MCP server."""
        return await create_sdk_mcp_server(
            name="filesystem",
            tools=[
                self._create_read_file_tool(),
                self._create_write_file_tool(),
                self._create_list_directory_tool(),
            ],
        )

    def _create_read_file_tool(self) -> Callable:
        """Create read_file tool using @tool decorator."""

        @tool()
        async def read_file(path: str) -> str:
            """Read file contents."""
            async with aiofiles.open(path, 'r') as f:
                return await f.read()

        return read_file
```

**4.2 Remove Subprocess Management**
- [ ] Delete `MCPServerManager` (subprocess handling)
- [ ] Delete `MCPConnection` (process tracking)
- [ ] Delete manual health checking
- [ ] Replace with SDK in-process servers

### 6.5 Phase 5: Enhanced Features (Week 4)

**5.1 Streaming Progress**
```python
class StreamingProgressReporter:
    """Reports real-time progress via SDK streaming."""

    async def report_progress(
        self,
        query_iterator: AsyncIterator,
        progress_callback: Callable,
    ) -> None:
        """Monitor SDK query stream and report progress."""

        async for chunk in query_iterator:
            if chunk.type == "thinking":
                progress_callback(f"Thinking: {chunk.content[:50]}...")
            elif chunk.type == "tool_use":
                progress_callback(f"Using tool: {chunk.tool_name}")
            elif chunk.type == "text":
                progress_callback(f"Response: {chunk.content[:50]}...")
```

**5.2 SDK Hooks for Tracking**
```python
class CCBHooks:
    """SDK hooks for CCB integration."""

    def __init__(self, logger: ComprehensiveLogger, cost_tracker: CostTracker):
        self.logger = logger
        self.cost_tracker = cost_tracker

    async def pre_tool_use(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Log before tool execution."""
        self.logger.logger.info(
            "sdk_tool_use",
            tool=tool_name,
            arguments=arguments,
        )
        return arguments  # Can modify

    async def post_tool_use(
        self,
        tool_name: str,
        result: Any,
    ) -> None:
        """Track after tool execution."""
        self.logger.logger.info(
            "sdk_tool_result",
            tool=tool_name,
            success=result.get("success", True),
        )

    async def user_prompt_submit(
        self,
        prompt: str,
    ) -> str:
        """Log and potentially modify prompts."""
        self.logger.logger.info("sdk_prompt", length=len(prompt))
        return prompt
```

**5.3 Subagent Delegation**
```python
class SubagentCoordinator:
    """Coordinates subagent delegation."""

    async def delegate_to_subagent(
        self,
        parent_agent: BaseAgent,
        task: str,
        subagent_type: AgentType,
    ) -> AgentResponse:
        """Delegate task to specialized subagent."""

        # Create subagent definition
        subagent_def = AgentDefinition(
            name=subagent_type.value,
            description=self._get_agent_description(subagent_type),
            system_prompt=self._get_agent_prompt(subagent_type),
            allowed_tools=self._get_agent_tools(subagent_type),
        )

        # Execute via SDK subagent delegation
        result = await parent_agent.delegate(subagent_def, task)

        return AgentResponse(
            agent_type=subagent_type,
            success=True,
            result=result,
        )
```

### 6.6 Phase 6: CLI Integration (Week 4)

**6.1 Update CLI Commands**
- [ ] Minimal changes to CLI interface
- [ ] Update internal calls to use SDK components
- [ ] Enhance progress reporting with SDK streams

**6.2 Enhanced Status Command**
```python
@cli.command()
async def status(project_dir: Path) -> None:
    """Show SDK session status."""

    # Load project state
    state = load_project_state(project_dir)

    # Show SDK-specific info
    console.print(Panel(f"""
    SDK Session: {state.sdk_session_id}
    Active Client: {state.client_active}
    Stream Events: {len(state.stream_events)}
    Tool Calls: {len(state.tool_calls)}
    Subagents Used: {len(state.subagent_calls)}
    """))
```

### 6.7 Phase 7: Testing (Week 5)

**7.1 SDK Mock Testing**
```python
import pytest
from unittest.mock import AsyncMock, patch

class TestSpecAnalyzer:
    """Test SpecAnalyzer with mocked SDK."""

    @pytest.mark.asyncio
    async def test_analyze_simple_spec(self):
        """Test specification analysis."""

        # Mock SDK client
        mock_client = AsyncMock(spec=ClaudeSDKClient)
        mock_client.query.return_value = self._mock_query_response()

        # Create agent with mocked SDK
        agent = SpecAnalyzer(
            AgentType.SPEC_ANALYZER,
            sdk_manager=MockSDKManager(mock_client),
            context_manager=MockContextManager(),
            logger=MockLogger(),
        )

        # Execute
        result = await agent.run(
            context=create_test_context(),
            specification="Build a REST API",
        )

        # Assert
        assert result.success
        assert result.result.project_type == ProjectType.API
```

**7.2 Integration Tests**
```python
class TestBuildOrchestrator:
    """Integration test with real SDK."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_build_simple_project(self):
        """Test complete build with SDK."""

        # Use real SDK but with minimal spec
        spec = """
        # Simple CLI Tool
        Build a Python CLI that says hello.
        """

        config = BuildConfig(
            model="claude-3-haiku-20240307",  # Cheap for tests
            max_cost=0.10,
        )

        orchestrator = BuildOrchestrator(config)
        result = await orchestrator.build(spec, config)

        assert result.success
        assert result.metrics.total_cost < 0.10
```

### 6.8 Phase 8: Documentation & Migration (Week 5)

**8.1 Update Documentation**
- [ ] Update README.md with SDK mentions
- [ ] Update CLAUDE.md with new architecture
- [ ] Create MIGRATION.md for v1 → v2
- [ ] Update API documentation
- [ ] Add SDK-specific examples

**8.2 Migration Guide**
```markdown
# Migrating from v0.1.0 to v2.0 (SDK-based)

## Breaking Changes
- Direct API client access removed
- MCP server configuration format changed
- Agent initialization requires SDK manager

## Compatibility
- All project states are compatible
- Checkpoints can be resumed
- Configuration files need updates

## Step-by-Step Migration
1. Update dependencies: `poetry update`
2. Update .mcp.json (new format)
3. Update custom agents (if any)
4. Test with dry-run: `claude-code-builder build spec.md --dry-run`
```

---

## 7. Migration Strategy

### 7.1 Backwards Compatibility

**Project States:**
- [ ] v2 can read v1 project states
- [ ] Checkpoint format unchanged
- [ ] Resume from v1 checkpoints works

**Configuration:**
- [ ] Auto-migrate old config files
- [ ] Support both old and new MCP formats
- [ ] Deprecation warnings for old patterns

### 7.2 Coexistence Strategy

**Parallel Versions:**
```
claude-code-builder (v1 - stable)
claude-code-builder-v2 (v2 - beta)
```

**After Validation:**
```
claude-code-builder → v2 (default)
claude-code-builder-legacy → v1 (deprecated)
```

### 7.3 Data Migration

**Automatic Migration Script:**
```python
async def migrate_project_v1_to_v2(project_dir: Path) -> None:
    """Migrate v1 project to v2 format."""

    # Load v1 state
    v1_state = load_v1_project_state(project_dir)

    # Convert to v2
    v2_state = ProjectState(
        # Copy all fields
        metadata=v1_state.metadata,
        current_phase=v1_state.current_phase,
        # ... etc

        # Add SDK fields
        sdk_session_id=str(uuid4()),
        sdk_version="0.2.0",
    )

    # Save v2 state
    save_project_state(project_dir, v2_state)
```

---

## 8. Testing Strategy

### 8.1 Unit Testing

**Coverage Target:** 90%+

**Test Categories:**
1. **SDK Integration Tests**
   - Client creation
   - Tool registration
   - Hook execution
   - Subagent delegation

2. **Agent Tests**
   - System prompt generation
   - Tool selection
   - Response parsing
   - Error handling

3. **Core Logic Tests**
   - Context management
   - Checkpoint/resume
   - Cost tracking
   - Logging

### 8.2 Integration Testing

**Real SDK Tests:**
- Use actual Claude SDK
- Small/cheap models (Haiku)
- Minimal specifications
- Budget limits ($0.10 per test)

### 8.3 Functional Testing

**End-to-End:**
- Build simple projects
- Verify output quality
- Test resume functionality
- Validate MCP integration

### 8.4 Performance Testing

**Benchmarks:**
- Compare v1 vs v2 performance
- Measure SDK overhead
- Token usage comparison
- Cost analysis

---

## 9. Success Criteria

### 9.1 Functional Parity

✅ All v1 features work in v2
✅ All CLI commands functional
✅ Checkpoint/resume working
✅ Cost tracking accurate
✅ MCP integration functional
✅ All 8 agents operational

### 9.2 Performance

✅ Build speed within 10% of v1
✅ Token usage within 5% of v1
✅ Memory usage reduced (no subprocesses)
✅ Startup time < 2 seconds

### 9.3 Code Quality

✅ Test coverage > 90%
✅ Type checking passes (mypy strict)
✅ Linting passes (ruff)
✅ Formatting consistent (black)
✅ Documentation complete

### 9.4 Developer Experience

✅ Easier to extend (use SDK patterns)
✅ Better debugging (SDK error messages)
✅ Simpler testing (mock SDK client)
✅ Clear architecture (SDK abstractions)

### 9.5 Production Readiness

✅ No regressions from v1
✅ Migration guide complete
✅ Rollback plan documented
✅ Performance validated
✅ Security audit passed

---

## 10. Risks & Mitigations

### 10.1 Technical Risks

**Risk: SDK API Changes**
- Mitigation: Pin SDK version, comprehensive tests
- Fallback: Vendor SDK code if needed

**Risk: Performance Regression**
- Mitigation: Extensive benchmarking before release
- Fallback: Keep v1 available

**Risk: MCP In-Process Issues**
- Mitigation: Thorough MCP testing
- Fallback: Hybrid approach (external + in-process)

**Risk: Breaking Changes**
- Mitigation: Maintain backwards compatibility
- Fallback: Migration tools

### 10.2 Timeline Risks

**Risk: Scope Creep**
- Mitigation: Strict feature parity focus
- Fallback: Release in phases (beta → stable)

**Risk: Dependencies**
- Mitigation: SDK is stable and documented
- Fallback: Direct Anthropic API if needed

---

## 11. Timeline Summary

**Total Duration: 5 weeks**

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Foundation | SDK layer, project structure, preserved components |
| 2 | Agents | All 8 agents rewritten with SDK |
| 3 | Executor | Phase executor, orchestrator, MCP integration |
| 4 | Enhancement | Streaming, hooks, CLI updates |
| 5 | Testing & Docs | Tests, documentation, migration guide |

**After Week 5:**
- Beta release for testing
- Community feedback
- Performance tuning
- Stable release (v2.0.0)

---

## 12. Conclusion

This rewrite leverages the Claude Agent SDK to create a more maintainable, testable, and feature-rich version of Claude Code Builder while preserving all existing functionality. The SDK-based architecture provides:

- **Simplified codebase**: ~2,000 fewer lines
- **Better maintainability**: Use SDK patterns instead of custom code
- **Enhanced features**: Native streaming, hooks, subagents
- **Improved testing**: Mock SDK instead of API calls
- **Future-proof**: Benefit from SDK updates

The rewrite is structured to minimize risk through phased implementation, comprehensive testing, and backwards compatibility. All existing projects can be seamlessly migrated to v2.

---

**Next Steps:**
1. Review and approve this specification
2. Set up development branch
3. Begin Phase 1 implementation
4. Regular progress reviews (weekly)
5. Beta release after Week 5
6. Community testing and feedback
7. Stable v2.0.0 release

**Document Maintained By:** Claude Code Builder Team
**Last Updated:** 2025-11-15
**Version:** 1.0 (Draft for Review)
