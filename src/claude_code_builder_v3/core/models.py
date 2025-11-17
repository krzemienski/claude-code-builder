"""
Pydantic v2 models for Claude Code Builder v3.

All models use Pydantic v2 with proper validation, JSON schema generation,
and type safety.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SkillMetadata(BaseModel):
    """Metadata for a Claude Skill (loaded from YAML frontmatter)."""

    model_config = ConfigDict(frozen=False, extra="allow")

    name: str = Field(description="Skill name in kebab-case")
    description: str = Field(description="What this skill does and when to use it")
    version: str = Field(default="1.0.0", description="Skill version (semver)")
    author: Optional[str] = Field(default=None, description="Skill author")
    category: Optional[str] = Field(default=None, description="Skill category")
    technologies: List[str] = Field(
        default_factory=list, description="Technologies involved"
    )
    triggers: List[str] = Field(
        default_factory=list, description="Keywords that trigger this skill"
    )
    path: Optional[Path] = Field(default=None, description="Filesystem path to skill")

    # Progressive disclosure metadata
    metadata_token_count: int = Field(default=100, description="Token count for metadata")
    instructions_token_count: int = Field(
        default=3000, description="Token count for instructions"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure skill name is kebab-case."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"Invalid skill name: {v}. Must be alphanumeric with hyphens/underscores.")
        return v


class SkillGap(BaseModel):
    """Represents a missing skill identified from spec analysis."""

    model_config = ConfigDict(frozen=False)

    name: str = Field(description="Proposed skill name")
    description: str = Field(description="What this skill should do")
    technologies: List[str] = Field(description="Technologies this skill should handle")
    patterns: List[str] = Field(
        default_factory=list, description="Patterns this skill should encode"
    )
    integration_points: List[str] = Field(
        default_factory=list, description="External integrations (APIs, services)"
    )
    doc_urls: List[str] = Field(
        default_factory=list, description="URLs to documentation for research"
    )
    priority: str = Field(default="medium", description="Priority: low, medium, high, critical")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class GeneratedSkill(BaseModel):
    """Complete generated skill ready for validation and use."""

    model_config = ConfigDict(frozen=False)

    id: UUID = Field(default_factory=uuid4)
    name: str
    skill_md: str = Field(description="Complete SKILL.md content with YAML frontmatter")
    examples: Dict[str, str] = Field(
        default_factory=dict, description="Example files (filename -> content)"
    )
    tests: Dict[str, str] = Field(
        default_factory=dict, description="Test files (filename -> content)"
    )
    metadata: SkillMetadata

    generated_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1, description="Skill version number")
    parent_skill_id: Optional[UUID] = Field(
        default=None, description="Parent skill if this is a refinement"
    )


class ValidationCheck(BaseModel):
    """Individual validation check result."""

    model_config = ConfigDict(frozen=False)

    name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class SkillValidationResult(BaseModel):
    """Result of skill validation."""

    model_config = ConfigDict(frozen=False)

    valid: bool
    results: List[ValidationCheck]
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validation_duration_ms: float = Field(default=0.0)


class SkillUsageFeedback(BaseModel):
    """Feedback from using a skill in a build."""

    model_config = ConfigDict(frozen=False)

    skill_name: str
    build_id: UUID
    successful: bool
    feedback_text: Optional[str] = None
    user_modifications: Dict[str, Any] = Field(
        default_factory=dict, description="User modifications to generated code"
    )
    linting_errors: List[str] = Field(default_factory=list)
    test_failures: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class BuildPhase(BaseModel):
    """Build pipeline phase."""

    model_config = ConfigDict(frozen=False)

    name: str
    skills_used: List[str] = Field(default_factory=list)
    status: str = Field(default="pending")  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Dict[str, Any] = Field(default_factory=dict)


class BuildResult(BaseModel):
    """Result of a complete build."""

    model_config = ConfigDict(frozen=False)

    build_id: UUID = Field(default_factory=uuid4)
    success: bool
    phases: List[BuildPhase] = Field(default_factory=list)
    generated_files: Dict[str, str] = Field(
        default_factory=dict, description="Generated files (path -> content)"
    )
    skills_used: List[str] = Field(default_factory=list)
    generated_skills: List[str] = Field(
        default_factory=list, description="Skills that were generated during this build"
    )
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    # Metrics
    total_duration_ms: float = Field(default=0.0)
    total_tokens_used: int = Field(default=0)
    total_cost_usd: float = Field(default=0.0)

    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class PipelineStage(BaseModel):
    """Multi-stage pipeline stage definition."""

    model_config = ConfigDict(frozen=False)

    name: str
    description: str
    skills: List[str] = Field(
        default_factory=list, description="Skills to use in this stage"
    )
    depends_on: List[str] = Field(
        default_factory=list, description="Stages this depends on"
    )
    parallel: bool = Field(default=False, description="Can run in parallel with other stages")
    quality_gates: List[str] = Field(
        default_factory=list, description="Quality gates that must pass"
    )


class BuildPipeline(BaseModel):
    """Complete multi-stage build pipeline."""

    model_config = ConfigDict(frozen=False)

    name: str
    stages: List[PipelineStage]

    @field_validator("stages")
    @classmethod
    def validate_stages(cls, v: List[PipelineStage]) -> List[PipelineStage]:
        """Validate stage dependencies exist."""
        stage_names = {stage.name for stage in v}
        for stage in v:
            for dep in stage.depends_on:
                if dep not in stage_names:
                    raise ValueError(f"Stage '{stage.name}' depends on unknown stage '{dep}'")
        return v


class SkillUsageStats(BaseModel):
    """Statistics for skill usage tracking."""

    model_config = ConfigDict(frozen=False)

    skill_name: str
    total_uses: int = Field(default=0)
    successful_uses: int = Field(default=0)
    failed_uses: int = Field(default=0)
    success_rate: float = Field(default=0.0)

    last_used_at: Optional[datetime] = None
    first_used_at: Optional[datetime] = None

    average_duration_ms: float = Field(default=0.0)
    total_tokens_saved: int = Field(
        default=0, description="Tokens saved by using this skill vs regenerating"
    )
