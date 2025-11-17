"""Task generator agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext


class TaskGenerator(BaseAgent):
    """Generates task breakdowns using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize TaskGenerator."""
        super().__init__(AgentType.TASK_GENERATOR, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for task generation."""
        return """You are a Task Generator for Claude Code Builder.

Your role is to:
1. Break down projects into concrete, actionable tasks
2. Identify task dependencies
3. Estimate effort for each task
4. Organize tasks into logical phases
5. Ensure comprehensive coverage
6. Create clear, specific task descriptions

Output should be structured JSON or markdown with:
- Task list with descriptions
- Dependencies between tasks
- Effort estimates
- Phase groupings
- Priority levels"""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        analysis: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute task generation using SDK.

        Args:
            context: Execution context
            analysis: Specification analysis
            **kwargs: Additional arguments

        Returns:
            AgentResponse with task breakdown
        """
        prompt = f"""Based on this specification analysis:

{analysis}

Generate a comprehensive task breakdown:
1. List all tasks needed to implement this project
2. Identify dependencies between tasks
3. Estimate effort for each task
4. Group tasks into logical phases
5. Assign priority levels

Be specific and actionable."""

        try:
            response_text = await self.query(prompt)

            return self.create_success_response(
                result={"tasks": response_text, "analysis": analysis},
                metadata={"task_breakdown_length": len(response_text)},
            )

        except Exception as e:
            return self.create_error_response(error=str(e))
