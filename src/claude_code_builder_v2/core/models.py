"""Data models for Claude Code Builder v2."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from claude_code_builder_v2.core.enums import AgentType, BuildStatus, PhaseStatus


class ExecutionContext(BaseModel):
    """Context for agent execution."""

    phase: str
    specification: str
    project_dir: Path
    previous_outputs: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Response from an agent."""

    agent_type: AgentType
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PhaseResult(BaseModel):
    """Result of a build phase."""

    phase_name: str
    status: PhaseStatus
    agent_responses: List[AgentResponse] = Field(default_factory=list)
    duration_seconds: float = 0.0
    cost: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BuildMetrics(BaseModel):
    """Metrics for a complete build."""

    build_id: str
    status: BuildStatus
    phases_completed: int = 0
    phases_failed: int = 0
    total_duration: float = 0.0
    total_cost: float = 0.0
    total_tokens: int = 0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SpecificationAnalysis(BaseModel):
    """Analysis of a specification."""

    summary: str
    complexity: str  # low, medium, high
    estimated_duration: Optional[str] = None
    key_requirements: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskBreakdown(BaseModel):
    """Breakdown of tasks for implementation."""

    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    estimated_duration: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
