"""
TRUE Claude Agent SDK Integration.

This module provides real integration with the Claude Agent SDK,
using the SDK's query() method with proper skills configuration.
"""

import asyncio
import os
import structlog
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional

from anthropic import AsyncAnthropic
from claude_agent_sdk import query

from claude_code_builder_v3.core.models import GeneratedSkill, BuildResult
from claude_code_builder_v3.mcp.client import MCPClient

logger = structlog.get_logger(__name__)


class SDKIntegration:
    """
    Real Claude Agent SDK integration using query() with skills.

    This replaces the simplified API approach with true SDK integration:
    - Uses SDK's query() method
    - Skills discovered automatically from filesystem
    - Progressive disclosure handled by SDK
    - MCP servers integrated
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
    ) -> None:
        """
        Initialize SDK integration.

        Args:
            api_key: Anthropic API key.
            model: Claude model to use.
        """
        self.api_key = api_key
        self.model = model

        # Set up skills paths for SDK
        self.skills_base_path = Path.home() / ".claude" / "skills"
        self.generated_skills_path = self.skills_base_path / "generated"

        # Ensure directories exist
        self.generated_skills_path.mkdir(parents=True, exist_ok=True)

        # Configure environment for SDK
        os.environ["CLAUDE_SKILLS_PATH"] = str(self.skills_base_path)
        os.environ["ANTHROPIC_API_KEY"] = api_key

        # Initialize MCP client
        self.mcp_client = MCPClient()

        logger.info(
            "sdk_integration_initialized",
            model=model,
            skills_path=str(self.skills_base_path),
        )

    async def initialize(self) -> None:
        """Initialize SDK and MCP connections."""
        await self.mcp_client.initialize()
        logger.info("sdk_integration_ready")

    async def execute_build_with_sdk(
        self,
        spec: str,
        required_skills: List[str],
        generated_skills: Optional[List[GeneratedSkill]] = None,
        output_dir: Optional[Path] = None,
    ) -> BuildResult:
        """
        Execute build using TRUE Claude Agent SDK with skills.

        This uses the SDK's query() method which:
        1. Automatically discovers skills from filesystem
        2. Loads skill metadata into context (~100 tokens each)
        3. Triggers skills based on conversation
        4. Loads full instructions when needed (~3-5K tokens)
        5. Accesses resources on-demand (0 tokens)

        Args:
            spec: Project specification.
            required_skills: List of required skill names.
            generated_skills: Optional freshly generated skills.
            output_dir: Output directory for generated code.

        Returns:
            BuildResult with all generated files and metrics.
        """
        build_result = BuildResult(success=False)
        start_time = datetime.now()

        try:
            logger.info(
                "starting_sdk_build",
                required_skills_count=len(required_skills),
                generated_skills_count=len(generated_skills) if generated_skills else 0,
            )

            # Step 1: Save generated skills to filesystem for SDK discovery
            if generated_skills:
                for skill in generated_skills:
                    await self._save_skill_to_filesystem(skill)
                    build_result.generated_skills.append(skill.name)

            # Step 2: Construct build messages
            # SDK will automatically discover skills from CLAUDE_SKILLS_PATH
            messages = [
                {
                    "role": "user",
                    "content": f"""Build a complete production-ready project from this specification:

{spec}

Requirements:
1. Generate complete project structure
2. Include all necessary code files
3. Add comprehensive tests
4. Include deployment configuration
5. Add documentation (README, API docs)

You have access to Claude Skills that will help guide the implementation.
The skills are already loaded and will be triggered automatically based on the technologies mentioned in the spec.

For each file you generate, output it in this format:
```filename: path/to/file.ext
[file content here]
```

Be systematic and complete. Follow best practices from the relevant skills.
""",
                }
            ]

            logger.info("executing_build_via_sdk", model=self.model)

            # Step 3: Execute via SDK's query() method
            # This is the TRUE SDK integration
            collected_response = []
            total_input_tokens = 0
            total_output_tokens = 0

            async for chunk in query(
                messages=messages,
                api_key=self.api_key,
                model=self.model,
            ):
                if hasattr(chunk, "type"):
                    if chunk.type == "text" and hasattr(chunk, "content"):
                        collected_response.append(chunk.content)
                    elif chunk.type == "usage":
                        # Track token usage
                        if hasattr(chunk, "input_tokens"):
                            total_input_tokens = chunk.input_tokens
                        if hasattr(chunk, "output_tokens"):
                            total_output_tokens = chunk.output_tokens

            # Combine response
            content = "".join(collected_response)

            # Step 4: Parse generated files from response
            generated_files = self._parse_generated_files(content)
            build_result.generated_files = generated_files

            # Step 5: Save files to output directory
            if output_dir and generated_files:
                await self._save_generated_files(generated_files, output_dir)

            # Step 6: Calculate metrics
            build_result.total_tokens_used = total_input_tokens + total_output_tokens
            build_result.total_cost_usd = self._calculate_cost(
                total_input_tokens, total_output_tokens
            )
            build_result.success = len(generated_files) > 0
            build_result.skills_used = required_skills

            build_result.completed_at = datetime.now()
            build_result.total_duration_ms = (
                build_result.completed_at - start_time
            ).total_seconds() * 1000

            logger.info(
                "sdk_build_completed",
                success=build_result.success,
                files_generated=len(generated_files),
                tokens_used=build_result.total_tokens_used,
                cost_usd=build_result.total_cost_usd,
                duration_ms=build_result.total_duration_ms,
            )

            return build_result

        except Exception as e:
            logger.error("sdk_build_failed", error=str(e))
            build_result.success = False
            build_result.errors.append(str(e))
            build_result.completed_at = datetime.now()
            build_result.total_duration_ms = (
                build_result.completed_at - start_time
            ).total_seconds() * 1000
            return build_result

    async def _save_skill_to_filesystem(self, skill: GeneratedSkill) -> None:
        """
        Save generated skill to filesystem for SDK to discover.

        The SDK will automatically find and load skills from:
        ~/.claude/skills/generated/{skill-name}/SKILL.md

        Args:
            skill: Generated skill to save.
        """
        skill_dir = self.generated_skills_path / skill.name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Write SKILL.md (required by SDK)
        skill_md_path = skill_dir / "SKILL.md"
        await self.mcp_client.write_file_safe(skill_md_path, skill.skill_md)

        # Write examples (optional resources)
        if skill.examples:
            examples_dir = skill_dir / "examples"
            examples_dir.mkdir(exist_ok=True)
            for filename, content in skill.examples.items():
                example_path = examples_dir / filename
                await self.mcp_client.write_file_safe(example_path, content)

        # Write tests (optional resources)
        if skill.tests:
            tests_dir = skill_dir / "tests"
            tests_dir.mkdir(exist_ok=True)
            for filename, content in skill.tests.items():
                test_path = tests_dir / filename
                await self.mcp_client.write_file_safe(test_path, content)

        logger.info(
            "skill_saved_for_sdk",
            skill=skill.name,
            path=str(skill_dir),
        )

    def _parse_generated_files(self, content: str) -> Dict[str, str]:
        """
        Parse generated files from SDK response.

        Looks for patterns like:
        ```filename: path/to/file.py
        [content]
        ```

        Args:
            content: Response content from SDK.

        Returns:
            Dictionary of filepath -> content.
        """
        import re

        files: Dict[str, str] = {}

        # Pattern: ```filename: path/to/file.ext
        pattern = r"```filename:\s*([^\n]+)\n(.*?)```"
        matches = re.findall(pattern, content, re.DOTALL)

        for filepath, file_content in matches:
            filepath = filepath.strip()
            file_content = file_content.strip()
            files[filepath] = file_content

        # Alternative pattern: # File: path/to/file.py
        alt_pattern = r"#\s*File:\s*([^\n]+)\n```(?:\w+)?\n(.*?)```"
        alt_matches = re.findall(alt_pattern, content, re.DOTALL)

        for filepath, file_content in alt_matches:
            filepath = filepath.strip()
            file_content = file_content.strip()
            if filepath not in files:
                files[filepath] = file_content

        logger.info("files_parsed_from_sdk_response", count=len(files))
        return files

    async def _save_generated_files(
        self, files: Dict[str, str], output_dir: Path
    ) -> None:
        """
        Save generated files to output directory using MCP.

        Args:
            files: Dictionary of filepath -> content.
            output_dir: Output directory.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for filepath, content in files.items():
            full_path = output_dir / filepath
            await self.mcp_client.write_file_safe(full_path, content)

        logger.info("files_saved_via_mcp", output_dir=str(output_dir), count=len(files))

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate API cost based on token usage.

        Claude Sonnet 4.5 pricing:
        - Input: $3 per 1M tokens
        - Output: $15 per 1M tokens

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Cost in USD.
        """
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        return input_cost + output_cost

    async def close(self) -> None:
        """Close SDK and MCP connections."""
        await self.mcp_client.close()
        logger.info("sdk_integration_closed")
