"""Configuration classes for Claude Code Builder v2."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: str = "INFO"
    json_logs: bool = False
    log_to_file: bool = True
    log_to_console: bool = True
    max_log_size_mb: int = 100


class ExecutorConfig(BaseModel):
    """Configuration for SDK executor."""

    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7
    max_turns: Optional[int] = 10
    system_prompt: Optional[str] = None
    allowed_tools: List[str] = Field(default_factory=list)
    permission_mode: str = "auto"
    cwd: Optional[str] = None
    timeout_seconds: Optional[int] = 300


class MCPConfig(BaseModel):
    """Configuration for MCP servers."""

    enabled: bool = True
    servers: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    timeout: int = 30

    @classmethod
    def default(cls) -> "MCPConfig":
        """Create default MCP configuration.

        Returns:
            MCPConfig with default servers
        """
        return cls(
            enabled=True,
            servers={
                "filesystem": {
                    "enabled": True,
                    "tools": ["read_file", "write_file", "list_directory"],
                },
                "memory": {
                    "enabled": True,
                    "tools": ["create_entity", "search_nodes"],
                },
                "git": {
                    "enabled": True,
                    "tools": ["git_status", "git_commit", "git_log"],
                },
            },
        )


class BuildConfig(BaseModel):
    """Configuration for build orchestration."""

    max_cost: float = 10.0
    max_duration_minutes: Optional[int] = None
    resume_enabled: bool = True
    checkpoint_interval: int = 5
    default_executor_config: Optional[ExecutorConfig] = Field(
        default_factory=ExecutorConfig
    )
    default_logging_config: Optional[LoggingConfig] = Field(
        default_factory=LoggingConfig
    )
    default_mcp_config: Optional[MCPConfig] = Field(default_factory=MCPConfig.default)
    output_dir: Optional[Path] = None
    spec_path: Optional[Path] = None
