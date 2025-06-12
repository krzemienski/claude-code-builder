"""Specification Analyzer agent for Claude Code Builder."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from claude_code_builder.agents.base import BaseAgent, AgentResponse
from claude_code_builder.core.enums import (
    AgentType,
    Complexity,
    MCPCheckpoint,
    MCPServer,
    ProjectType,
)
from claude_code_builder.core.models import (
    ExecutionContext,
    ProcessedSpec,
    SpecAnalysis,
)


class SpecAnalyzer(BaseAgent):
    """Analyzes project specifications to extract requirements and structure."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the SpecAnalyzer."""
        super().__init__(AgentType.SPEC_ANALYZER, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for specification analysis."""
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
- Use MCP servers for documentation lookups and storage

Output structured analysis following the SpecAnalysis model."""

    def get_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return [
            "Read",
            "Grep",
            "WebFetch",
            "WebSearch",
        ]

    async def execute(
        self,
        context: ExecutionContext,
        spec_content: str,
        spec_path: Path,
        **kwargs: Any,
    ) -> AgentResponse:
        """Analyze the specification."""
        try:
            await self.log_progress("Starting specification analysis")
            
            # Get any existing analysis from memory
            existing_analysis = await self._check_existing_analysis(spec_path)
            if existing_analysis:
                await self.log_progress("Found existing analysis in memory")
                return AgentResponse(
                    agent_type=self.agent_type,
                    success=True,
                    result=existing_analysis,
                    metadata={"cached": True},
                )
            
            # Prepare analysis context
            analysis_context = await self._prepare_analysis_context(spec_content)
            
            # Analyze specification using Claude
            analysis = await self._analyze_specification(
                spec_content,
                analysis_context,
                spec_path,
            )
            
            # Validate and enhance analysis
            analysis = await self._validate_and_enhance_analysis(analysis)
            
            # Store analysis in memory
            await self._store_analysis(analysis, spec_path)
            
            # Calculate metrics
            metrics = self._calculate_analysis_metrics(analysis)
            
            await self.log_progress("Specification analysis completed successfully")
            
            # Record checkpoint
            await self.mcp_orchestrator.checkpoint_manager.record_checkpoint(
                MCPCheckpoint.SPECIFICATION_ANALYZED,
                self.mcp_servers_used,
                {"analysis": analysis.model_dump()},
            )
            
            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result=analysis,
                metadata=metrics,
                tokens_used=sum(call.tokens_total for call in self.api_calls),
                cost=sum(call.estimated_cost for call in self.api_calls),
            )
            
        except Exception as e:
            return await self.handle_error(e, "specification analysis", recoverable=False)

    async def _check_existing_analysis(self, spec_path: Path) -> Optional[SpecAnalysis]:
        """Check for existing analysis in memory."""
        try:
            results = await self.search_memory(f"SpecAnalysis:{spec_path.name}")
            if results:
                # Parse stored analysis
                for node in results:
                    for obs in node.get("observations", []):
                        if obs.startswith("{") and "project_name" in obs:
                            return SpecAnalysis(**json.loads(obs))
            return None
        except Exception:
            return None

    async def _prepare_analysis_context(self, spec_content: str) -> str:
        """Prepare context for analysis."""
        context_parts = []
        
        # Add Claude Code documentation if analyzing a Claude Code project
        if "claude" in spec_content.lower() and "code" in spec_content.lower():
            try:
                claude_docs = await self.get_documentation("claude-code-sdk", "overview")
                context_parts.append("## Claude Code SDK Documentation\n" + claude_docs[:5000])
            except Exception:
                pass
        
        # Add analysis guidelines
        context_parts.append("""## Analysis Guidelines

Focus on extracting:
- Explicit requirements (MUST, SHALL, WILL)
- Implicit requirements (assumed functionality)
- Technical constraints
- Quality attributes
- Success criteria

Categorize by:
- Priority: High/Medium/Low
- Type: Functional/Non-functional/Technical
- Risk: High/Medium/Low
""")
        
        return "\n\n".join(context_parts)

    async def _analyze_specification(
        self,
        spec_content: str,
        analysis_context: str,
        spec_path: Path,
    ) -> SpecAnalysis:
        """Analyze the specification using Claude."""
        messages = [
            {
                "role": "user",
                "content": f"""Analyze this project specification and provide a comprehensive SpecAnalysis.

Specification Path: {spec_path}

{analysis_context}

## Specification Content:
{spec_content}

Provide a complete analysis following the SpecAnalysis model structure:
- project_name
- project_type (enum: API, CLI, WEB_APP, LIBRARY, SERVICE, FULLSTACK, MOBILE, DESKTOP, DATA_PIPELINE, ML_MODEL, UNKNOWN)
- complexity (enum: SIMPLE, MODERATE, COMPLEX, VERY_COMPLEX)
- estimated_hours (float)
- estimated_cost (float)
- summary (string)
- key_features (list of strings)
- technical_requirements (list of strings)
- suggested_technologies (list of strings)
- identified_risks (list of strings)
- integration_points (list of strings)

Also include if available:
- description
- technology_stack
- requirements (list of detailed requirements)
- success_criteria
- estimated_phases
- risks
- assumptions
- non_functional_requirements

Be thorough and extract ALL information."""
            }
        ]
        
        response = await self.call_claude(messages, max_tokens=8000)
        
        # Parse response into SpecAnalysis
        content = response.get("content", "")
        
        # Try to extract JSON if present
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
            analysis_data = json.loads(json_str)
        else:
            # Parse structured response
            analysis_data = await self._parse_analysis_response(content)
        
        return SpecAnalysis(**analysis_data)

    async def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """Parse analysis response into structured data."""
        # This would implement parsing logic for non-JSON responses
        # For now, return a basic structure
        lines = content.split('\n')
        
        analysis_data = {
            "project_name": "Unknown Project",
            "project_type": ProjectType.LIBRARY,
            "complexity": Complexity.MODERATE,
            "integration_points": [],  # Changed from {} to []
            # Add all required fields
            "estimated_hours": 80.0,  # Default estimate
            "estimated_cost": 5000.0,  # Default estimate
            "summary": "Project analysis summary",
            "key_features": [],
            "technical_requirements": [],
            "suggested_technologies": [],
            "identified_risks": [],
        }
        
        # Extract information from content
        current_section = None
        for line in lines:
            line = line.strip()
            
            if line.startswith("Project Name:"):
                analysis_data["project_name"] = line.replace("Project Name:", "").strip()
            elif line.startswith("Project Type:"):
                type_str = line.replace("Project Type:", "").strip().upper()
                try:
                    analysis_data["project_type"] = ProjectType[type_str]
                except KeyError:
                    pass
            elif line.startswith("Description:") or line.startswith("Summary:"):
                summary = line.replace("Description:", "").replace("Summary:", "").strip()
                analysis_data["summary"] = summary
            elif line.startswith("## Key Features"):
                current_section = "key_features"
            elif line.startswith("## Technical Requirements"):
                current_section = "technical_requirements"
            elif line.startswith("## Technologies") or line.startswith("## Suggested Technologies"):
                current_section = "suggested_technologies"
            elif line.startswith("## Risks") or line.startswith("## Identified Risks"):
                current_section = "identified_risks"
            elif line.startswith("## Integration Points"):
                current_section = "integration_points"
            elif current_section and line.startswith("-"):
                item = line[1:].strip()
                if current_section in ["key_features", "technical_requirements", "suggested_technologies", "identified_risks", "integration_points"]:
                    analysis_data[current_section].append(item)
        
        # Estimate hours and cost based on complexity
        complexity_multipliers = {
            Complexity.SIMPLE: 0.5,
            Complexity.MODERATE: 1.0,
            Complexity.COMPLEX: 2.0,
            Complexity.VERY_COMPLEX: 3.0,
        }
        multiplier = complexity_multipliers.get(analysis_data["complexity"], 1.0)
        analysis_data["estimated_hours"] = 80.0 * multiplier
        analysis_data["estimated_cost"] = 5000.0 * multiplier
        
        return analysis_data

    async def _validate_and_enhance_analysis(
        self,
        analysis: SpecAnalysis,
    ) -> SpecAnalysis:
        """Validate and enhance the analysis."""
        # Check for missing critical information
        issues = []
        
        if not analysis.key_features:
            issues.append("No key features identified")
        
        if not analysis.technical_requirements:
            issues.append("No technical requirements defined")
        
        if not analysis.suggested_technologies:
            issues.append("No technologies suggested")
        
        # If issues found, try to enhance
        if issues:
            await self.log_progress(f"Enhancing analysis: {', '.join(issues)}")
            
            # Use sequential thinking to fill gaps
            thinking_results = await self.sequential_think(
                f"Enhance specification analysis by addressing: {', '.join(issues)}",
                estimated_steps=3,
            )
            
            # Apply enhancements (simplified)
            if not analysis.key_features:
                analysis.key_features = ["Core functionality as specified"]
            
            if not analysis.technical_requirements:
                analysis.technical_requirements = ["Implement all specified requirements"]
            
            if not analysis.suggested_technologies:
                analysis.suggested_technologies = ["Python", "Async/Await"]
        
        return analysis

    async def _store_analysis(
        self,
        analysis: SpecAnalysis,
        spec_path: Path,
    ) -> None:
        """Store analysis in memory."""
        await self.store_in_memory(
            entity_name=f"SpecAnalysis:{spec_path.name}",
            entity_type="Analysis",
            observations=[
                f"Project: {analysis.project_name}",
                f"Type: {analysis.project_type.value if hasattr(analysis.project_type, 'value') else analysis.project_type}",
                f"Complexity: {analysis.complexity.value if hasattr(analysis.complexity, 'value') else analysis.complexity}",
                f"Requirements: {len(analysis.technical_requirements)}",
                f"Estimated Hours: {analysis.estimated_hours}",
                json.dumps(analysis.model_dump()),  # Store full analysis
            ],
        )
        
        # Create relationships for key features
        entities = []
        for i, feature in enumerate(analysis.key_features[:20]):  # Limit to 20
            entities.append({
                "name": f"Feature:{i+1}",
                "entityType": "Feature",
                "observations": [feature, f"Priority: Medium"],
            })
        
        if entities:
            await self.mcp_orchestrator.memory.create_entities(entities)

    def _calculate_analysis_metrics(self, analysis: SpecAnalysis) -> Dict[str, Any]:
        """Calculate metrics from analysis."""
        return {
            "total_requirements": len(analysis.technical_requirements),
            "functional_requirements": sum(
                1 for r in analysis.technical_requirements
                if not any(nfr in r.lower() for nfr in ["performance", "security", "scalability"])
            ),
            "key_features": len(analysis.key_features),
            "integration_points": len(analysis.integration_points),
            "identified_risks": len(analysis.identified_risks),
            "complexity_score": {
                Complexity.SIMPLE: 1,
                Complexity.MODERATE: 2,
                Complexity.COMPLEX: 3,
                Complexity.VERY_COMPLEX: 4,
            }.get(analysis.complexity, 2),
            "estimated_effort_days": analysis.estimated_hours / 8,  # Convert hours to days
        }


__all__ = ["SpecAnalyzer"]