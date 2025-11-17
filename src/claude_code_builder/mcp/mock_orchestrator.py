"""Mock MCP orchestrator for testing without real MCP servers.

DEPRECATED: This module is part of v1 which uses mock implementations.
Please use claude_code_builder_v2 which uses the real Claude Agent SDK.

v2 Features:
- Real Claude Agent SDK integration
- No mocks - all real implementations
- MCP via create_sdk_mcp_server
- Async throughout
- Complete CLI with all commands

To use v2:
    from claude_code_builder_v2.cli.main import cli
    # or
    poetry run claude-code-builder --help
"""

import warnings
from pathlib import Path

warnings.warn(
    "claude_code_builder.mcp.mock_orchestrator is deprecated. "
    "Use claude_code_builder_v2 with real Claude Agent SDK instead.",
    DeprecationWarning,
    stacklevel=2,
)
from typing import Any, Dict, List, Optional

from claude_code_builder.core.config import MCPConfig
from claude_code_builder.core.enums import MCPCheckpoint, MCPServer
from claude_code_builder.core.logging_system import ComprehensiveLogger


class MockMCPOrchestrator:
    """Mock implementation of MCPOrchestrator for testing."""
    
    def __init__(
        self,
        mcp_config: MCPConfig,
        project_dir: Path,
        logger: ComprehensiveLogger,
    ) -> None:
        """Initialize the mock orchestrator."""
        self.mcp_config = mcp_config
        self.project_dir = project_dir
        self.logger = logger
        self.checkpoint_manager = self
        self.server_calls = {}
        self.checkpoint_usage = {}
        
        # Mock clients
        self.filesystem = self
        self.memory = self
        self.context7 = self
        self.git = self
        self.github = self
        self.sequential_thinking = self
        self.taskmaster = self
        
        # Mock server manager
        self.server_manager = self
        self.connections = {}

    async def initialize(self) -> None:
        """Initialize the mock orchestrator."""
        self.logger.print_info("Initializing mock MCP orchestrator (no real servers)")

    async def shutdown(self) -> None:
        """Shutdown the mock orchestrator."""
        self.logger.print_info("Shutting down mock MCP orchestrator")

    async def ensure_server_running(self, server: MCPServer) -> None:
        """Mock ensure server running."""
        pass

    async def record_checkpoint(
        self,
        checkpoint: MCPCheckpoint,
        servers: List[MCPServer],
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Mock record checkpoint."""
        self.checkpoint_usage[checkpoint] = servers

    async def call_server(
        self,
        server: MCPServer,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Mock server call."""
        self.server_calls[server] = self.server_calls.get(server, 0) + 1
        return {"status": "success", "data": {}}

    # Mock filesystem methods
    async def read_file(self, path: str) -> str:
        """Mock read file."""
        file_path = Path(path)
        if file_path.exists():
            return file_path.read_text()
        return ""

    async def write_file(self, path: str, content: str) -> None:
        """Mock write file."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    async def search_files(
        self,
        path: str,
        pattern: str,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[str]:
        """Mock search files."""
        return []

    async def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """Mock list directory."""
        return []

    # Mock memory methods
    async def create_entities(self, entities: List[Dict[str, Any]]) -> None:
        """Mock create entities."""
        pass

    async def search_nodes(self, query: str) -> List[Dict[str, Any]]:
        """Mock search nodes."""
        return []

    # Mock context7 methods
    async def resolve_library_id(self, library: str) -> Dict[str, Any]:
        """Mock resolve library ID."""
        return {"id": library}

    async def get_library_docs(
        self,
        library_id: str,
        topic: Optional[str] = None,
    ) -> str:
        """Mock get library docs."""
        return f"Mock documentation for {library_id}"

    # Mock sequential thinking
    async def solve_problem(
        self,
        problem: str,
        estimated_steps: int = 5,
    ) -> List[Dict[str, Any]]:
        """Mock solve problem."""
        return [
            {"thought": f"Mock thought {i}", "step": i}
            for i in range(estimated_steps)
        ]

    # Mock git methods
    async def add(self, repo_path: str, files: List[str]) -> None:
        """Mock git add."""
        pass

    async def commit(self, repo_path: str, message: str) -> None:
        """Mock git commit."""
        pass

    # Mock checkpoint manager methods
    async def export_checkpoint_report(self, output_file: Path) -> None:
        """Mock export checkpoint report."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("{}")

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get mock usage stats."""
        return {
            "total_calls": sum(self.server_calls.values()),
            "calls_by_server": dict(self.server_calls),
            "checkpoints_recorded": len(self.checkpoint_usage),
            "active_connections": [],
        }

    async def export_usage_report(self, output_dir: Path) -> Path:
        """Export mock usage report."""
        report_file = output_dir / "mcp_usage_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        report = {
            "timestamp": "2025-06-12T15:00:00",
            "project_dir": str(self.project_dir),
            "usage_stats": self.get_usage_stats(),
            "mock": True,
        }
        
        report_file.write_text(json.dumps(report, indent=2))
        return report_file


__all__ = ["MockMCPOrchestrator"]