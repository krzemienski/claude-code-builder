#!/bin/bash
# CCB SessionStart Hook
# Loads ccb-principles.md on session startup

# Get plugin root directory
PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Display initialization message
echo ""
echo "🏗️  ======================================"
echo "   Claude Code Builder v3 Loaded"
echo "   Specification-First Development Active"
echo "========================================"
echo ""
echo "Framework Principles:"
echo "✓ NO MOCKS - Functional testing only"
echo "✓ Quantitative analysis required"
echo "✓ State persisted via Serena MCP"
echo "✓ Spec-before-code enforcement"
echo ""

# Load CCB principles (core reference document)
cat "${PLUGIN_ROOT}/core/ccb-principles.md"

echo ""
echo "========================================"
echo "CCB v3 Ready - Use /ccb:init to start"
echo "========================================"
echo ""
