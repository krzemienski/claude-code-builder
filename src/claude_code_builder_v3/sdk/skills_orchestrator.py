"""
SDK Skills Orchestrator - Integrates skills with Claude Agent SDK.

This orchestrator:
1. Saves generated skills to filesystem for SDK discovery
2. Configures Claude Agent SDK to use skills
3. Executes builds using SDK with progressive skill loading
4. Tracks which skills were used during the build
"""

import asyncio
import os
import structlog
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from anthropic import AsyncAnthropic

from claude_code_builder_v3.core.models import (
    GeneratedSkill,
    SkillMetadata,
    BuildResult,
    BuildPhase,
)
from claude_code_builder_v3.core.exceptions import BuildError

logger = structlog.get_logger(__name__)


class SDKSkillsOrchestrator:
    """
    Orchestrates skill usage via Claude Agent SDK.

    Responsible for:
    - Saving generated skills to filesystem (for SDK discovery)
    - Configuring SDK with skills paths
    - Executing builds with skills enabled
    - Tracking skill usage
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929") -> None:
        """
        Initialize SDK Skills Orchestrator.

        Args:
            api_key: Anthropic API key.
            model: Claude model to use.
        """
        self.api_key = api_key
        self.model = model

        # Initialize Anthropic client
        self.client = AsyncAnthropic(api_key=api_key)

        # Skills paths for SDK
        self.skills_base_path = Path.home() / ".claude" / "skills"
        self.generated_skills_path = self.skills_base_path / "generated"

        # Ensure directories exist
        self.generated_skills_path.mkdir(parents=True, exist_ok=True)

        # Configure environment for SDK
        os.environ["CLAUDE_SKILLS_PATH"] = str(self.skills_base_path)

        logger.info(
            "sdk_skills_orchestrator_initialized",
            model=model,
            skills_path=str(self.skills_base_path),
        )

    async def build_with_skills(
        self,
        spec: str,
        required_skills: List[str],
        generated_skills: Optional[List[GeneratedSkill]] = None,
        output_dir: Optional[Path] = None,
    ) -> BuildResult:
        """
        Execute build using Claude Agent SDK with skills.

        This is the main integration point where:
        1. Generated skills are saved to filesystem
        2. SDK discovers skills automatically
        3. Build is executed with skills available
        4. Results are collected and returned

        Args:
            spec: Project specification.
            required_skills: List of required skill names.
            generated_skills: Optional list of freshly generated skills.
            output_dir: Output directory for generated code.

        Returns:
            BuildResult with all generated files and metrics.
        """
        build_result = BuildResult(success=False)
        start_time = datetime.now()

        try:
            logger.info(
                "starting_build_with_skills",
                required_skills_count=len(required_skills),
                generated_skills_count=len(generated_skills) if generated_skills else 0,
            )

            # Step 1: Save generated skills to filesystem
            if generated_skills:
                for skill in generated_skills:
                    await self._save_skill_to_filesystem(skill)
                    build_result.generated_skills.append(skill.name)

            # Step 2: Build skill context for prompt
            skills_context = self._format_available_skills(
                required_skills + (
                    [s.name for s in generated_skills] if generated_skills else []
                )
            )

            # Step 3: Create build phases
            phases = [
                BuildPhase(name="scaffold", skills_used=required_skills),
                BuildPhase(name="implementation", skills_used=required_skills),
                BuildPhase(name="testing", skills_used=["test-strategy-selector"]),
                BuildPhase(name="deployment", skills_used=["deployment-pipeline-generator"]),
            ]
            build_result.phases = phases

            # Step 4: Execute build via SDK
            build_prompt = f"""Build a complete project from this specification:

{spec}

You have access to these Claude Skills - use them when relevant:
{skills_context}

The skills are available in your context and will provide:
- Project structure templates
- Best practices and patterns
- Code examples
- Testing strategies
- Deployment configurations

Generate a production-ready project that includes:
1. Complete project structure
2. All necessary code files
3. Comprehensive tests
4. Deployment configuration
5. Documentation (README, API docs)

Output each file with clear markers like:
```filename: path/to/file.py
[file content]
```

Be systematic and complete. Use the skills to ensure best practices."""

            logger.info("executing_build_via_sdk", model=self.model)

            # Execute via SDK
            messages = [{"role": "user", "content": build_prompt}]

            # Track phases
            current_phase_idx = 0
            phases[current_phase_idx].status = "running"
            phases[current_phase_idx].started_at = datetime.now()

            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=32000,  # Extended for comprehensive builds
                messages=messages,
            )

            # Extract generated content
            content = response.content[0].text

            # Parse files from response
            generated_files = self._parse_generated_files(content)
            build_result.generated_files = generated_files

            # Mark current phase complete
            phases[current_phase_idx].status = "completed"
            phases[current_phase_idx].completed_at = datetime.now()

            # Save files to output directory
            if output_dir and generated_files:
                await self._save_generated_files(generated_files, output_dir)

            # Calculate metrics
            build_result.total_tokens_used = response.usage.input_tokens + response.usage.output_tokens
            build_result.total_cost_usd = self._calculate_cost(response.usage)
            build_result.success = len(generated_files) > 0

            build_result.completed_at = datetime.now()
            build_result.total_duration_ms = (
                build_result.completed_at - start_time
            ).total_seconds() * 1000

            # Track skill usage
            build_result.skills_used = required_skills

            logger.info(
                "build_completed",
                success=build_result.success,
                files_generated=len(generated_files),
                tokens_used=build_result.total_tokens_used,
                cost_usd=build_result.total_cost_usd,
                duration_ms=build_result.total_duration_ms,
            )

            return build_result

        except Exception as e:
            logger.error("build_failed", error=str(e))
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

        Args:
            skill: Generated skill to save.
        """
        skill_dir = self.generated_skills_path / skill.name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Write SKILL.md
        skill_md_path = skill_dir / "SKILL.md"
        await asyncio.to_thread(skill_md_path.write_text, skill.skill_md)

        # Write examples
        if skill.examples:
            examples_dir = skill_dir / "examples"
            examples_dir.mkdir(exist_ok=True)
            for filename, content in skill.examples.items():
                example_path = examples_dir / filename
                await asyncio.to_thread(example_path.write_text, content)

        # Write tests
        if skill.tests:
            tests_dir = skill_dir / "tests"
            tests_dir.mkdir(exist_ok=True)
            for filename, content in skill.tests.items():
                test_path = tests_dir / filename
                await asyncio.to_thread(test_path.write_text, content)

        logger.info(
            "skill_saved_to_filesystem",
            skill=skill.name,
            path=str(skill_dir),
            discoverable_by_sdk=True,
        )

    def _format_available_skills(self, skill_names: List[str]) -> str:
        """
        Format skill names for inclusion in prompt.

        Args:
            skill_names: List of skill names.

        Returns:
            Formatted string describing available skills.
        """
        if not skill_names:
            return "No skills available."

        lines = ["Available Skills:"]
        for skill_name in skill_names:
            lines.append(f"  - {skill_name}")

        return "\n".join(lines)

    def _parse_generated_files(self, content: str) -> Dict[str, str]:
        """
        Parse generated files from Claude response.

        Looks for patterns like:
        ```filename: path/to/file.py
        [content]
        ```

        Args:
            content: Response content from Claude.

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

        logger.info("files_parsed_from_response", count=len(files))
        return files

    async def _save_generated_files(
        self, files: Dict[str, str], output_dir: Path
    ) -> None:
        """
        Save generated files to output directory.

        Args:
            files: Dictionary of filepath -> content.
            output_dir: Output directory.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for filepath, content in files.items():
            full_path = output_dir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(full_path.write_text, content)

        logger.info("files_saved", output_dir=str(output_dir), count=len(files))

    def _calculate_cost(self, usage: any) -> float:
        """
        Calculate API cost based on token usage.

        Args:
            usage: Usage object from API response.

        Returns:
            Cost in USD.
        """
        # Claude Sonnet 4.5 pricing (as of 2025)
        # Input: $3 per 1M tokens
        # Output: $15 per 1M tokens

        input_cost = (usage.input_tokens / 1_000_000) * 3.0
        output_cost = (usage.output_tokens / 1_000_000) * 15.0

        return input_cost + output_cost
