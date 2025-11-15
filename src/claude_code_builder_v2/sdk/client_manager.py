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
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize SDK client manager."""
        self.config = config
        self.logger = logger

        # SDK client (using Anthropic's AsyncAnthropic for now)
        # Note: Will be replaced with actual Claude Agent SDK when available
        # Use provided api_key or default to test key if not provided
        self.api_key = api_key or "test-key-placeholder"
        self.client = AsyncAnthropic(api_key=self.api_key)

        # Track active sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        # Tool and hook registries (will be initialized after imports)
        self.tool_registry: Optional[Any] = None
        self.hook_registry: Optional[Any] = None
        self.subagent_factory: Optional[Any] = None

    def initialize_registries(self) -> None:
        """Initialize tool and hook registries."""
        from claude_code_builder_v2.sdk.tool_registry import ToolRegistry
        from claude_code_builder_v2.sdk.hook_registry import HookRegistry
        from claude_code_builder_v2.sdk.subagent_factory import SubagentFactory

        self.tool_registry = ToolRegistry(self.logger)
        self.hook_registry = HookRegistry(self.logger)
        self.subagent_factory = SubagentFactory(self.config)

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
        tool_defs: List[Dict[str, Any]] = []
        if self.tool_registry:
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
            delta = getattr(chunk, "delta", None)
            if delta:
                text = getattr(delta, "text", "")
                return {
                    "type": "text",
                    "content": text,
                }
        elif chunk_type == "message_start":
            return {
                "type": "start",
                "usage": getattr(getattr(chunk, "message", None), "usage", {}),
            }
        elif chunk_type == "message_stop":
            return {
                "type": "stop",
            }

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
