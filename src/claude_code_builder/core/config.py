"""Configuration models and settings for Claude Code Builder."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from claude_code_builder.core.base_model import BaseModel
from claude_code_builder.core.enums import LogLevel, MCPServer, OutputFormat


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""

    command: str
    args: List[str] = Field(default_factory=list)
    description: str
    required: bool = True
    usage: str
    health_check_timeout: int = 5
    retry_attempts: int = 3
    retry_delay: float = 1.0


class MCPConfig(BaseModel):
    """MCP configuration."""

    servers: Dict[MCPServer, MCPServerConfig] = Field(default_factory=dict)
    global_timeout: int = 30
    health_check_interval: int = 60

    @classmethod
    def default(cls) -> "MCPConfig":
        """Get default MCP configuration."""
        return cls(
            servers={
                MCPServer.CONTEXT7: MCPServerConfig(
                    command="npx",
                    args=["@context/mcp"],
                    description="Access documentation and library information",
                    required=True,
                    usage="MANDATORY for all documentation lookups",
                ),
                MCPServer.MEMORY: MCPServerConfig(
                    command="npx",
                    args=["@memory/mcp"],
                    description="Store and retrieve project context and knowledge",
                    required=True,
                    usage="MANDATORY for context persistence",
                ),
                MCPServer.SEQUENTIAL_THINKING: MCPServerConfig(
                    command="npx",
                    args=["@sequential-thinking/mcp"],
                    description="Complex problem decomposition and reasoning",
                    required=True,
                    usage="MANDATORY for complex problem solving",
                ),
                MCPServer.FILESYSTEM: MCPServerConfig(
                    command="npx",
                    args=["@filesystem/mcp"],
                    description="File system operations",
                    required=True,
                    usage="MANDATORY for all file operations",
                ),
                MCPServer.GIT: MCPServerConfig(
                    command="npx",
                    args=["@git/mcp"],
                    description="Version control operations",
                    required=True,
                    usage="MANDATORY for version control",
                ),
            }
        )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: LogLevel = LogLevel.INFO
    console_enabled: bool = True
    file_enabled: bool = True
    json_enabled: bool = True
    api_logging_enabled: bool = True
    code_logging_enabled: bool = True
    log_rotation_size: int = 10 * 1024 * 1024  # 10MB
    log_retention_days: int = 30
    structured_logging: bool = True
    include_timestamps: bool = True
    include_context: bool = True


class ExecutorConfig(BaseModel):
    """Configuration for Claude Code executor."""

    model: str = "claude-3-opus-20240229"
    max_tokens: int = 4096
    temperature: float = 0.3
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_seconds: int = 300
    stream_output: bool = True
    output_format: OutputFormat = OutputFormat.STREAM_JSON
    allowed_tools: List[str] = Field(default_factory=lambda: [
        "Agent",
        "Glob",
        "Grep",
        "LS",
        "NotebookRead",
        "Read",
        "TodoRead",
        "Bash",
        "Edit",
        "MultiEdit",
        "NotebookEdit",
        "WebFetch",
        "WebSearch",
        "Write",
    ])
    custom_system_prompt: Optional[str] = None
    append_system_prompt: Optional[str] = None
    enable_extended_thinking: bool = True
    parallel_execution: bool = False
    max_parallel_tasks: int = 3


class ContextConfig(BaseModel):
    """Configuration for context management."""

    max_tokens: int = 150000  # Opus 4 extended context
    chunk_overlap: int = 500
    min_chunk_size: int = 1000
    summarization_enabled: bool = True
    archive_completed: bool = True
    context_cache_size: int = 10
    cross_reference_depth: int = 3


class BuildConfig(BaseModel):
    """Configuration for the build process."""

    max_cost: float = 100.0
    max_tokens: int = 10_000_000
    parallel_phases: bool = False
    continue_on_error: bool = False
    dry_run: bool = False
    skip_tests: bool = False
    verbose: int = 0
    phases_to_execute: Optional[List[str]] = None
    checkpoint_interval: int = 300  # seconds
    auto_commit: bool = True
    commit_message_format: str = "{type}({scope}): {description}"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CCB_",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-3-opus-20240229"
    anthropic_small_fast_model: str = "claude-3-haiku-20240307"

    # Paths
    base_output_dir: Path = Path("./claude-builds")
    templates_dir: Path = Path(__file__).parent.parent / "templates"
    
    # Feature Flags
    telemetry_enabled: bool = True
    error_reporting_enabled: bool = True
    auto_update_enabled: bool = True
    
    # Proxy Configuration
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    no_proxy: Optional[str] = None
    
    # Performance
    max_concurrent_api_calls: int = 5
    api_rate_limit: int = 100  # requests per minute
    
    # Defaults
    default_logging_config: LoggingConfig = Field(default_factory=LoggingConfig)
    default_executor_config: ExecutorConfig = Field(default_factory=ExecutorConfig)
    default_context_config: ContextConfig = Field(default_factory=ContextConfig)
    default_build_config: BuildConfig = Field(default_factory=BuildConfig)
    default_mcp_config: MCPConfig = Field(default_factory=MCPConfig.default)

    @field_validator("anthropic_api_key")
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is provided."""
        if not v:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set. "
                "Get your API key from https://console.anthropic.com"
            )
        return v

    @field_validator("base_output_dir")
    def validate_output_dir(cls, v: Path) -> Path:
        """Ensure output directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    def get_mcp_config(self, custom_config_path: Optional[Path] = None) -> MCPConfig:
        """Get MCP configuration, merging custom if provided."""
        config = self.default_mcp_config.model_copy()
        
        if custom_config_path and custom_config_path.exists():
            # Load and merge custom config
            import json
            with open(custom_config_path) as f:
                custom_data = json.load(f)
                # Merge logic would go here
                
        return config


# Global settings instance
settings = Settings()


# Configuration loader functions
def load_project_config(project_dir: Path) -> Dict[str, Any]:
    """Load project-specific configuration."""
    config_file = project_dir / ".claude-code-builder.json"
    if not config_file.exists():
        return {}
    
    import json
    with open(config_file) as f:
        return json.load(f)


def save_project_config(project_dir: Path, config: Dict[str, Any]) -> None:
    """Save project-specific configuration."""
    config_file = project_dir / ".claude-code-builder.json"
    
    import json
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)


__all__ = [
    "MCPServerConfig",
    "MCPConfig",
    "LoggingConfig",
    "ExecutorConfig",
    "ContextConfig",
    "BuildConfig",
    "Settings",
    "settings",
    "load_project_config",
    "save_project_config",
]