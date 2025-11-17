"""
Skill Registry - Central registry for all available skills.

Manages skill discovery, registration, and lookup across:
- Built-in skills
- User-installed skills
- Generated skills
- Marketplace skills
"""

import asyncio
import structlog
from pathlib import Path
from typing import Dict, List, Optional

from claude_code_builder_v3.core.models import SkillMetadata, SkillUsageStats
from claude_code_builder_v3.core.exceptions import SkillNotFoundError

logger = structlog.get_logger(__name__)


class SkillRegistry:
    """
    Central registry for all Claude Skills.

    Provides:
    - Skill discovery from multiple locations
    - Skill lookup by name/tags/category
    - Skill usage tracking
    - Skill version management
    """

    def __init__(self, skills_paths: Optional[List[Path]] = None) -> None:
        """
        Initialize skill registry.

        Args:
            skills_paths: List of paths to search for skills.
                          Defaults to:
                          - ~/.claude/skills/ (built-in)
                          - ~/.claude/skills/generated/ (generated)
                          - ~/.claude/skills/marketplace/ (installed from marketplace)
        """
        if skills_paths is None:
            home = Path.home()
            self.skills_paths = [
                home / ".claude" / "skills",
                home / ".claude" / "skills" / "generated",
                home / ".claude" / "skills" / "marketplace",
            ]
        else:
            self.skills_paths = skills_paths

        # Registries
        self._skills: Dict[str, SkillMetadata] = {}
        self._usage_stats: Dict[str, SkillUsageStats] = {}
        self._categories: Dict[str, List[str]] = {}  # category -> [skill_names]
        self._triggers: Dict[str, List[str]] = {}  # trigger -> [skill_names]

        logger.info("skill_registry_initialized", paths=str(self.skills_paths))

    async def discover_all_skills(self) -> List[SkillMetadata]:
        """
        Discover all available skills from configured paths.

        Returns:
            List of discovered skill metadata.
        """
        logger.info("discovering_skills", paths=str(self.skills_paths))

        discovered = []
        for base_path in self.skills_paths:
            if not base_path.exists():
                logger.debug("path_not_found", path=str(base_path))
                continue

            # Scan for skill directories
            for skill_dir in base_path.iterdir():
                if not skill_dir.is_dir():
                    continue

                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    logger.debug("no_skill_md", path=str(skill_dir))
                    continue

                try:
                    metadata = await self._parse_skill_metadata(skill_md)
                    metadata.path = skill_dir
                    discovered.append(metadata)
                    await self.register_skill(metadata)
                    logger.info("skill_discovered", skill=metadata.name, path=str(skill_dir))
                except Exception as e:
                    logger.error(
                        "skill_parse_error", path=str(skill_md), error=str(e)
                    )
                    continue

        logger.info("skills_discovered", count=len(discovered))
        return discovered

    async def register_skill(self, metadata: SkillMetadata) -> None:
        """
        Register a skill in the registry.

        Args:
            metadata: Skill metadata to register.
        """
        self._skills[metadata.name] = metadata

        # Index by category
        if metadata.category:
            if metadata.category not in self._categories:
                self._categories[metadata.category] = []
            if metadata.name not in self._categories[metadata.category]:
                self._categories[metadata.category].append(metadata.name)

        # Index by triggers
        for trigger in metadata.triggers:
            if trigger not in self._triggers:
                self._triggers[trigger] = []
            if metadata.name not in self._triggers[trigger]:
                self._triggers[trigger].append(metadata.name)

        # Initialize usage stats
        if metadata.name not in self._usage_stats:
            self._usage_stats[metadata.name] = SkillUsageStats(skill_name=metadata.name)

        logger.debug("skill_registered", skill=metadata.name)

    def get_skill(self, name: str) -> SkillMetadata:
        """
        Get skill metadata by name.

        Args:
            name: Skill name.

        Returns:
            SkillMetadata for the skill.

        Raises:
            SkillNotFoundError: If skill is not found.
        """
        if name not in self._skills:
            raise SkillNotFoundError(name)
        return self._skills[name]

    def list_skills(
        self,
        category: Optional[str] = None,
        trigger: Optional[str] = None,
    ) -> List[SkillMetadata]:
        """
        List all registered skills with optional filtering.

        Args:
            category: Filter by category.
            trigger: Filter by trigger keyword.

        Returns:
            List of skill metadata matching filters.
        """
        if category:
            skill_names = self._categories.get(category, [])
            return [self._skills[name] for name in skill_names]

        if trigger:
            skill_names = self._triggers.get(trigger, [])
            return [self._skills[name] for name in skill_names]

        return list(self._skills.values())

    def search_skills(self, query: str) -> List[SkillMetadata]:
        """
        Search for skills by query.

        Searches in:
        - Skill name
        - Description
        - Technologies
        - Triggers

        Args:
            query: Search query.

        Returns:
            List of matching skills.
        """
        query_lower = query.lower()
        results = []

        for skill in self._skills.values():
            # Search in name
            if query_lower in skill.name.lower():
                results.append(skill)
                continue

            # Search in description
            if query_lower in skill.description.lower():
                results.append(skill)
                continue

            # Search in technologies
            if any(query_lower in tech.lower() for tech in skill.technologies):
                results.append(skill)
                continue

            # Search in triggers
            if any(query_lower in trigger.lower() for trigger in skill.triggers):
                results.append(skill)
                continue

        logger.info("skill_search", query=query, results=len(results))
        return results

    def get_usage_stats(self, skill_name: str) -> SkillUsageStats:
        """
        Get usage statistics for a skill.

        Args:
            skill_name: Name of the skill.

        Returns:
            SkillUsageStats for the skill.
        """
        if skill_name not in self._usage_stats:
            self._usage_stats[skill_name] = SkillUsageStats(skill_name=skill_name)
        return self._usage_stats[skill_name]

    def update_usage_stats(
        self, skill_name: str, successful: bool, duration_ms: float = 0.0
    ) -> None:
        """
        Update usage statistics for a skill.

        Args:
            skill_name: Name of the skill.
            successful: Whether the skill usage was successful.
            duration_ms: Duration in milliseconds.
        """
        stats = self.get_usage_stats(skill_name)
        stats.total_uses += 1

        if successful:
            stats.successful_uses += 1
        else:
            stats.failed_uses += 1

        stats.success_rate = (
            stats.successful_uses / stats.total_uses if stats.total_uses > 0 else 0.0
        )

        # Update duration
        if duration_ms > 0:
            if stats.average_duration_ms == 0:
                stats.average_duration_ms = duration_ms
            else:
                # Running average
                stats.average_duration_ms = (
                    stats.average_duration_ms * (stats.total_uses - 1) + duration_ms
                ) / stats.total_uses

        logger.debug(
            "usage_stats_updated",
            skill=skill_name,
            total_uses=stats.total_uses,
            success_rate=stats.success_rate,
        )

    async def _parse_skill_metadata(self, skill_md_path: Path) -> SkillMetadata:
        """
        Parse skill metadata from SKILL.md YAML frontmatter.

        Args:
            skill_md_path: Path to SKILL.md file.

        Returns:
            Parsed SkillMetadata.

        Raises:
            ValueError: If SKILL.md has invalid format.
        """
        import yaml

        content = await asyncio.to_thread(skill_md_path.read_text)

        # Extract YAML frontmatter
        if not content.startswith("---"):
            raise ValueError(f"SKILL.md missing YAML frontmatter: {skill_md_path}")

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid SKILL.md format: {skill_md_path}")

        yaml_content = parts[1]
        metadata_dict = yaml.safe_load(yaml_content)

        return SkillMetadata(**metadata_dict)

    def get_categories(self) -> List[str]:
        """Get all available skill categories."""
        return list(self._categories.keys())

    def get_triggers(self) -> List[str]:
        """Get all available skill triggers."""
        return list(self._triggers.keys())

    def __len__(self) -> int:
        """Return number of registered skills."""
        return len(self._skills)

    def __contains__(self, skill_name: str) -> bool:
        """Check if skill is registered."""
        return skill_name in self._skills
