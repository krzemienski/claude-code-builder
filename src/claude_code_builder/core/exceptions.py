"""Custom exceptions for Claude Code Builder."""

from typing import Any, Dict, Optional

from claude_code_builder.core.enums import ErrorType


class ClaudeCodeBuilderError(Exception):
    """Base exception for all Claude Code Builder errors."""

    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}


class SpecificationError(ClaudeCodeBuilderError):
    """Error in specification processing."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the exception."""
        super().__init__(message, ErrorType.VALIDATION_ERROR, details)


class ContextOverflowError(ClaudeCodeBuilderError):
    """Context exceeds maximum token limit."""

    def __init__(
        self,
        message: str,
        current_tokens: int,
        max_tokens: int,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "current_tokens": current_tokens,
            "max_tokens": max_tokens,
            "overflow": current_tokens - max_tokens,
        })
        super().__init__(message, ErrorType.CONTEXT_OVERFLOW, details)


class APIError(ClaudeCodeBuilderError):
    """Error from Anthropic API."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "status_code": status_code,
            "response_body": response_body,
        })
        super().__init__(message, ErrorType.API_ERROR, details)


class RateLimitError(APIError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details["retry_after"] = retry_after
        super().__init__(message, status_code=429, details=details)
        self.error_type = ErrorType.API_RATE_LIMIT


class MCPServerError(ClaudeCodeBuilderError):
    """Error from MCP server."""

    def __init__(
        self,
        message: str,
        server: str,
        method: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "server": server,
            "method": method,
        })
        super().__init__(message, ErrorType.MCP_SERVER_ERROR, details)


class ExecutionTimeoutError(ClaudeCodeBuilderError):
    """Execution exceeded timeout."""

    def __init__(
        self,
        message: str,
        timeout_seconds: int,
        elapsed_seconds: float,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "timeout_seconds": timeout_seconds,
            "elapsed_seconds": elapsed_seconds,
        })
        super().__init__(message, ErrorType.EXECUTION_TIMEOUT, details)


class FileConflictError(ClaudeCodeBuilderError):
    """File operation conflict."""

    def __init__(
        self,
        message: str,
        file_path: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "file_path": file_path,
            "operation": operation,
        })
        super().__init__(message, ErrorType.FILE_CONFLICT, details)


class TestFailure(ClaudeCodeBuilderError):
    """Test execution failure."""

    def __init__(
        self,
        message: str,
        test_id: str,
        test_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "test_id": test_id,
            "test_type": test_type,
        })
        super().__init__(message, ErrorType.TEST_FAILURE, details)


class ResourceLimitExceeded(ClaudeCodeBuilderError):
    """Resource limit exceeded."""

    def __init__(
        self,
        message: str,
        resource_type: str,
        current_usage: float,
        limit: float,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "resource_type": resource_type,
            "current_usage": current_usage,
            "limit": limit,
            "percentage": (current_usage / limit) * 100 if limit > 0 else 0,
        })
        super().__init__(message, ErrorType.RESOURCE_LIMIT, details)


class ValidationError(ClaudeCodeBuilderError):
    """Validation error."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "field": field,
            "value": value,
        })
        super().__init__(message, ErrorType.VALIDATION_ERROR, details)


class PhaseExecutionError(ClaudeCodeBuilderError):
    """Error during phase execution."""

    def __init__(
        self,
        phase_name: str,
        message: str,
        task_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "phase_name": phase_name,
            "task_name": task_name,
        })
        super().__init__(message, ErrorType.UNKNOWN_ERROR, details)


class ConfigurationError(ClaudeCodeBuilderError):
    """Configuration error."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "config_key": config_key,
            "config_file": config_file,
        })
        super().__init__(message, ErrorType.VALIDATION_ERROR, details)


class ResumeError(ClaudeCodeBuilderError):
    """Error resuming project."""

    def __init__(
        self,
        message: str,
        project_dir: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception."""
        details = details or {}
        details.update({
            "project_dir": project_dir,
            "reason": reason,
        })
        super().__init__(message, ErrorType.UNKNOWN_ERROR, details)


__all__ = [
    "ClaudeCodeBuilderError",
    "SpecificationError",
    "ContextOverflowError",
    "APIError",
    "RateLimitError",
    "MCPServerError",
    "ExecutionTimeoutError",
    "FileConflictError",
    "TestFailure",
    "ResourceLimitExceeded",
    "ValidationError",
    "PhaseExecutionError",
    "ConfigurationError",
    "ResumeError",
]