"""Slash command builder for generated projects."""

from pathlib import Path
from typing import Any, Dict, List

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class CommandBuilder:
    """Builds slash commands (.claude/commands/) for generated projects."""

    def __init__(self, logger: ComprehensiveLogger) -> None:
        """Initialize CommandBuilder.

        Args:
            logger: Comprehensive logger instance
        """
        self.logger = logger

    async def build_commands(
        self,
        commands: List[Dict[str, str]],
    ) -> Dict[str, str]:
        """Build slash commands from specifications.

        Args:
            commands: List of command specifications with 'name' and 'prompt'

        Returns:
            Dictionary mapping command filenames to their content
        """
        self.logger.info("building_commands", count=len(commands))

        command_files = {}

        for cmd in commands:
            name = cmd.get("name", "")
            prompt = cmd.get("prompt", "")

            if not name or not prompt:
                self.logger.warning("skipping_invalid_command", name=name)
                continue

            filename = f"{name}.md"
            command_files[filename] = prompt

            self.logger.info("command_built", name=name, filename=filename)

        return command_files

    async def build_default_commands(
        self,
        project_name: str,
        test_command: str = "pytest",
        build_command: str = "python -m build",
    ) -> Dict[str, str]:
        """Build default slash commands for a project.

        Args:
            project_name: Name of the project
            test_command: Command to run tests
            build_command: Command to build the project

        Returns:
            Dictionary of default commands
        """
        self.logger.info("building_default_commands", project=project_name)

        return {
            "test.md": f"""Run all tests for {project_name}.

Execute the test suite:
```bash
{test_command}
```

Report any failures found.""",
            "build.md": f"""Build the {project_name} project.

Execute the build:
```bash
{build_command}
```

Verify the build artifacts are created successfully.""",
            "check.md": f"""Run code quality checks for {project_name}.

This should:
1. Run linters
2. Check formatting
3. Validate type hints
4. Report any issues found""",
            "review.md": """Review recent code changes.

Analyze the git diff and provide:
1. Code quality assessment
2. Potential bugs or issues
3. Suggestions for improvement
4. Security concerns""",
        }

    async def write_commands(
        self,
        output_path: Path,
        commands: Dict[str, str],
    ) -> None:
        """Write command files to .claude/commands/ directory.

        Args:
            output_path: Project root path
            commands: Dictionary mapping command filenames to content
        """
        commands_dir = output_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(
            "writing_commands",
            path=str(commands_dir),
            count=len(commands),
        )

        for filename, content in commands.items():
            command_path = commands_dir / filename
            try:
                command_path.write_text(content, encoding="utf-8")
                self.logger.info(
                    "command_written",
                    filename=filename,
                    path=str(command_path),
                    size_bytes=len(content),
                )
            except Exception as e:
                self.logger.error(
                    "command_write_failed",
                    filename=filename,
                    path=str(command_path),
                    error=str(e),
                )
                raise

    async def create_commands_readme(self, output_path: Path) -> None:
        """Create README.md in .claude/commands/ explaining usage.

        Args:
            output_path: Project root path
        """
        commands_dir = output_path / ".claude" / "commands"
        readme_path = commands_dir / "README.md"

        content = """# Slash Commands

This directory contains custom slash commands for use with Claude Code.

## Usage

To use a command, type `/` followed by the command name in Claude Code:

- `/test` - Run tests
- `/build` - Build the project
- `/check` - Run code quality checks
- `/review` - Review code changes

## Adding Custom Commands

Create a new `.md` file in this directory with your command prompt.
The filename (without `.md`) becomes the command name.

Example (`custom.md`):
```
Do something custom with the codebase.
```

Then use it with `/custom` in Claude Code.
"""

        try:
            readme_path.write_text(content, encoding="utf-8")
            self.logger.info("commands_readme_written", path=str(readme_path))
        except Exception as e:
            self.logger.error(
                "commands_readme_failed",
                path=str(readme_path),
                error=str(e),
            )
            raise
