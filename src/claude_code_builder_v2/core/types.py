"""Type definitions for Claude Code Builder."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, TypeAlias, Union

from pydantic import BaseModel

# Basic type aliases
JSON: TypeAlias = Dict[str, Any]
JSONArray: TypeAlias = List[JSON]
PathLike: TypeAlias = Union[str, Path]
AsyncCallable: TypeAlias = Callable[..., Any]  # Should be Awaitable[Any] but simplified

# Tool definitions for Anthropic API
ToolDefinition: TypeAlias = Dict[str, Any]
ToolCall: TypeAlias = Dict[str, Any]
Message: TypeAlias = Dict[str, Any]

# Configuration types
Config: TypeAlias = Dict[str, Any]
EnvVars: TypeAlias = Dict[str, str]

# Progress callback type
ProgressCallback: TypeAlias = Callable[[str, float], None]

# Token counting
TokenCount: TypeAlias = int
TokenUsage: TypeAlias = Dict[str, TokenCount]

# Cost tracking
Cost: TypeAlias = float
CostBreakdown: TypeAlias = Dict[str, Cost]


class MCPClient(Protocol):
    """Protocol for MCP client interface."""

    async def call(
        self, server: str, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call an MCP server method."""
        ...

    async def health_check(self, server: str) -> bool:
        """Check if an MCP server is healthy."""
        ...


class Logger(Protocol):
    """Protocol for logger interface."""

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        ...

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        ...


class SpecProcessor(Protocol):
    """Protocol for specification processors."""

    async def process(self, spec: str) -> BaseModel:
        """Process a specification."""
        ...


class Agent(Protocol):
    """Protocol for agent interface."""

    async def execute(self, context: Any) -> BaseModel:
        """Execute agent logic."""
        ...


class ErrorHandler(Protocol):
    """Protocol for error handlers."""

    async def handle(self, error: Exception, context: Any) -> Any:
        """Handle an error."""
        ...


# Session and state types
SessionID: TypeAlias = str
PhaseID: TypeAlias = str
TaskID: TypeAlias = str
AgentID: TypeAlias = str

# File system types
FileContent: TypeAlias = str
FileMetadata: TypeAlias = Dict[str, Any]

# API types
APIResponse: TypeAlias = Dict[str, Any]
APIError: TypeAlias = Dict[str, Any]

# Validation types
ValidationResult: TypeAlias = Dict[str, Any]
ValidationError: TypeAlias = Dict[str, Any]

# Test types
TestResult: TypeAlias = Dict[str, Any]
TestReport: TypeAlias = Dict[str, Any]

# Documentation types
DocSection: TypeAlias = Dict[str, str]
Documentation: TypeAlias = Dict[str, DocSection]