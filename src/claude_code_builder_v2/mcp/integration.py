"""SDK-based MCP integration for Claude Code Builder v2.

This module provides MCP server configuration and integration with the Claude Agent SDK.
The SDK handles MCP server connections internally, so this module focuses on configuration
and tool integration rather than subprocess management.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from claude_code_builder_v2.core.config import MCPConfig, MCPServerConfig
from claude_code_builder_v2.core.enums import MCPServer
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
from claude_code_builder_v2.sdk import ToolRegistry


class SDKMCPIntegration:
    """Manages MCP server configuration for SDK integration.

    The Claude Agent SDK handles MCP server connections internally.
    This class provides configuration and tool registration.
    """

    def __init__(
        self,
        mcp_config: MCPConfig,
        logger: ComprehensiveLogger,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        """Initialize SDK MCP integration.

        Args:
            mcp_config: MCP configuration
            logger: Logger instance
            tool_registry: Optional tool registry for MCP tools
        """
        self.mcp_config = mcp_config
        self.logger = logger
        self.tool_registry = tool_registry
        self.active_servers: Dict[str, MCPServerConfig] = {}

    def get_server_config(self, server: MCPServer) -> Optional[MCPServerConfig]:
        """Get configuration for an MCP server.

        Args:
            server: MCP server type

        Returns:
            Server configuration or None
        """
        for config in self.mcp_config.servers:
            if config.server_type == server:
                return config
        return None

    def get_servers_for_phase(self, phase_name: str) -> List[MCPServerConfig]:
        """Get MCP servers required for a phase.

        Args:
            phase_name: Name of the phase

        Returns:
            List of server configurations
        """
        # Default servers for all phases
        default_servers = [
            MCPServer.FILESYSTEM,
            MCPServer.MEMORY,
        ]

        # Phase-specific servers
        phase_servers = {
            "analysis": [MCPServer.CONTEXT7, MCPServer.SEQUENTIAL_THINKING],
            "planning": [MCPServer.CONTEXT7, MCPServer.SEQUENTIAL_THINKING],
            "implementation": [MCPServer.FILESYSTEM, MCPServer.GIT],
            "testing": [MCPServer.FILESYSTEM],
            "documentation": [MCPServer.FILESYSTEM, MCPServer.CONTEXT7],
        }

        # Combine default and phase-specific
        required_servers = set(default_servers)
        phase_lower = phase_name.lower()

        for key, servers in phase_servers.items():
            if key in phase_lower:
                required_servers.update(servers)

        # Get configurations
        configs = []
        for server in required_servers:
            config = self.get_server_config(server)
            if config:
                configs.append(config)
            else:
                self.logger.print_warning(
                    f"No configuration found for MCP server: {server.value}"
                )

        return configs

    def prepare_mcp_options(
        self,
        servers: List[MCPServerConfig],
    ) -> Dict[str, Any]:
        """Prepare MCP options for SDK ClaudeAgentOptions.

        Args:
            servers: List of server configurations

        Returns:
            Dictionary of MCP options for SDK
        """
        mcp_servers = {}

        for config in servers:
            server_name = config.server_type.value

            # Build server configuration for SDK
            mcp_servers[server_name] = {
                "command": config.command,
                "args": config.args,
                "env": config.env or {},
            }

            self.logger.logger.info(
                "mcp_server_configured",
                server=server_name,
                command=config.command,
            )

        return {"mcp_servers": mcp_servers}

    def get_filesystem_tools(self) -> List[str]:
        """Get list of filesystem MCP tools.

        Returns:
            List of tool names
        """
        return [
            "read_file",
            "write_file",
            "list_directory",
            "create_directory",
            "move_file",
            "delete_file",
        ]

    def get_memory_tools(self) -> List[str]:
        """Get list of memory MCP tools.

        Returns:
            List of tool names
        """
        return [
            "create_entity",
            "add_observation",
            "search_nodes",
            "get_entity",
            "delete_entity",
        ]

    def get_context7_tools(self) -> List[str]:
        """Get list of context7 MCP tools.

        Returns:
            List of tool names
        """
        return [
            "search_docs",
            "get_documentation",
            "search_packages",
        ]

    def get_git_tools(self) -> List[str]:
        """Get list of git MCP tools.

        Returns:
            List of tool names
        """
        return [
            "git_status",
            "git_diff",
            "git_commit",
            "git_log",
            "git_branch",
        ]

    def get_sequential_thinking_tools(self) -> List[str]:
        """Get list of sequential thinking MCP tools.

        Returns:
            List of tool names
        """
        return [
            "think_step",
            "analyze_problem",
            "decompose_task",
        ]

    def get_all_tools_for_servers(
        self,
        servers: List[MCPServerConfig],
    ) -> List[str]:
        """Get all tool names for given servers.

        Args:
            servers: List of server configurations

        Returns:
            List of all tool names
        """
        tools = []

        for config in servers:
            server_type = config.server_type

            if server_type == MCPServer.FILESYSTEM:
                tools.extend(self.get_filesystem_tools())
            elif server_type == MCPServer.MEMORY:
                tools.extend(self.get_memory_tools())
            elif server_type == MCPServer.CONTEXT7:
                tools.extend(self.get_context7_tools())
            elif server_type == MCPServer.GIT:
                tools.extend(self.get_git_tools())
            elif server_type == MCPServer.SEQUENTIAL_THINKING:
                tools.extend(self.get_sequential_thinking_tools())

        return tools

    async def validate_servers(
        self,
        servers: List[MCPServerConfig],
    ) -> Dict[str, bool]:
        """Validate that MCP servers are configured correctly.

        Args:
            servers: List of server configurations

        Returns:
            Dictionary of server name to validation status
        """
        results = {}

        for config in servers:
            server_name = config.server_type.value

            # Basic validation
            is_valid = bool(config.command and config.args)

            results[server_name] = is_valid

            if is_valid:
                self.logger.logger.info(
                    "mcp_server_validated",
                    server=server_name,
                    status="valid",
                )
            else:
                self.logger.print_error(
                    f"MCP server configuration invalid: {server_name}"
                )

        return results


__all__ = ["SDKMCPIntegration"]
