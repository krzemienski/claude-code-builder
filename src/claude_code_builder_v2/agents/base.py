"""Base agent using Claude SDK."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from claude_code_builder_v2.core.config import ExecutorConfig
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext
from claude_code_builder_v2.sdk.client_manager import SDKClientManager


class BaseAgent(ABC):
    """Base class for all agents using Claude SDK."""

    def __init__(
        self,
        agent_type: AgentType,
        config: ExecutorConfig,
        logger: ComprehensiveLogger,
        client_manager: SDKClientManager,
    ) -> None:
        """Initialize base agent.

        Args:
            agent_type: Type of agent
            config: Executor configuration
            logger: Comprehensive logger
            client_manager: SDK client manager
        """
        self.agent_type = agent_type
        self.config = config
        self.logger = logger
        self.client_manager = client_manager

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent.

        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent.

        Returns:
            List of tool names
        """
        pass

    @abstractmethod
    async def execute(
        self, context: ExecutionContext, **kwargs: Any
    ) -> AgentResponse:
        """Execute agent task.

        Args:
            context: Execution context
            **kwargs: Additional arguments

        Returns:
            Agent response
        """
        pass

    async def query(self, prompt: str, **kwargs: Any) -> str:
        """Execute query using SDK.

        Args:
            prompt: User prompt
            **kwargs: Additional options

        Returns:
            Response text
        """
        try:
            # Get system prompt and merge with kwargs
            system_prompt = kwargs.get("system_prompt", self.get_system_prompt())

            self.logger.info(
                "agent_query_start",
                msg=f"Agent {self.agent_type.value} query starting",
                agent=self.agent_type.value,
            )

            # Use SDK client manager
            response = await self.client_manager.query_simple(
                prompt=prompt, system_prompt=system_prompt, **kwargs
            )

            self.logger.info(
                "agent_query_complete",
                msg=f"Agent {self.agent_type.value} query completed",
                agent=self.agent_type.value,
                response_length=len(response),
            )

            return response

        except Exception as e:
            self.logger.error(
                "agent_query_error",
                msg=f"Agent {self.agent_type.value} query failed: {e}",
                agent=self.agent_type.value,
                error=str(e),
            )
            raise

    def create_success_response(
        self, result: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Create success response.

        Args:
            result: Result data
            metadata: Optional metadata

        Returns:
            AgentResponse
        """
        return AgentResponse(
            agent_type=self.agent_type,
            success=True,
            result=result,
            metadata=metadata or {},
        )

    def create_error_response(
        self, error: str, metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Create error response.

        Args:
            error: Error message
            metadata: Optional metadata

        Returns:
            AgentResponse
        """
        return AgentResponse(
            agent_type=self.agent_type,
            success=False,
            result=None,
            error=error,
            metadata=metadata or {},
        )
