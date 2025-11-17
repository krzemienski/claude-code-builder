"""CLAUDE.md file builder for generated projects."""

from pathlib import Path
from typing import Any, Dict, Optional

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class ClaudeMdBuilder:
    """Builds CLAUDE.md files for generated projects."""

    def __init__(self, logger: ComprehensiveLogger) -> None:
        """Initialize ClaudeMdBuilder.

        Args:
            logger: Comprehensive logger instance
        """
        self.logger = logger

    async def build(
        self,
        project_name: str,
        description: str,
        structure: str,
        commands: Dict[str, str],
        key_patterns: Optional[Dict[str, Any]] = None,
        mcp_requirements: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build CLAUDE.md content for a project.

        Args:
            project_name: Name of the project
            description: Project description
            structure: Project structure overview
            commands: Development commands (install, run, test, build, etc.)
            key_patterns: Key implementation patterns to follow
            mcp_requirements: MCP server requirements

        Returns:
            CLAUDE.md content as string
        """
        self.logger.info(
            "building_claude_md",
            project_name=project_name,
            has_patterns=bool(key_patterns),
            has_mcp=bool(mcp_requirements),
        )

        content = f"""# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

{project_name}

{description}

## Architecture Overview

{structure}

## Key Development Commands

```bash
{self._format_commands(commands)}
```

"""

        if key_patterns:
            content += self._format_patterns_section(key_patterns)

        if mcp_requirements:
            content += self._format_mcp_section(mcp_requirements)

        content += """
## Common Operations

- Follow the project structure outlined above
- Use the development commands for all operations
- Maintain consistency with existing code patterns
- Document any changes appropriately

## Success Criteria

- All commands execute successfully
- Code follows established patterns
- Tests pass (if applicable)
- Documentation is up-to-date
"""

        return content

    def _format_commands(self, commands: Dict[str, str]) -> str:
        """Format commands dictionary into bash code block."""
        lines = []
        for name, cmd in commands.items():
            lines.append(f"# {name}")
            lines.append(cmd)
            lines.append("")
        return "\n".join(lines)

    def _format_patterns_section(self, patterns: Dict[str, Any]) -> str:
        """Format key patterns section."""
        content = "## Key Implementation Patterns\n\n"

        for pattern_name, pattern_details in patterns.items():
            content += f"### {pattern_name}\n\n"
            if isinstance(pattern_details, str):
                content += f"{pattern_details}\n\n"
            elif isinstance(pattern_details, dict):
                for key, value in pattern_details.items():
                    content += f"**{key}**: {value}\n\n"

        return content

    def _format_mcp_section(self, mcp_requirements: Dict[str, Any]) -> str:
        """Format MCP requirements section."""
        content = "## MCP Server Requirements\n\n"
        content += "This project requires the following MCP servers:\n\n"

        for server, config in mcp_requirements.items():
            content += f"- **{server}**: {config.get('purpose', 'Required for project operations')}\n"

        content += "\n"
        return content

    async def write_file(self, output_path: Path, content: str) -> None:
        """Write CLAUDE.md file to disk.

        Args:
            output_path: Path to write CLAUDE.md
            content: CLAUDE.md content
        """
        claude_md_path = output_path / "CLAUDE.md"
        self.logger.info("writing_claude_md", path=str(claude_md_path))

        try:
            claude_md_path.write_text(content, encoding="utf-8")
            self.logger.info(
                "claude_md_written",
                path=str(claude_md_path),
                size_bytes=len(content),
            )
        except Exception as e:
            self.logger.error(
                "claude_md_write_failed",
                path=str(claude_md_path),
                error=str(e),
            )
            raise
