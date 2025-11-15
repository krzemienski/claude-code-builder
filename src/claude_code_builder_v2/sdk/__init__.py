"""SDK Integration Layer for CCB v2."""

from claude_code_builder_v2.sdk.client_manager import (
    SDKClientManager,
    ClaudeAgentOptions,
)
from claude_code_builder_v2.sdk.tool_registry import ToolRegistry, tool
from claude_code_builder_v2.sdk.hook_registry import HookRegistry
from claude_code_builder_v2.sdk.subagent_factory import SubagentFactory, AgentDefinition

__all__ = [
    "SDKClientManager",
    "ClaudeAgentOptions",
    "ToolRegistry",
    "tool",
    "HookRegistry",
    "SubagentFactory",
    "AgentDefinition",
]
