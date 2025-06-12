"""Core data models for Claude Code Builder."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from claude_code_builder.core.base_model import (
    BaseModel,
    IdentifiedModel,
    MetadataModel,
    NamedModel,
    TimestampedModel,
)
from claude_code_builder.core.enums import (
    AgentType,
    ChunkStrategy,
    Complexity,
    ErrorType,
    MCPCheckpoint,
    MCPServer,
    OutputFormat,
    Priority,
    ProjectType,
    RecoveryAction,
    TaskStatus,
    TestType,
)
from claude_code_builder.core.types import (
    Cost,
    CostBreakdown,
    JSON,
    PathLike,
    SessionID,
    TokenCount,
    TokenUsage,
)


# Specification Analysis Models
class SpecAnalysis(BaseModel):
    """Result of specification analysis."""

    project_type: ProjectType
    project_name: str
    complexity: Complexity
    estimated_hours: float
    estimated_cost: float
    summary: str
    key_features: List[str]
    technical_requirements: List[str]
    suggested_technologies: List[str]
    identified_risks: List[str]
    integration_points: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Task and Phase Models
class Task(NamedModel):
    """Individual task within a phase."""

    phase_id: UUID
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    dependencies: List[UUID] = Field(default_factory=list)
    assigned_agent: Optional[AgentType] = None
    context_required: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    error_count: int = 0
    last_error: Optional[str] = None
    completion_percentage: float = 0.0

    @field_validator("completion_percentage")
    def validate_percentage(cls, v: float) -> float:
        """Ensure percentage is between 0 and 100."""
        return max(0.0, min(100.0, v))


class Phase(NamedModel):
    """Phase containing multiple tasks."""

    order: int
    status: TaskStatus = TaskStatus.PENDING
    tasks: List[Task] = Field(default_factory=list)
    dependencies: List[UUID] = Field(default_factory=list)
    context_requirements: List[str] = Field(default_factory=list)
    acceptance_criteria_id: Optional[UUID] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    completion_percentage: float = 0.0

    @property
    def total_tasks(self) -> int:
        """Get total number of tasks."""
        return len(self.tasks)

    @property
    def completed_tasks(self) -> int:
        """Get number of completed tasks."""
        return sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)

    def update_completion(self) -> None:
        """Update completion percentage based on tasks."""
        if self.total_tasks > 0:
            self.completion_percentage = (self.completed_tasks / self.total_tasks) * 100


class TaskBreakdown(BaseModel):
    """Complete task breakdown for a project."""

    phases: List[Phase]
    total_estimated_hours: float
    total_estimated_cost: float
    critical_path: List[UUID] = Field(default_factory=list)
    parallel_phases: List[List[UUID]] = Field(default_factory=list)

    @property
    def total_phases(self) -> int:
        """Get total number of phases."""
        return len(self.phases)

    @property
    def total_tasks(self) -> int:
        """Get total number of tasks across all phases."""
        return sum(phase.total_tasks for phase in self.phases)
    
    @property
    def tasks(self) -> List[Task]:
        """Get all tasks across all phases."""
        all_tasks = []
        for phase in self.phases:
            all_tasks.extend(phase.tasks)
        return all_tasks

    def get_phase(self, phase_id: UUID) -> Optional[Phase]:
        """Get phase by ID."""
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None


# Context Management Models
class SpecChunk(BaseModel):
    """Chunk of a large specification."""

    index: int
    total_chunks: int
    content: str
    tokens: TokenCount
    sections: List[str] = Field(default_factory=list)
    cross_references: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_section(self, section: str) -> None:
        """Add a section to this chunk."""
        self.sections.append(section)

    def add_context(self, context: str) -> None:
        """Add cross-reference context."""
        self.cross_references.append(context)


class ProcessedSpec(BaseModel):
    """Processed specification with chunking information."""

    chunks: List[SpecChunk]
    total_tokens: TokenCount
    requires_chunking: bool
    chunk_strategy: ChunkStrategy
    summaries: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PhaseContext(BaseModel):
    """Context loaded for a specific phase."""

    phase_id: UUID
    content: str
    token_count: TokenCount
    sections_included: List[str]
    dependencies_loaded: List[UUID] = Field(default_factory=list)
    memory_context: Optional[str] = None


# Execution and State Models
class ExecutionContext(TimestampedModel):
    """Context for current execution."""

    session_id: SessionID
    current_phase: Optional[UUID] = None
    current_task: Optional[UUID] = None
    completed_phases: Set[UUID] = Field(default_factory=set)
    completed_tasks: Set[UUID] = Field(default_factory=set)
    full_context: str = ""
    critical_sections: List[str] = Field(default_factory=list)
    token_usage: TokenUsage = Field(default_factory=dict)
    cost_tracking: CostBreakdown = Field(default_factory=dict)


class Message(BaseModel):
    """Chat message."""
    role: str
    content: str


class ToolDefinition(BaseModel):
    """Tool definition for API calls."""
    name: str
    description: str
    input_schema: Dict[str, Any]


class ToolCall(BaseModel):
    """Tool call in API response."""
    id: str
    name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None


class GeneratedCode(TimestampedModel):
    """Generated code information."""
    file_path: str
    content: str
    language: str
    phase: str
    task: str
    model: str
    line_count: int
    tokens_used: int
    checksum: Optional[str] = None


class APICall(TimestampedModel):
    """Record of an API call to Anthropic."""

    call_id: UUID = Field(default_factory=lambda: UUID(int=0))  # Will be set properly
    session_id: SessionID
    agent_type: AgentType
    endpoint: str
    model: str
    phase: Optional[str] = None
    task: Optional[str] = None
    request_messages: List[Message] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    tools: List[ToolDefinition] = Field(default_factory=list)
    temperature: float = 0.3
    max_tokens: int = 4096
    response_content: Optional[str] = None
    tool_calls: List["ToolCall"] = Field(default_factory=list)
    tokens_in: TokenCount = 0
    tokens_out: TokenCount = 0
    tokens_total: TokenCount = 0
    latency_ms: int = 0
    stream_chunks: int = 0
    estimated_cost: Cost = 0.0
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if the API call was successful."""
        return self.error is None


# Output and Project Management Models
class ProjectMetadata(TimestampedModel):
    """Metadata for a project."""

    project_name: str
    specification_path: Path
    output_directory: Path
    claude_code_version: str
    model_used: str = "claude-3-opus-20240229"
    max_cost: float = 100.0
    phases_to_execute: Optional[List[str]] = None
    custom_mcp_config: Optional[Path] = None
    subdirectories: Dict[str, Path] = Field(default_factory=dict)


class ProjectState(TimestampedModel):
    """Persistent state of a project."""

    metadata: ProjectMetadata
    spec_hash: str
    current_phase: Optional[UUID] = None
    completed_phases: List[UUID] = Field(default_factory=list)
    completed_tasks: List[UUID] = Field(default_factory=list)
    failed_tasks: List[UUID] = Field(default_factory=list)
    skipped_tasks: List[UUID] = Field(default_factory=list)
    last_checkpoint: datetime = Field(default_factory=datetime.utcnow)
    total_tokens_used: TokenCount = 0
    total_cost: Cost = 0.0
    error_log: List[Dict[str, Any]] = Field(default_factory=list)
    resume_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Analysis and breakdown
    spec_analysis: Optional[SpecAnalysis] = None
    task_breakdown: Optional[TaskBreakdown] = None
    project_type: Optional[ProjectType] = None
    estimated_tokens: int = 0
    
    # Execution tracking
    api_calls_made: int = 0
    tokens_used: int = 0
    cost_incurred: float = 0.0
    build_completed: bool = False
    completed_at: Optional[datetime] = None

    def can_resume(self) -> bool:
        """Check if the project can be resumed."""
        return bool(self.resume_data)

    def add_error(self, error: Exception, context: str) -> None:
        """Add an error to the log."""
        self.error_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
        })


# Acceptance Criteria Models
class TestStep(BaseModel):
    """Individual test step."""

    description: str
    expected_result: str
    validation_method: str = "manual"
    automated: bool = False


class AcceptanceCriterion(IdentifiedModel):
    """Single acceptance criterion."""

    criterion_id: str  # e.g., "FC001"
    description: str
    test_type: TestType
    test_steps: List[TestStep]
    expected_result: str
    validation_method: str
    test_data_requirements: List[str] = Field(default_factory=list)
    priority: Priority = Priority.MEDIUM
    automated: bool = False


class AcceptanceCriteria(BaseModel):
    """Complete acceptance criteria for a phase."""

    phase_id: UUID
    functional_criteria: List[AcceptanceCriterion] = Field(default_factory=list)
    performance_criteria: List[AcceptanceCriterion] = Field(default_factory=list)
    security_criteria: List[AcceptanceCriterion] = Field(default_factory=list)
    integration_criteria: List[AcceptanceCriterion] = Field(default_factory=list)

    @property
    def total_criteria(self) -> int:
        """Get total number of criteria."""
        return (
            len(self.functional_criteria)
            + len(self.performance_criteria)
            + len(self.security_criteria)
            + len(self.integration_criteria)
        )

    @property
    def categories(self) -> List[str]:
        """Get list of categories with criteria."""
        categories = []
        if self.functional_criteria:
            categories.append("functional")
        if self.performance_criteria:
            categories.append("performance")
        if self.security_criteria:
            categories.append("security")
        if self.integration_criteria:
            categories.append("integration")
        return categories


# Test Result Models
class TestResult(TimestampedModel):
    """Result of a single test execution."""

    criterion_id: str
    passed: bool
    actual_result: Optional[str] = None
    expected_result: Optional[str] = None
    duration_ms: int = 0
    test_type: TestType
    error: Optional[str] = None
    screenshots: List[Path] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)


class TestResults(BaseModel):
    """Aggregated test results."""

    phase_id: UUID
    results: List[TestResult]
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_ms: int = 0

    @property
    def total_tests(self) -> int:
        """Get total number of tests."""
        return len(self.results)

    @property
    def passed_tests(self) -> int:
        """Get number of passed tests."""
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_tests(self) -> int:
        """Get number of failed tests."""
        return sum(1 for r in self.results if not r.passed)

    @property
    def all_passed(self) -> bool:
        """Check if all tests passed."""
        return self.failed_tests == 0

    @property
    def pass_rate(self) -> float:
        """Get pass rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    def add_result(self, result: TestResult) -> None:
        """Add a test result."""
        self.results.append(result)

    @property
    def failure_summary(self) -> str:
        """Get summary of failures."""
        failures = [r for r in self.results if not r.passed]
        if not failures:
            return "All tests passed"
        
        summary_lines = [f"Failed {len(failures)} out of {self.total_tests} tests:"]
        for failure in failures:
            summary_lines.append(f"- {failure.criterion_id}: {failure.error or 'No error message'}")
        return "\n".join(summary_lines)


# MCP Models
class MCPViolation(BaseModel):
    """Record of MCP usage violation."""

    server: MCPServer
    checkpoint: MCPCheckpoint
    severity: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MCPValidation(BaseModel):
    """MCP usage validation result."""

    violations: List[MCPViolation] = Field(default_factory=list)
    compliant: bool = True

    def add_violation(
        self, server: MCPServer, checkpoint: MCPCheckpoint, severity: str, message: str
    ) -> None:
        """Add a violation."""
        self.violations.append(
            MCPViolation(
                server=server, checkpoint=checkpoint, severity=severity, message=message
            )
        )
        self.compliant = False


# Error Recovery Models
class RecoveryStrategy(BaseModel):
    """Strategy for recovering from an error."""

    error_type: ErrorType
    action: RecoveryAction
    max_retries: int = 3
    backoff_factor: float = 2.0
    context_optimization: bool = False
    manual_intervention_message: Optional[str] = None


class RecoveryResult(BaseModel):
    """Result of error recovery attempt."""

    success: bool
    action_taken: RecoveryAction
    retries_used: int = 0
    modified_context: Optional[Any] = None
    error_message: Optional[str] = None


# Resource Tracking Models
class ResourceUsage(TimestampedModel):
    """Track resource usage."""

    tokens_used: TokenUsage = Field(default_factory=dict)
    cost_breakdown: CostBreakdown = Field(default_factory=dict)
    api_calls: int = 0
    errors: int = 0
    mcp_calls: Dict[str, int] = Field(default_factory=dict)
    phase_durations: Dict[str, float] = Field(default_factory=dict)


# Build Metrics Models
class BuildMetrics(BaseModel):
    """Metrics for a complete build."""

    total_duration: float = 0.0
    phase_durations: Dict[str, float] = Field(default_factory=dict)
    task_durations: Dict[str, float] = Field(default_factory=dict)
    api_latencies: List[float] = Field(default_factory=list)
    total_tokens: TokenCount = 0
    tokens_by_phase: Dict[str, TokenCount] = Field(default_factory=dict)
    total_cost: Cost = 0.0
    cost_by_agent: Dict[str, Cost] = Field(default_factory=dict)
    test_pass_rate: float = 0.0
    criteria_met_count: int = 0
    error_count: int = 0
    recovery_success_rate: float = 0.0
    mcp_calls: Dict[str, int] = Field(default_factory=dict)
    mcp_compliance_rate: float = 100.0


# Session Models
class ResumeStatus(BaseModel):
    """Status of resume capability."""

    can_resume: bool
    reason: Optional[str] = None
    requires_confirmation: bool = False
    last_phase: Optional[str] = None
    completed_phases: List[str] = Field(default_factory=list)
    completed_tasks: int = 0
    last_checkpoint: Optional[datetime] = None
    corruption_details: Optional[Dict[str, Any]] = None


class ResumePoint(BaseModel):
    """Point from which to resume execution."""

    phase_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    description: str
    restore_context: bool = True
    skip_completed: bool = True


# Documentation Models
class DocumentationSection(BaseModel):
    """Section of documentation."""

    title: str
    content: str
    order: int
    subsections: List["DocumentationSection"] = Field(default_factory=list)


class Documentation(BaseModel):
    """Complete project documentation."""

    sections: Dict[str, DocumentationSection] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    format: str = "markdown"

    def add_section(self, key: str, section: DocumentationSection) -> None:
        """Add a documentation section."""
        self.sections[key] = section

    async def save_to_directory(self, directory: Path) -> None:
        """Save documentation to directory."""
        # Implementation will be in the documentation builder
        pass


# Allow self-referencing models
DocumentationSection.model_rebuild()


# Export all models
__all__ = [
    "SpecAnalysis",
    "Task",
    "Phase",
    "TaskBreakdown",
    "SpecChunk",
    "ProcessedSpec",
    "PhaseContext",
    "ExecutionContext",
    "APICall",
    "ProjectMetadata",
    "ProjectState",
    "TestStep",
    "AcceptanceCriterion",
    "AcceptanceCriteria",
    "TestResult",
    "TestResults",
    "MCPViolation",
    "MCPValidation",
    "RecoveryStrategy",
    "RecoveryResult",
    "ResourceUsage",
    "BuildMetrics",
    "ResumeStatus",
    "ResumePoint",
    "DocumentationSection",
    "Documentation",
]