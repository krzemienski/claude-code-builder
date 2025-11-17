"""Documentation builder for generated projects."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class DocumentationBuilder:
    """Builds documentation (README, guides, API docs) for generated projects."""

    def __init__(self, logger: ComprehensiveLogger) -> None:
        """Initialize DocumentationBuilder.

        Args:
            logger: Comprehensive logger instance
        """
        self.logger = logger

    async def build_readme(
        self,
        project_name: str,
        description: str,
        features: List[str],
        installation: str,
        usage: str,
        requirements: Optional[List[str]] = None,
        license_info: str = "MIT",
    ) -> str:
        """Build README.md content.

        Args:
            project_name: Name of the project
            description: Project description
            features: List of key features
            installation: Installation instructions
            usage: Usage instructions
            requirements: List of requirements/dependencies
            license_info: License information

        Returns:
            README.md content as string
        """
        self.logger.info("building_readme", project_name=project_name)

        content = f"""# {project_name}

{description}

## Features

{self._format_list(features)}

## Requirements

{self._format_list(requirements or ["Python 3.11+"])}

## Installation

{installation}

## Usage

{usage}

## License

{license_info}
"""

        return content

    async def build_contributing_guide(
        self,
        project_name: str,
        dev_setup: str,
        testing: str,
        code_style: Optional[str] = None,
    ) -> str:
        """Build CONTRIBUTING.md content.

        Args:
            project_name: Name of the project
            dev_setup: Development setup instructions
            testing: Testing instructions
            code_style: Code style guidelines

        Returns:
            CONTRIBUTING.md content as string
        """
        self.logger.info("building_contributing_guide", project_name=project_name)

        content = f"""# Contributing to {project_name}

Thank you for your interest in contributing!

## Development Setup

{dev_setup}

## Testing

{testing}
"""

        if code_style:
            content += f"""
## Code Style

{code_style}
"""

        content += """
## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## Questions?

Feel free to open an issue for any questions or concerns.
"""

        return content

    async def build_api_docs(
        self,
        modules: List[Dict[str, Any]],
    ) -> str:
        """Build API documentation.

        Args:
            modules: List of module specifications with 'name', 'description', 'classes', 'functions'

        Returns:
            API.md content as string
        """
        self.logger.info("building_api_docs", module_count=len(modules))

        content = """# API Documentation

## Overview

This document provides API documentation for the project modules.

"""

        for module in modules:
            name = module.get("name", "Unknown")
            desc = module.get("description", "")
            classes = module.get("classes", [])
            functions = module.get("functions", [])

            content += f"## {name}\n\n{desc}\n\n"

            if classes:
                content += "### Classes\n\n"
                for cls in classes:
                    content += f"#### {cls.get('name', 'Unknown')}\n\n"
                    content += f"{cls.get('description', '')}\n\n"

            if functions:
                content += "### Functions\n\n"
                for func in functions:
                    content += f"#### {func.get('name', 'Unknown')}\n\n"
                    content += f"{func.get('description', '')}\n\n"

        return content

    async def write_documentation(
        self,
        output_path: Path,
        readme_content: str,
        contributing_content: Optional[str] = None,
        api_content: Optional[str] = None,
    ) -> None:
        """Write documentation files to project root.

        Args:
            output_path: Project root path
            readme_content: README.md content
            contributing_content: Optional CONTRIBUTING.md content
            api_content: Optional API.md content
        """
        self.logger.info("writing_documentation", path=str(output_path))

        # Write README.md
        readme_path = output_path / "README.md"
        try:
            readme_path.write_text(readme_content, encoding="utf-8")
            self.logger.info(
                "readme_written",
                path=str(readme_path),
                size_bytes=len(readme_content),
            )
        except Exception as e:
            self.logger.error(
                "readme_write_failed",
                path=str(readme_path),
                error=str(e),
            )
            raise

        # Write CONTRIBUTING.md if provided
        if contributing_content:
            contrib_path = output_path / "CONTRIBUTING.md"
            try:
                contrib_path.write_text(contributing_content, encoding="utf-8")
                self.logger.info(
                    "contributing_written",
                    path=str(contrib_path),
                    size_bytes=len(contributing_content),
                )
            except Exception as e:
                self.logger.error(
                    "contributing_write_failed",
                    path=str(contrib_path),
                    error=str(e),
                )
                raise

        # Write API.md if provided
        if api_content:
            docs_dir = output_path / "docs"
            docs_dir.mkdir(exist_ok=True)
            api_path = docs_dir / "API.md"
            try:
                api_path.write_text(api_content, encoding="utf-8")
                self.logger.info(
                    "api_docs_written",
                    path=str(api_path),
                    size_bytes=len(api_content),
                )
            except Exception as e:
                self.logger.error(
                    "api_docs_write_failed",
                    path=str(api_path),
                    error=str(e),
                )
                raise

    def _format_list(self, items: List[str]) -> str:
        """Format a list as markdown bullet points."""
        if not items:
            return "- None"
        return "\n".join(f"- {item}" for item in items)
