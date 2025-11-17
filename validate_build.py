#!/usr/bin/env python3
"""Functional validation script for Claude Code Builder v2.

This script validates that a built project has all expected artifacts
and structure. NO mocks - tests real outputs.

Usage:
    python validate_build.py <project_directory>
"""

import sys
from pathlib import Path
from typing import List, Tuple


class BuildValidator:
    """Validates built project artifacts."""

    def __init__(self, project_dir: Path) -> None:
        """Initialize validator.

        Args:
            project_dir: Path to project directory to validate
        """
        self.project_dir = project_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checks_passed = 0
        self.checks_failed = 0

    def check_file_exists(self, path: Path, description: str) -> bool:
        """Check if a file exists.

        Args:
            path: Path to check
            description: Description of the file

        Returns:
            True if exists, False otherwise
        """
        if path.exists():
            print(f"✓ {description}: {path}")
            self.checks_passed += 1
            return True
        else:
            error = f"✗ {description} missing: {path}"
            print(error)
            self.errors.append(error)
            self.checks_failed += 1
            return False

    def check_directory_exists(self, path: Path, description: str) -> bool:
        """Check if a directory exists.

        Args:
            path: Path to check
            description: Description of the directory

        Returns:
            True if exists, False otherwise
        """
        if path.exists() and path.is_dir():
            print(f"✓ {description}: {path}")
            self.checks_passed += 1
            return True
        else:
            error = f"✗ {description} missing: {path}"
            print(error)
            self.errors.append(error)
            self.checks_failed += 1
            return False

    def check_file_not_empty(self, path: Path, description: str) -> bool:
        """Check if a file exists and is not empty.

        Args:
            path: Path to check
            description: Description of the file

        Returns:
            True if exists and not empty, False otherwise
        """
        if not path.exists():
            error = f"✗ {description} missing: {path}"
            print(error)
            self.errors.append(error)
            self.checks_failed += 1
            return False

        if path.stat().st_size == 0:
            warning = f"⚠ {description} is empty: {path}"
            print(warning)
            self.warnings.append(warning)
            return False

        print(f"✓ {description} ({path.stat().st_size} bytes): {path}")
        self.checks_passed += 1
        return True

    def validate_basic_structure(self) -> None:
        """Validate basic project structure."""
        print("\n=== Validating Basic Structure ===\n")

        # Check project directory exists
        if not self.project_dir.exists():
            print(f"✗ Project directory does not exist: {self.project_dir}")
            self.errors.append(f"Project directory not found: {self.project_dir}")
            self.checks_failed += 1
            return

        # Check for common documentation files
        self.check_file_not_empty(
            self.project_dir / "README.md", "README.md"
        )
        self.check_file_exists(
            self.project_dir / "CLAUDE.md", "CLAUDE.md (optional)"
        )

    def validate_python_project(self) -> None:
        """Validate Python project structure."""
        print("\n=== Validating Python Project ===\n")

        # Check for Python project files
        has_pyproject = self.check_file_exists(
            self.project_dir / "pyproject.toml", "pyproject.toml"
        )
        has_setup = self.check_file_exists(
            self.project_dir / "setup.py", "setup.py (optional)"
        )

        if not has_pyproject and not has_setup:
            self.warnings.append("No Python project configuration found")

        # Check for source directory
        src_dir = self.project_dir / "src"
        if src_dir.exists():
            self.check_directory_exists(src_dir, "src directory")

    def validate_logs(self) -> None:
        """Validate build logs exist."""
        print("\n=== Validating Build Logs ===\n")

        logs_dir = self.project_dir / "logs"
        if self.check_directory_exists(logs_dir, "logs directory"):
            # Check for at least one log file
            log_files = list(logs_dir.glob("*.log"))
            if log_files:
                print(f"✓ Found {len(log_files)} log file(s)")
                self.checks_passed += 1

                # Check latest log is not empty
                latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
                self.check_file_not_empty(latest_log, "Latest log file")
            else:
                warning = "⚠ No log files found in logs directory"
                print(warning)
                self.warnings.append(warning)

    def validate_claude_config(self) -> None:
        """Validate Claude Code configuration."""
        print("\n=== Validating Claude Code Configuration ===\n")

        # Check for .claude directory
        claude_dir = self.project_dir / ".claude"
        if self.check_directory_exists(claude_dir, ".claude directory"):
            # Check for commands directory
            commands_dir = claude_dir / "commands"
            if self.check_directory_exists(commands_dir, ".claude/commands directory"):
                # Check for at least one command file
                command_files = list(commands_dir.glob("*.md"))
                if command_files:
                    print(f"✓ Found {len(command_files)} command file(s)")
                    self.checks_passed += 1
                else:
                    self.warnings.append("No command files found in .claude/commands")

    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Checks passed: {self.checks_passed}")
        print(f"Checks failed: {self.checks_failed}")
        print(f"Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        print("\n" + "=" * 60)

        if self.checks_failed == 0:
            print("✅ VALIDATION PASSED")
            print("=" * 60)
            return True
        else:
            print("❌ VALIDATION FAILED")
            print("=" * 60)
            return False

    def run(self) -> bool:
        """Run all validation checks.

        Returns:
            True if all checks passed, False otherwise
        """
        print(f"\nValidating build at: {self.project_dir}\n")

        self.validate_basic_structure()
        self.validate_python_project()
        self.validate_logs()
        self.validate_claude_config()

        return self.print_summary()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if len(sys.argv) != 2:
        print("Usage: python validate_build.py <project_directory>")
        print("\nExample:")
        print("  python validate_build.py ./test_output")
        return 1

    project_dir = Path(sys.argv[1])

    validator = BuildValidator(project_dir)
    success = validator.run()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
