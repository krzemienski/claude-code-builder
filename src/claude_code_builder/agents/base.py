"""Base agent implementation for Claude Code Builder."""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from uuid import uuid4

from pydantic import Field

from claude_code_builder.core.base_model import BaseModel
from claude_code_builder.core.config import ExecutorConfig
from claude_code_builder.core.context_manager import ContextManager
from claude_code_builder.core.enums import AgentType, MCPServer
from claude_code_builder.core.exceptions import APIError, PhaseExecutionError
from claude_code_builder.core.logging_system import ComprehensiveLogger
from claude_code_builder.core.models import APICall, ExecutionContext

if TYPE_CHECKING:
    from claude_code_builder.executor import ClaudeCodeExecutor
    from claude_code_builder.mcp.orchestrator import MCPOrchestrator


class AgentResponse(BaseModel):
    """Response from an agent execution."""
    
    agent_type: AgentType
    success: bool
    result: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    api_calls: List[APICall] = Field(default_factory=list)
    mcp_servers_used: List[MCPServer] = Field(default_factory=list)
    tokens_used: int = 0
    cost: float = 0.0
    duration_seconds: float = 0.0
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(
        self,
        agent_type: AgentType,
        executor: "ClaudeCodeExecutor",
        context_manager: ContextManager,
        mcp_orchestrator: "MCPOrchestrator",
        logger: ComprehensiveLogger,
        config: Optional[ExecutorConfig] = None,
    ) -> None:
        """Initialize the agent."""
        self.agent_type = agent_type
        self.executor = executor
        self.context_manager = context_manager
        self.mcp_orchestrator = mcp_orchestrator
        self.logger = logger
        self.config = config or ExecutorConfig()
        
        # Track execution state
        self.current_context: Optional[ExecutionContext] = None
        self.api_calls: List[APICall] = []
        self.mcp_servers_used: List[MCPServer] = []

    @abstractmethod
    async def execute(
        self,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute the agent's primary task."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass

    @abstractmethod
    def get_tools(self) -> List[str]:
        """Get the list of tools this agent can use."""
        pass

    async def run(
        self,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> AgentResponse:
        """Run the agent with full lifecycle management."""
        start_time = asyncio.get_event_loop().time()
        self.current_context = context
        self.api_calls = []
        self.mcp_servers_used = []
        
        try:
            # Log agent start
            self.logger.logger.info(
                "agent_started",
                agent_type=self.agent_type.value,
                phase=context.current_phase,
                task=context.current_task,
            )
            
            # Execute agent logic
            response = await self.execute(context, **kwargs)
            
            # Update response with tracking data
            response.api_calls = self.api_calls
            response.mcp_servers_used = list(set(self.mcp_servers_used))
            response.duration_seconds = asyncio.get_event_loop().time() - start_time
            
            # Log success
            self.logger.logger.info(
                "agent_completed",
                agent_type=self.agent_type.value,
                success=response.success,
                tokens_used=response.tokens_used,
                cost=response.cost,
                duration=response.duration_seconds,
            )
            
            return response
            
        except Exception as e:
            # Log error
            self.logger.logger.error(
                "agent_failed",
                agent_type=self.agent_type.value,
                error=str(e),
                exc_info=True,
            )
            
            # Return error response
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                result=None,
                error=str(e),
                api_calls=self.api_calls,
                mcp_servers_used=list(set(self.mcp_servers_used)),
                duration_seconds=asyncio.get_event_loop().time() - start_time,
            )

    async def call_claude(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make a call to Claude API."""
        # Use agent's system prompt by default
        system_prompt = system_prompt_override or self.get_system_prompt()
        
        # Use agent's tools by default
        if tools is None:
            tool_names = self.get_tools()
            tools = self.executor.get_tool_definitions(tool_names)
        
        # Create API call record
        from claude_code_builder.core.models import Message, ToolDefinition
        
        # Convert messages to Message objects
        message_objects = []
        for msg in messages:
            message_objects.append(Message(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
            ))
        
        # Convert tools to ToolDefinition objects
        tool_definitions = []
        if tools:
            for tool in tools:
                tool_definitions.append(ToolDefinition(
                    name=tool.get("name", "unknown"),
                    description=tool.get("description", ""),
                    input_schema=tool.get("input_schema", {}),
                ))
        
        api_call = APICall(
            call_id=uuid4(),
            session_id=self.current_context.session_id if self.current_context else "unknown",
            endpoint="claude.ai/v1/messages",
            model=self.config.model,
            agent_type=self.agent_type,
            phase=str(self.current_context.current_phase) if self.current_context and self.current_context.current_phase else None,
            task=str(self.current_context.current_task) if self.current_context and self.current_context.current_task else None,
            request_messages=message_objects,
            system_prompt=system_prompt,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            tools=tool_definitions,
        )
        
        # LOG THE FULL REQUEST PAYLOAD
        self.logger.logger.info(
            "api_request_payload",
            agent_type=self.agent_type.value,
            phase=self.current_context.current_phase if self.current_context else None,
            task=self.current_context.current_task if self.current_context else None,
            system_prompt=system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt,
            messages=[{
                "role": msg.get("role"),
                "content": msg.get("content", "")[:1000] + "..." if len(msg.get("content", "")) > 1000 else msg.get("content", "")
            } for msg in messages],
            tools=[tool.get("name") for tool in tools] if tools else [],
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            model=self.config.model,
        )
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Make the actual call
            response = await self.executor.call_claude(
                messages=messages,
                system_prompt=system_prompt,
                tools=tools,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                stream=self.config.stream_output,
            )
            
            # Update API call record
            api_call.response_content = response.get("content", "")
            api_call.tool_calls = response.get("tool_calls", [])
            api_call.tokens_in = response.get("usage", {}).get("input_tokens", 0)
            api_call.tokens_out = response.get("usage", {}).get("output_tokens", 0)
            api_call.tokens_total = api_call.tokens_in + api_call.tokens_out
            api_call.latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            api_call.estimated_cost = self._estimate_cost(api_call)
            
            # LOG THE FULL RESPONSE
            self.logger.logger.info(
                "api_response_payload",
                agent_type=self.agent_type.value,
                phase=self.current_context.current_phase if self.current_context else None,
                task=self.current_context.current_task if self.current_context else None,
                response_content=response.get("content", "")[:2000] + "..." if len(response.get("content", "")) > 2000 else response.get("content", ""),
                tool_calls=[{
                    "name": tc.get("name"),
                    "arguments": tc.get("arguments", {})
                } for tc in response.get("tool_calls", [])][:5],  # Limit to first 5 tool calls
                tokens_in=api_call.tokens_in,
                tokens_out=api_call.tokens_out,
                latency_ms=api_call.latency_ms,
                cost=api_call.estimated_cost,
                model=self.config.model,
            )
            
            # Track the call
            self.api_calls.append(api_call)
            await self.logger.log_api_call(api_call)
            
            return response
            
        except Exception as e:
            # Update API call with error
            api_call.error = str(e)
            api_call.latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            
            # LOG THE ERROR
            self.logger.logger.error(
                "api_call_error",
                agent_type=self.agent_type.value,
                phase=self.current_context.current_phase if self.current_context else None,
                task=self.current_context.current_task if self.current_context else None,
                error=str(e),
                latency_ms=api_call.latency_ms,
                model=self.config.model,
                exc_info=True,
            )
            
            # Track the failed call
            self.api_calls.append(api_call)
            await self.logger.log_api_call(api_call)
            
            raise APIError(
                f"Claude API call failed: {str(e)}",
                details={"agent": self.agent_type.value, "error": str(e)},
            )

    async def use_mcp_server(self, server: MCPServer) -> None:
        """Record MCP server usage."""
        if server not in self.mcp_servers_used:
            self.mcp_servers_used.append(server)
        
        # Ensure server is running
        await self.mcp_orchestrator.ensure_server_running(server)

    async def get_context_for_phase(self, phase: str) -> str:
        """Get optimized context for a phase."""
        return await self.context_manager.get_context_for_phase(phase)

    async def store_in_memory(
        self,
        entity_name: str,
        entity_type: str,
        observations: List[str],
    ) -> None:
        """Store information in memory MCP."""
        await self.use_mcp_server(MCPServer.MEMORY)
        
        entities = [{
            "name": entity_name,
            "entityType": entity_type,
            "observations": observations,
        }]
        
        await self.mcp_orchestrator.memory.create_entities(entities)

    async def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """Search memory MCP."""
        await self.use_mcp_server(MCPServer.MEMORY)
        return await self.mcp_orchestrator.memory.search_nodes(query)

    async def read_file(self, path: str) -> str:
        """Read file using filesystem MCP."""
        await self.use_mcp_server(MCPServer.FILESYSTEM)
        return await self.mcp_orchestrator.filesystem.read_file(path)

    async def write_file(self, path: str, content: str) -> None:
        """Write file using filesystem MCP."""
        await self.use_mcp_server(MCPServer.FILESYSTEM)
        await self.mcp_orchestrator.filesystem.write_file(path, content)

    async def search_files(
        self,
        path: str,
        pattern: str,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[str]:
        """Search files using filesystem MCP."""
        await self.use_mcp_server(MCPServer.FILESYSTEM)
        return await self.mcp_orchestrator.filesystem.search_files(
            path, pattern, exclude_patterns
        )

    async def get_documentation(
        self,
        library: str,
        topic: Optional[str] = None,
    ) -> str:
        """Get documentation using Context7 MCP."""
        await self.use_mcp_server(MCPServer.CONTEXT7)
        
        # Resolve library ID
        library_info = await self.mcp_orchestrator.context7.resolve_library_id(library)
        library_id = library_info.get("id", library)
        
        # Get documentation
        return await self.mcp_orchestrator.context7.get_library_docs(
            library_id, topic=topic
        )

    async def sequential_think(
        self,
        problem: str,
        estimated_steps: int = 5,
    ) -> List[Dict[str, Any]]:
        """Use sequential thinking for complex problems."""
        await self.use_mcp_server(MCPServer.SEQUENTIAL_THINKING)
        return await self.mcp_orchestrator.sequential_thinking.solve_problem(
            problem, estimated_steps
        )

    def _estimate_cost(self, api_call: APICall) -> float:
        """Estimate cost of an API call."""
        # Rough estimates - update with actual pricing
        cost_per_1k_input = 0.015  # $15 per 1M tokens
        cost_per_1k_output = 0.075  # $75 per 1M tokens
        
        input_cost = (api_call.tokens_in / 1000) * cost_per_1k_input
        output_cost = (api_call.tokens_out / 1000) * cost_per_1k_output
        
        return input_cost + output_cost

    async def log_progress(self, message: str, level: str = "info") -> None:
        """Log progress message."""
        log_method = getattr(self.logger, f"print_{level}", self.logger.print_info)
        log_method(f"[{self.agent_type.value}] {message}")

    async def handle_error(
        self,
        error: Exception,
        context: str,
        recoverable: bool = True,
    ) -> Optional[Any]:
        """Handle errors during agent execution."""
        error_msg = f"Error in {context}: {str(error)}"
        
        if recoverable:
            self.logger.print_warning(error_msg)
            # Could implement retry logic here
            return None
        else:
            self.logger.print_error(error_msg)
            raise PhaseExecutionError(
                self.current_context.current_phase if self.current_context else "unknown",
                error_msg,
                self.current_context.current_task if self.current_context else None,
                {"agent": self.agent_type.value, "error": str(error)},
            )


__all__ = ["BaseAgent", "AgentResponse"]