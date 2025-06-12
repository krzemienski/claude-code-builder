"""Instruction Builder agent for Claude Code Builder."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from claude_code_builder.agents.base import BaseAgent, AgentResponse
from claude_code_builder.core.enums import (
    AgentType,
    MCPServer,
)
from claude_code_builder.core.models import (
    ExecutionContext,
    Task,
    TaskBreakdown,
)


class InstructionSet(BaseAgent):
    """Container for task instructions."""
    
    task_id: str
    task_title: str
    instructions: List[str]
    code_structure: Dict[str, Any]
    test_cases: List[Dict[str, Any]]
    dependencies: List[str]
    tools_required: List[str]
    estimated_tokens: int
    
    def __init__(self, **data: Any) -> None:
        """Initialize instruction set."""
        super().__init__(**data)


class InstructionBuilder(BaseAgent):
    """Builds detailed implementation instructions for tasks."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the InstructionBuilder."""
        super().__init__(AgentType.INSTRUCTION_BUILDER, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for instruction building."""
        return """You are an Instruction Builder for Claude Code Builder.

Your role is to create detailed implementation instructions for each task:
1. Break down tasks into step-by-step instructions
2. Define code structure and architecture
3. Specify implementation patterns and best practices
4. Create test cases and validation criteria
5. Identify required tools and dependencies
6. Provide code examples and templates
7. Flag potential issues and edge cases

You must:
- Create instructions that are clear and unambiguous
- Include all necessary technical details
- Follow project conventions and standards
- Consider error handling and edge cases
- Provide testable acceptance criteria
- Use MCP servers for documentation and examples
- Optimize instructions for Claude Code execution

Output detailed instructions that can be directly executed by the Code Generator."""

    def get_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return [
            "Read",
            "Glob",
            "WebFetch",
            "WebSearch",
        ]

    async def execute(
        self,
        context: ExecutionContext,
        task: Task,
        task_breakdown: TaskBreakdown,
        project_context: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResponse:
        """Build instructions for a task."""
        try:
            await self.log_progress(f"Building instructions for: {task.title}")
            
            # Get related context
            task_context = await self._gather_task_context(
                task,
                task_breakdown,
                project_context,
            )
            
            # Get relevant documentation
            documentation = await self._gather_documentation(
                task,
                project_context,
            )
            
            # Build implementation instructions
            instructions = await self._build_instructions(
                task,
                task_context,
                documentation,
            )
            
            # Define code structure
            code_structure = await self._define_code_structure(
                task,
                project_context,
            )
            
            # Create test cases
            test_cases = await self._create_test_cases(
                task,
                instructions,
            )
            
            # Identify dependencies and tools
            dependencies = await self._identify_dependencies(
                task,
                project_context,
            )
            
            # Create instruction set
            instruction_set = {
                "task_id": str(task.task_id),
                "task_title": task.title,
                "instructions": instructions,
                "code_structure": code_structure,
                "test_cases": test_cases,
                "dependencies": dependencies,
                "tools_required": task.required_tools,
                "estimated_tokens": await self._estimate_tokens(instructions),
                "metadata": {
                    "phase": str(task.phase_id),
                    "complexity": task.complexity.value,
                    "priority": task.priority.value,
                },
            }
            
            # Validate instructions
            instruction_set = await self._validate_instructions(instruction_set, task)
            
            # Store in memory
            await self._store_instructions(instruction_set, task)
            
            # Calculate metrics
            metrics = self._calculate_instruction_metrics(instruction_set)
            
            await self.log_progress(f"Instructions built successfully for: {task.title}")
            
            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result=instruction_set,
                metadata=metrics,
                tokens_used=sum(call.tokens_total for call in self.api_calls),
                cost=sum(call.estimated_cost for call in self.api_calls),
            )
            
        except Exception as e:
            return await self.handle_error(
                e,
                f"instruction building for {task.title}",
                recoverable=True,
            )

    async def _gather_task_context(
        self,
        task: Task,
        task_breakdown: TaskBreakdown,
        project_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Gather context relevant to the task."""
        context = {
            "task": task.model_dump(),
            "phase": None,
            "dependent_tasks": [],
            "depending_tasks": [],
            "parallel_tasks": [],
        }
        
        # Find task's phase
        for phase in task_breakdown.phases:
            if phase.phase_id == task.phase_id:
                context["phase"] = phase.model_dump()
                break
        
        # Find related tasks
        for other_task in task_breakdown.tasks:
            if other_task.task_id in task.dependencies:
                context["dependent_tasks"].append({
                    "id": str(other_task.task_id),
                    "title": other_task.title,
                    "status": other_task.status.value,
                })
            elif task.task_id in other_task.dependencies:
                context["depending_tasks"].append({
                    "id": str(other_task.task_id),
                    "title": other_task.title,
                })
        
        # Find parallel tasks
        for track in task_breakdown.parallel_tracks:
            if task.task_id in track:
                for task_id in track:
                    if task_id != task.task_id:
                        parallel_task = next(
                            (t for t in task_breakdown.tasks if t.task_id == task_id),
                            None
                        )
                        if parallel_task:
                            context["parallel_tasks"].append({
                                "id": str(parallel_task.task_id),
                                "title": parallel_task.title,
                            })
        
        # Add project context
        context["project"] = {
            "name": project_context.get("project_name", "Unknown"),
            "type": project_context.get("project_type", "Unknown"),
            "stack": project_context.get("technology_stack", []),
        }
        
        return context

    async def _gather_documentation(
        self,
        task: Task,
        project_context: Dict[str, Any],
    ) -> Dict[str, str]:
        """Gather relevant documentation for the task."""
        documentation = {}
        
        try:
            # Get documentation for required tools
            for tool in task.required_tools[:3]:  # Limit to prevent token overflow
                if tool.lower() in ["claude", "claude-code", "claude-sdk"]:
                    await self.use_mcp_server(MCPServer.CONTEXT7)
                    docs = await self.get_documentation("claude-code-sdk", "tools")
                    documentation[tool] = docs[:2000]  # Limit size
                
                elif tool.lower() in ["python", "asyncio", "pydantic"]:
                    # Could fetch Python docs
                    documentation[tool] = f"Standard {tool} documentation"
            
            # Get technology-specific docs
            tech_stack = project_context.get("technology_stack", [])
            for tech in tech_stack[:2]:  # Limit
                if tech.lower() in ["fastapi", "django", "flask"]:
                    # Could fetch framework docs
                    documentation[tech] = f"{tech} framework documentation"
                
        except Exception as e:
            await self.log_progress(
                f"Documentation gathering partial: {e}",
                level="warning"
            )
        
        return documentation

    async def _build_instructions(
        self,
        task: Task,
        task_context: Dict[str, Any],
        documentation: Dict[str, str],
    ) -> List[str]:
        """Build step-by-step instructions."""
        # Prepare documentation context
        doc_context = "\n\n".join([
            f"## {tool} Documentation\n{doc[:500]}"
            for tool, doc in documentation.items()
        ])
        
        messages = [
            {
                "role": "user",
                "content": f"""Create detailed step-by-step implementation instructions for this task:

Task: {task.title}
Description: {task.description}

Acceptance Criteria:
{chr(10).join(f"- {criterion}" for criterion in task.acceptance_criteria)}

Task Context:
- Phase: {task_context['phase']['name'] if task_context['phase'] else 'Unknown'}
- Dependencies: {len(task_context['dependent_tasks'])} tasks must be completed first
- Depending: {len(task_context['depending_tasks'])} tasks depend on this
- Complexity: {task.complexity.value}
- Estimated Hours: {task.estimated_hours}

Project Context:
- Type: {task_context['project']['type']}
- Stack: {', '.join(task_context['project']['stack'])}

{doc_context}

Create detailed instructions that:
1. Break down the task into clear, actionable steps
2. Include specific implementation details
3. Reference best practices and patterns
4. Handle error cases and edge conditions
5. Ensure all acceptance criteria are met
6. Include validation and testing steps

Format as a numbered list of detailed instructions."""
            }
        ]
        
        response = await self.call_claude(messages, max_tokens=4000)
        content = response.get("content", "")
        
        # Parse instructions
        instructions = []
        lines = content.split('\n')
        current_instruction = ""
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                if current_instruction:
                    instructions.append(current_instruction)
                current_instruction = line.lstrip('0123456789.-').strip()
            elif line and current_instruction:
                current_instruction += " " + line
        
        if current_instruction:
            instructions.append(current_instruction)
        
        # Ensure we have instructions
        if not instructions:
            instructions = [
                f"Implement {task.title} according to specifications",
                "Follow project coding standards",
                "Add appropriate error handling",
                "Write unit tests for the implementation",
                "Update documentation as needed",
            ]
        
        return instructions

    async def _define_code_structure(
        self,
        task: Task,
        project_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Define the code structure for the task."""
        messages = [
            {
                "role": "user",
                "content": f"""Define the code structure for implementing this task:

Task: {task.title}
Description: {task.description}

Project Type: {project_context.get('project_type', 'Unknown')}
Technology Stack: {', '.join(project_context.get('technology_stack', []))}

Define:
1. Files to create/modify
2. Classes and functions to implement
3. Module structure
4. Key interfaces and contracts
5. Configuration requirements

Provide as a JSON structure with:
- files: array of file paths and descriptions
- classes: array of class definitions
- functions: array of function signatures
- interfaces: array of interface contracts
- config: configuration requirements"""
            }
        ]
        
        response = await self.call_claude(messages, max_tokens=2000)
        content = response.get("content", "")
        
        # Parse structure
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
            try:
                structure = json.loads(json_str)
            except json.JSONDecodeError:
                structure = self._get_default_structure(task)
        else:
            structure = self._get_default_structure(task)
        
        return structure

    async def _create_test_cases(
        self,
        task: Task,
        instructions: List[str],
    ) -> List[Dict[str, Any]]:
        """Create test cases for the task."""
        messages = [
            {
                "role": "user",
                "content": f"""Create test cases for this task implementation:

Task: {task.title}

Acceptance Criteria:
{chr(10).join(f"- {criterion}" for criterion in task.acceptance_criteria)}

Implementation Steps:
{chr(10).join(f"{i+1}. {inst}" for i, inst in enumerate(instructions[:5]))}

Create test cases that:
1. Verify each acceptance criterion
2. Test happy path scenarios
3. Test error conditions
4. Test edge cases
5. Include setup and teardown

For each test case provide:
- name: descriptive test name
- description: what is being tested
- setup: preparation steps
- input: test input data
- expected: expected output/behavior
- validation: how to verify success

Provide as JSON array of test case objects."""
            }
        ]
        
        response = await self.call_claude(messages, max_tokens=3000)
        content = response.get("content", "")
        
        # Parse test cases
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
            try:
                test_cases = json.loads(json_str)
            except json.JSONDecodeError:
                test_cases = self._get_default_test_cases(task)
        else:
            test_cases = self._get_default_test_cases(task)
        
        return test_cases

    async def _identify_dependencies(
        self,
        task: Task,
        project_context: Dict[str, Any],
    ) -> List[str]:
        """Identify task dependencies beyond what's in task definition."""
        dependencies = []
        
        # Add explicit dependencies
        dependencies.extend(task.required_tools)
        
        # Add technology stack dependencies
        tech_stack = project_context.get("technology_stack", [])
        for tech in tech_stack:
            if tech.lower() not in [d.lower() for d in dependencies]:
                dependencies.append(tech)
        
        # Add common dependencies based on task type
        task_lower = task.title.lower()
        
        if "api" in task_lower or "endpoint" in task_lower:
            if "fastapi" not in dependencies:
                dependencies.append("fastapi")
        
        if "database" in task_lower or "model" in task_lower:
            if "sqlalchemy" not in dependencies:
                dependencies.append("sqlalchemy")
        
        if "test" in task_lower:
            if "pytest" not in dependencies:
                dependencies.append("pytest")
        
        return list(set(dependencies))  # Remove duplicates

    async def _estimate_tokens(self, instructions: List[str]) -> int:
        """Estimate tokens needed for code generation."""
        # Rough estimation
        instruction_text = '\n'.join(instructions)
        instruction_tokens = len(instruction_text.split()) * 1.5  # Rough token estimate
        
        # Add overhead for code generation
        code_multiplier = 3  # Code typically 3x longer than instructions
        
        return int(instruction_tokens * code_multiplier)

    async def _validate_instructions(
        self,
        instruction_set: Dict[str, Any],
        task: Task,
    ) -> Dict[str, Any]:
        """Validate and enhance instructions."""
        issues = []
        
        # Check instruction completeness
        if len(instruction_set["instructions"]) < 3:
            issues.append("Too few instructions")
        
        # Check code structure
        if not instruction_set["code_structure"].get("files"):
            issues.append("No files defined in code structure")
        
        # Check test cases
        if len(instruction_set["test_cases"]) < 2:
            issues.append("Insufficient test cases")
        
        # Check coverage of acceptance criteria
        criteria_covered = 0
        instruction_text = ' '.join(instruction_set["instructions"]).lower()
        for criterion in task.acceptance_criteria:
            if any(word in instruction_text for word in criterion.lower().split()):
                criteria_covered += 1
        
        coverage = criteria_covered / len(task.acceptance_criteria) if task.acceptance_criteria else 0
        if coverage < 0.7:
            issues.append(f"Low acceptance criteria coverage: {coverage:.0%}")
        
        if issues:
            await self.log_progress(
                f"Instruction validation issues: {', '.join(issues)}",
                level="warning"
            )
        
        return instruction_set

    async def _store_instructions(
        self,
        instruction_set: Dict[str, Any],
        task: Task,
    ) -> None:
        """Store instructions in memory."""
        await self.store_in_memory(
            entity_name=f"Instructions:{task.task_id}",
            entity_type="Instructions",
            observations=[
                f"Task: {task.title}",
                f"Instructions: {len(instruction_set['instructions'])}",
                f"Files: {len(instruction_set['code_structure'].get('files', []))}",
                f"Test Cases: {len(instruction_set['test_cases'])}",
                f"Dependencies: {len(instruction_set['dependencies'])}",
                json.dumps(instruction_set),  # Store full instructions
            ],
        )

    def _calculate_instruction_metrics(
        self,
        instruction_set: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate metrics from instructions."""
        return {
            "instruction_count": len(instruction_set["instructions"]),
            "file_count": len(instruction_set["code_structure"].get("files", [])),
            "class_count": len(instruction_set["code_structure"].get("classes", [])),
            "function_count": len(instruction_set["code_structure"].get("functions", [])),
            "test_case_count": len(instruction_set["test_cases"]),
            "dependency_count": len(instruction_set["dependencies"]),
            "estimated_tokens": instruction_set["estimated_tokens"],
            "complexity": instruction_set["metadata"]["complexity"],
        }

    def _get_default_structure(self, task: Task) -> Dict[str, Any]:
        """Get default code structure."""
        return {
            "files": [
                {
                    "path": f"src/{task.title.lower().replace(' ', '_')}.py",
                    "description": f"Implementation for {task.title}",
                }
            ],
            "classes": [],
            "functions": [
                {
                    "name": f"execute_{task.title.lower().replace(' ', '_')}",
                    "signature": "async def execute_task() -> Any",
                    "description": f"Main function for {task.title}",
                }
            ],
            "interfaces": [],
            "config": {},
        }

    def _get_default_test_cases(self, task: Task) -> List[Dict[str, Any]]:
        """Get default test cases."""
        return [
            {
                "name": f"test_{task.title.lower().replace(' ', '_')}_success",
                "description": f"Test successful execution of {task.title}",
                "setup": "Initialize test environment",
                "input": {"test": "data"},
                "expected": {"success": True},
                "validation": "Assert success response",
            },
            {
                "name": f"test_{task.title.lower().replace(' ', '_')}_error",
                "description": f"Test error handling for {task.title}",
                "setup": "Initialize test environment with error condition",
                "input": {"test": "error_data"},
                "expected": {"success": False},
                "validation": "Assert error is handled gracefully",
            },
        ]


__all__ = ["InstructionBuilder"]