"""Enumerations used throughout Claude Code Builder."""

from enum import Enum, auto


class ProjectType(str, Enum):
    """Types of projects that can be analyzed."""

    API = "api"
    CLI = "cli"
    WEB_APP = "web_app"
    LIBRARY = "library"
    SERVICE = "service"
    FULLSTACK = "fullstack"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    DATA_PIPELINE = "data_pipeline"
    ML_MODEL = "ml_model"
    UNKNOWN = "unknown"


class Complexity(str, Enum):
    """Project complexity levels."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class TaskStatus(str, Enum):
    """Status of a task or phase."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class Priority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(str, Enum):
    """Types of errors that can occur."""

    API_RATE_LIMIT = "api_rate_limit"
    API_ERROR = "api_error"
    CONTEXT_OVERFLOW = "context_overflow"
    MCP_SERVER_ERROR = "mcp_server_error"
    EXECUTION_TIMEOUT = "execution_timeout"
    FILE_CONFLICT = "file_conflict"
    TEST_FAILURE = "test_failure"
    RESOURCE_LIMIT = "resource_limit"
    VALIDATION_ERROR = "validation_error"
    UNKNOWN_ERROR = "unknown_error"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OutputFormat(str, Enum):
    """Output format options for CLI."""

    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"
    RICH = "rich"


class TestType(str, Enum):
    """Types of tests for acceptance criteria."""

    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    INTEGRATION = "integration"
    ACCEPTANCE = "acceptance"


class AgentType(str, Enum):
    """Types of agents in the system."""

    SPEC_ANALYZER = "spec_analyzer"
    TASK_GENERATOR = "task_generator"
    INSTRUCTION_BUILDER = "instruction_builder"
    ACCEPTANCE_GENERATOR = "acceptance_generator"
    DOCUMENTATION_AGENT = "documentation_agent"
    CLAUDE_CODE_EXECUTOR = "claude_code_executor"
    CODE_GENERATOR = "code_generator"
    TEST_GENERATOR = "test_generator"
    ERROR_HANDLER = "error_handler"


class MCPServer(str, Enum):
    """Available MCP servers."""

    CONTEXT7 = "context7"
    MEMORY = "memory"
    SEQUENTIAL_THINKING = "sequential-thinking"
    FILESYSTEM = "filesystem"
    GIT = "git"
    GITHUB = "github"
    FETCH = "fetch"
    PERPLEXITY = "perplexity"
    TASKMASTER = "taskmaster"


class MCPCheckpoint(str, Enum):
    """MCP usage checkpoints."""

    PROJECT_INITIALIZED = "project_initialized"
    CONTEXT_LOADED = "context_loaded"
    SPECIFICATION_ANALYZED = "specification_analyzed"
    TASKS_GENERATED = "tasks_generated"
    PHASE_START = "phase_start"
    BEFORE_IMPLEMENTATION = "before_implementation"
    RESEARCH = "research"
    TASK_COMPLETE = "task_complete"
    PHASE_COMPLETE = "phase_complete"
    PHASE_COMPLETED = "phase_completed"
    CODE_GENERATED = "code_generated"
    TESTS_EXECUTED = "tests_executed"
    CHECKPOINT = "checkpoint"
    BUILD_COMPLETED = "build_completed"


class ChunkStrategy(str, Enum):
    """Strategies for chunking large specifications."""

    SECTION_BASED = "section_based"
    TOKEN_BASED = "token_based"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class RecoveryAction(str, Enum):
    """Actions for error recovery."""

    RETRY = "retry"
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    RETRY_WITH_OPTIMIZED_CONTEXT = "retry_with_optimized_context"
    SKIP_TASK = "skip_task"
    FAIL_PHASE = "fail_phase"
    RESUME_FROM_CHECKPOINT = "resume_from_checkpoint"
    MANUAL_INTERVENTION = "manual_intervention"