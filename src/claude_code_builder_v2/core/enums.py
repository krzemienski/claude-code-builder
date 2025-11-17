"""Enums for Claude Code Builder v2."""

from enum import Enum


class AgentType(str, Enum):
    """Types of agents in the system."""

    SPEC_ANALYZER = "spec_analyzer"
    TASK_GENERATOR = "task_generator"
    INSTRUCTION_BUILDER = "instruction_builder"
    DOCUMENTATION_AGENT = "documentation_agent"
    TEST_GENERATOR = "test_generator"
    CODE_REVIEWER = "code_reviewer"
    ACCEPTANCE_GENERATOR = "acceptance_generator"
    PHASE_EXECUTOR = "phase_executor"


class PhaseStatus(str, Enum):
    """Status of a build phase."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PermissionMode(str, Enum):
    """Permission modes for SDK."""

    AUTO = "auto"
    MANUAL = "manual"
    ALWAYS_ALLOW = "always_allow"
    ALWAYS_DENY = "always_deny"


class BuildStatus(str, Enum):
    """Overall build status."""

    INITIALIZING = "initializing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
