#!/usr/bin/env python3
"""Smoke test for Claude Code Builder v2.

This test verifies that all v2 components can be imported and basic
initialization works. Does NOT make API calls (no API key required).
"""

import sys
from pathlib import Path


def test_imports() -> bool:
    """Test all v2 imports work."""
    print("Testing v2 imports...")

    try:
        # Core imports
        from claude_code_builder_v2.core.config import (
            BuildConfig,
            ExecutorConfig,
            LoggingConfig,
            MCPConfig,
        )
        from claude_code_builder_v2.core.enums import (
            AgentType,
            BuildStatus,
            PhaseStatus,
            PermissionMode,
        )
        from claude_code_builder_v2.core.exceptions import (
            BuildError,
            SpecificationError,
            PhaseError,
        )
        from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
        from claude_code_builder_v2.core.models import (
            ExecutionContext,
            AgentResponse,
            PhaseResult,
            BuildMetrics,
        )

        # Agent imports
        from claude_code_builder_v2.agents import (
            BaseAgent,
            SpecAnalyzer,
            TaskGenerator,
            InstructionBuilder,
            DocumentationAgent,
            TestGenerator,  # Critical: was missing!
            CodeReviewer,
            AcceptanceGenerator,
        )

        # Builder imports
        from claude_code_builder_v2.builders import (
            ClaudeMdBuilder,
            CommandBuilder,
            DocumentationBuilder,
        )

        # SDK imports
        from claude_code_builder_v2.sdk.client_manager import SDKClientManager
        from claude_code_builder_v2.sdk.cost_tracker import CostTracker
        from claude_code_builder_v2.sdk.hook_manager import SDKHookManager
        from claude_code_builder_v2.sdk.progress_reporter import StreamingProgressReporter
        from claude_code_builder_v2.sdk.tool_registry import SDKToolRegistry

        # MCP imports
        from claude_code_builder_v2.mcp.integration import SDKMCPIntegration

        # Executor imports
        from claude_code_builder_v2.executor.build_orchestrator import (
            SDKBuildOrchestrator,
        )
        from claude_code_builder_v2.executor.phase_executor import SDKPhaseExecutor

        # CLI imports
        from claude_code_builder_v2.cli.main import cli

        print("✓ All v2 imports successful")
        return True

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_basic_initialization() -> bool:
    """Test basic component initialization."""
    print("\nTesting basic initialization...")

    try:
        from claude_code_builder_v2.core.config import BuildConfig, LoggingConfig
        from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
        from claude_code_builder_v2.builders import (
            ClaudeMdBuilder,
            CommandBuilder,
            DocumentationBuilder,
        )

        # Test config creation
        build_config = BuildConfig(max_cost=10.0)
        logging_config = LoggingConfig(level="INFO")
        print("✓ Config objects created")

        # Test logger creation
        logger = ComprehensiveLogger(project_dir=Path("/tmp/test"), config=logging_config)
        print("✓ Logger created")

        # Test builder creation
        claude_md = ClaudeMdBuilder(logger=logger)
        command = CommandBuilder(logger=logger)
        docs = DocumentationBuilder(logger=logger)
        print("✓ Builders created")

        return True

    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_cli_commands() -> bool:
    """Test CLI commands are available."""
    print("\nTesting CLI commands...")

    try:
        from claude_code_builder_v2.cli.main import cli

        # Get command names
        command_names = [cmd.name for cmd in cli.commands.values()]

        expected_commands = {"build", "init", "resume", "status", "logs"}
        found_commands = set(command_names)

        if expected_commands.issubset(found_commands):
            print(f"✓ All expected CLI commands found: {sorted(found_commands)}")
            return True
        else:
            missing = expected_commands - found_commands
            print(f"✗ Missing CLI commands: {missing}")
            return False

    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False


def test_sdk_imports() -> bool:
    """Test real Claude Agent SDK imports."""
    print("\nTesting real Claude Agent SDK...")

    try:
        from claude_agent_sdk import (
            AssistantMessage,
            ClaudeAgentOptions,
            ClaudeSDKClient,
            UserMessage,
            query,
            tool,
            create_sdk_mcp_server,
        )

        print("✓ Real Claude Agent SDK imports successful")
        print("  - AssistantMessage, UserMessage, ClaudeSDKClient available")
        print("  - query function available")
        print("  - tool decorator available")
        print("  - create_sdk_mcp_server available")
        return True

    except ImportError as e:
        print(f"✗ SDK import failed: {e}")
        return False


def test_no_mocks() -> bool:
    """Verify no mock implementations in v2."""
    print("\nVerifying no mocks in v2...")

    try:
        # Use grep-like search instead
        v2_src = Path("/home/user/claude-code-builder/src/claude_code_builder_v2")

        if not v2_src.exists():
            print(f"✗ v2 source directory not found: {v2_src}")
            return False

        # Search for actual mock imports (not just mentions in docs)
        mock_found = False
        for file_path in v2_src.rglob("*.py"):
            content = file_path.read_text()
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                # Look for actual import statements with mock
                if ("from" in line or "import" in line) and "mock" in line.lower():
                    # Check if it's actually an import line (not in a string or comment)
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        continue
                    # Check for actual mock imports
                    if (
                        "from unittest.mock" in line
                        or "import mock" in line
                        or "from mock import" in line
                    ):
                        print(f"  Found mock import in: {file_path}:{line_num}")
                        print(f"    {line}")
                        mock_found = True

        if not mock_found:
            print("✓ No mock implementations found in v2")
            return True
        else:
            print("✗ Mock imports found in v2")
            return False

    except Exception as e:
        print(f"✗ Mock check failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> int:
    """Run all smoke tests.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    print("Claude Code Builder v2 - Smoke Test")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Basic Initialization", test_basic_initialization),
        ("CLI Commands", test_cli_commands),
        ("Real Claude Agent SDK", test_sdk_imports),
        ("No Mocks", test_no_mocks),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("SMOKE TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print("=" * 60)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n✅ ALL SMOKE TESTS PASSED - v2 is functional!")
        return 0
    else:
        print("\n❌ SOME SMOKE TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
