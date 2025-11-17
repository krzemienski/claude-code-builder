"""MCP integration using Claude SDK."""

from typing import Any, Dict, List

from claude_agent_sdk import create_sdk_mcp_server

from claude_code_builder_v2.core.config import MCPConfig
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class SDKMCPIntegration:
    """Integrates MCP servers using Claude SDK."""

    def __init__(
        self,
        config: MCPConfig,
        logger: ComprehensiveLogger,
    ) -> None:
        """Initialize MCP integration.

        Args:
            config: MCP configuration
            logger: Comprehensive logger
        """
        self.config = config
        self.logger = logger
        self.servers: Dict[str, Any] = {}

    def create_filesystem_server(self) -> Any:
        """Create in-process filesystem MCP server.

        Returns:
            MCP server instance
        """
        try:
            # Use SDK's create_sdk_mcp_server for in-process MCP
            server = create_sdk_mcp_server(
                name="filesystem",
                tools=["read_file", "write_file", "list_directory", "search_files"],
            )

            self.servers["filesystem"] = server

            self.logger.info(
                "mcp_server_created",
                msg="Created filesystem MCP server",
                server="filesystem",
            )

            return server

        except Exception as e:
            self.logger.error(
                "mcp_server_error",
                msg=f"Failed to create filesystem server: {e}",
                error=str(e),
            )
            raise

    def create_memory_server(self) -> Any:
        """Create in-process memory MCP server.

        Returns:
            MCP server instance
        """
        try:
            server = create_sdk_mcp_server(
                name="memory",
                tools=["create_entity", "search_nodes", "open_node", "delete_node"],
            )

            self.servers["memory"] = server

            self.logger.info(
                "mcp_server_created",
                msg="Created memory MCP server",
                server="memory",
            )

            return server

        except Exception as e:
            self.logger.error(
                "mcp_server_error",
                msg=f"Failed to create memory server: {e}",
                error=str(e),
            )
            raise

    def create_git_server(self) -> Any:
        """Create in-process git MCP server.

        Returns:
            MCP server instance
        """
        try:
            server = create_sdk_mcp_server(
                name="git",
                tools=["git_status", "git_commit", "git_log", "git_diff"],
            )

            self.servers["git"] = server

            self.logger.info(
                "mcp_server_created",
                msg="Created git MCP server",
                server="git",
            )

            return server

        except Exception as e:
            self.logger.error(
                "mcp_server_error",
                msg=f"Failed to create git server: {e}",
                error=str(e),
            )
            raise

    def initialize_all_servers(self) -> None:
        """Initialize all configured MCP servers."""
        if not self.config.enabled:
            self.logger.info(
                "mcp_disabled",
                msg="MCP integration is disabled",
            )
            return

        for server_name, server_config in self.config.servers.items():
            if not server_config.get("enabled", True):
                continue

            try:
                if server_name == "filesystem":
                    self.create_filesystem_server()
                elif server_name == "memory":
                    self.create_memory_server()
                elif server_name == "git":
                    self.create_git_server()
                else:
                    self.logger.warning(
                        "unknown_mcp_server",
                        msg=f"Unknown MCP server: {server_name}",
                        server=server_name,
                    )

            except Exception as e:
                self.logger.error(
                    "mcp_init_error",
                    msg=f"Failed to initialize server {server_name}: {e}",
                    server=server_name,
                    error=str(e),
                )

        self.logger.info(
            "mcp_init_complete",
            msg="MCP initialization complete",
            servers_initialized=len(self.servers),
        )

    def get_server(self, name: str) -> Any:
        """Get MCP server by name.

        Args:
            name: Server name

        Returns:
            MCP server instance or None
        """
        return self.servers.get(name)

    def get_all_servers(self) -> Dict[str, Any]:
        """Get all initialized servers.

        Returns:
            Dictionary of server name -> instance
        """
        return self.servers.copy()

    def get_filesystem_tools(self) -> List[str]:
        """Get filesystem tools list.

        Returns:
            List of tool names
        """
        return ["read_file", "write_file", "list_directory", "search_files"]

    def get_memory_tools(self) -> List[str]:
        """Get memory tools list.

        Returns:
            List of tool names
        """
        return ["create_entity", "search_nodes", "open_node", "delete_node"]

    def get_git_tools(self) -> List[str]:
        """Get git tools list.

        Returns:
            List of tool names
        """
        return ["git_status", "git_commit", "git_log", "git_diff"]

    def get_all_tools(self) -> List[str]:
        """Get all available tools from all servers.

        Returns:
            List of all tool names
        """
        tools = []
        tools.extend(self.get_filesystem_tools())
        tools.extend(self.get_memory_tools())
        tools.extend(self.get_git_tools())
        return tools
