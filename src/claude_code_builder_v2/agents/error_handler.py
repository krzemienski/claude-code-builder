"""Error Handler agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent, AgentResponse
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import ExecutionContext


class ErrorHandler(BaseAgent):
    """Handles and recovers from errors using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ErrorHandler."""
        super().__init__(AgentType.ERROR_HANDLER, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for error handling."""
        return """You are an Error Handler for Claude Code Builder.

Your role is to analyze errors and provide recovery strategies:
1. Identify the root cause of errors
2. Suggest specific fixes
3. Provide alternative approaches
4. Recommend preventive measures
5. Assess if manual intervention is needed

Generate actionable error resolution strategies."""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        error_details: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute error handling using SDK."""

        prompt = f"""Analyze this error and provide a recovery strategy:

{error_details}

Identify the root cause and suggest specific fixes."""

        try:
            response_text = await self.query(prompt)

            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result={"recovery_strategy": response_text},
                metadata={"error_type": "unknown"},
            )

        except Exception as e:
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                result=None,
                error=str(e),
            )
