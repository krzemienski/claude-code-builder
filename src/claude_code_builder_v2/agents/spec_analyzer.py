"""Specification analyzer agent using Claude SDK."""

from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.models import AgentResponse, ExecutionContext


class SpecAnalyzer(BaseAgent):
    """Analyzes project specifications using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize SpecAnalyzer."""
        super().__init__(AgentType.SPEC_ANALYZER, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for specification analysis."""
        return """You are a Specification Analyzer for Claude Code Builder.

Your role is to:
1. Analyze project specifications comprehensively
2. Identify key requirements and constraints
3. Assess technical complexity
4. Identify technology stack requirements
5. Flag potential risks or ambiguities
6. Provide structured analysis output

Output your analysis in a clear, structured format with:
- Summary of the project
- Complexity assessment (low/medium/high)
- Key requirements list
- Recommended tech stack
- Identified risks
- Estimated timeline range"""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []

    async def execute(
        self,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute specification analysis using SDK.

        Args:
            context: Execution context with specification
            **kwargs: Additional arguments

        Returns:
            AgentResponse with analysis
        """
        prompt = f"""Analyze this project specification:

{context.specification}

Provide a comprehensive analysis covering:
1. Project summary
2. Complexity assessment
3. Key requirements
4. Recommended technology stack
5. Potential risks
6. Estimated timeline

Be thorough and identify any ambiguities or concerns."""

        try:
            response_text = await self.query(prompt)

            return self.create_success_response(
                result={"analysis": response_text, "specification": context.specification},
                metadata={"analysis_length": len(response_text)},
            )

        except Exception as e:
            return self.create_error_response(
                error=str(e),
                metadata={"specification_length": len(context.specification)},
            )
