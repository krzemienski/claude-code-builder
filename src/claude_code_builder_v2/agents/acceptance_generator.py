"""Acceptance criteria generator using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext


class AcceptanceGenerator(BaseAgent):
    """Generates acceptance criteria using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize AcceptanceGenerator."""
        super().__init__(AgentType.ACCEPTANCE_GENERATOR, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for acceptance criteria."""
        return """You are an Acceptance Criteria Generator for Claude Code Builder.

Your role is to:
1. Generate comprehensive acceptance criteria
2. Define success metrics
3. Create testable conditions
4. Include functional requirements
5. Specify non-functional requirements
6. Provide validation scenarios

Output should include:
- Acceptance criteria checklist
- Success metrics
- Functional validation tests
- Non-functional requirements
- Edge case scenarios
- Validation procedures"""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        requirements: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute acceptance criteria generation using SDK.

        Args:
            context: Execution context
            requirements: Requirements to create criteria for
            **kwargs: Additional arguments

        Returns:
            AgentResponse with acceptance criteria
        """
        prompt = f"""Generate acceptance criteria for:

{requirements}

Provide:
1. Comprehensive acceptance checklist
2. Success metrics
3. Functional validation tests
4. Non-functional requirements
5. Edge case scenarios
6. Validation procedures

Be specific and testable."""

        try:
            response_text = await self.query(prompt)

            return self.create_success_response(
                result={"acceptance_criteria": response_text},
                metadata={"criteria_length": len(response_text)},
            )

        except Exception as e:
            return self.create_error_response(error=str(e))
