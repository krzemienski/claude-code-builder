"""Custom exceptions for Claude Code Builder v2."""


class BuildError(Exception):
    """Base exception for build errors."""

    pass


class ConfigurationError(BuildError):
    """Exception for configuration errors."""

    pass


class SpecificationError(BuildError):
    """Exception for specification errors."""

    pass


class SDKError(BuildError):
    """Exception for SDK-related errors."""

    pass


class PhaseError(BuildError):
    """Exception for phase execution errors."""

    pass


class AgentError(BuildError):
    """Exception for agent errors."""

    pass


class CostLimitExceeded(BuildError):
    """Exception when cost limit is exceeded."""

    pass


class ContextOverflowError(BuildError):
    """Exception when context size is exceeded."""

    pass
