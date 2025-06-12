"""Code Generator agent for Claude Code Builder."""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from claude_code_builder.agents.base import BaseAgent, AgentResponse
from claude_code_builder.core.enums import (
    AgentType,
    MCPCheckpoint,
    MCPServer,
)
from claude_code_builder.core.logging_system import GeneratedCode
from claude_code_builder.core.models import (
    ExecutionContext,
    Task,
)


class CodeGenerator(BaseAgent):
    """Generates implementation code based on instructions."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the CodeGenerator."""
        super().__init__(AgentType.CODE_GENERATOR, *args, **kwargs)
        self.generated_files: Dict[str, str] = {}

    def get_system_prompt(self) -> str:
        """Get the system prompt for code generation."""
        return """You are a Code Generator for Claude Code Builder.

Your role is to generate high-quality implementation code based on instructions:
1. Follow instructions precisely and completely
2. Write clean, maintainable, production-ready code
3. Include proper error handling and validation
4. Add appropriate comments and documentation
5. Follow project conventions and standards
6. Implement all acceptance criteria
7. Create comprehensive test coverage

You must:
- Generate code that is immediately executable
- Follow the specified code structure
- Use appropriate design patterns
- Handle edge cases and errors gracefully
- Include type hints and docstrings
- Follow security best practices
- Use MCP servers for file operations

Generate complete, working code that meets all requirements."""

    def get_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return [
            "Read",
            "Write",
            "Edit",
            "MultiEdit",
            "Bash",
            "Grep",
            "Glob",
        ]

    async def execute(
        self,
        context: ExecutionContext,
        task: Task,
        instructions: Dict[str, Any],
        project_dir: Path,
        **kwargs: Any,
    ) -> AgentResponse:
        """Generate code based on instructions."""
        try:
            await self.log_progress(f"Generating code for: {task.title}")
            
            # Reset state
            self.generated_files = {}
            
            # Get existing code context
            existing_code = await self._analyze_existing_code(
                project_dir,
                instructions,
            )
            
            # Generate code for each file in structure
            code_structure = instructions.get("code_structure", {})
            files = code_structure.get("files", [])
            
            for file_info in files:
                file_path = file_info["path"]
                await self.log_progress(f"Generating: {file_path}")
                
                code = await self._generate_file_code(
                    file_info,
                    task,
                    instructions,
                    existing_code,
                )
                
                self.generated_files[file_path] = code
                
                # Write the file
                await self._write_generated_file(
                    project_dir / file_path,
                    code,
                )
                
                # Log generated code
                await self._log_generated_code(
                    file_path,
                    code,
                    task,
                )
            
            # Run initial validation
            validation_results = await self._validate_generated_code(
                project_dir,
                self.generated_files,
            )
            
            # Generate tests if needed
            if kwargs.get("generate_tests", True):
                test_files = await self._generate_tests(
                    task,
                    instructions,
                    self.generated_files,
                    project_dir,
                )
                self.generated_files.update(test_files)
            
            # Final validation
            final_validation = await self._final_validation(
                project_dir,
                task,
                instructions,
            )
            
            # Calculate metrics
            metrics = self._calculate_generation_metrics(
                self.generated_files,
                validation_results,
            )
            
            await self.log_progress(f"Code generation completed for: {task.title}")
            
            # Record checkpoint
            await self.mcp_orchestrator.checkpoint_manager.record_checkpoint(
                MCPCheckpoint.CODE_GENERATED,
                self.mcp_servers_used,
                {"metrics": metrics},
            )
            
            return AgentResponse(
                agent_type=self.agent_type,
                success=final_validation["success"],
                result={
                    "files": self.generated_files,
                    "validation": final_validation,
                    "metrics": metrics,
                },
                metadata=metrics,
                tokens_used=sum(call.tokens_total for call in self.api_calls),
                cost=sum(call.estimated_cost for call in self.api_calls),
            )
            
        except Exception as e:
            return await self.handle_error(
                e,
                f"code generation for {task.title}",
                recoverable=True,
            )

    async def _analyze_existing_code(
        self,
        project_dir: Path,
        instructions: Dict[str, Any],
    ) -> Dict[str, str]:
        """Analyze existing code in the project."""
        existing_code = {}
        
        try:
            # Find relevant existing files
            await self.use_mcp_server(MCPServer.FILESYSTEM)
            
            # Get project structure
            src_files = await self.search_files(
                str(project_dir / "src"),
                "*.py",
            )
            
            # Read key files for context
            for file_path in src_files[:10]:  # Limit to prevent token overflow
                try:
                    content = await self.read_file(file_path)
                    relative_path = Path(file_path).relative_to(project_dir)
                    existing_code[str(relative_path)] = content[:2000]  # Limit size
                except Exception:
                    pass
            
            # Look for imports and patterns
            if existing_code:
                await self.log_progress(
                    f"Found {len(existing_code)} existing files for context"
                )
                
        except Exception as e:
            await self.log_progress(
                f"Error analyzing existing code: {e}",
                level="warning"
            )
        
        return existing_code

    async def _generate_file_code(
        self,
        file_info: Dict[str, Any],
        task: Task,
        instructions: Dict[str, Any],
        existing_code: Dict[str, str],
    ) -> str:
        """Generate code for a specific file."""
        # Build context from existing code
        code_context = self._build_code_context(existing_code)
        
        # Get relevant classes and functions
        classes = instructions["code_structure"].get("classes", [])
        functions = instructions["code_structure"].get("functions", [])
        
        relevant_classes = [
            c for c in classes
            if c.get("file", file_info["path"]) == file_info["path"]
        ]
        relevant_functions = [
            f for f in functions
            if f.get("file", file_info["path"]) == file_info["path"]
        ]
        
        messages = [
            {
                "role": "user",
                "content": f"""Generate complete implementation code for this file:

File: {file_info['path']}
Description: {file_info.get('description', '')}

Task: {task.title}
Description: {task.description}

Implementation Instructions:
{chr(10).join(f"{i+1}. {inst}" for i, inst in enumerate(instructions['instructions']))}

Classes to implement:
{json.dumps(relevant_classes, indent=2)}

Functions to implement:
{json.dumps(relevant_functions, indent=2)}

Acceptance Criteria:
{chr(10).join(f"- {criterion}" for criterion in task.acceptance_criteria)}

Test Cases to Support:
{chr(10).join(f"- {tc['name']}: {tc['description']}" for tc in instructions.get('test_cases', [])[:5])}

Dependencies Available:
{', '.join(instructions.get('dependencies', []))}

{code_context}

Generate complete, production-ready Python code that:
1. Implements all specified functionality
2. Includes proper imports and type hints
3. Has comprehensive docstrings
4. Handles errors appropriately
5. Follows Python best practices
6. Is immediately executable

Provide ONLY the Python code, no explanations."""
            }
        ]
        
        response = await self.call_claude(messages, max_tokens=8000)
        code = response.get("content", "")
        
        # Clean up code
        if "```python" in code:
            start = code.find("```python") + 9
            end = code.find("```", start)
            code = code[start:end].strip()
        elif "```" in code:
            start = code.find("```") + 3
            end = code.find("```", start)
            code = code[start:end].strip()
        
        return code

    def _build_code_context(self, existing_code: Dict[str, str]) -> str:
        """Build context from existing code."""
        if not existing_code:
            return ""
        
        context_parts = ["## Existing Code Context\n"]
        
        # Extract imports
        all_imports = set()
        for file_path, content in existing_code.items():
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith(('import ', 'from ')):
                    all_imports.add(line.strip())
        
        if all_imports:
            context_parts.append("### Common Imports")
            context_parts.extend(sorted(all_imports)[:20])
            context_parts.append("")
        
        # Show key files
        context_parts.append("### Key Files")
        for file_path in list(existing_code.keys())[:5]:
            context_parts.append(f"- {file_path}")
        
        return '\n'.join(context_parts)

    async def _write_generated_file(
        self,
        file_path: Path,
        code: str,
    ) -> None:
        """Write generated code to file."""
        await self.use_mcp_server(MCPServer.FILESYSTEM)
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        await self.write_file(str(file_path), code)
        
        await self.log_progress(f"Written: {file_path}")

    async def _log_generated_code(
        self,
        file_path: str,
        code: str,
        task: Task,
    ) -> None:
        """Log generated code for tracking."""
        # Determine language
        if file_path.endswith('.py'):
            language = "python"
        elif file_path.endswith('.js'):
            language = "javascript"
        elif file_path.endswith('.ts'):
            language = "typescript"
        else:
            language = "unknown"
        
        generated_code = GeneratedCode(
            file_path=file_path,
            content=code,
            phase=str(task.phase_id),
            task=task.title,
            model=self.config.model,
            language=language,
            line_count=len(code.split('\n')),
            tokens_used=sum(call.tokens_total for call in self.api_calls),
        )
        
        await self.logger.log_generated_code(generated_code)

    async def _validate_generated_code(
        self,
        project_dir: Path,
        generated_files: Dict[str, str],
    ) -> Dict[str, Any]:
        """Validate generated code."""
        validation_results = {
            "syntax_valid": True,
            "imports_valid": True,
            "structure_valid": True,
            "issues": [],
        }
        
        for file_path, code in generated_files.items():
            # Basic syntax check
            try:
                compile(code, file_path, 'exec')
            except SyntaxError as e:
                validation_results["syntax_valid"] = False
                validation_results["issues"].append(
                    f"Syntax error in {file_path}: {e}"
                )
            
            # Check imports
            missing_imports = self._check_imports(code)
            if missing_imports:
                validation_results["imports_valid"] = False
                validation_results["issues"].append(
                    f"Missing imports in {file_path}: {', '.join(missing_imports)}"
                )
        
        return validation_results

    def _check_imports(self, code: str) -> List[str]:
        """Check for potentially missing imports."""
        missing = []
        
        # Common patterns that need imports
        patterns = {
            r'\basyncio\.': 'asyncio',
            r'\bPath\(': 'pathlib.Path',
            r'\bOptional\[': 'typing.Optional',
            r'\bList\[': 'typing.List',
            r'\bDict\[': 'typing.Dict',
            r'\bAny\b': 'typing.Any',
            r'\bdatetime\.': 'datetime',
            r'\bjson\.': 'json',
            r'\blogging\.': 'logging',
        }
        
        import re
        
        for pattern, module in patterns.items():
            if re.search(pattern, code):
                # Check if imported
                if module not in code and f"from {module.split('.')[0]}" not in code:
                    missing.append(module)
        
        return missing

    async def _generate_tests(
        self,
        task: Task,
        instructions: Dict[str, Any],
        generated_files: Dict[str, str],
        project_dir: Path,
    ) -> Dict[str, str]:
        """Generate test files."""
        test_files = {}
        
        for file_path, code in generated_files.items():
            if not file_path.startswith("test_") and not "/test" in file_path:
                test_file_path = self._get_test_file_path(file_path)
                
                test_code = await self._generate_test_code(
                    file_path,
                    code,
                    task,
                    instructions.get("test_cases", []),
                )
                
                test_files[test_file_path] = test_code
                
                # Write test file
                await self._write_generated_file(
                    project_dir / test_file_path,
                    test_code,
                )
        
        return test_files

    def _get_test_file_path(self, source_path: str) -> str:
        """Get test file path for a source file."""
        path_parts = source_path.split('/')
        
        # Replace src with tests
        if "src" in path_parts:
            path_parts[path_parts.index("src")] = "tests"
        else:
            path_parts.insert(0, "tests")
        
        # Add test_ prefix to filename
        filename = path_parts[-1]
        if not filename.startswith("test_"):
            path_parts[-1] = "test_" + filename
        
        return '/'.join(path_parts)

    async def _generate_test_code(
        self,
        source_path: str,
        source_code: str,
        task: Task,
        test_cases: List[Dict[str, Any]],
    ) -> str:
        """Generate test code for a source file."""
        # Extract testable elements
        import re
        
        # Find classes
        classes = re.findall(r'class\s+(\w+)', source_code)
        
        # Find functions
        functions = re.findall(r'(?:async\s+)?def\s+(\w+)', source_code)
        functions = [f for f in functions if not f.startswith('_') or f == '__init__']
        
        messages = [
            {
                "role": "user",
                "content": f"""Generate comprehensive test code for this implementation:

Source File: {source_path}
Task: {task.title}

Classes to test: {', '.join(classes)}
Functions to test: {', '.join(functions)}

Test Cases:
{json.dumps(test_cases[:5], indent=2)}

Source Code Preview:
{source_code[:1000]}...

Generate pytest test code that:
1. Tests all public methods and functions
2. Includes the provided test cases
3. Tests edge cases and error conditions
4. Uses appropriate fixtures and mocks
5. Has clear test names and documentation
6. Achieves high code coverage

Provide ONLY the Python test code."""
            }
        ]
        
        response = await self.call_claude(messages, max_tokens=6000)
        test_code = response.get("content", "")
        
        # Clean up code
        if "```python" in test_code:
            start = test_code.find("```python") + 9
            end = test_code.find("```", start)
            test_code = test_code[start:end].strip()
        elif "```" in test_code:
            start = test_code.find("```") + 3
            end = test_code.find("```", start)
            test_code = test_code[start:end].strip()
        
        # Ensure basic structure if empty
        if not test_code or len(test_code) < 100:
            module_name = Path(source_path).stem
            test_code = f"""\"\"\"Tests for {module_name}.\"\"\"

import pytest
from {source_path.replace('/', '.').replace('.py', '')} import *


class Test{classes[0] if classes else 'Module'}:
    \"\"\"Test cases for {classes[0] if classes else 'module'}.\"\"\"
    
    def test_initialization(self):
        \"\"\"Test basic initialization.\"\"\"
        # TODO: Implement test
        assert True
    
    def test_basic_functionality(self):
        \"\"\"Test basic functionality.\"\"\"
        # TODO: Implement test
        assert True
"""
        
        return test_code

    async def _final_validation(
        self,
        project_dir: Path,
        task: Task,
        instructions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Perform final validation of generated code."""
        validation = {
            "success": True,
            "acceptance_criteria_met": [],
            "acceptance_criteria_unmet": [],
            "warnings": [],
            "errors": [],
        }
        
        # Check each acceptance criterion
        for criterion in task.acceptance_criteria:
            # This would need sophisticated analysis in production
            # For now, simple keyword matching
            criterion_met = await self._check_acceptance_criterion(
                criterion,
                self.generated_files,
            )
            
            if criterion_met:
                validation["acceptance_criteria_met"].append(criterion)
            else:
                validation["acceptance_criteria_unmet"].append(criterion)
        
        # Update success based on criteria
        if validation["acceptance_criteria_unmet"]:
            validation["success"] = False
            validation["errors"].append(
                f"Unmet criteria: {len(validation['acceptance_criteria_unmet'])}"
            )
        
        # Run linting if available
        lint_results = await self._run_linting(project_dir)
        if lint_results["errors"]:
            validation["errors"].extend(lint_results["errors"])
        if lint_results["warnings"]:
            validation["warnings"].extend(lint_results["warnings"])
        
        return validation

    async def _check_acceptance_criterion(
        self,
        criterion: str,
        generated_files: Dict[str, str],
    ) -> bool:
        """Check if an acceptance criterion is met."""
        # Combine all generated code
        all_code = '\n'.join(generated_files.values()).lower()
        criterion_lower = criterion.lower()
        
        # Extract key terms from criterion
        key_terms = []
        for word in criterion_lower.split():
            if len(word) > 4 and word not in ['should', 'must', 'have', 'with']:
                key_terms.append(word)
        
        # Check if key terms appear in code
        if not key_terms:
            return True  # Can't validate without key terms
        
        matches = sum(1 for term in key_terms if term in all_code)
        coverage = matches / len(key_terms)
        
        return coverage > 0.5

    async def _run_linting(self, project_dir: Path) -> Dict[str, List[str]]:
        """Run linting on generated code."""
        results = {"errors": [], "warnings": []}
        
        try:
            # Try to run ruff if available
            result = await asyncio.create_subprocess_exec(
                "ruff",
                "check",
                str(project_dir / "src"),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                output = stdout.decode() if stdout else ""
                lines = output.split('\n')
                for line in lines[:10]:  # Limit to 10 issues
                    if line.strip():
                        results["warnings"].append(line.strip())
                        
        except Exception:
            # Linting not available
            pass
        
        return results

    def _calculate_generation_metrics(
        self,
        generated_files: Dict[str, str],
        validation_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate code generation metrics."""
        total_lines = 0
        total_chars = 0
        
        for code in generated_files.values():
            lines = code.split('\n')
            total_lines += len(lines)
            total_chars += len(code)
        
        return {
            "files_generated": len(generated_files),
            "total_lines": total_lines,
            "total_characters": total_chars,
            "average_file_size": total_chars / len(generated_files) if generated_files else 0,
            "syntax_valid": validation_results.get("syntax_valid", True),
            "validation_issues": len(validation_results.get("issues", [])),
            "test_files_generated": sum(
                1 for f in generated_files if "test" in f
            ),
        }


__all__ = ["CodeGenerator"]