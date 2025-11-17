"""
Skill Manager - High-level API for skill management.

Combines registry and loader into a unified interface for:
- Discovering skills
- Loading skill instructions and resources
- Tracking skill usage
- Managing skill lifecycle
"""

import asyncio
import structlog
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from claude_code_builder_v3.core.models import SkillMetadata, SkillUsageStats
from claude_code_builder_v3.core.exceptions import SkillNotFoundError
from claude_code_builder_v3.skills.registry import SkillRegistry
from claude_code_builder_v3.skills.loader import SkillLoader

logger = structlog.get_logger(__name__)


class SkillManager:
    """
    High-level skill management interface.

    Provides unified API for:
    - Skill discovery and registration
    - Progressive loading (metadata -> instructions -> resources)
    - Usage tracking and analytics
    - Cache management
    """

    def __init__(self, skills_paths: Optional[List[Path]] = None) -> None:
        """
        Initialize skill manager.

        Args:
            skills_paths: List of paths to search for skills.
        """
        self.registry = SkillRegistry(skills_paths=skills_paths)
        self.loader = SkillLoader()

        logger.info("skill_manager_initialized")

    async def initialize(self) -> None:
        """
        Initialize skill manager by discovering all available skills.

        This should be called once at startup to populate the registry.
        """
        logger.info("initializing_skill_manager")
        start_time = datetime.now()

        # Discover all skills
        skills = await self.registry.discover_all_skills()

        duration = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(
            "skill_manager_initialized",
            skills_count=len(skills),
            duration_ms=duration,
        )

    async def get_skill_metadata(self, name: str) -> SkillMetadata:
        """
        Get skill metadata by name.

        Args:
            name: Skill name.

        Returns:
            SkillMetadata.

        Raises:
            SkillNotFoundError: If skill not found.
        """
        return self.registry.get_skill(name)

    async def load_skill(self, name: str) -> tuple[SkillMetadata, str]:
        """
        Load complete skill (metadata + instructions).

        Args:
            name: Skill name.

        Returns:
            Tuple of (metadata, instructions).

        Raises:
            SkillNotFoundError: If skill not found.
        """
        metadata = self.registry.get_skill(name)
        instructions = await self.loader.load_skill_instructions(metadata)
        return metadata, instructions

    async def load_skill_resource(self, skill_name: str, resource_path: str) -> str:
        """
        Load a skill resource.

        Args:
            skill_name: Skill name.
            resource_path: Relative path to resource.

        Returns:
            Resource content.

        Raises:
            SkillNotFoundError: If skill not found.
        """
        metadata = self.registry.get_skill(skill_name)
        return await self.loader.load_skill_resource(metadata, resource_path)

    async def list_all_skills(
        self,
        category: Optional[str] = None,
        trigger: Optional[str] = None,
    ) -> List[SkillMetadata]:
        """
        List all available skills with optional filtering.

        Args:
            category: Filter by category.
            trigger: Filter by trigger keyword.

        Returns:
            List of skill metadata.
        """
        return self.registry.list_skills(category=category, trigger=trigger)

    async def search_skills(self, query: str) -> List[SkillMetadata]:
        """
        Search for skills by query.

        Args:
            query: Search query.

        Returns:
            List of matching skill metadata.
        """
        return self.registry.search_skills(query)

    async def find_skills_for_spec(self, spec: str) -> List[SkillMetadata]:
        """
        Find relevant skills for a specification.

        Analyzes the spec and matches it against:
        - Skill descriptions
        - Technologies
        - Triggers

        Args:
            spec: Project specification.

        Returns:
            List of relevant skills, sorted by relevance.
        """
        logger.info("finding_skills_for_spec", spec_length=len(spec))

        # Extract keywords from spec
        keywords = self._extract_keywords(spec)

        # Find matching skills
        matched_skills: Dict[str, tuple[SkillMetadata, int]] = {}

        for keyword in keywords:
            matching = self.registry.search_skills(keyword)
            for skill in matching:
                if skill.name in matched_skills:
                    # Increase relevance score
                    current_skill, score = matched_skills[skill.name]
                    matched_skills[skill.name] = (current_skill, score + 1)
                else:
                    matched_skills[skill.name] = (skill, 1)

        # Sort by relevance score
        sorted_skills = sorted(
            matched_skills.values(), key=lambda x: x[1], reverse=True
        )

        result = [skill for skill, _ in sorted_skills]

        logger.info(
            "skills_found_for_spec",
            keywords_extracted=len(keywords),
            skills_found=len(result),
            top_skills=[s.name for s in result[:5]],
        )

        return result

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from text.

        Args:
            text: Input text.

        Returns:
            List of keywords.
        """
        # Common technology/framework keywords
        common_keywords = [
            "fastapi",
            "django",
            "flask",
            "react",
            "nextjs",
            "next.js",
            "vue",
            "angular",
            "typescript",
            "javascript",
            "python",
            "go",
            "rust",
            "java",
            "kubernetes",
            "docker",
            "kafka",
            "redis",
            "postgresql",
            "mongodb",
            "graphql",
            "rest",
            "api",
            "microservices",
            "serverless",
            "aws",
            "gcp",
            "azure",
            "stripe",
            "authentication",
            "oauth",
            "jwt",
            "testing",
            "deployment",
            "ci/cd",
            "github actions",
            "gitlab ci",
        ]

        text_lower = text.lower()
        found_keywords = [kw for kw in common_keywords if kw in text_lower]

        logger.debug("keywords_extracted", keywords=found_keywords)
        return found_keywords

    async def record_skill_usage(
        self, skill_name: str, successful: bool, duration_ms: float = 0.0
    ) -> None:
        """
        Record skill usage for tracking.

        Args:
            skill_name: Name of the skill.
            successful: Whether usage was successful.
            duration_ms: Duration in milliseconds.
        """
        self.registry.update_usage_stats(
            skill_name=skill_name, successful=successful, duration_ms=duration_ms
        )

        # Update last used timestamp
        stats = self.registry.get_usage_stats(skill_name)
        stats.last_used_at = datetime.now()
        if not stats.first_used_at:
            stats.first_used_at = datetime.now()

    def get_skill_stats(self, skill_name: str) -> SkillUsageStats:
        """
        Get usage statistics for a skill.

        Args:
            skill_name: Skill name.

        Returns:
            SkillUsageStats.
        """
        return self.registry.get_usage_stats(skill_name)

    def get_all_stats(self) -> List[SkillUsageStats]:
        """
        Get usage statistics for all skills.

        Returns:
            List of SkillUsageStats, sorted by total uses.
        """
        all_stats = [
            self.registry.get_usage_stats(skill_name)
            for skill_name in self.registry._skills.keys()
        ]
        return sorted(all_stats, key=lambda s: s.total_uses, reverse=True)

    def get_categories(self) -> List[str]:
        """Get all available skill categories."""
        return self.registry.get_categories()

    def get_triggers(self) -> List[str]:
        """Get all available skill triggers."""
        return self.registry.get_triggers()

    def clear_caches(self, skill_name: Optional[str] = None) -> None:
        """
        Clear skill caches.

        Args:
            skill_name: If provided, clear only this skill's cache.
        """
        self.loader.clear_cache(skill_name=skill_name)
        logger.info("skill_caches_cleared", skill=skill_name)

    def get_manager_stats(self) -> Dict[str, any]:
        """
        Get overall manager statistics.

        Returns:
            Dictionary with stats.
        """
        cache_stats = self.loader.get_cache_stats()
        usage_stats = self.get_all_stats()

        total_uses = sum(s.total_uses for s in usage_stats)
        successful_uses = sum(s.successful_uses for s in usage_stats)

        return {
            "total_skills": len(self.registry),
            "categories": len(self.get_categories()),
            "total_skill_uses": total_uses,
            "successful_uses": successful_uses,
            "overall_success_rate": (
                successful_uses / total_uses if total_uses > 0 else 0.0
            ),
            "cache_stats": cache_stats,
        }

    async def reload_skills(self) -> None:
        """
        Reload all skills from filesystem.

        Useful when skills have been updated externally.
        """
        logger.info("reloading_all_skills")
        self.clear_caches()
        self.registry._skills.clear()
        self.registry._categories.clear()
        self.registry._triggers.clear()
        await self.initialize()
