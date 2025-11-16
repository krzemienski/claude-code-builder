"""Code Generator agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent, AgentResponse
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import ExecutionContext


class CodeGenerator(BaseAgent):
    """Generates production code using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the CodeGenerator."""
        super().__init__(AgentType.CODE_GENERATOR, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for code generation."""
        return """You are a Code Generator for Claude Code Builder.

Your role is to generate high-quality, production-ready code that:
1. Follows best practices and design patterns
2. Includes proper error handling
3. Is well-documented with docstrings
4. Follows the specified coding standards
5. Is secure and performant
6. Includes type hints where applicable

Generate complete, functional code that can be directly used."""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        task_description: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute code generation using SDK."""

        prompt = f"""Generate production-ready code for this task:

{task_description}

Provide complete, well-documented code with error handling."""

        try:
            response_text = await self.query(prompt)

            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result={"code": response_text},
                metadata={"code_length": len(response_text)},
            )

        except Exception as e:
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                result=None,
                error=str(e),
            )
