#!/usr/bin/env python3
"""
CCB PostToolUse Hook

Blocks mock patterns in test files (NO MOCKS enforcement).
Fires after Write/Edit/MultiEdit operations.
"""

import json
import re
import sys
from pathlib import Path


# Mock patterns to detect and block
MOCK_PATTERNS = [
    r'jest\.mock\(',
    r'jest\.spyOn\(',
    r'jest\.fn\(',
    r'from\s+unittest\.mock\s+import',
    r'@patch\(',
    r'@mock\.patch',
    r'import\s+mock\b',
    r'sinon\.stub\(',
    r'sinon\.mock\(',
    r'sinon\.spy\(',
    r'MockedFunction',
    r'MockedClass',
    r'vi\.mock\(',
    r'vi\.spyOn\(',
    r'testify/mock',
    r'gomock',
    r'Mockito',
    r'EasyMock',
    r'PowerMock',
    r'mockall',
    r'TestDouble',
    r'createMock',
]


def is_test_file(file_path: str) -> bool:
    """Check if file is a test file."""
    path = Path(file_path)
    name = path.name.lower()
    parts = path.parts

    # Test file patterns
    if any([
        name.startswith('test_'),
        name.endswith('_test.py'),
        name.endswith('.test.ts'),
        name.endswith('.test.js'),
        name.endswith('.spec.ts'),
        name.endswith('.spec.js'),
        name.endswith('_spec.rb'),
        name.endswith('_test.go'),
        'test' in parts,
        '__tests__' in parts,
        'tests' in parts,
        'spec' in parts,
    ]):
        return True

    return False


def detect_mock_patterns(content: str) -> list:
    """Detect mock patterns in content."""
    violations = []

    for i, line in enumerate(content.split('\n'), 1):
        for pattern in MOCK_PATTERNS:
            if re.search(pattern, line):
                violations.append({
                    'line': i,
                    'pattern': pattern,
                    'content': line.strip()
                })

    return violations


def get_alternatives(pattern: str) -> str:
    """Get functional testing alternatives for detected pattern."""
    alternatives = {
        'jest.mock': 'Puppeteer MCP for real browser testing',
        'unittest.mock': 'testcontainers for real database/services',
        'sinon': 'Real HTTP requests to test server',
        'Mockito': 'Real dependencies via dependency injection',
        'vi.mock': 'Vitest with real integrations',
    }

    for key, alt in alternatives.items():
        if key in pattern:
            return alt

    return 'Real dependencies via MCP integration (Puppeteer, testcontainers, etc.)'


def main():
    """Check for mock patterns and block if found."""
    try:
        # Read hook input
        hook_input = json.load(sys.stdin)

        # Get tool name and file path
        tool_name = hook_input.get('tool', '')
        tool_params = hook_input.get('parameters', {})

        # Only check Write/Edit operations
        if tool_name not in ['Write', 'Edit', 'MultiEdit']:
            return

        # Get file path
        file_path = tool_params.get('file_path', '')
        if not file_path:
            return

        # Only check test files
        if not is_test_file(file_path):
            return

        # Get content
        if tool_name == 'Write':
            content = tool_params.get('content', '')
        elif tool_name == 'Edit':
            content = tool_params.get('new_string', '')
        else:
            return  # MultiEdit not yet supported

        # Detect mock patterns
        violations = detect_mock_patterns(content)

        # If mocks detected, BLOCK operation
        if violations:
            first_violation = violations[0]
            pattern = first_violation['pattern']
            line = first_violation['line']
            alternative = get_alternatives(pattern)

            # Output block decision
            response = {
                "decision": "block",
                "reason": f"""Mock pattern detected in {file_path}

**Violation**: Line {line} contains '{pattern}'

**CCB enforces functional testing with REAL dependencies (NO MOCKS).**

Rationale:
- Mock-based tests create false confidence
- Integration bugs hidden by mocked interfaces
- Production failures not caught by mocked tests
- 73% more bugs caught with real dependencies

**Alternative**: {alternative}

**References**:
- .claude/core/testing-philosophy.md
- .claude/core/ccb-principles.md (Law 2: NO MOCKS)
- .claude/skills/functional-testing/SKILL.md

To fix: Rewrite test using REAL dependencies:
1. Use testcontainers for databases
2. Use Puppeteer MCP for browser testing
3. Use real test servers for API testing
4. Use iOS Simulator MCP for mobile testing

**This operation is BLOCKED.**"""
            }

            print(json.dumps(response))
            sys.exit(1)  # Block operation

        # No mocks detected, allow operation
        # (no output = allow)

    except Exception as e:
        # Log error but don't block operation
        print(f"⚠️  CCB post_tool_use warning: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
