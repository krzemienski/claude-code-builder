"""Test generator using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext


class TestGenerator(BaseAgent):
    """Generates functional tests using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize TestGenerator."""
        super().__init__(AgentType.TEST_GENERATOR, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for test generation."""
        return """You are a Test Generator for Claude Code Builder.

Your role is to:
1. Generate functional test scenarios
2. Create production validation tests
3. Define integration test cases
4. Provide real-world test examples
5. Specify test data requirements
6. Create end-to-end test flows

Output should include:
- Functional test scenarios
- Integration test cases
- Production validation scripts
- Test data specifications
- Expected outcomes
- Test execution procedures

IMPORTANT: Generate REAL functional tests only, NO unit tests, NO mocks.
Tests should validate actual functionality by running the built application."""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        implementation: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute test generation using SDK.

        Args:
            context: Execution context
            implementation: Implementation to create tests for
            **kwargs: Additional arguments

        Returns:
            AgentResponse with test specifications
        """
        prompt = f"""Generate functional tests for:

{implementation}

Provide:
1. Functional test scenarios (real-world usage)
2. Integration test cases (component interactions)
3. Production validation scripts (actual execution)
4. Test data specifications
5. Expected outcomes
6. Test execution procedures

CRITICAL: Generate only REAL functional tests that:
- Test actual built artifacts
- Use real input/output
- Validate end-to-end functionality
- NO unit tests
- NO mocks
- NO stubs

Be specific, executable, and production-focused."""

        try:
            response_text = await self.query(prompt)

            return self.create_success_response(
                result={"test_specifications": response_text},
                metadata={
                    "test_spec_length": len(response_text),
                    "test_type": "functional_only",
                },
            )

        except Exception as e:
            return self.create_error_response(error=str(e))
