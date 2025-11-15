# Claude Code Builder v2.0: Implementation Guide

**Document Type:** Step-by-Step Implementation Guide
**Version:** 1.0
**For:** Development Team
**Date:** 2025-11-15

---

## Quick Start

This guide provides detailed, actionable steps for implementing the Claude Code Builder v2.0 rewrite based on the Claude Agent SDK.

**Prerequisites:**
- Read `REWRITE_SPEC.md` (complete specification)
- Read `TECHNICAL_ARCHITECTURE.md` (technical design)
- Python 3.11+ installed
- Poetry installed
- Access to Anthropic API key

---

## Phase 1: Foundation Setup (Days 1-5)

### Day 1: Project Structure

**Step 1.1: Create Development Branch**
```bash
cd /home/user/claude-code-builder
git checkout -b rewrite/agent-sdk-v2
git push -u origin rewrite/agent-sdk-v2
```

**Step 1.2: Update Dependencies**

Edit `pyproject.toml`:
```toml
[tool.poetry.dependencies]
python = ">=3.11,<3.14"
anthropic = "^0.40.0"  # Update to latest
# Add new dependencies:
mcp-sdk = "^0.2.0"  # If available

# Keep existing:
click = "^8.1.7"
rich = "^13.7.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
aiofiles = "^23.2.1"
structlog = "^24.1.0"
# ... rest unchanged
```

Install:
```bash
poetry install
```

**Step 1.3: Create New Module Structure**

```bash
# Create v2 structure alongside v1
mkdir -p src/claude_code_builder_v2/{sdk,agents,core,executor,mcp,cli,utils,testing}

# Create __init__.py files
touch src/claude_code_builder_v2/__init__.py
touch src/claude_code_builder_v2/sdk/__init__.py
touch src/claude_code_builder_v2/agents/__init__.py
touch src/claude_code_builder_v2/core/__init__.py
touch src/claude_code_builder_v2/executor/__init__.py
touch src/claude_code_builder_v2/mcp/__init__.py
touch src/claude_code_builder_v2/cli/__init__.py
touch src/claude_code_builder_v2/utils/__init__.py
touch src/claude_code_builder_v2/testing/__init__.py
```

**Step 1.4: Copy Preserved Components**

```bash
# Copy data models (no changes needed)
cp src/claude_code_builder/core/models.py src/claude_code_builder_v2/core/
cp src/claude_code_builder/core/enums.py src/claude_code_builder_v2/core/
cp src/claude_code_builder/core/base_model.py src/claude_code_builder_v2/core/
cp src/claude_code_builder/core/types.py src/claude_code_builder_v2/core/
cp src/claude_code_builder/core/exceptions.py src/claude_code_builder_v2/core/

# Copy configuration (will enhance later)
cp src/claude_code_builder/core/config.py src/claude_code_builder_v2/core/

# Copy infrastructure
cp src/claude_code_builder/core/output_manager.py src/claude_code_builder_v2/core/
cp src/claude_code_builder/core/context_manager.py src/claude_code_builder_v2/core/
cp src/claude_code_builder/core/logging_system.py src/claude_code_builder_v2/core/
```

### Day 2-3: SDK Integration Layer

**Create: `src/claude_code_builder_v2/sdk/client_manager.py`**

```python
"""SDK Client Manager for CCB v2."""

import asyncio
from typing import Dict, List, Optional, AsyncIterator, Any
from uuid import uuid4

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from claude_code_builder_v2.core.config import ExecutorConfig
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class ClaudeAgentOptions(BaseModel):
    """Options for Claude Agent SDK client."""
    system_prompt: str
    allowed_tools: List[str]
    model: str = "claude-3-opus-20240229"
    max_tokens: int = 4096
    temperature: float = 0.3
    permission_mode: str = "default"


class SDKClientManager:
    """
    Manages Claude SDK client lifecycle.

    This is the central point for all SDK interactions in CCB v2.
    """

    def __init__(
        self,
        config: ExecutorConfig,
        logger: ComprehensiveLogger,
    ) -> None:
        """Initialize SDK client manager."""
        self.config = config
        self.logger = logger

        # SDK client (using Anthropic's AsyncAnthropic for now)
        # Note: Will be replaced with actual Claude Agent SDK when available
        self.client = AsyncAnthropic(api_key=config.api_key)

        # Track active sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        # Tool and hook registries
        from claude_code_builder_v2.sdk.tool_registry import ToolRegistry
        from claude_code_builder_v2.sdk.hook_registry import HookRegistry
        from claude_code_builder_v2.sdk.subagent_factory import SubagentFactory

        self.tool_registry = ToolRegistry(logger)
        self.hook_registry = HookRegistry(logger)
        self.subagent_factory = SubagentFactory(config)

    async def create_session(
        self,
        session_id: str,
        agent_options: ClaudeAgentOptions,
    ) -> Dict[str, Any]:
        """
        Create a new SDK session.

        Args:
            session_id: Unique session identifier
            agent_options: SDK configuration for this session

        Returns:
            Session context dictionary
        """
        session_ctx = {
            "session_id": session_id,
            "options": agent_options,
            "messages": [],
            "tools_used": [],
            "started_at": asyncio.get_event_loop().time(),
        }

        self.active_sessions[session_id] = session_ctx

        self.logger.logger.info(
            "sdk_session_created",
            session_id=session_id,
            model=agent_options.model,
        )

        return session_ctx

    async def query_stateless(
        self,
        prompt: str,
        system_prompt: str,
        tools: List[str],
        model: Optional[str] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a stateless query.

        This is equivalent to SDK's query() function.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            tools: List of allowed tool names
            model: Optional model override

        Yields:
            Response chunks
        """
        model = model or self.config.model

        # Get tool definitions
        tool_defs = self.tool_registry.get_tool_definitions(tools)

        # Prepare messages
        messages = [{"role": "user", "content": prompt}]

        # Log request
        self.logger.logger.info(
            "sdk_stateless_query",
            model=model,
            tools=tools,
            prompt_length=len(prompt),
        )

        # Make API call (simulating SDK behavior)
        try:
            response = await self.client.messages.create(
                model=model,
                messages=messages,
                system=system_prompt,
                tools=tool_defs if tool_defs else None,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stream=True,
            )

            # Stream response
            async for chunk in response:
                # Convert to SDK-like chunk format
                yield self._convert_chunk(chunk)

        except Exception as e:
            self.logger.logger.error(
                "sdk_query_error",
                error=str(e),
                exc_info=True,
            )
            raise

    async def query_with_session(
        self,
        session_id: str,
        prompt: str,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute query with existing session.

        This maintains conversation history.

        Args:
            session_id: Existing session ID
            prompt: User prompt

        Yields:
            Response chunks
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session_ctx = self.active_sessions[session_id]
        options = session_ctx["options"]

        # Add message to history
        session_ctx["messages"].append({
            "role": "user",
            "content": prompt,
        })

        # Execute query
        async for chunk in self.query_stateless(
            prompt=prompt,
            system_prompt=options.system_prompt,
            tools=options.allowed_tools,
            model=options.model,
        ):
            yield chunk

    def _convert_chunk(self, chunk: Any) -> Dict[str, Any]:
        """Convert Anthropic API chunk to SDK-like format."""
        # This simulates what the actual SDK would return
        chunk_type = getattr(chunk, "type", "unknown")

        if chunk_type == "content_block_delta":
            return {
                "type": "text",
                "content": getattr(chunk.delta, "text", ""),
            }
        elif chunk_type == "message_start":
            return {
                "type": "start",
                "usage": getattr(chunk.message, "usage", {}),
            }
        else:
            return {
                "type": chunk_type,
                "data": chunk,
            }

    async def close_session(self, session_id: str) -> None:
        """Close and cleanup session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

            self.logger.logger.info(
                "sdk_session_closed",
                session_id=session_id,
            )

    async def shutdown(self) -> None:
        """Shutdown all sessions and cleanup."""
        for session_id in list(self.active_sessions.keys()):
            await self.close_session(session_id)

        await self.client.close()
```

**Create: `src/claude_code_builder_v2/sdk/tool_registry.py`**

```python
"""Tool Registry for SDK."""

from typing import Dict, List, Callable, Any, Optional
import inspect
from functools import wraps

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


def tool(description: Optional[str] = None):
    """
    Decorator to mark a function as an SDK tool.

    Usage:
        @tool("Description of what this tool does")
        async def my_tool(arg1: str, arg2: int) -> dict:
            return {"result": "..."}
    """
    def decorator(func: Callable) -> Callable:
        # Extract function signature
        sig = inspect.signature(func)

        # Build JSON schema from type hints
        schema = _build_schema_from_signature(sig)

        # Add metadata
        func._is_tool = True
        func._tool_description = description or func.__doc__ or ""
        func._tool_schema = schema

        return func

    return decorator


def _build_schema_from_signature(sig: inspect.Signature) -> Dict[str, Any]:
    """Build JSON schema from function signature."""
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        # Get type hint
        param_type = param.annotation

        # Convert to JSON schema type
        json_type = _python_type_to_json_type(param_type)

        properties[param_name] = {"type": json_type}

        # Check if required (no default)
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _python_type_to_json_type(py_type: Any) -> str:
    """Convert Python type to JSON schema type."""
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    return type_map.get(py_type, "string")


class ToolRegistry:
    """Registry for SDK tools."""

    def __init__(self, logger: ComprehensiveLogger) -> None:
        """Initialize tool registry."""
        self.logger = logger
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool function.

        Args:
            name: Tool name
            func: Tool function (should be @tool decorated)
        """
        if not getattr(func, "_is_tool", False):
            raise ValueError(f"Function {name} is not decorated with @tool")

        self.tools[name] = func
        self.tool_metadata[name] = {
            "description": func._tool_description,
            "schema": func._tool_schema,
        }

        self.logger.logger.debug(
            "tool_registered",
            tool=name,
        )

    def get_tool_definitions(self, tool_names: List[str]) -> List[Dict[str, Any]]:
        """
        Get tool definitions for SDK.

        Args:
            tool_names: List of tool names

        Returns:
            List of tool definitions in SDK format
        """
        definitions = []

        for name in tool_names:
            if name in self.tool_metadata:
                metadata = self.tool_metadata[name]
                definitions.append({
                    "name": name,
                    "description": metadata["description"],
                    "input_schema": metadata["schema"],
                })

        return definitions

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """
        Execute a tool.

        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        tool_func = self.tools[tool_name]

        # Execute tool
        try:
            if inspect.iscoroutinefunction(tool_func):
                result = await tool_func(**arguments)
            else:
                result = tool_func(**arguments)

            return result

        except Exception as e:
            self.logger.logger.error(
                "tool_execution_error",
                tool=tool_name,
                error=str(e),
                exc_info=True,
            )
            raise
```

**Create: `src/claude_code_builder_v2/sdk/hook_registry.py`**

```python
"""Hook Registry for SDK events."""

from typing import Dict, Any, Callable, List
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class HookRegistry:
    """Registry for SDK hooks."""

    def __init__(self, logger: ComprehensiveLogger) -> None:
        """Initialize hook registry."""
        self.logger = logger
        self.hooks: Dict[str, List[Callable]] = {
            "pre_tool_use": [],
            "post_tool_use": [],
            "user_prompt_submit": [],
        }

    def register_hook(self, event: str, callback: Callable) -> None:
        """Register a hook callback."""
        if event not in self.hooks:
            raise ValueError(f"Unknown hook event: {event}")

        self.hooks[event].append(callback)

    async def pre_tool_use(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Hook called before tool execution."""
        self.logger.logger.info(
            "hook_pre_tool_use",
            tool=tool_name,
            arguments=arguments,
        )

        # Execute registered callbacks
        for callback in self.hooks["pre_tool_use"]:
            arguments = await callback(tool_name, arguments, context)

        return arguments

    async def post_tool_use(
        self,
        tool_name: str,
        result: Any,
        context: Dict[str, Any],
    ) -> None:
        """Hook called after tool execution."""
        self.logger.logger.info(
            "hook_post_tool_use",
            tool=tool_name,
            success=not isinstance(result, Exception),
        )

        # Execute registered callbacks
        for callback in self.hooks["post_tool_use"]:
            await callback(tool_name, result, context)

    async def user_prompt_submit(
        self,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """Hook called before prompt submission."""
        self.logger.logger.info(
            "hook_user_prompt",
            prompt_length=len(prompt),
        )

        # Execute registered callbacks
        for callback in self.hooks["user_prompt_submit"]:
            prompt = await callback(prompt, context)

        return prompt
```

**Create: `src/claude_code_builder_v2/sdk/subagent_factory.py`**

```python
"""Subagent Factory for SDK."""

from typing import Dict, List, Optional
from pydantic import BaseModel

from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.config import ExecutorConfig


class AgentDefinition(BaseModel):
    """SDK Agent Definition."""
    name: str
    description: str
    system_prompt: str
    allowed_tools: List[str]
    model: str


class SubagentFactory:
    """Factory for creating subagent definitions."""

    def __init__(self, config: ExecutorConfig) -> None:
        """Initialize subagent factory."""
        self.config = config
        self.definitions: Dict[AgentType, AgentDefinition] = {}

    def create_definition(
        self,
        agent_type: AgentType,
        system_prompt: str,
        allowed_tools: List[str],
        model: Optional[str] = None,
    ) -> AgentDefinition:
        """Create agent definition."""
        definition = AgentDefinition(
            name=agent_type.value,
            description=self._get_description(agent_type),
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            model=model or self.config.model,
        )

        self.definitions[agent_type] = definition
        return definition

    def _get_description(self, agent_type: AgentType) -> str:
        """Get agent description."""
        descriptions = {
            AgentType.SPEC_ANALYZER: "Analyzes project specifications",
            AgentType.TASK_GENERATOR: "Generates task breakdowns",
            AgentType.INSTRUCTION_BUILDER: "Builds implementation instructions",
            AgentType.CODE_GENERATOR: "Generates production code",
            AgentType.TEST_GENERATOR: "Creates test suites",
            AgentType.REVIEW_AGENT: "Reviews code quality",
            AgentType.ERROR_HANDLER: "Handles and recovers from errors",
            AgentType.DOCUMENTATION_AGENT: "Generates documentation",
        }
        return descriptions.get(agent_type, "Agent")
```

**Create: `src/claude_code_builder_v2/sdk/__init__.py`**

```python
"""SDK Integration Layer for CCB v2."""

from claude_code_builder_v2.sdk.client_manager import (
    SDKClientManager,
    ClaudeAgentOptions,
)
from claude_code_builder_v2.sdk.tool_registry import ToolRegistry, tool
from claude_code_builder_v2.sdk.hook_registry import HookRegistry
from claude_code_builder_v2.sdk.subagent_factory import SubagentFactory, AgentDefinition

__all__ = [
    "SDKClientManager",
    "ClaudeAgentOptions",
    "ToolRegistry",
    "tool",
    "HookRegistry",
    "SubagentFactory",
    "AgentDefinition",
]
```

### Day 4-5: Testing SDK Layer

**Create: `tests/test_sdk_integration.py`**

```python
"""Tests for SDK integration layer."""

import pytest
from claude_code_builder_v2.sdk import (
    SDKClientManager,
    ClaudeAgentOptions,
    ToolRegistry,
    tool,
)
from claude_code_builder_v2.core.config import ExecutorConfig
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


@pytest.fixture
def sdk_manager():
    """Create SDK manager for tests."""
    config = ExecutorConfig(
        api_key="test-key",
        model="claude-3-haiku-20240307",
    )
    logger = ComprehensiveLogger()
    return SDKClientManager(config, logger)


@pytest.mark.asyncio
async def test_create_session(sdk_manager):
    """Test session creation."""
    options = ClaudeAgentOptions(
        system_prompt="Test prompt",
        allowed_tools=["tool1"],
    )

    session = await sdk_manager.create_session("test-session", options)

    assert session["session_id"] == "test-session"
    assert session["options"] == options


def test_tool_decorator():
    """Test @tool decorator."""

    @tool("Test tool")
    async def my_tool(arg1: str, arg2: int = 0) -> dict:
        return {"result": "test"}

    assert hasattr(my_tool, "_is_tool")
    assert my_tool._tool_description == "Test tool"
    assert "arg1" in my_tool._tool_schema["properties"]


@pytest.mark.asyncio
async def test_tool_registration():
    """Test tool registration."""
    logger = ComprehensiveLogger()
    registry = ToolRegistry(logger)

    @tool("Test tool")
    async def my_tool(arg: str) -> str:
        return arg.upper()

    registry.register_tool("my_tool", my_tool)

    definitions = registry.get_tool_definitions(["my_tool"])
    assert len(definitions) == 1
    assert definitions[0]["name"] == "my_tool"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Run Tests:**
```bash
poetry run pytest tests/test_sdk_integration.py -v
```

---

## Phase 2: Agent System Rewrite (Days 6-10)

### Day 6: BaseAgent (SDK-based)

**Create: `src/claude_code_builder_v2/agents/base.py`**

```python
"""SDK-based Base Agent."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import uuid4

from claude_code_builder_v2.sdk import SDKClientManager, ClaudeAgentOptions
from claude_code_builder_v2.core.context_manager import ContextManager
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext
from claude_code_builder_v2.core.config import ExecutorConfig


class BaseAgent(ABC):
    """Base class for SDK-based agents."""

    def __init__(
        self,
        agent_type: AgentType,
        sdk_manager: SDKClientManager,
        context_manager: ContextManager,
        logger: ComprehensiveLogger,
        config: Optional[ExecutorConfig] = None,
    ) -> None:
        """Initialize base agent."""
        self.agent_type = agent_type
        self.sdk_manager = sdk_manager
        self.context_manager = context_manager
        self.logger = logger
        self.config = config or ExecutorConfig()

        # Session state
        self.current_session_id: Optional[str] = None
        self.current_session_ctx: Optional[Dict[str, Any]] = None

    @abstractmethod
    async def execute(
        self,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute agent task. Must be implemented by subclass."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        pass

    @abstractmethod
    def get_allowed_tools(self) -> List[str]:
        """Get list of allowed tools."""
        pass

    async def run(
        self,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> AgentResponse:
        """
        Run agent with full lifecycle management.

        This handles:
        - Session creation
        - Execution
        - Cleanup
        - Error handling
        - Metrics tracking
        """
        start_time = time.time()
        self.current_session_id = str(uuid4())

        try:
            # Create SDK session
            agent_options = ClaudeAgentOptions(
                system_prompt=self.get_system_prompt(),
                allowed_tools=self.get_allowed_tools(),
                model=self.config.model,
            )

            self.current_session_ctx = await self.sdk_manager.create_session(
                self.current_session_id,
                agent_options,
            )

            # Log start
            self.logger.logger.info(
                "agent_started",
                agent_type=self.agent_type.value,
                session_id=self.current_session_id,
            )

            # Execute
            response = await self.execute(context, **kwargs)

            # Update metrics
            response.duration_seconds = time.time() - start_time
            response.sdk_session_id = self.current_session_id

            # Log completion
            self.logger.logger.info(
                "agent_completed",
                agent_type=self.agent_type.value,
                success=response.success,
                duration=response.duration_seconds,
            )

            return response

        except Exception as e:
            self.logger.logger.error(
                "agent_failed",
                agent_type=self.agent_type.value,
                error=str(e),
                exc_info=True,
            )

            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                result=None,
                error=str(e),
                duration_seconds=time.time() - start_time,
            )

        finally:
            # Cleanup
            if self.current_session_id:
                await self.sdk_manager.close_session(self.current_session_id)
                self.current_session_id = None

    async def query(self, prompt: str) -> str:
        """Execute query in current session."""
        if not self.current_session_id:
            raise RuntimeError("No active session. Call run() first.")

        response_text = ""

        async for chunk in self.sdk_manager.query_with_session(
            self.current_session_id,
            prompt,
        ):
            if chunk["type"] == "text":
                response_text += chunk["content"]

        return response_text
```

### Day 7-9: Rewrite Each Agent

**Template for each agent:**

```python
"""[Agent Name] using Claude SDK."""

from typing import Any

from claude_code_builder_v2.agents.base import BaseAgent
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext


class [AgentName](BaseAgent):
    """[Agent description]."""

    def get_system_prompt(self) -> str:
        """Get system prompt."""
        return """[Agent-specific system prompt]"""

    def get_allowed_tools(self) -> List[str]:
        """Get allowed tools."""
        return [
            "[list of tools this agent needs]",
        ]

    async def execute(
        self,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute agent task."""

        # Build prompt
        prompt = self._build_prompt(**kwargs)

        # Query SDK
        response_text = await self.query(prompt)

        # Parse response
        result = self._parse_response(response_text)

        return AgentResponse(
            agent_type=self.agent_type,
            success=True,
            result=result,
        )

    def _build_prompt(self, **kwargs) -> str:
        """Build prompt for this agent."""
        # Agent-specific prompt construction
        pass

    def _parse_response(self, response: str) -> Any:
        """Parse agent response."""
        # Agent-specific parsing
        pass
```

**Implement each agent:**
1. [ ] SpecAnalyzer
2. [ ] TaskGenerator
3. [ ] InstructionBuilder
4. [ ] CodeGenerator
5. [ ] TestGenerator
6. [ ] ReviewAgent
7. [ ] ErrorHandler
8. [ ] DocumentationAgent

### Day 10: Agent Testing

**Create: `tests/test_agents.py`**

```python
"""Tests for SDK-based agents."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from claude_code_builder_v2.agents import SpecAnalyzer
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import ExecutionContext


@pytest.mark.asyncio
async def test_spec_analyzer():
    """Test SpecAnalyzer agent."""

    # Create mocks
    sdk_manager = AsyncMock()
    context_manager = MagicMock()
    logger = MagicMock()

    # Create agent
    agent = SpecAnalyzer(
        AgentType.SPEC_ANALYZER,
        sdk_manager,
        context_manager,
        logger,
    )

    # Create context
    context = ExecutionContext(
        session_id="test",
        full_context="Test specification",
    )

    # Mock SDK response
    sdk_manager.query_with_session.return_value = AsyncMock()

    # Execute
    response = await agent.run(context, specification="Test spec")

    # Assert
    assert response.agent_type == AgentType.SPEC_ANALYZER
```

---

## Next Steps

After completing Phase 1, proceed to:
- **Phase 3**: Executor System (see REWRITE_SPEC.md section 6.3)
- **Phase 4**: MCP Integration (see REWRITE_SPEC.md section 6.4)
- **Phase 5**: Enhanced Features (see REWRITE_SPEC.md section 6.5)

**Important:** Commit frequently and run tests after each component!

---

**Document Status:** Complete for Phase 1
**Next Update:** After Phase 1 completion
**Questions?** Create issue in GitHub repo
