"""Review agent implementation."""

import json
from typing import Dict, Any, List, Optional

from claude_code_builder.agents.base import BaseAgent
from claude_code_builder.core.models import AgentResponse, ExecutionContext


class ReviewAgent(BaseAgent):
    """Reviews generated code for quality, completeness, and best practices."""
    
    def __init__(self):
        super().__init__(
            name="ReviewAgent",
            description="Validates code quality and ensures requirements are met",
            capabilities=[
                "code_review",
                "quality_assurance",
                "requirements_validation",
                "security_analysis",
                "performance_review",
                "best_practices"
            ]
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        code_files: Optional[Dict[str, str]] = None,
        requirements: Optional[List[str]] = None,
        **kwargs
    ) -> AgentResponse:
        """Review generated code for quality and completeness.
        
        Args:
            context: Execution context
            code_files: Dictionary of file paths to code content
            requirements: List of requirements to validate
            **kwargs: Additional arguments
            
        Returns:
            AgentResponse with review results
        """
        try:
            # Get code files from context if not provided
            if not code_files:
                code_output = context.agent_outputs.get("CodeGenerator", {})
                code_files = code_output.get("files", {})
            
            if not code_files:
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    output={},
                    error="No code files found to review"
                )
            
            # Get requirements from context if not provided
            if not requirements:
                spec_analysis = context.agent_outputs.get("SpecAnalyzer", {})
                requirements = spec_analysis.get("requirements", {}).get("functional", [])
            
            # Perform comprehensive review
            review_results = {
                "overall_quality": 0,
                "requirements_coverage": {},
                "code_quality": {},
                "security_issues": [],
                "performance_issues": [],
                "best_practices": {},
                "suggestions": [],
                "approval_status": "pending"
            }
            
            # Review each file
            for file_path, code in code_files.items():
                file_review = await self._review_file(
                    file_path=file_path,
                    code=code,
                    requirements=requirements,
                    context=context
                )
                
                # Aggregate results
                self._aggregate_review_results(review_results, file_review, file_path)
            
            # Calculate overall metrics
            review_results["overall_quality"] = self._calculate_overall_quality(review_results)
            review_results["approval_status"] = self._determine_approval_status(review_results)
            
            # Generate improvement suggestions
            review_results["suggestions"] = self._generate_suggestions(review_results)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                output=review_results,
                metadata={
                    "files_reviewed": len(code_files),
                    "quality_score": review_results["overall_quality"],
                    "approved": review_results["approval_status"] == "approved"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Code review failed: {e}")
            return AgentResponse(
                agent_name=self.name,
                success=False,
                output={},
                error=str(e)
            )
    
    async def _review_file(
        self,
        file_path: str,
        code: str,
        requirements: List[str],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Review a single file comprehensively."""
        # Create review prompt
        prompt = self._create_review_prompt(file_path, code, requirements)
        
        # Get AI review
        response = await context.executor.execute(
            prompt=prompt,
            response_format="json"
        )
        
        # Parse response
        try:
            ai_review = json.loads(response)
        except json.JSONDecodeError:
            ai_review = self._parse_text_review(response)
        
        # Perform static analysis
        static_analysis = self._perform_static_analysis(code)
        
        # Combine results
        file_review = {
            "quality_score": ai_review.get("quality_score", 0),
            "requirements_met": ai_review.get("requirements_met", []),
            "requirements_missing": ai_review.get("requirements_missing", []),
            "code_issues": ai_review.get("code_issues", []) + static_analysis["issues"],
            "security_concerns": ai_review.get("security_concerns", []),
            "performance_concerns": ai_review.get("performance_concerns", []),
            "best_practices_violations": ai_review.get("best_practices_violations", []),
            "positive_aspects": ai_review.get("positive_aspects", []),
            "complexity_score": static_analysis["complexity"]
        }
        
        return file_review
    
    def _create_review_prompt(
        self,
        file_path: str,
        code: str,
        requirements: List[str]
    ) -> str:
        """Create prompt for code review."""
        requirements_text = "\n".join([f"- {req}" for req in requirements[:10]])  # Limit to 10
        
        return f"""Review the following code for quality, completeness, and adherence to requirements.

FILE: {file_path}

REQUIREMENTS TO VALIDATE:
{requirements_text}

CODE TO REVIEW:
```python
{code}
```

Provide a comprehensive review in JSON format with the following structure:
{{
    "quality_score": <0-100>,
    "requirements_met": ["list of requirements that are implemented"],
    "requirements_missing": ["list of requirements not found"],
    "code_issues": [
        {{"type": "error|warning", "line": <number>, "message": "description"}}
    ],
    "security_concerns": ["list of security issues"],
    "performance_concerns": ["list of performance issues"],
    "best_practices_violations": ["list of violations"],
    "positive_aspects": ["list of good practices found"]
}}

Consider:
1. Code correctness and functionality
2. Error handling and edge cases
3. Code organization and readability
4. Security vulnerabilities
5. Performance implications
6. Python best practices
7. Documentation completeness
8. Test coverage potential
"""
    
    def _parse_text_review(self, response: str) -> Dict[str, Any]:
        """Parse text review response as fallback."""
        # Default structure
        review = {
            "quality_score": 70,
            "requirements_met": [],
            "requirements_missing": [],
            "code_issues": [],
            "security_concerns": [],
            "performance_concerns": [],
            "best_practices_violations": [],
            "positive_aspects": []
        }
        
        # Try to extract information from text
        lines = response.lower().split('\n')
        
        for line in lines:
            if "quality" in line and any(char.isdigit() for char in line):
                # Extract quality score
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    review["quality_score"] = int(numbers[0])
            
            elif "security" in line and ("issue" in line or "concern" in line):
                review["security_concerns"].append(line.strip())
            
            elif "performance" in line and ("issue" in line or "concern" in line):
                review["performance_concerns"].append(line.strip())
        
        return review
    
    def _perform_static_analysis(self, code: str) -> Dict[str, Any]:
        """Perform static code analysis."""
        analysis = {
            "issues": [],
            "complexity": 0
        }
        
        # Basic checks
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 88:  # PEP 8 recommendation
                analysis["issues"].append({
                    "type": "warning",
                    "line": i,
                    "message": f"Line too long ({len(line)} > 88 characters)"
                })
            
            # Check for common issues
            if "except:" in line:  # Bare except
                analysis["issues"].append({
                    "type": "warning",
                    "line": i,
                    "message": "Bare except clause - should specify exception type"
                })
            
            if "TODO" in line or "FIXME" in line:
                analysis["issues"].append({
                    "type": "warning",
                    "line": i,
                    "message": "Unresolved TODO/FIXME comment"
                })
            
            # Check for potential security issues
            if "eval(" in line or "exec(" in line:
                analysis["issues"].append({
                    "type": "error",
                    "line": i,
                    "message": "Use of eval/exec - potential security risk"
                })
            
            if "pickle.loads" in line:
                analysis["issues"].append({
                    "type": "warning",
                    "line": i,
                    "message": "Unpickling data - potential security risk"
                })
        
        # Calculate complexity (simplified)
        import re
        
        # Count functions and classes
        functions = len(re.findall(r'^\s*def\s+', code, re.MULTILINE))
        classes = len(re.findall(r'^\s*class\s+', code, re.MULTILINE))
        
        # Count control structures
        if_statements = len(re.findall(r'\bif\b', code))
        for_loops = len(re.findall(r'\bfor\b', code))
        while_loops = len(re.findall(r'\bwhile\b', code))
        
        # Simple complexity score
        analysis["complexity"] = functions + (classes * 2) + if_statements + for_loops + while_loops
        
        return analysis
    
    def _aggregate_review_results(
        self,
        overall_results: Dict[str, Any],
        file_review: Dict[str, Any],
        file_path: str
    ) -> None:
        """Aggregate file review into overall results."""
        # Update code quality
        overall_results["code_quality"][file_path] = {
            "score": file_review["quality_score"],
            "complexity": file_review["complexity_score"],
            "issues": len(file_review["code_issues"])
        }
        
        # Update requirements coverage
        for req in file_review["requirements_met"]:
            if req not in overall_results["requirements_coverage"]:
                overall_results["requirements_coverage"][req] = []
            overall_results["requirements_coverage"][req].append(file_path)
        
        # Aggregate issues
        overall_results["security_issues"].extend([
            {"file": file_path, "issue": issue}
            for issue in file_review["security_concerns"]
        ])
        
        overall_results["performance_issues"].extend([
            {"file": file_path, "issue": issue}
            for issue in file_review["performance_concerns"]
        ])
        
        # Update best practices
        overall_results["best_practices"][file_path] = file_review["best_practices_violations"]
    
    def _calculate_overall_quality(self, review_results: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        if not review_results["code_quality"]:
            return 0.0
        
        # Average quality scores
        quality_scores = [
            file_data["score"]
            for file_data in review_results["code_quality"].values()
        ]
        
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Apply penalties
        security_penalty = min(len(review_results["security_issues"]) * 5, 30)
        performance_penalty = min(len(review_results["performance_issues"]) * 3, 20)
        
        # Calculate final score
        final_score = max(0, avg_quality - security_penalty - performance_penalty)
        
        return round(final_score, 1)
    
    def _determine_approval_status(self, review_results: Dict[str, Any]) -> str:
        """Determine if code is approved, needs revision, or rejected."""
        quality_score = review_results["overall_quality"]
        security_issues = len(review_results["security_issues"])
        
        if quality_score >= 80 and security_issues == 0:
            return "approved"
        elif quality_score >= 60 and security_issues <= 2:
            return "needs_revision"
        else:
            return "rejected"
    
    def _generate_suggestions(self, review_results: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on review."""
        suggestions = []
        
        # Quality-based suggestions
        if review_results["overall_quality"] < 70:
            suggestions.append("Consider refactoring to improve code quality and readability")
        
        # Security suggestions
        if review_results["security_issues"]:
            suggestions.append("Address security vulnerabilities before deployment")
            for issue in review_results["security_issues"][:3]:
                suggestions.append(f"Fix security issue in {issue['file']}: {issue['issue']}")
        
        # Performance suggestions
        if review_results["performance_issues"]:
            suggestions.append("Optimize performance bottlenecks")
            for issue in review_results["performance_issues"][:3]:
                suggestions.append(f"Improve performance in {issue['file']}: {issue['issue']}")
        
        # Best practices
        total_violations = sum(
            len(violations)
            for violations in review_results["best_practices"].values()
        )
        
        if total_violations > 5:
            suggestions.append("Review and fix best practice violations")
        
        # Requirements coverage
        if review_results["requirements_coverage"]:
            uncovered = [
                req for req, files in review_results["requirements_coverage"].items()
                if not files
            ]
            if uncovered:
                suggestions.append(f"Implement missing requirements: {', '.join(uncovered[:3])}")
        
        return suggestions