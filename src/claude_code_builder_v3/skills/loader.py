"""
Skill Loader - Progressive disclosure for skills.

Implements the three-level loading strategy:
1. Metadata: Always loaded (~100 tokens per skill)
2. Instructions: Loaded when skill is triggered (~3-5K tokens)
3. Resources: Accessed on-demand from filesystem (0 tokens)
"""

import asyncio
import structlog
from pathlib import Path
from typing import Dict, Optional

from claude_code_builder_v3.core.models import SkillMetadata
from claude_code_builder_v3.core.exceptions import SkillLoadError

logger = structlog.get_logger(__name__)


class SkillLoader:
    """
    Progressive disclosure loader for Claude Skills.

    Optimizes token usage by loading skills in stages:
    - Level 1: Metadata (always in context)
    - Level 2: Instructions (loaded when triggered)
    - Level 3: Resources (filesystem access, zero tokens)
    """

    def __init__(self) -> None:
        """Initialize skill loader."""
        # Cache loaded instructions
        self._instructions_cache: Dict[str, str] = {}
        self._resources_cache: Dict[str, Dict[str, str]] = {}

        logger.info("skill_loader_initialized")

    async def load_skill_instructions(
        self, metadata: SkillMetadata, force_reload: bool = False
    ) -> str:
        """
        Load full skill instructions from SKILL.md.

        This is Level 2 of progressive disclosure - only loaded when skill
        is triggered by Claude during conversation.

        Args:
            metadata: Skill metadata (includes path).
            force_reload: Force reload even if cached.

        Returns:
            Full SKILL.md content (YAML frontmatter + instructions).

        Raises:
            SkillLoadError: If skill cannot be loaded.
        """
        skill_name = metadata.name

        # Check cache
        if not force_reload and skill_name in self._instructions_cache:
            logger.debug("skill_instructions_cache_hit", skill=skill_name)
            return self._instructions_cache[skill_name]

        # Load from filesystem
        if not metadata.path:
            raise SkillLoadError(skill_name, "Skill path not set")

        skill_md_path = metadata.path / "SKILL.md"
        if not skill_md_path.exists():
            raise SkillLoadError(skill_name, f"SKILL.md not found at {skill_md_path}")

        try:
            logger.info("loading_skill_instructions", skill=skill_name, path=str(skill_md_path))
            content = await asyncio.to_thread(skill_md_path.read_text)

            # Cache for future use
            self._instructions_cache[skill_name] = content

            logger.info(
                "skill_instructions_loaded",
                skill=skill_name,
                size_bytes=len(content),
                estimated_tokens=len(content) // 4,  # Rough estimate
            )
            return content

        except Exception as e:
            raise SkillLoadError(skill_name, f"Failed to read SKILL.md: {e}") from e

    async def load_skill_resource(
        self, metadata: SkillMetadata, resource_path: str
    ) -> str:
        """
        Load a skill resource from filesystem.

        This is Level 3 of progressive disclosure - resources are accessed
        on-demand with zero token cost (filesystem access only).

        Args:
            metadata: Skill metadata (includes path).
            resource_path: Relative path to resource within skill directory.
                          e.g., "examples/basic.py", "templates/router.py"

        Returns:
            Resource content as string.

        Raises:
            SkillLoadError: If resource cannot be loaded.
        """
        skill_name = metadata.name
        cache_key = f"{skill_name}:{resource_path}"

        # Check cache
        if cache_key in self._resources_cache.get(skill_name, {}):
            logger.debug(
                "skill_resource_cache_hit", skill=skill_name, resource=resource_path
            )
            return self._resources_cache[skill_name][resource_path]

        # Load from filesystem
        if not metadata.path:
            raise SkillLoadError(skill_name, "Skill path not set")

        full_path = metadata.path / resource_path
        if not full_path.exists():
            raise SkillLoadError(
                skill_name, f"Resource not found: {resource_path} at {full_path}"
            )

        try:
            logger.info(
                "loading_skill_resource",
                skill=skill_name,
                resource=resource_path,
                path=str(full_path),
            )
            content = await asyncio.to_thread(full_path.read_text)

            # Cache for future use
            if skill_name not in self._resources_cache:
                self._resources_cache[skill_name] = {}
            self._resources_cache[skill_name][resource_path] = content

            logger.info(
                "skill_resource_loaded",
                skill=skill_name,
                resource=resource_path,
                size_bytes=len(content),
            )
            return content

        except Exception as e:
            raise SkillLoadError(
                skill_name, f"Failed to read resource '{resource_path}': {e}"
            ) from e

    async def list_skill_resources(self, metadata: SkillMetadata) -> Dict[str, list[str]]:
        """
        List all available resources in a skill directory.

        Args:
            metadata: Skill metadata (includes path).

        Returns:
            Dictionary of resource types to file paths.
            e.g., {"examples": ["basic.py", "advanced.py"], "templates": ["api.py"]}
        """
        skill_name = metadata.name

        if not metadata.path:
            logger.warning("skill_path_not_set", skill=skill_name)
            return {}

        resources: Dict[str, list[str]] = {}

        # Common resource directories
        resource_dirs = ["examples", "templates", "tests", "resources"]

        for dir_name in resource_dirs:
            dir_path = metadata.path / dir_name
            if not dir_path.exists() or not dir_path.is_dir():
                continue

            # List files in directory
            files = []
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    files.append(file_path.name)

            if files:
                resources[dir_name] = files

        logger.debug(
            "skill_resources_listed",
            skill=skill_name,
            resource_types=list(resources.keys()),
            total_files=sum(len(files) for files in resources.values()),
        )
        return resources

    def clear_cache(self, skill_name: Optional[str] = None) -> None:
        """
        Clear cached instructions and resources.

        Args:
            skill_name: If provided, clear only this skill's cache.
                       If None, clear all caches.
        """
        if skill_name:
            if skill_name in self._instructions_cache:
                del self._instructions_cache[skill_name]
            if skill_name in self._resources_cache:
                del self._resources_cache[skill_name]
            logger.info("skill_cache_cleared", skill=skill_name)
        else:
            self._instructions_cache.clear()
            self._resources_cache.clear()
            logger.info("all_skill_caches_cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats.
        """
        total_resources = sum(
            len(resources) for resources in self._resources_cache.values()
        )

        return {
            "instructions_cached": len(self._instructions_cache),
            "resources_cached": total_resources,
            "skills_with_resources": len(self._resources_cache),
        }
