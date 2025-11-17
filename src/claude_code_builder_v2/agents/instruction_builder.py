"""Instruction builder agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext


class InstructionBuilder(BaseAgent):
    """Builds implementation instructions using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize InstructionBuilder."""
        super().__init__(AgentType.INSTRUCTION_BUILDER, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for instruction building."""
        return """You are an Instruction Builder for Claude Code Builder.

Your role is to:
1. Create detailed implementation instructions
2. Specify file structure and organization
3. Define interfaces and APIs
4. Include code examples and patterns
5. Provide configuration details
6. Ensure clarity and completeness

Output should include:
- Step-by-step implementation guide
- File/directory structure
- Code templates and examples
- Configuration instructions
- Testing guidelines"""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        tasks: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute instruction building using SDK.

        Args:
            context: Execution context
            tasks: Task breakdown
            **kwargs: Additional arguments

        Returns:
            AgentResponse with instructions
        """
        prompt = f"""Based on this task breakdown:

{tasks}

Create detailed implementation instructions:
1. Step-by-step implementation guide
2. Recommended file structure
3. Code templates and patterns
4. Configuration setup
5. Testing approach

Be specific with code examples and structure."""

        try:
            response_text = await self.query(prompt)

            return self.create_success_response(
                result={"instructions": response_text, "tasks": tasks},
                metadata={"instructions_length": len(response_text)},
            )

        except Exception as e:
            return self.create_error_response(error=str(e))
