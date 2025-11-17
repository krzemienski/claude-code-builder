"""Tool registry for Claude SDK custom tools."""

from typing import Any, Callable, Dict, List, Optional

from claude_agent_sdk import tool

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class SDKToolRegistry:
    """Registry for custom SDK tools using @tool decorator."""

    def __init__(self, logger: ComprehensiveLogger) -> None:
        """Initialize tool registry.

        Args:
            logger: Comprehensive logger
        """
        self.logger = logger
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        """Register a custom tool.

        Args:
            name: Tool name
            func: Tool function
            description: Tool description
            parameters: Optional parameter schema

        Returns:
            Decorated tool function
        """
        # Store metadata
        self.tool_metadata[name] = {
            "description": description,
            "parameters": parameters or {},
        }

        # Decorate with SDK @tool
        decorated_func = tool(func)

        # Store in registry
        self.tools[name] = decorated_func

        self.logger.info(
            "tool_registered",
            msg=f"Registered tool: {name}",
            tool_name=name,
        )

        return decorated_func

    def get_tool(self, name: str) -> Optional[Callable]:
        """Get tool by name.

        Args:
            name: Tool name

        Returns:
            Tool function or None
        """
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tools.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool metadata.

        Args:
            name: Tool name

        Returns:
            Tool metadata or None
        """
        return self.tool_metadata.get(name)

    def unregister_tool(self, name: str) -> None:
        """Unregister a tool.

        Args:
            name: Tool name
        """
        if name in self.tools:
            del self.tools[name]
            del self.tool_metadata[name]
            self.logger.info(
                "tool_unregistered",
                msg=f"Unregistered tool: {name}",
                tool_name=name,
            )

    def create_filesystem_tool(self) -> Callable:
        """Create filesystem tool using SDK @tool decorator.

        Returns:
            Filesystem tool function
        """

        @tool
        async def read_file(path: str) -> str:
            """Read file contents.

            Args:
                path: File path

            Returns:
                File contents
            """
            import aiofiles

            try:
                async with aiofiles.open(path, "r") as f:
                    content = await f.read()
                self.logger.debug(
                    "tool_read_file",
                    msg=f"Read file: {path}",
                    path=path,
                    size=len(content),
                )
                return content
            except Exception as e:
                self.logger.error(
                    "tool_read_file_error",
                    msg=f"Failed to read file: {e}",
                    path=path,
                    error=str(e),
                )
                raise

        self.register_tool(
            name="read_file",
            func=read_file,
            description="Read contents of a file",
            parameters={
                "path": {"type": "string", "description": "Path to file"}
            },
        )

        return read_file

    def create_shell_tool(self) -> Callable:
        """Create shell command tool using SDK @tool decorator.

        Returns:
            Shell tool function
        """

        @tool
        async def run_command(command: str) -> str:
            """Run shell command.

            Args:
                command: Shell command to run

            Returns:
                Command output
            """
            import asyncio

            try:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await proc.communicate()

                output = stdout.decode() + stderr.decode()

                self.logger.debug(
                    "tool_run_command",
                    msg=f"Ran command: {command}",
                    command=command,
                    output_length=len(output),
                )

                return output

            except Exception as e:
                self.logger.error(
                    "tool_run_command_error",
                    msg=f"Failed to run command: {e}",
                    command=command,
                    error=str(e),
                )
                raise

        self.register_tool(
            name="run_command",
            func=run_command,
            description="Run a shell command",
            parameters={
                "command": {"type": "string", "description": "Command to run"}
            },
        )

        return run_command

    def get_all_tools(self) -> Dict[str, Callable]:
        """Get all registered tools.

        Returns:
            Dictionary of tool name -> function
        """
        return self.tools.copy()
