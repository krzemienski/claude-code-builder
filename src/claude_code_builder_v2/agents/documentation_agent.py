"""Documentation Agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent, AgentResponse
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import ExecutionContext


class DocumentationAgent(BaseAgent):
    """Generates comprehensive documentation using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the DocumentationAgent."""
        super().__init__(AgentType.DOCUMENTATION_AGENT, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for documentation generation."""
        return """You are a Documentation Agent for Claude Code Builder.

Your role is to create comprehensive documentation that:
1. Explains how to use the software
2. Provides clear API documentation
3. Includes usage examples
4. Documents configuration options
5. Covers troubleshooting common issues
6. Is well-organized and easy to navigate

Generate professional, user-friendly documentation."""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        code_or_project: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute documentation generation using SDK."""

        prompt = f"""Generate comprehensive documentation for this code/project:

{code_or_project}

Provide clear, well-organized documentation with usage examples."""

        try:
            response_text = await self.query(prompt)

            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result={"documentation": response_text},
                metadata={"doc_length": len(response_text)},
            )

        except Exception as e:
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                result=None,
                error=str(e),
            )
