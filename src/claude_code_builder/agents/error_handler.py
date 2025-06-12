"""Error Handler agent for Claude Code Builder."""

from typing import Any, Dict, List

from claude_code_builder.agents.base import BaseAgent, AgentResponse
from claude_code_builder.core.enums import AgentType, RecoveryAction
from claude_code_builder.core.models import RecoveryStrategy


class ErrorHandler(BaseAgent):
    """Handles errors and implements recovery strategies."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ErrorHandler."""
        super().__init__(AgentType.ERROR_HANDLER, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for error handling."""
        return """You are an Error Handler for Claude Code Builder.

Your role is to analyze errors and implement recovery strategies."""

    def get_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return ["Read", "Edit", "Bash"]

    async def execute(
        self,
        context: Any,
        error: Exception,
        **kwargs: Any,
    ) -> AgentResponse:
        """Handle error and attempt recovery."""
        # Analyze error
        strategy = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_attempts=3,
            delay_seconds=1.0,
        )
        
        return AgentResponse(
            agent_type=self.agent_type,
            success=True,
            result={"strategy": strategy.model_dump()},
        )


__all__ = ["ErrorHandler"]