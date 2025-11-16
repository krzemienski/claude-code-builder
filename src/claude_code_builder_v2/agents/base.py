"""SDK-based Base Agent for CCB v2."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import uuid4

from claude_code_builder_v2.sdk import SDKClientManager, ClaudeAgentOptions
from claude_code_builder_v2.core.context_manager import ContextManager
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import ExecutionContext
from claude_code_builder_v2.core.config import ExecutorConfig
from claude_code_builder_v2.core.base_model import BaseModel


class AgentResponse(BaseModel):
    """Response from an SDK-based agent execution."""
    agent_type: AgentType
    success: bool
    result: Any
    metadata: Dict[str, Any] = {}
    sdk_session_id: Optional[str] = None
    tokens_used: int = 0
    cost: float = 0.0
    duration_seconds: float = 0.0
    error: Optional[str] = None


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
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
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

    async def query_stateless(self, prompt: str) -> str:
        """Execute stateless query without session."""
        response_text = ""

        async for chunk in self.sdk_manager.query_stateless(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            tools=self.get_allowed_tools(),
        ):
            if chunk["type"] == "text":
                response_text += chunk["content"]

        return response_text
