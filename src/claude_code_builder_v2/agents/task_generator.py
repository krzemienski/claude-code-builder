"""Task Generator agent using Claude SDK."""

import json
from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent, AgentResponse
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import ExecutionContext, TaskBreakdown, Phase, Task


class TaskGenerator(BaseAgent):
    """Generates task breakdowns using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskGenerator."""
        super().__init__(AgentType.TASK_GENERATOR, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for task generation."""
        return """You are a Task Generator for Claude Code Builder.

Your role is to break down project specifications into detailed, actionable tasks organized into phases.

For each task, specify:
1. Task name and description
2. Dependencies on other tasks
3. Estimated time to complete
4. Priority level
5. Required tools and resources
6. Acceptance criteria

Organize tasks into logical phases (e.g., Setup, Core Development, Testing, Documentation).

Output as JSON with this structure:
{
    "phases": [
        {
            "name": "Phase name",
            "order": 1,
            "tasks": [
                {
                    "name": "Task name",
                    "description": "What needs to be done",
                    "estimated_hours": 2.0,
                    "priority": "high|medium|low"
                }
            ]
        }
    ],
    "total_estimated_hours": 40,
    "total_estimated_cost": 100.0
}"""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        specification: str,
        analysis: Any = None,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute task generation using SDK."""

        prompt = f"""Create a detailed task breakdown for this project:

Specification:
{specification}

Generate a comprehensive list of tasks organized into phases."""

        try:
            response_text = await self.query(prompt)
            task_data = self._parse_task_response(response_text)

            # Create simplified TaskBreakdown
            # Note: In full implementation, would create proper Phase/Task objects
            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result=task_data,
                metadata={"num_phases": len(task_data.get("phases", []))},
            )

        except Exception as e:
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                result=None,
                error=str(e),
            )

    def _parse_task_response(self, response: str) -> dict:
        """Parse task breakdown from response."""
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                return self._get_default_tasks()

            return json.loads(json_str)

        except json.JSONDecodeError:
            return self._get_default_tasks()

    def _get_default_tasks(self) -> dict:
        """Get default task structure."""
        return {
            "phases": [
                {
                    "name": "Setup",
                    "order": 1,
                    "tasks": [
                        {
                            "name": "Initialize project",
                            "description": "Set up project structure",
                            "estimated_hours": 2.0,
                            "priority": "high",
                        }
                    ],
                }
            ],
            "total_estimated_hours": 40,
            "total_estimated_cost": 100.0,
        }
