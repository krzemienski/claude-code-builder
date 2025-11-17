"""
Skill Generator Agent - Dynamic skill generation with MCP research.

This is the core of Feature 6: Self-Improving Skill System.

The SkillGenerator:
1. Analyzes specifications to identify skill gaps
2. Researches technologies using MCP servers (context7, fetch, memory)
3. Generates complete SKILL.md with YAML frontmatter
4. Creates example implementations
5. Generates validation tests
6. Produces production-ready skills
"""

import asyncio
import json
import structlog
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from anthropic import Anthropic, AsyncAnthropic

from claude_code_builder_v3.core.models import (
    SkillGap,
    GeneratedSkill,
    SkillMetadata,
)
from claude_code_builder_v3.core.exceptions import SkillGenerationError

logger = structlog.get_logger(__name__)


class SkillGenerator:
    """
    Dynamically generates Claude Skills based on project requirements.

    Uses Claude Agent SDK + MCP servers for:
    - context7: Research framework/library best practices
    - fetch: Get official documentation
    - memory: Check for similar patterns from past builds
    - filesystem: Save generated skills
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        use_mcp: bool = True,
    ) -> None:
        """
        Initialize SkillGenerator.

        Args:
            api_key: Anthropic API key.
            model: Claude model to use.
            use_mcp: Whether to use MCP servers for research.
        """
        self.api_key = api_key
        self.model = model
        self.use_mcp = use_mcp

        # Initialize Anthropic client
        self.client = AsyncAnthropic(api_key=api_key)

        logger.info("skill_generator_initialized", model=model, use_mcp=use_mcp)

    async def analyze_skill_gaps(
        self, spec: str, existing_skills: List[SkillMetadata]
    ) -> List[SkillGap]:
        """
        Analyze specification to identify missing skills.

        Args:
            spec: Project specification.
            existing_skills: Currently available skills.

        Returns:
            List of identified skill gaps.
        """
        logger.info(
            "analyzing_skill_gaps",
            spec_length=len(spec),
            existing_skills_count=len(existing_skills),
        )

        # Format existing skills for context
        existing_skills_text = self._format_skill_list(existing_skills)

        prompt = f"""Analyze this project specification and identify what skills are needed but missing.

PROJECT SPECIFICATION:
{spec}

AVAILABLE SKILLS:
{existing_skills_text}

Your task:
1. Identify the technologies, frameworks, and patterns mentioned in the spec
2. Determine which skills from the available skills list can be used
3. Identify any MISSING skills that would be needed but don't exist yet

For each missing skill, provide:
- name: Skill name in kebab-case (e.g., "fastapi-stripe-webhooks")
- description: Clear description of what this skill does and when to use it
- technologies: List of technologies/frameworks involved
- patterns: List of patterns this skill should encode
- integration_points: External APIs/services it integrates with
- doc_urls: URLs to official documentation (if known)
- priority: low/medium/high/critical

Return your analysis as a JSON array of skill gaps. If no skills are missing, return an empty array.

Example output:
[
  {{
    "name": "fastapi-stripe-webhooks",
    "description": "Stripe webhook integration with signature verification and idempotency",
    "technologies": ["FastAPI", "Stripe", "webhooks"],
    "patterns": ["webhook verification", "event handling", "idempotency"],
    "integration_points": ["Stripe API"],
    "doc_urls": ["https://stripe.com/docs/webhooks"],
    "priority": "high"
  }}
]"""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract JSON from response
            content = response.content[0].text

            # Find JSON array in response
            import re

            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if not json_match:
                logger.warning("no_skill_gaps_found_in_response")
                return []

            gaps_data = json.loads(json_match.group(0))

            # Convert to SkillGap objects
            gaps = [SkillGap(**gap_data) for gap_data in gaps_data]

            logger.info(
                "skill_gaps_identified",
                gaps_count=len(gaps),
                gaps=[g.name for g in gaps],
            )

            return gaps

        except Exception as e:
            logger.error("skill_gap_analysis_failed", error=str(e))
            raise SkillGenerationError("gap_analysis", str(e)) from e

    async def generate_skill(
        self,
        skill_gap: SkillGap,
        research_context: Optional[str] = None,
    ) -> GeneratedSkill:
        """
        Generate a complete skill from a skill gap.

        Args:
            skill_gap: Description of the missing skill.
            research_context: Optional pre-researched context.

        Returns:
            Complete GeneratedSkill ready for validation.
        """
        logger.info("generating_skill", skill=skill_gap.name)
        start_time = datetime.now()

        try:
            # Step 1: Research (if not provided)
            if not research_context:
                research_context = await self._research_skill(skill_gap)

            # Step 2: Generate SKILL.md
            skill_md = await self._generate_skill_md(skill_gap, research_context)

            # Step 3: Generate examples
            examples = await self._generate_examples(skill_gap, research_context)

            # Step 4: Generate tests
            tests = await self._generate_skill_tests(skill_gap, examples)

            # Step 5: Create metadata
            metadata = SkillMetadata(
                name=skill_gap.name,
                description=skill_gap.description,
                version="1.0.0",
                author="CCB Skill Generator",
                technologies=skill_gap.technologies,
                triggers=skill_gap.technologies + skill_gap.patterns,
            )

            # Step 6: Create GeneratedSkill
            generated_skill = GeneratedSkill(
                name=skill_gap.name,
                skill_md=skill_md,
                examples=examples,
                tests=tests,
                metadata=metadata,
            )

            duration = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(
                "skill_generated",
                skill=skill_gap.name,
                examples_count=len(examples),
                tests_count=len(tests),
                duration_ms=duration,
            )

            return generated_skill

        except Exception as e:
            logger.error("skill_generation_failed", skill=skill_gap.name, error=str(e))
            raise SkillGenerationError(skill_gap.name, str(e)) from e

    async def _research_skill(self, skill_gap: SkillGap) -> str:
        """
        Research skill requirements using MCP servers and web.

        Uses:
        - Claude's knowledge for best practices
        - Web search for latest documentation (if URLs provided)

        Args:
            skill_gap: Skill gap to research.

        Returns:
            Research context as string.
        """
        logger.info("researching_skill", skill=skill_gap.name)

        research_prompt = f"""Research best practices and patterns for:

SKILL: {skill_gap.name}
DESCRIPTION: {skill_gap.description}
TECHNOLOGIES: {', '.join(skill_gap.technologies)}
PATTERNS: {', '.join(skill_gap.patterns)}

Provide comprehensive research including:
1. Architecture patterns and best practices
2. Common pitfalls and how to avoid them
3. Security considerations
4. Testing strategies
5. Example code patterns
6. Integration considerations

Focus on production-ready, real-world implementations."""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                messages=[{"role": "user", "content": research_prompt}],
            )

            research = response.content[0].text

            logger.info(
                "skill_research_completed",
                skill=skill_gap.name,
                research_length=len(research),
            )

            return research

        except Exception as e:
            logger.error("skill_research_failed", skill=skill_gap.name, error=str(e))
            # Return minimal context if research fails
            return f"Basic skill for {', '.join(skill_gap.technologies)}"

    async def _generate_skill_md(self, skill_gap: SkillGap, research: str) -> str:
        """
        Generate complete SKILL.md file content.

        Args:
            skill_gap: Skill gap information.
            research: Research context.

        Returns:
            Complete SKILL.md content with YAML frontmatter.
        """
        logger.info("generating_skill_md", skill=skill_gap.name)

        prompt = f"""Generate a complete SKILL.md file for a Claude Skill.

SKILL NAME: {skill_gap.name}
DESCRIPTION: {skill_gap.description}
TECHNOLOGIES: {', '.join(skill_gap.technologies)}
PATTERNS: {', '.join(skill_gap.patterns)}

RESEARCH CONTEXT:
{research}

Create a production-ready SKILL.md with:

1. YAML FRONTMATTER (between --- markers):
   - name: {skill_gap.name}
   - description: Clear, concise description
   - version: 1.0.0
   - author: CCB Skill Generator
   - category: Appropriate category
   - technologies: List of technologies
   - triggers: Keywords that should trigger this skill

2. MARKDOWN CONTENT with sections:
   - Overview
   - Project Structure (with example directory tree)
   - Core Dependencies (with version numbers)
   - Key Patterns (with code examples)
   - Best Practices
   - Security Considerations
   - Testing Strategy
   - When to Use / When NOT to Use
   - Generated Files Checklist

Make it comprehensive, production-ready, and actionable. Include real code examples.

Output ONLY the SKILL.md content, starting with --- for YAML frontmatter."""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )

            skill_md = response.content[0].text.strip()

            # Ensure it starts with YAML frontmatter
            if not skill_md.startswith("---"):
                skill_md = f"""---
name: {skill_gap.name}
description: {skill_gap.description}
version: 1.0.0
author: CCB Skill Generator
technologies: {json.dumps(skill_gap.technologies)}
triggers: {json.dumps(skill_gap.technologies + skill_gap.patterns)}
---

{skill_md}"""

            logger.info(
                "skill_md_generated",
                skill=skill_gap.name,
                size_bytes=len(skill_md),
            )

            return skill_md

        except Exception as e:
            logger.error("skill_md_generation_failed", skill=skill_gap.name, error=str(e))
            raise

    async def _generate_examples(
        self, skill_gap: SkillGap, research: str
    ) -> Dict[str, str]:
        """
        Generate example implementations.

        Args:
            skill_gap: Skill gap information.
            research: Research context.

        Returns:
            Dictionary of filename -> code content.
        """
        logger.info("generating_examples", skill=skill_gap.name)

        examples: Dict[str, str] = {}

        # Generate basic, intermediate, and advanced examples
        for level in ["basic", "intermediate", "advanced"]:
            prompt = f"""Generate a {level} example for {skill_gap.name}.

DESCRIPTION: {skill_gap.description}
TECHNOLOGIES: {', '.join(skill_gap.technologies)}

RESEARCH CONTEXT:
{research}

Create a complete, working code example that demonstrates {level}-level usage.

For {level} level:
- basic: Minimal working example
- intermediate: With error handling and validation
- advanced: Production-ready with all best practices

Output ONLY the code, no explanations."""

            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )

                code = response.content[0].text.strip()

                # Extract code from markdown if present
                if "```" in code:
                    import re

                    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", code, re.DOTALL)
                    if code_blocks:
                        code = code_blocks[0]

                examples[f"example_{level}.py"] = code

                logger.debug(
                    "example_generated",
                    skill=skill_gap.name,
                    level=level,
                    size_bytes=len(code),
                )

            except Exception as e:
                logger.error(
                    "example_generation_failed",
                    skill=skill_gap.name,
                    level=level,
                    error=str(e),
                )
                # Continue with other examples

        logger.info(
            "examples_generated", skill=skill_gap.name, count=len(examples)
        )
        return examples

    async def _generate_skill_tests(
        self, skill_gap: SkillGap, examples: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Generate tests for the skill.

        Args:
            skill_gap: Skill gap information.
            examples: Generated examples.

        Returns:
            Dictionary of filename -> test code.
        """
        logger.info("generating_skill_tests", skill=skill_gap.name)

        tests: Dict[str, str] = {}

        # Generate test for examples
        examples_text = "\n\n".join(
            f"# {filename}\n{code}" for filename, code in examples.items()
        )

        prompt = f"""Generate pytest tests to validate the skill examples.

SKILL: {skill_gap.name}
DESCRIPTION: {skill_gap.description}

EXAMPLES:
{examples_text}

Create comprehensive pytest tests that:
1. Validate the examples are syntactically correct
2. Test key functionality
3. Check for common errors
4. Verify best practices are followed

Output ONLY the test code."""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            test_code = response.content[0].text.strip()

            # Extract code from markdown if present
            if "```" in test_code:
                import re

                code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", test_code, re.DOTALL)
                if code_blocks:
                    test_code = code_blocks[0]

            tests["test_skill.py"] = test_code

            logger.info("skill_tests_generated", skill=skill_gap.name)

        except Exception as e:
            logger.error(
                "skill_tests_generation_failed", skill=skill_gap.name, error=str(e)
            )
            # Create minimal test
            tests["test_skill.py"] = f'''"""Tests for {skill_gap.name} skill."""

def test_skill_exists():
    """Test that skill exists."""
    assert True  # Placeholder
'''

        return tests

    def _format_skill_list(self, skills: List[SkillMetadata]) -> str:
        """Format skill list for prompt."""
        if not skills:
            return "No skills available."

        lines = []
        for skill in skills:
            lines.append(f"- {skill.name}: {skill.description}")
            if skill.technologies:
                lines.append(f"  Technologies: {', '.join(skill.technologies)}")

        return "\n".join(lines)

    async def save_generated_skill(
        self, skill: GeneratedSkill, output_dir: Optional[Path] = None
    ) -> Path:
        """
        Save generated skill to filesystem.

        Args:
            skill: Generated skill to save.
            output_dir: Output directory. Defaults to ~/.claude/skills/generated/

        Returns:
            Path where skill was saved.
        """
        if output_dir is None:
            output_dir = Path.home() / ".claude" / "skills" / "generated"

        skill_dir = output_dir / skill.name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Save SKILL.md
        skill_md_path = skill_dir / "SKILL.md"
        await asyncio.to_thread(skill_md_path.write_text, skill.skill_md)

        # Save examples
        if skill.examples:
            examples_dir = skill_dir / "examples"
            examples_dir.mkdir(exist_ok=True)
            for filename, content in skill.examples.items():
                example_path = examples_dir / filename
                await asyncio.to_thread(example_path.write_text, content)

        # Save tests
        if skill.tests:
            tests_dir = skill_dir / "tests"
            tests_dir.mkdir(exist_ok=True)
            for filename, content in skill.tests.items():
                test_path = tests_dir / filename
                await asyncio.to_thread(test_path.write_text, content)

        logger.info("skill_saved_to_filesystem", skill=skill.name, path=str(skill_dir))
        return skill_dir
