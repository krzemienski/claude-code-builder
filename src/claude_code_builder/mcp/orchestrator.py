"""MCP Server orchestration and management."""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aiofiles
from pydantic import Field

from claude_code_builder.core.base_model import BaseModel
from claude_code_builder.core.config import MCPConfig, MCPServerConfig
from claude_code_builder.core.enums import MCPCheckpoint, MCPServer
from claude_code_builder.core.exceptions import MCPServerError
from claude_code_builder.core.logging_system import ComprehensiveLogger


class MCPConnection(BaseModel):
    """Represents a connection to an MCP server."""
    
    server: MCPServer
    config: MCPServerConfig
    process: Optional[Any] = None  # subprocess.Popen
    is_connected: bool = False
    connection_time: Optional[datetime] = None
    last_used: Optional[datetime] = None
    error_count: int = 0
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


class MCPServerManager:
    """Manages individual MCP server connections."""
    
    def __init__(
        self,
        mcp_config: MCPConfig,
        logger: ComprehensiveLogger,
        project_dir: Optional[Path] = None,
    ) -> None:
        """Initialize the server manager."""
        self.mcp_config = mcp_config
        self.logger = logger
        self.project_dir = project_dir or Path.cwd()
        self.connections: Dict[MCPServer, MCPConnection] = {}
        self.startup_timeout = 30  # seconds
        self.health_check_interval = 60  # seconds
        self._health_check_task: Optional[asyncio.Task] = None

    async def start_server(self, server: MCPServer) -> MCPConnection:
        """Start an MCP server."""
        if server in self.connections and self.connections[server].is_connected:
            return self.connections[server]
        
        config = self._get_server_config(server)
        if not config:
            raise MCPServerError(
                f"No configuration found for server: {server.value}",
                server.value,
            )
        
        self.logger.print_info(f"Starting MCP server: {server.value}")
        
        try:
            # Build command
            cmd = self._build_server_command(config, server)
            
            # Start process
            process = await self._start_process(cmd, config)
            
            # Check if process started successfully
            await asyncio.sleep(0.5)  # Give it a moment to start
            if process.poll() is not None:
                # Process already exited
                stdout, stderr = process.communicate()
                error_msg = f"Process exited immediately. stdout: {stdout}, stderr: {stderr}"
                self.logger.print_error(error_msg)
                raise Exception(error_msg)
            
            # Create connection
            connection = MCPConnection(
                server=server,
                config=config,
                process=process,
                is_connected=True,
                connection_time=datetime.utcnow(),
            )
            
            # Store connection before waiting
            self.connections[server] = connection
            
            # Wait for server to be ready
            await self._wait_for_server_ready(connection)
            
            self.logger.print_success(f"MCP server started: {server.value}")
            
            return connection
            
        except Exception as e:
            self.logger.print_error(f"Failed to start MCP server {server.value}: {e}")
            import traceback
            self.logger.print_error(f"Traceback: {traceback.format_exc()}")
            raise MCPServerError(
                f"Failed to start server: {str(e)}",
                server.value,
                details={"error": str(e), "traceback": traceback.format_exc()},
            )

    async def stop_server(self, server: MCPServer) -> None:
        """Stop an MCP server."""
        if server not in self.connections:
            return
        
        connection = self.connections[server]
        if connection.process:
            try:
                connection.process.terminate()
                await asyncio.sleep(0.5)
                
                if connection.process.poll() is None:
                    connection.process.kill()
                    
            except Exception as e:
                self.logger.print_warning(f"Error stopping server {server.value}: {e}")
        
        connection.is_connected = False
        del self.connections[server]
        
        self.logger.print_info(f"MCP server stopped: {server.value}")

    async def restart_server(self, server: MCPServer) -> MCPConnection:
        """Restart an MCP server."""
        await self.stop_server(server)
        await asyncio.sleep(1)
        return await self.start_server(server)

    async def check_server_health(self, server: MCPServer) -> bool:
        """Check if a server is healthy."""
        if server not in self.connections:
            return False
        
        connection = self.connections[server]
        
        if not connection.is_connected:
            return False
        
        if connection.process and connection.process.poll() is not None:
            # Process has terminated
            connection.is_connected = False
            return False
        
        # Server-specific health checks
        try:
            if server == MCPServer.FILESYSTEM:
                # Check if can list directories
                return await self._check_filesystem_health()
            elif server == MCPServer.MEMORY:
                # Check if can read graph
                return await self._check_memory_health()
            # Add more server-specific checks
            
            return True
            
        except Exception:
            return False

    async def start_health_monitoring(self) -> None:
        """Start background health monitoring."""
        if self._health_check_task:
            return
        
        self._health_check_task = asyncio.create_task(self._health_monitor_loop())

    async def stop_health_monitoring(self) -> None:
        """Stop health monitoring."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None

    async def _health_monitor_loop(self) -> None:
        """Background health monitoring loop."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for server, connection in list(self.connections.items()):
                    if not await self.check_server_health(server):
                        self.logger.print_warning(
                            f"MCP server {server.value} is unhealthy, attempting restart"
                        )
                        
                        connection.error_count += 1
                        
                        if connection.error_count < 3:
                            await self.restart_server(server)
                        else:
                            self.logger.print_error(
                                f"MCP server {server.value} failed too many times, stopping"
                            )
                            await self.stop_server(server)
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.print_error(f"Health monitor error: {e}")

    def _get_server_config(self, server: MCPServer) -> Optional[MCPServerConfig]:
        """Get configuration for a server."""
        config_map = {
            MCPServer.FILESYSTEM: self.mcp_config.filesystem,
            MCPServer.MEMORY: self.mcp_config.memory,
            MCPServer.CONTEXT7: self.mcp_config.context7,
            MCPServer.GIT: self.mcp_config.git,
            MCPServer.GITHUB: self.mcp_config.github,
            MCPServer.SEQUENTIAL_THINKING: self.mcp_config.sequential_thinking,
            MCPServer.TASKMASTER: self.mcp_config.taskmaster,
        }
        
        return config_map.get(server)

    def _build_server_command(self, config: MCPServerConfig, server: MCPServer) -> List[str]:
        """Build command to start server."""
        cmd = [config.command]
        
        if config.args:
            cmd.extend(config.args)
        
        # Special handling for filesystem server - add project directory
        if server == MCPServer.FILESYSTEM and "@modelcontextprotocol/server-filesystem" in str(config.args):
            # Remove the placeholder "." if it exists
            if cmd[-1] == ".":
                cmd.pop()
            # Add the actual project directory
            cmd.append(str(self.project_dir))
        
        return cmd

    async def _start_process(
        self,
        cmd: List[str],
        config: MCPServerConfig,
    ) -> subprocess.Popen:
        """Start server process."""
        env = dict(os.environ)
        
        # Ensure node modules are in PATH
        if "npx" in cmd[0]:
            node_bin = Path(sys.prefix) / "bin"
            if node_bin.exists():
                env["PATH"] = f"{node_bin}:{env.get('PATH', '')}"
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            env=env,
        )
        
        return process

    async def _wait_for_server_ready(self, connection: MCPConnection) -> None:
        """Wait for server to be ready."""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < self.startup_timeout:
            if await self.check_server_health(connection.server):
                return
            
            await asyncio.sleep(0.5)
        
        # Debug: log the actual type and value
        server_info = f"Server type: {type(connection.server)}, value: {connection.server}"
        if hasattr(connection.server, 'value'):
            server_value = connection.server.value
        else:
            server_value = str(connection.server)
            
        raise MCPServerError(
            f"Server {server_value} failed to start within timeout",
            server_value,
        )

    async def _check_filesystem_health(self) -> bool:
        """Check filesystem server health."""
        # For now, just check if process is running
        connection = self.connections.get(MCPServer.FILESYSTEM)
        if connection and connection.process:
            # Check if process is still running
            return connection.process.poll() is None
        return False

    async def _check_memory_health(self) -> bool:
        """Check memory server health."""
        # For now, just check if process is running
        connection = self.connections.get(MCPServer.MEMORY)
        if connection and connection.process:
            # Check if process is still running
            return connection.process.poll() is None
        return False


class MCPOrchestrator:
    """Orchestrates all MCP server interactions."""
    
    def __init__(
        self,
        mcp_config: MCPConfig,
        project_dir: Path,
        logger: ComprehensiveLogger,
    ) -> None:
        """Initialize the orchestrator."""
        self.mcp_config = mcp_config
        self.project_dir = project_dir
        self.logger = logger
        self.server_manager = MCPServerManager(mcp_config, logger, project_dir)
        
        # Track usage
        self.checkpoint_usage: Dict[MCPCheckpoint, List[MCPServer]] = {}
        self.server_calls: Dict[MCPServer, int] = {}
        
        # Checkpoint manager will be set by BuildOrchestrator
        self.checkpoint_manager = None
        
        # Initialize clients
        self._init_clients()

    def _init_clients(self) -> None:
        """Initialize MCP clients."""
        from claude_code_builder.mcp.clients import (
            FilesystemClient,
            MemoryClient,
            Context7Client,
            GitClient,
            GithubClient,
            SequentialThinkingClient,
            TaskMasterClient,
        )
        
        self.filesystem = FilesystemClient(self)
        self.memory = MemoryClient(self)
        self.context7 = Context7Client(self)
        self.git = GitClient(self)
        self.github = GithubClient(self)
        self.sequential_thinking = SequentialThinkingClient(self)
        self.taskmaster = TaskMasterClient(self)

    async def initialize(self) -> None:
        """Initialize the orchestrator and start required servers."""
        self.logger.print_info("Initializing MCP orchestrator")
        
        # Start mandatory servers
        mandatory_servers = self._get_mandatory_servers()
        
        for server in mandatory_servers:
            try:
                await self.server_manager.start_server(server)
            except Exception as e:
                self.logger.print_error(f"Failed to start mandatory server {server.value}: {e}")
                raise
        
        # Start health monitoring
        await self.server_manager.start_health_monitoring()
        
        self.logger.print_success("MCP orchestrator initialized")

    async def shutdown(self) -> None:
        """Shutdown all MCP servers."""
        self.logger.print_info("Shutting down MCP orchestrator")
        
        # Stop health monitoring
        await self.server_manager.stop_health_monitoring()
        
        # Stop all servers
        for server in list(self.server_manager.connections.keys()):
            await self.server_manager.stop_server(server)
        
        self.logger.print_success("MCP orchestrator shutdown complete")

    async def ensure_server_running(self, server: MCPServer) -> None:
        """Ensure a server is running before use."""
        if server not in self.server_manager.connections:
            await self.server_manager.start_server(server)
        elif not await self.server_manager.check_server_health(server):
            await self.server_manager.restart_server(server)
        
        # Update last used time
        connection = self.server_manager.connections[server]
        connection.last_used = datetime.utcnow()

    async def record_checkpoint_usage(
        self,
        checkpoint: MCPCheckpoint,
        servers: List[MCPServer],
    ) -> None:
        """Record MCP usage at a checkpoint."""
        self.checkpoint_usage[checkpoint] = servers
        
        # Update call counts
        for server in servers:
            self.server_calls[server] = self.server_calls.get(server, 0) + 1
        
        # Log usage
        self.logger.logger.info(
            "mcp_checkpoint",
            checkpoint=checkpoint.value,
            servers=[s.value for s in servers],
        )

    def _get_mandatory_servers(self) -> List[MCPServer]:
        """Get list of mandatory servers."""
        mandatory = [MCPServer.FILESYSTEM, MCPServer.MEMORY]
        
        if self.mcp_config.require_all:
            # Add all configured servers
            if self.mcp_config.context7:
                mandatory.append(MCPServer.CONTEXT7)
            if self.mcp_config.git:
                mandatory.append(MCPServer.GIT)
            if self.mcp_config.github:
                mandatory.append(MCPServer.GITHUB)
            if self.mcp_config.sequential_thinking:
                mandatory.append(MCPServer.SEQUENTIAL_THINKING)
            if self.mcp_config.taskmaster:
                mandatory.append(MCPServer.TASKMASTER)
        
        return mandatory

    async def call_server(
        self,
        server: MCPServer,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a call to an MCP server."""
        await self.ensure_server_running(server)
        
        # Track the call
        self.server_calls[server] = self.server_calls.get(server, 0) + 1
        
        # In real implementation, would make actual MCP protocol call
        # For now, return mock response
        self.logger.logger.debug(
            "mcp_call",
            server=server.value,
            method=method,
            params=params,
        )
        
        return {"status": "success", "data": {}}

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get MCP usage statistics."""
        return {
            "total_calls": sum(self.server_calls.values()),
            "calls_by_server": dict(self.server_calls),
            "checkpoints_recorded": len(self.checkpoint_usage),
            "active_connections": [
                s.value for s, c in self.server_manager.connections.items()
                if c.is_connected
            ],
        }

    async def export_usage_report(self, output_dir: Path) -> Path:
        """Export detailed usage report."""
        report_file = output_dir / "mcp_usage_report.json"
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "project_dir": str(self.project_dir),
            "usage_stats": self.get_usage_stats(),
            "checkpoint_details": {
                cp.value: [s.value for s in servers]
                for cp, servers in self.checkpoint_usage.items()
            },
            "server_configurations": {
                server.value: {
                    "command": config.command,
                    "args": config.args,
                    "required": config.required,
                }
                for server, config in [
                    (MCPServer.FILESYSTEM, self.mcp_config.filesystem),
                    (MCPServer.MEMORY, self.mcp_config.memory),
                    (MCPServer.CONTEXT7, self.mcp_config.context7),
                    (MCPServer.GIT, self.mcp_config.git),
                    (MCPServer.GITHUB, self.mcp_config.github),
                    (MCPServer.SEQUENTIAL_THINKING, self.mcp_config.sequential_thinking),
                    (MCPServer.TASKMASTER, self.mcp_config.taskmaster),
                ]
                if config
            },
        }
        
        async with aiofiles.open(report_file, 'w') as f:
            await f.write(json.dumps(report, indent=2))
        
        return report_file


import os  # Add this import at the top


__all__ = [
    "MCPOrchestrator",
    "MCPConnection",
    "MCPServerManager",
]