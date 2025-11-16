"""Instruction Builder agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent, AgentResponse
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import ExecutionContext


class InstructionBuilder(BaseAgent):
    """Builds detailed implementation instructions using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the InstructionBuilder."""
        super().__init__(AgentType.INSTRUCTION_BUILDER, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for instruction building."""
        return """You are an Instruction Builder for Claude Code Builder.

Your role is to create detailed, step-by-step implementation instructions that:
1. Break down complex tasks into clear steps
2. Specify exact commands and code to write
3. Include rationale for technical decisions
4. Anticipate potential issues
5. Provide alternative approaches when applicable

Generate actionable instructions that developers can follow exactly."""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        task: Any,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute instruction building using SDK."""

        prompt = f"""Create detailed implementation instructions for this task:

{task}

Provide step-by-step instructions with exact commands and code examples."""

        try:
            response_text = await self.query(prompt)

            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result={"instructions": response_text},
                metadata={"instruction_length": len(response_text)},
            )

        except Exception as e:
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                result=None,
                error=str(e),
            )
