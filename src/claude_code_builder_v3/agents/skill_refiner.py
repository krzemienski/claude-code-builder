"""
Skill Refiner - Self-improving skill system.

Refines skills based on usage feedback, build results, and
user modifications. This creates the learning loop that makes
v3 self-improving.
"""

import asyncio
import structlog
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from anthropic import AsyncAnthropic

from claude_code_builder_v3.core.models import (
    GeneratedSkill,
    SkillUsageFeedback,
    SkillMetadata,
)
from claude_code_builder_v3.core.exceptions import SkillGenerationError
from claude_code_builder_v3.agents.skill_validator import SkillValidator

logger = structlog.get_logger(__name__)


class SkillRefiner:
    """
    Refines skills based on real-world usage feedback.

    Implements the learning loop:
    1. Collect feedback from builds
    2. Analyze what went wrong/right
    3. Generate improved skill version
    4. Validate improved skill
    5. Replace if better
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
    ) -> None:
        """
        Initialize skill refiner.

        Args:
            api_key: Anthropic API key.
            model: Claude model to use.
        """
        self.api_key = api_key
        self.model = model
        self.client = AsyncAnthropic(api_key=api_key)
        self.validator = SkillValidator()

        logger.info("skill_refiner_initialized", model=model)

    async def refine_skill(
        self,
        skill: GeneratedSkill,
        feedback: SkillUsageFeedback,
    ) -> Optional[GeneratedSkill]:
        """
        Refine skill based on usage feedback.

        Args:
            skill: Current skill to refine.
            feedback: Feedback from using the skill.

        Returns:
            Refined skill if improvements found, None otherwise.
        """
        logger.info(
            "refining_skill",
            skill=skill.name,
            successful=feedback.successful,
        )

        start_time = datetime.now()

        try:
            # Step 1: Analyze feedback
            issues = await self._analyze_feedback(feedback)

            if not issues:
                logger.info("no_issues_found", skill=skill.name)
                return None

            logger.info("issues_identified", skill=skill.name, issues=len(issues))

            # Step 2: Generate refinements
            refinements = await self._generate_refinements(skill, issues)

            # Step 3: Apply refinements to create new version
            refined_skill = await self._apply_refinements(skill, refinements)

            # Step 4: Validate refined skill
            validation = await self.validator.validate_skill(refined_skill)

            if not validation.valid:
                logger.warning(
                    "refined_skill_invalid",
                    skill=skill.name,
                    errors=validation.errors,
                )
                return None

            # Step 5: Compare with original
            if await self._is_better(skill, refined_skill, feedback):
                logger.info("skill_refined_successfully", skill=skill.name)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                logger.info("refinement_duration_ms", duration=duration)
                return refined_skill
            else:
                logger.info("refined_skill_not_better", skill=skill.name)
                return None

        except Exception as e:
            logger.error("skill_refinement_failed", skill=skill.name, error=str(e))
            return None

    async def _analyze_feedback(
        self, feedback: SkillUsageFeedback
    ) -> List[Dict[str, str]]:
        """
        Analyze feedback to identify issues.

        Args:
            feedback: Usage feedback.

        Returns:
            List of identified issues.
        """
        issues = []

        # Check for build failures
        if not feedback.successful:
            issues.append({
                "type": "build_failure",
                "description": feedback.feedback_text or "Build failed",
            })

        # Check for linting errors
        if feedback.linting_errors:
            issues.append({
                "type": "linting_errors",
                "description": f"{len(feedback.linting_errors)} linting errors",
                "details": feedback.linting_errors[:5],  # First 5
            })

        # Check for test failures
        if feedback.test_failures:
            issues.append({
                "type": "test_failures",
                "description": f"{len(feedback.test_failures)} test failures",
                "details": feedback.test_failures[:5],  # First 5
            })

        # Check for user modifications (indicates skill could be better)
        if feedback.user_modifications:
            common_mods = self._extract_common_modifications(
                feedback.user_modifications
            )
            if common_mods:
                issues.append({
                    "type": "user_modifications",
                    "description": "Users frequently modify generated code",
                    "details": common_mods,
                })

        logger.info("feedback_analyzed", issues=len(issues))
        return issues

    def _extract_common_modifications(
        self, modifications: Dict[str, any]
    ) -> List[str]:
        """
        Extract common modification patterns.

        Args:
            modifications: User modifications data.

        Returns:
            List of common modification patterns.
        """
        # In real implementation, would analyze patterns
        # For now, return sample patterns
        patterns = []

        if "added_files" in modifications:
            patterns.append(f"Users often add: {modifications['added_files']}")

        if "changed_patterns" in modifications:
            patterns.append(f"Common changes: {modifications['changed_patterns']}")

        return patterns

    async def _generate_refinements(
        self,
        skill: GeneratedSkill,
        issues: List[Dict[str, str]],
    ) -> Dict[str, str]:
        """
        Generate refinements to address issues.

        Args:
            skill: Current skill.
            issues: Identified issues.

        Returns:
            Dictionary of refinements.
        """
        logger.info("generating_refinements", skill=skill.name, issues=len(issues))

        # Format issues for prompt
        issues_text = "\n".join(
            f"- {issue['type']}: {issue['description']}"
            for issue in issues
        )

        prompt = f"""Analyze this skill and the issues encountered, then suggest improvements.

CURRENT SKILL: {skill.name}
DESCRIPTION: {skill.metadata.description}

SKILL.MD CONTENT (first 1000 chars):
{skill.skill_md[:1000]}

ISSUES ENCOUNTERED:
{issues_text}

Provide specific, actionable improvements to:
1. Fix the identified issues
2. Prevent similar issues in the future
3. Improve the overall quality and completeness

Format as JSON:
{{
  "improvements": [
    {{
      "area": "SKILL.md instructions",
      "change": "Add explicit error handling patterns"
    }},
    {{
      "area": "Examples",
      "change": "Include edge case handling"
    }}
  ],
  "new_sections": ["Common Pitfalls", "Troubleshooting"],
  "updated_best_practices": ["Always validate input", "Use async/await"]
}}"""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text

        # Extract JSON from response
        import re
        import json

        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            refinements = json.loads(json_match.group(0))
            logger.info("refinements_generated", improvements=len(refinements.get("improvements", [])))
            return refinements
        else:
            logger.warning("no_refinements_extracted")
            return {}

    async def _apply_refinements(
        self,
        skill: GeneratedSkill,
        refinements: Dict[str, any],
    ) -> GeneratedSkill:
        """
        Apply refinements to create new skill version.

        Args:
            skill: Current skill.
            refinements: Refinements to apply.

        Returns:
            New refined skill.
        """
        logger.info("applying_refinements", skill=skill.name)

        # Generate improved SKILL.md
        improvements = refinements.get("improvements", [])
        new_sections = refinements.get("new_sections", [])
        updated_best_practices = refinements.get("updated_best_practices", [])

        improvements_text = "\n".join(
            f"- {imp['area']}: {imp['change']}" for imp in improvements
        )

        prompt = f"""Revise this SKILL.md to incorporate these improvements:

CURRENT SKILL.MD:
{skill.skill_md}

IMPROVEMENTS TO APPLY:
{improvements_text}

NEW SECTIONS TO ADD:
{', '.join(new_sections)}

UPDATED BEST PRACTICES:
{', '.join(updated_best_practices)}

Generate the complete revised SKILL.md with:
1. All improvements incorporated
2. New sections added
3. Updated best practices
4. Maintained YAML frontmatter
5. Enhanced examples if needed

Output ONLY the complete SKILL.md content."""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )

        revised_skill_md = response.content[0].text.strip()

        # Create new skill version
        refined_skill = GeneratedSkill(
            name=skill.name,
            skill_md=revised_skill_md,
            examples=skill.examples.copy(),  # Keep existing examples for now
            tests=skill.tests.copy(),  # Keep existing tests for now
            metadata=skill.metadata.copy(),
            version=skill.version + 1,
            parent_skill_id=skill.id,
        )

        logger.info("refinements_applied", skill=skill.name, new_version=refined_skill.version)
        return refined_skill

    async def _is_better(
        self,
        original: GeneratedSkill,
        refined: GeneratedSkill,
        feedback: SkillUsageFeedback,
    ) -> bool:
        """
        Determine if refined skill is better than original.

        Args:
            original: Original skill.
            refined: Refined skill.
            feedback: Feedback that triggered refinement.

        Returns:
            True if refined is better, False otherwise.
        """
        # Simple heuristic: refined is better if it:
        # 1. Has more content (more comprehensive)
        # 2. Addresses the specific issues from feedback

        refined_length = len(refined.skill_md)
        original_length = len(original.skill_md)

        # Must have more content
        if refined_length <= original_length:
            return False

        # Check if it addresses the issues
        if feedback.linting_errors:
            # Should mention linting or code quality
            if "linting" not in refined.skill_md.lower() and "code quality" not in refined.skill_md.lower():
                return False

        if feedback.test_failures:
            # Should have enhanced testing guidance
            if "testing" not in refined.skill_md.lower():
                return False

        logger.info("refined_skill_is_better", skill=refined.name)
        return True

    async def batch_refine_skills(
        self,
        feedbacks: List[SkillUsageFeedback],
        skills_by_name: Dict[str, GeneratedSkill],
    ) -> Dict[str, GeneratedSkill]:
        """
        Refine multiple skills based on batched feedback.

        Args:
            feedbacks: List of feedback items.
            skills_by_name: Current skills indexed by name.

        Returns:
            Dictionary of refined skills (name -> skill).
        """
        logger.info("batch_refining_skills", feedback_count=len(feedbacks))

        # Group feedback by skill
        feedback_by_skill: Dict[str, List[SkillUsageFeedback]] = {}
        for feedback in feedbacks:
            if feedback.skill_name not in feedback_by_skill:
                feedback_by_skill[feedback.skill_name] = []
            feedback_by_skill[feedback.skill_name].append(feedback)

        # Refine each skill
        refined_skills = {}
        for skill_name, skill_feedbacks in feedback_by_skill.items():
            if skill_name not in skills_by_name:
                logger.warning("skill_not_found_for_refinement", skill=skill_name)
                continue

            skill = skills_by_name[skill_name]

            # Aggregate feedback
            aggregated_feedback = self._aggregate_feedback(skill_feedbacks)

            # Refine
            refined = await self.refine_skill(skill, aggregated_feedback)
            if refined:
                refined_skills[skill_name] = refined

        logger.info("batch_refinement_completed", refined_count=len(refined_skills))
        return refined_skills

    def _aggregate_feedback(
        self, feedbacks: List[SkillUsageFeedback]
    ) -> SkillUsageFeedback:
        """
        Aggregate multiple feedback items into one.

        Args:
            feedbacks: List of feedback items for a skill.

        Returns:
            Aggregated feedback.
        """
        # Combine all errors and modifications
        all_linting_errors = []
        all_test_failures = []
        all_modifications = {}

        successful_count = 0
        total_count = len(feedbacks)

        for feedback in feedbacks:
            if feedback.successful:
                successful_count += 1
            all_linting_errors.extend(feedback.linting_errors)
            all_test_failures.extend(feedback.test_failures)
            # Merge modifications
            for key, value in feedback.user_modifications.items():
                if key not in all_modifications:
                    all_modifications[key] = []
                if isinstance(value, list):
                    all_modifications[key].extend(value)
                else:
                    all_modifications[key].append(value)

        # Create aggregated feedback
        return SkillUsageFeedback(
            skill_name=feedbacks[0].skill_name,
            build_id=feedbacks[0].build_id,  # Use first build_id
            successful=successful_count > total_count / 2,  # Majority successful
            feedback_text=f"Aggregated from {total_count} builds ({successful_count} successful)",
            linting_errors=list(set(all_linting_errors)),  # Unique errors
            test_failures=list(set(all_test_failures)),  # Unique failures
            user_modifications=all_modifications,
        )
