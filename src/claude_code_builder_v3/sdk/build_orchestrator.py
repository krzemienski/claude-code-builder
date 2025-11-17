"""
Build Orchestrator - Main entry point for v3 builds.

Coordinates:
1. Skill gap analysis
2. Skill generation (if needed)
3. Skill validation
4. Build execution via SDK
5. Feedback collection and skill refinement
"""

import asyncio
import structlog
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID, uuid4

from claude_code_builder_v3.core.models import (
    SkillGap,
    GeneratedSkill,
    BuildResult,
)
from claude_code_builder_v3.core.exceptions import BuildError
from claude_code_builder_v3.skills.manager import SkillManager
from claude_code_builder_v3.agents.skill_generator import SkillGenerator
from claude_code_builder_v3.agents.skill_validator import SkillValidator
from claude_code_builder_v3.sdk.skills_orchestrator import SDKSkillsOrchestrator

logger = structlog.get_logger(__name__)


class BuildOrchestrator:
    """
    Main orchestrator for v3 builds with dynamic skill generation.

    This is the entry point for all v3 builds, coordinating:
    - Skill discovery and gap analysis
    - Dynamic skill generation (Feature 6)
    - Skill validation
    - SDK-based build execution
    - Skill usage tracking and refinement
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        skills_paths: Optional[List[Path]] = None,
    ) -> None:
        """
        Initialize build orchestrator.

        Args:
            api_key: Anthropic API key.
            model: Claude model to use.
            skills_paths: Optional custom skills paths.
        """
        self.api_key = api_key
        self.model = model

        # Initialize components
        self.skill_manager = SkillManager(skills_paths=skills_paths)
        self.skill_generator = SkillGenerator(api_key=api_key, model=model)
        self.skill_validator = SkillValidator()
        self.sdk_orchestrator = SDKSkillsOrchestrator(api_key=api_key, model=model)

        logger.info("build_orchestrator_initialized", model=model)

    async def initialize(self) -> None:
        """
        Initialize orchestrator by discovering skills.

        Should be called once before first build.
        """
        logger.info("initializing_build_orchestrator")
        await self.skill_manager.initialize()
        logger.info(
            "build_orchestrator_ready",
            skills_count=len(self.skill_manager.registry),
        )

    async def execute_build(
        self,
        spec_path: Path,
        output_dir: Path,
        generate_missing_skills: bool = True,
    ) -> BuildResult:
        """
        Execute complete build with skill generation.

        This is the main entry point that:
        1. Analyzes spec for skill gaps
        2. Generates missing skills (if enabled)
        3. Validates generated skills
        4. Executes build via SDK
        5. Collects feedback for refinement

        Args:
            spec_path: Path to specification file.
            output_dir: Output directory for generated code.
            generate_missing_skills: Whether to generate missing skills.

        Returns:
            BuildResult with all build information.
        """
        build_id = uuid4()
        logger.info(
            "starting_build",
            build_id=str(build_id),
            spec=str(spec_path),
            output_dir=str(output_dir),
        )

        start_time = datetime.now()

        try:
            # Phase 1: Load and analyze spec
            logger.info("phase_1_spec_analysis")
            spec = await asyncio.to_thread(spec_path.read_text)

            # Find relevant existing skills
            relevant_skills = await self.skill_manager.find_skills_for_spec(spec)
            logger.info(
                "relevant_skills_found",
                count=len(relevant_skills),
                skills=[s.name for s in relevant_skills],
            )

            # Phase 2: Identify skill gaps
            logger.info("phase_2_skill_gap_analysis")
            skill_gaps = await self.skill_generator.analyze_skill_gaps(
                spec, relevant_skills
            )

            if skill_gaps:
                logger.info(
                    "skill_gaps_identified",
                    count=len(skill_gaps),
                    gaps=[g.name for g in skill_gaps],
                )
            else:
                logger.info("no_skill_gaps_found")

            # Phase 3: Generate missing skills
            generated_skills: List[GeneratedSkill] = []

            if generate_missing_skills and skill_gaps:
                logger.info("phase_3_skill_generation", count=len(skill_gaps))

                for gap in skill_gaps:
                    try:
                        logger.info("generating_skill", skill=gap.name)

                        # Generate skill
                        skill = await self.skill_generator.generate_skill(gap)

                        # Validate skill
                        logger.info("validating_skill", skill=gap.name)
                        validation = await self.skill_validator.validate_skill(skill)

                        if not validation.valid:
                            logger.error(
                                "skill_validation_failed",
                                skill=gap.name,
                                errors=validation.errors,
                            )
                            continue

                        logger.info("skill_generated_and_validated", skill=gap.name)

                        # Save to filesystem
                        await self.skill_generator.save_generated_skill(skill)

                        generated_skills.append(skill)

                        # Register with skill manager
                        await self.skill_manager.registry.register_skill(skill.metadata)

                    except Exception as e:
                        logger.error(
                            "skill_generation_failed", skill=gap.name, error=str(e)
                        )
                        # Continue with other skills

                logger.info(
                    "skill_generation_completed",
                    generated_count=len(generated_skills),
                )

            # Phase 4: Execute build via SDK
            logger.info("phase_4_build_execution")

            required_skill_names = [s.name for s in relevant_skills]

            result = await self.sdk_orchestrator.build_with_skills(
                spec=spec,
                required_skills=required_skill_names,
                generated_skills=generated_skills,
                output_dir=output_dir,
            )

            # Phase 5: Record skill usage
            if result.success:
                logger.info("phase_5_recording_skill_usage")
                for skill_name in result.skills_used:
                    await self.skill_manager.record_skill_usage(
                        skill_name=skill_name,
                        successful=True,
                        duration_ms=result.total_duration_ms,
                    )

                for skill_name in result.generated_skills:
                    await self.skill_manager.record_skill_usage(
                        skill_name=skill_name,
                        successful=True,
                        duration_ms=0.0,
                    )

            duration = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(
                "build_completed",
                build_id=str(build_id),
                success=result.success,
                duration_ms=duration,
                files_generated=len(result.generated_files),
                skills_used=len(result.skills_used),
                skills_generated=len(result.generated_skills),
            )

            return result

        except Exception as e:
            logger.error("build_failed", build_id=str(build_id), error=str(e))
            raise BuildError(str(e), build_id=str(build_id)) from e

    async def build_from_spec_string(
        self,
        spec: str,
        output_dir: Path,
        generate_missing_skills: bool = True,
    ) -> BuildResult:
        """
        Execute build from specification string.

        Args:
            spec: Specification as string.
            output_dir: Output directory.
            generate_missing_skills: Whether to generate missing skills.

        Returns:
            BuildResult.
        """
        # Create temporary spec file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(spec)
            temp_spec_path = Path(f.name)

        try:
            result = await self.execute_build(
                spec_path=temp_spec_path,
                output_dir=output_dir,
                generate_missing_skills=generate_missing_skills,
            )
            return result
        finally:
            # Cleanup
            temp_spec_path.unlink(missing_ok=True)

    def get_build_stats(self) -> dict:
        """
        Get overall build statistics.

        Returns:
            Dictionary with stats.
        """
        return self.skill_manager.get_manager_stats()
