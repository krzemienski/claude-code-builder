"""Documentation agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext


class DocumentationAgent(BaseAgent):
    """Generates documentation using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize DocumentationAgent."""
        super().__init__(AgentType.DOCUMENTATION_AGENT, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for documentation."""
        return """You are a Documentation Agent for Claude Code Builder.

Your role is to:
1. Create comprehensive documentation
2. Write clear README files
3. Document APIs and interfaces
4. Provide usage examples
5. Include troubleshooting guides
6. Ensure professional quality

Output should include:
- README with overview and quickstart
- API documentation
- Usage examples
- Configuration guides
- Contributing guidelines
- Troubleshooting sections"""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        project_details: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute documentation generation using SDK.

        Args:
            context: Execution context
            project_details: Project details
            **kwargs: Additional arguments

        Returns:
            AgentResponse with documentation
        """
        prompt = f"""Based on this project:

{project_details}

Generate comprehensive documentation:
1. README.md with overview and quickstart
2. API/interface documentation
3. Usage examples
4. Configuration guide
5. Contributing guidelines
6. Troubleshooting section

Be thorough and professional."""

        try:
            response_text = await self.query(prompt)

            return self.create_success_response(
                result={"documentation": response_text},
                metadata={"documentation_length": len(response_text)},
            )

        except Exception as e:
            return self.create_error_response(error=str(e))
