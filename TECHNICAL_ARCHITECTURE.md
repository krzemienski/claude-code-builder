# Claude Code Builder v2.0: Technical Architecture

**Document Type:** Technical Design Document
**Version:** 1.0
**Date:** 2025-11-15

---

## Table of Contents

1. [System Overview](#system-overview)
2. [SDK Integration Architecture](#sdk-integration-architecture)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [API Specifications](#api-specifications)
6. [Performance Considerations](#performance-considerations)
7. [Security Model](#security-model)

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (CLI - Click + Rich)                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                          │
│  ┌─────────────────────┐    ┌──────────────────────────┐       │
│  │ BuildOrchestrator   │◄──►│ CheckpointManager       │       │
│  └─────────────────────┘    └──────────────────────────┘       │
│  ┌─────────────────────┐    ┌──────────────────────────┐       │
│  │ SDKPhaseExecutor    │◄──►│ CostTracker             │       │
│  └─────────────────────┘    └──────────────────────────┘       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SDK INTEGRATION LAYER                        │
│  ┌─────────────────────┐    ┌──────────────────────────┐       │
│  │ SDKClientManager    │◄──►│ ToolRegistry            │       │
│  └─────────────────────┘    └──────────────────────────┘       │
│  ┌─────────────────────┐    ┌──────────────────────────┐       │
│  │ SubagentFactory     │◄──►│ HookRegistry            │       │
│  └─────────────────────┘    └──────────────────────────┘       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT SYSTEM                               │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐        │
│  │ SpecAnalyzer  │ │ TaskGenerator │ │ CodeGenerator │        │
│  └───────────────┘ └───────────────┘ └───────────────┘        │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐        │
│  │ TestGenerator │ │ ReviewAgent   │ │ ErrorHandler  │        │
│  └───────────────┘ └───────────────┘ └───────────────┘        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CLAUDE AGENT SDK                              │
│  ┌─────────────────────┐    ┌──────────────────────────┐       │
│  │ ClaudeSDKClient     │    │ query() function         │       │
│  │ (Stateful)          │    │ (Stateless)              │       │
│  └─────────────────────┘    └──────────────────────────┘       │
│  ┌─────────────────────┐    ┌──────────────────────────┐       │
│  │ @tool decorators    │    │ create_sdk_mcp_server()  │       │
│  └─────────────────────┘    └──────────────────────────┘       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              MCP SERVERS (In-Process)                           │
│  ┌────────────┐ ┌────────┐ ┌─────────┐ ┌──────────────┐       │
│  │ Filesystem │ │ Memory │ │ Context7│ │ Sequential   │       │
│  │            │ │        │ │         │ │ Thinking     │       │
│  └────────────┘ └────────┘ └─────────┘ └──────────────┘       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              CORE INFRASTRUCTURE                                │
│  ┌─────────────────────┐    ┌──────────────────────────┐       │
│  │ ContextManager      │    │ LoggingSystem            │       │
│  │ (150K+ tokens)      │    │ (Structured + JSON)      │       │
│  └─────────────────────┘    └──────────────────────────┘       │
│  ┌─────────────────────┐    ┌──────────────────────────┐       │
│  │ OutputManager       │    │ DataModels (Pydantic v2) │       │
│  └─────────────────────┘    └──────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. SDK Integration Architecture

### 2.1 SDKClientManager

**Purpose:** Central manager for all Claude SDK client interactions

```python
class SDKClientManager:
    """
    Manages Claude SDK client lifecycle and configuration.

    Responsibilities:
    - Create and configure SDK clients
    - Manage client sessions
    - Register MCP servers
    - Set up hooks
    - Handle client cleanup
    """

    def __init__(
        self,
        config: ExecutorConfig,
        logger: ComprehensiveLogger,
    ) -> None:
        self.config = config
        self.logger = logger
        self.active_clients: Dict[str, ClaudeSDKClient] = {}
        self.tool_registry = ToolRegistry()
        self.hook_registry = HookRegistry()

    async def create_client(
        self,
        session_id: str,
        agent_options: ClaudeAgentOptions,
    ) -> ClaudeSDKClient:
        """
        Create a configured SDK client.

        Args:
            session_id: Unique session identifier
            agent_options: SDK agent configuration

        Returns:
            Configured ClaudeSDKClient instance
        """
        # Create client with options
        client = ClaudeSDKClient(
            api_key=self.config.api_key,
            model=self.config.model,
            options=agent_options,
        )

        # Connect client
        await client.connect()

        # Register hooks
        self._register_hooks(client)

        # Track client
        self.active_clients[session_id] = client

        return client

    async def create_stateless_query(
        self,
        prompt: str,
        system_prompt: str,
        tools: List[str],
    ) -> AsyncIterator:
        """
        Execute a stateless query using SDK query() function.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            tools: List of allowed tool names

        Yields:
            Stream chunks from SDK
        """
        async for chunk in await query(
            prompt=prompt,
            system=system_prompt,
            tools=tools,
            model=self.config.model,
        ):
            yield chunk

    def _register_hooks(self, client: ClaudeSDKClient) -> None:
        """Register all hooks for client."""
        client.on("pre_tool_use", self.hook_registry.pre_tool_use)
        client.on("post_tool_use", self.hook_registry.post_tool_use)
        client.on("user_prompt_submit", self.hook_registry.user_prompt_submit)

    async def shutdown(self) -> None:
        """Cleanup all active clients."""
        for client in self.active_clients.values():
            await client.disconnect()
        self.active_clients.clear()
```

### 2.2 ToolRegistry

**Purpose:** Manage tool definitions and MCP server creation

```python
class ToolRegistry:
    """
    Registry for SDK tools and MCP servers.

    Features:
    - Register custom tools via @tool decorator
    - Create in-process MCP servers
    - Map tool names to implementations
    - Manage tool permissions
    """

    def __init__(self) -> None:
        self.tools: Dict[str, Callable] = {}
        self.mcp_servers: Dict[str, Any] = {}

    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool function.

        Args:
            name: Tool name
            func: Tool implementation (should be @tool decorated)
        """
        self.tools[name] = func
        self.logger.debug(f"Registered tool: {name}")

    async def create_mcp_servers(
        self,
        configs: List[MCPServerConfig],
    ) -> Dict[str, Any]:
        """
        Create in-process MCP servers using SDK.

        Args:
            configs: MCP server configurations

        Returns:
            Dictionary of server name to server instance
        """
        servers = {}

        for config in configs:
            if config.server == MCPServer.FILESYSTEM:
                server = await self._create_filesystem_server(config)
                servers['filesystem'] = server

            elif config.server == MCPServer.MEMORY:
                server = await self._create_memory_server(config)
                servers['memory'] = server

            # ... other servers

        self.mcp_servers = servers
        return servers

    async def _create_filesystem_server(
        self,
        config: MCPServerConfig,
    ) -> Any:
        """Create in-process filesystem MCP server."""

        # Define tools as functions
        @tool()
        async def read_file(path: str, offset: int = 0, limit: int = None) -> str:
            """Read file contents."""
            async with aiofiles.open(path, 'r') as f:
                if offset:
                    await f.seek(offset)
                content = await f.read(limit) if limit else await f.read()
                return content

        @tool()
        async def write_file(path: str, content: str) -> bool:
            """Write content to file."""
            async with aiofiles.open(path, 'w') as f:
                await f.write(content)
                return True

        @tool()
        async def list_directory(path: str) -> List[str]:
            """List directory contents."""
            return os.listdir(path)

        # Create MCP server with tools
        server = await create_sdk_mcp_server(
            name="filesystem",
            tools=[read_file, write_file, list_directory],
        )

        return server

    async def _create_memory_server(
        self,
        config: MCPServerConfig,
    ) -> Any:
        """Create in-process memory MCP server."""

        # Memory store
        memory_store = {}

        @tool()
        async def create_entities(entities: List[Dict[str, Any]]) -> bool:
            """Create memory entities."""
            for entity in entities:
                key = entity['name']
                memory_store[key] = entity
            return True

        @tool()
        async def search_nodes(query: str) -> List[Dict[str, Any]]:
            """Search memory nodes."""
            results = []
            for key, value in memory_store.items():
                if query.lower() in str(value).lower():
                    results.append(value)
            return results

        server = await create_sdk_mcp_server(
            name="memory",
            tools=[create_entities, search_nodes],
        )

        return server
```

### 2.3 HookRegistry

**Purpose:** Manage SDK event hooks for tracking and logging

```python
class HookRegistry:
    """
    Registry for SDK hooks.

    Hooks enable:
    - Pre/post tool use tracking
    - Prompt modification
    - Cost tracking
    - Security checks
    """

    def __init__(
        self,
        logger: ComprehensiveLogger,
        cost_tracker: CostTracker,
    ) -> None:
        self.logger = logger
        self.cost_tracker = cost_tracker

    async def pre_tool_use(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Hook called before tool execution.

        Returns modified arguments or raises to block execution.
        """
        # Log tool use
        self.logger.logger.info(
            "sdk_pre_tool_use",
            tool=tool_name,
            arguments=arguments,
        )

        # Security check
        if tool_name == "write_file":
            path = arguments.get("path", "")
            if not self._is_safe_path(path):
                raise PermissionError(f"Unsafe path: {path}")

        return arguments

    async def post_tool_use(
        self,
        tool_name: str,
        result: Any,
        context: Dict[str, Any],
    ) -> None:
        """Hook called after tool execution."""
        self.logger.logger.info(
            "sdk_post_tool_use",
            tool=tool_name,
            success=not isinstance(result, Exception),
        )

    async def user_prompt_submit(
        self,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Hook called before prompt submission.

        Can modify prompt or log it.
        """
        self.logger.logger.info(
            "sdk_prompt_submit",
            prompt_length=len(prompt),
        )

        # Track token estimate
        estimated_tokens = len(prompt) // 4
        self.cost_tracker.add_input_tokens(estimated_tokens)

        return prompt

    def _is_safe_path(self, path: str) -> bool:
        """Check if file path is safe."""
        # Ensure path is within project directory
        abs_path = Path(path).resolve()
        project_root = Path.cwd().resolve()
        return str(abs_path).startswith(str(project_root))
```

### 2.4 SubagentFactory

**Purpose:** Create SDK subagent definitions for task delegation

```python
class SubagentFactory:
    """
    Factory for creating SDK subagent definitions.

    Subagents enable:
    - Task specialization
    - Isolated tool access
    - Model selection per task
    - Custom prompts
    """

    def __init__(self, config: ExecutorConfig) -> None:
        self.config = config
        self.agent_definitions: Dict[AgentType, AgentDefinition] = {}

    def create_agent_definition(
        self,
        agent_type: AgentType,
        system_prompt: str,
        allowed_tools: List[str],
        model: Optional[str] = None,
    ) -> AgentDefinition:
        """
        Create SDK AgentDefinition for subagent.

        Args:
            agent_type: Type of agent
            system_prompt: Agent-specific instructions
            allowed_tools: Tools this agent can use
            model: Optional model override

        Returns:
            AgentDefinition for SDK
        """
        definition = AgentDefinition(
            name=agent_type.value,
            description=self._get_agent_description(agent_type),
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            model=model or self.config.model,
        )

        self.agent_definitions[agent_type] = definition
        return definition

    def _get_agent_description(self, agent_type: AgentType) -> str:
        """Get description for agent type."""
        descriptions = {
            AgentType.SPEC_ANALYZER: "Analyzes project specifications",
            AgentType.TASK_GENERATOR: "Generates task breakdowns",
            AgentType.CODE_GENERATOR: "Generates production code",
            # ... etc
        }
        return descriptions.get(agent_type, "Agent")

    async def delegate_to_subagent(
        self,
        parent_client: ClaudeSDKClient,
        agent_type: AgentType,
        task: str,
    ) -> Any:
        """
        Delegate task to subagent.

        Args:
            parent_client: Parent SDK client
            agent_type: Type of subagent
            task: Task description

        Returns:
            Subagent response
        """
        # Get or create agent definition
        definition = self.agent_definitions.get(agent_type)
        if not definition:
            raise ValueError(f"No definition for {agent_type}")

        # Delegate via SDK
        result = await parent_client.delegate(
            subagent=definition,
            prompt=task,
        )

        return result
```

---

## 3. Component Design

### 3.1 BaseAgent (SDK-based)

```python
class BaseAgent(ABC):
    """
    Base class for all SDK-based agents.

    Key Features:
    - SDK client integration
    - Automatic lifecycle management
    - Hook support
    - Progress streaming
    - Error recovery
    """

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

        # SDK-specific state
        self.current_session_id: Optional[str] = None
        self.current_client: Optional[ClaudeSDKClient] = None

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
        """Get agent system prompt."""
        pass

    @abstractmethod
    def get_allowed_tools(self) -> List[str]:
        """Get list of allowed tools."""
        pass

    async def run(
        self,
        context: ExecutionContext,
        use_stateless: bool = False,
        **kwargs: Any,
    ) -> AgentResponse:
        """
        Run agent with full lifecycle management.

        Args:
            context: Execution context
            use_stateless: Use stateless query() vs stateful client
            **kwargs: Additional arguments for execute()

        Returns:
            AgentResponse with results
        """
        start_time = time.time()
        self.current_session_id = str(uuid4())

        try:
            # Create SDK client if not stateless
            if not use_stateless:
                self.current_client = await self._create_client()

            # Log start
            self.logger.logger.info(
                "agent_started",
                agent_type=self.agent_type.value,
                session_id=self.current_session_id,
                stateless=use_stateless,
            )

            # Execute agent logic
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
            raise

        finally:
            # Cleanup
            if self.current_client:
                await self.current_client.disconnect()
                self.current_client = None

    async def _create_client(self) -> ClaudeSDKClient:
        """Create SDK client for this agent."""
        options = ClaudeAgentOptions(
            system_prompt=self.get_system_prompt(),
            allowed_tools=self.get_allowed_tools(),
            permission_mode="default",
        )

        return await self.sdk_manager.create_client(
            session_id=self.current_session_id,
            agent_options=options,
        )

    async def query_stateless(
        self,
        prompt: str,
        **kwargs,
    ) -> str:
        """
        Execute stateless query.

        Use for simple, one-off queries.
        """
        response_text = ""

        async for chunk in await self.sdk_manager.create_stateless_query(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            tools=self.get_allowed_tools(),
        ):
            if chunk.type == "text":
                response_text += chunk.content

        return response_text

    async def query_with_client(
        self,
        prompt: str,
        stream_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Execute query with stateful client.

        Use for multi-turn conversations.
        """
        if not self.current_client:
            raise RuntimeError("No active client. Call run() first.")

        # Send query
        response_chunks = []

        async for chunk in self.current_client.query(prompt):
            response_chunks.append(chunk)

            # Stream callback
            if stream_callback:
                await stream_callback(chunk)

        return {
            "chunks": response_chunks,
            "final_text": self._extract_text(response_chunks),
        }

    def _extract_text(self, chunks: List[Any]) -> str:
        """Extract text content from chunks."""
        return "".join(
            chunk.content for chunk in chunks
            if chunk.type == "text"
        )

    async def delegate_to_subagent(
        self,
        subagent_type: AgentType,
        task: str,
    ) -> Any:
        """
        Delegate task to subagent.

        Args:
            subagent_type: Type of subagent
            task: Task description

        Returns:
            Subagent result
        """
        if not self.current_client:
            raise RuntimeError("Cannot delegate without active client")

        return await self.sdk_manager.subagent_factory.delegate_to_subagent(
            parent_client=self.current_client,
            agent_type=subagent_type,
            task=task,
        )
```

---

## 4. Data Flow

### 4.1 Request Flow

```
User CLI Command
    │
    ▼
CLI Handler (Click)
    │
    ▼
BuildOrchestrator.build()
    │
    ├──► Load/Parse Specification
    ├──► Create SDKClientManager
    ├──► Initialize MCP Servers (in-process)
    └──► For each Phase:
            │
            ▼
        SDKPhaseExecutor.execute_phase()
            │
            ├──► Load Phase Context
            └──► For each Task:
                    │
                    ▼
                Agent.run()
                    │
                    ├──► Create SDK Client
                    ├──► Set System Prompt
                    ├──► Configure Tools
                    └──► Execute Query:
                            │
                            ▼
                        ClaudeSDKClient.query()
                            │
                            ├──► Stream Response
                            ├──► Execute Tools
                            ├──► Call Hooks
                            └──► Return Result
                                │
                                ▼
                            Parse Response
                                │
                                ▼
                            Save Checkpoint
                                │
                                ▼
                            Update Metrics
                                │
                                ▼
                            Return to CLI
```

### 4.2 Streaming Flow

```
Agent.query_with_client()
    │
    ▼
SDK Client Query
    │
    ├──► Thinking Block
    │    └──► CLI: Show "Thinking..."
    │
    ├──► Tool Use Block
    │    ├──► Hook: pre_tool_use
    │    ├──► Execute Tool
    │    ├──► Hook: post_tool_use
    │    └──► CLI: Show "Using tool X..."
    │
    ├──► Text Block
    │    └──► CLI: Stream text output
    │
    └──► Final Response
         └──► Parse & Return
```

### 4.3 Tool Execution Flow

```
SDK Receives Tool Request
    │
    ▼
Hook: pre_tool_use
    ├──► Validate Arguments
    ├──► Check Permissions
    └──► Log Request
    │
    ▼
ToolRegistry.execute(tool_name, args)
    │
    ├──► Filesystem Tool?
    │    └──► Execute on in-process server
    │
    ├──► Memory Tool?
    │    └──► Execute on in-process server
    │
    └──► Custom Tool?
         └──► Execute @tool function
    │
    ▼
Hook: post_tool_use
    ├──► Log Result
    ├──► Track Metrics
    └──► Return to SDK
    │
    ▼
SDK Returns Tool Result
```

---

## 5. API Specifications

### 5.1 SDK Client API

**Create Client:**
```python
client = await sdk_manager.create_client(
    session_id="unique_id",
    agent_options=ClaudeAgentOptions(
        system_prompt="...",
        allowed_tools=["tool1", "tool2"],
    ),
)
```

**Query (Stateless):**
```python
async for chunk in await query(
    prompt="...",
    system="...",
    tools=["..."],
    model="claude-3-opus-20240229",
):
    process(chunk)
```

**Query (Stateful):**
```python
async for chunk in client.query("..."):
    if chunk.type == "text":
        print(chunk.content)
    elif chunk.type == "tool_use":
        print(f"Using: {chunk.tool_name}")
```

### 5.2 Tool Definition API

```python
@tool()
async def my_tool(arg1: str, arg2: int = 0) -> dict:
    """
    Tool description for Claude.

    Args are automatically validated via type hints.
    """
    return {"result": "..."}

# Register
tool_registry.register_tool("my_tool", my_tool)
```

### 5.3 Hook API

```python
async def my_pre_hook(
    tool_name: str,
    arguments: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Pre-tool hook. Return modified args."""
    # Modify or validate
    return arguments

client.on("pre_tool_use", my_pre_hook)
```

---

## 6. Performance Considerations

### 6.1 Optimizations

**SDK Client Pooling:**
- Reuse clients across phases
- Reduce connection overhead
- Session management

**In-Process MCP:**
- No subprocess spawning
- Direct function calls
- Reduced latency

**Streaming:**
- Native async iteration
- Real-time progress
- Better UX

**Context Management:**
- Leverage SDK session state
- Reduce redundant context
- Smart chunking

### 6.2 Metrics

**Target Performance:**
- Build time: Within 10% of v1
- Memory usage: 20% reduction (no subprocesses)
- Startup time: < 2 seconds
- Tool call latency: < 50ms

---

## 7. Security Model

### 7.1 Permission System

**Tool-Level:**
```python
options = ClaudeAgentOptions(
    allowed_tools=["safe_tool"],
    disallowed_tools=["dangerous_tool"],
)
```

**Dynamic Permissions:**
```python
async def can_use_tool(
    tool_name: str,
    arguments: Dict[str, Any],
) -> bool:
    if tool_name == "write_file":
        return is_safe_path(arguments["path"])
    return True

options.can_use_tool = can_use_tool
```

### 7.2 Filesystem Security

- Restrict to project directory
- No parent directory access
- Path sanitization
- Symlink prevention

### 7.3 API Key Protection

- Never log full keys
- Environment variables only
- Secure storage
- Key rotation support

---

**Document Status:** Complete
**Next Review:** After implementation Phase 1
**Maintainers:** Claude Code Builder Team
