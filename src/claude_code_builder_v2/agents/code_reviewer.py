"""Code reviewer agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext


class CodeReviewer(BaseAgent):
    """Reviews code using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize CodeReviewer."""
        super().__init__(AgentType.CODE_REVIEWER, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for code review."""
        return """You are a Code Reviewer for Claude Code Builder.

Your role is to:
1. Review code for correctness and quality
2. Identify bugs and potential issues
3. Suggest improvements and optimizations
4. Check for best practices compliance
5. Assess security vulnerabilities
6. Evaluate code maintainability

Output should include:
- Overall assessment
- Identified issues by severity
- Specific suggestions for improvement
- Security concerns
- Performance considerations
- Maintainability score"""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        code: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute code review using SDK.

        Args:
            context: Execution context
            code: Code to review
            **kwargs: Additional arguments

        Returns:
            AgentResponse with review
        """
        prompt = f"""Review this code:

{code}

Provide:
1. Overall assessment
2. Issues identified (by severity)
3. Specific improvement suggestions
4. Security concerns
5. Performance considerations
6. Maintainability evaluation

Be thorough and constructive."""

        try:
            response_text = await self.query(prompt)

            return self.create_success_response(
                result={"review": response_text},
                metadata={"code_length": len(code), "review_length": len(response_text)},
            )

        except Exception as e:
            return self.create_error_response(error=str(e))
