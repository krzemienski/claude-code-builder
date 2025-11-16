"""Acceptance Criteria Generator agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent, AgentResponse
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import ExecutionContext


class AcceptanceGenerator(BaseAgent):
    """Generates acceptance criteria using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the AcceptanceGenerator."""
        super().__init__(AgentType.ACCEPTANCE_GENERATOR, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for acceptance criteria generation."""
        return """You are an Acceptance Criteria Generator for Claude Code Builder.

Your role is to create clear, testable acceptance criteria that:
1. Define what "done" means for each feature
2. Are specific and measurable
3. Cover functional and non-functional requirements
4. Include success and failure scenarios
5. Can be automated where possible

Generate comprehensive acceptance criteria following Given-When-Then format."""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        feature_description: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute acceptance criteria generation using SDK."""

        prompt = f"""Generate acceptance criteria for this feature:

{feature_description}

Provide clear, testable acceptance criteria in Given-When-Then format."""

        try:
            response_text = await self.query(prompt)

            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result={"acceptance_criteria": response_text},
                metadata={"criteria_length": len(response_text)},
            )

        except Exception as e:
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                result=None,
                error=str(e),
            )
