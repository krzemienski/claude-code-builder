"""Custom exceptions for Claude Code Builder v3."""


class CCBError(Exception):
    """Base exception for all Claude Code Builder errors."""

    pass


class SkillError(CCBError):
    """Base exception for skill-related errors."""

    pass


class SkillNotFoundError(SkillError):
    """Raised when a skill cannot be found."""

    def __init__(self, skill_name: str) -> None:
        super().__init__(f"Skill not found: {skill_name}")
        self.skill_name = skill_name


class SkillValidationError(SkillError):
    """Raised when skill validation fails."""

    def __init__(self, skill_name: str, errors: list[str]) -> None:
        error_msg = "\n".join(f"  - {err}" for err in errors)
        super().__init__(f"Skill validation failed for '{skill_name}':\n{error_msg}")
        self.skill_name = skill_name
        self.errors = errors


class SkillGenerationError(SkillError):
    """Raised when skill generation fails."""

    def __init__(self, skill_name: str, reason: str) -> None:
        super().__init__(f"Failed to generate skill '{skill_name}': {reason}")
        self.skill_name = skill_name
        self.reason = reason


class SkillLoadError(SkillError):
    """Raised when skill loading fails."""

    def __init__(self, skill_name: str, reason: str) -> None:
        super().__init__(f"Failed to load skill '{skill_name}': {reason}")
        self.skill_name = skill_name
        self.reason = reason


class PipelineError(CCBError):
    """Base exception for pipeline errors."""

    pass


class PipelineStageError(PipelineError):
    """Raised when a pipeline stage fails."""

    def __init__(self, stage_name: str, reason: str) -> None:
        super().__init__(f"Pipeline stage '{stage_name}' failed: {reason}")
        self.stage_name = stage_name
        self.reason = reason


class BuildError(CCBError):
    """Raised when a build fails."""

    def __init__(self, reason: str, build_id: str | None = None) -> None:
        msg = f"Build failed: {reason}"
        if build_id:
            msg += f" (build_id: {build_id})"
        super().__init__(msg)
        self.reason = reason
        self.build_id = build_id
