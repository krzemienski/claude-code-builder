"""Specification Analyzer agent using Claude SDK."""

import json
from pathlib import Path
from typing import Any, List

from claude_code_builder_v2.agents.base import BaseAgent, AgentResponse
from claude_code_builder_v2.core.enums import AgentType, Complexity, ProjectType
from claude_code_builder_v2.core.models import ExecutionContext, SpecAnalysis


class SpecAnalyzer(BaseAgent):
    """Analyzes project specifications using Claude SDK."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the SpecAnalyzer."""
        super().__init__(AgentType.SPEC_ANALYZER, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for specification analysis."""
        return """You are a Specification Analyzer for Claude Code Builder.

Your role is to analyze project specifications and extract:
1. Project type and technology stack
2. Core functional requirements
3. Non-functional requirements (performance, security, scalability)
4. Technical constraints and dependencies
5. Integration points and external services
6. Success criteria and acceptance tests
7. Project complexity assessment
8. Risks and assumptions

You must:
- Be thorough and extract ALL requirements
- Identify implicit requirements not explicitly stated
- Flag any ambiguities or missing information
- Categorize requirements by priority
- Assess technical feasibility

Output your analysis as a JSON object with these fields:
{
    "project_type": "api|cli|web|library|fullstack|microservice|mobile|desktop|embedded|ml|data",
    "project_name": "string",
    "complexity": "simple|medium|complex|very_complex",
    "estimated_hours": number,
    "estimated_cost": number,
    "summary": "string",
    "key_features": ["string"],
    "technical_requirements": ["string"],
    "suggested_technologies": ["string"],
    "identified_risks": ["string"],
    "integration_points": ["string"]
}"""

    def get_allowed_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return []  # Stateless analysis doesn't need tools

    async def execute(
        self,
        context: ExecutionContext,
        specification: str,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute specification analysis using SDK."""

        # Build prompt
        prompt = f"""Analyze this project specification:

{specification}

Provide a comprehensive analysis following the JSON format specified in your system prompt.
Be thorough and extract all requirements, assess complexity, and identify risks."""

        try:
            # Query Claude via SDK
            response_text = await self.query(prompt)

            # Parse response as JSON
            analysis_data = self._parse_analysis_response(response_text)

            # Create SpecAnalysis model
            analysis = SpecAnalysis(
                project_type=ProjectType(analysis_data.get("project_type", "api")),
                project_name=analysis_data.get("project_name", "Unknown Project"),
                complexity=Complexity(analysis_data.get("complexity", "medium")),
                estimated_hours=analysis_data.get("estimated_hours", 40),
                estimated_cost=analysis_data.get("estimated_cost", 100.0),
                summary=analysis_data.get("summary", ""),
                key_features=analysis_data.get("key_features", []),
                technical_requirements=analysis_data.get("technical_requirements", []),
                suggested_technologies=analysis_data.get("suggested_technologies", []),
                identified_risks=analysis_data.get("identified_risks", []),
                integration_points=analysis_data.get("integration_points", []),
            )

            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result=analysis,
                metadata={"specification_length": len(specification)},
            )

        except Exception as e:
            self.logger.logger.error(
                "spec_analysis_failed",
                error=str(e),
                exc_info=True,
            )
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                result=None,
                error=str(e),
            )

    def _parse_analysis_response(self, response: str) -> dict:
        """Parse Claude's response into analysis data."""
        try:
            # Try to extract JSON from response
            # Look for JSON block in response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                # Fallback: return default structure
                return self._get_default_analysis()

            return json.loads(json_str)

        except json.JSONDecodeError:
            self.logger.logger.warning(
                "failed_to_parse_json",
                response_preview=response[:200],
            )
            return self._get_default_analysis()

    def _get_default_analysis(self) -> dict:
        """Get default analysis structure."""
        return {
            "project_type": "api",
            "project_name": "Unknown Project",
            "complexity": "medium",
            "estimated_hours": 40,
            "estimated_cost": 100.0,
            "summary": "Unable to fully parse specification",
            "key_features": [],
            "technical_requirements": [],
            "suggested_technologies": [],
            "identified_risks": ["Specification may need clarification"],
            "integration_points": [],
        }
