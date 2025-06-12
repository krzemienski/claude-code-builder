"""Output directory management for Claude Code Builder."""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import aiofiles
from pydantic import Field

from claude_code_builder.core.base_model import BaseModel
from claude_code_builder.core.exceptions import FileConflictError, ResumeError
from claude_code_builder.core.models import (
    ProjectMetadata,
    ProjectState,
    ResumeStatus,
    SpecAnalysis,
    TaskBreakdown,
)


class ProjectDirectory(BaseModel):
    """Represents a project output directory."""

    path: Path
    metadata: ProjectMetadata
    subdirs: Dict[str, Path] = Field(default_factory=dict)
    can_resume: bool = False
    last_phase: Optional[str] = None

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

    @classmethod
    async def load(cls, path: Path) -> "ProjectDirectory":
        """Load an existing project directory."""
        metadata_file = path / ".claude-code-builder" / "metadata.json"
        if not metadata_file.exists():
            raise ResumeError(
                f"Project directory not found or invalid: {path}",
                str(path),
                "No metadata file found",
            )

        async with aiofiles.open(metadata_file, "r") as f:
            metadata_data = json.loads(await f.read())

        metadata = ProjectMetadata(**metadata_data)
        
        # Load subdirectories
        subdirs = {}
        for key, subdir_path in metadata.subdirectories.items():
            subdirs[key] = Path(subdir_path)

        # Check resume capability
        state_file = path / ".checkpoints" / "latest_state.json"
        can_resume = state_file.exists()
        
        last_phase = None
        if can_resume:
            async with aiofiles.open(state_file, "r") as f:
                state_data = json.loads(await f.read())
                state = ProjectState(**state_data)
                if state.current_phase:
                    last_phase = str(state.current_phase)

        return cls(
            path=path,
            metadata=metadata,
            subdirs=subdirs,
            can_resume=can_resume,
            last_phase=last_phase,
        )

    async def save_artifacts(self, artifacts: Dict[str, Any]) -> None:
        """Save project artifacts."""
        artifacts_dir = self.subdirs["artifacts"]
        
        for name, artifact in artifacts.items():
            file_path = artifacts_dir / f"{name}.json"
            
            # Convert Pydantic models to dict
            if hasattr(artifact, "model_dump"):
                data = artifact.model_dump()
            else:
                data = artifact

            async with aiofiles.open(file_path, "w") as f:
                await f.write(json.dumps(data, indent=2, default=str))

    async def save_state(self, state: ProjectState) -> None:
        """Save project state."""
        checkpoint_dir = self.subdirs["checkpoints"]
        
        # Save timestamped checkpoint
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = checkpoint_dir / f"checkpoint_{timestamp}.json"
        
        async with aiofiles.open(checkpoint_file, "w") as f:
            await f.write(state.model_dump_json(indent=2))

        # Update latest state
        latest_file = checkpoint_dir / "latest_state.json"
        async with aiofiles.open(latest_file, "w") as f:
            await f.write(state.model_dump_json(indent=2))

    async def save_final_state(self) -> None:
        """Save final project state."""
        final_file = self.path / ".claude-code-builder" / "final_state.json"
        latest_file = self.subdirs["checkpoints"] / "latest_state.json"
        
        if latest_file.exists():
            shutil.copy2(latest_file, final_file)

    def load_project(self) -> Dict[str, Any]:
        """Load project data synchronously."""
        # This would load various project files
        # Implementation depends on specific needs
        return {}

    def load_implementation(self) -> Dict[str, Any]:
        """Load implementation data synchronously."""
        # This would load generated code and artifacts
        return {}


class OutputManager:
    """Manages project output directories."""

    def __init__(self, base_output_dir: Path = Path("./claude-builds")) -> None:
        """Initialize the output manager."""
        self.base_output_dir = base_output_dir
        self.base_output_dir.mkdir(exist_ok=True)

    async def create_project_directory(
        self,
        project_name: str,
        spec_path: Path,
        user_specified_dir: Optional[Path] = None,
        model: str = "claude-3-opus-20240229",
        max_cost: float = 100.0,
    ) -> ProjectDirectory:
        """Create or resume a project directory."""
        if user_specified_dir:
            # Check if resuming existing project
            if user_specified_dir.exists():
                try:
                    existing = await ProjectDirectory.load(user_specified_dir)
                    resume = await self._should_resume_project(existing)
                    if resume:
                        return existing
                    else:
                        # Backup and create new
                        backup_path = await self._backup_existing(user_specified_dir)
                        print(f"Backed up existing project to: {backup_path}")
                except Exception:
                    # Not a valid project directory, backup and create new
                    if list(user_specified_dir.iterdir()):  # Not empty
                        backup_path = await self._backup_existing(user_specified_dir)
                        print(f"Backed up existing directory to: {backup_path}")

            return await self._create_new_project_directory(
                project_name, spec_path, user_specified_dir, model, max_cost
            )

        # Create timestamped directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"{project_name}_{timestamp}"
        project_dir = self.base_output_dir / dir_name

        return await self._create_new_project_directory(
            project_name, spec_path, project_dir, model, max_cost
        )

    async def _should_resume_project(self, project_dir: ProjectDirectory) -> bool:
        """Check if we should resume the existing project."""
        if not project_dir.can_resume:
            return False

        # In a real implementation, this might prompt the user
        # For now, we'll return True if resumable
        return True

    async def _backup_existing(self, path: Path) -> Path:
        """Backup an existing directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.parent / f"{path.name}_backup_{timestamp}"
        
        shutil.move(str(path), str(backup_path))
        return backup_path

    async def _create_new_project_directory(
        self,
        project_name: str,
        spec_path: Path,
        path: Path,
        model: str,
        max_cost: float,
    ) -> ProjectDirectory:
        """Create a new project directory structure."""
        path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        subdirs = {
            "source": path / "src",
            "logs": path / "logs",
            "artifacts": path / "artifacts",
            "checkpoints": path / ".checkpoints",
            "memory": path / ".memory",
            "documentation": path / "docs",
            "tests": path / "tests",
            "api_logs": path / "logs" / "api_calls",
            "config": path / ".claude-code-builder",
        }

        for subdir in subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)

        # Create metadata
        from claude_code_builder import __version__
        
        metadata = ProjectMetadata(
            project_name=project_name,
            specification_path=spec_path,
            output_directory=path,
            claude_code_version=__version__,
            model_used=model,
            max_cost=max_cost,
            subdirectories={k: str(v) for k, v in subdirs.items()},
        )

        # Save metadata
        metadata_file = subdirs["config"] / "metadata.json"
        async with aiofiles.open(metadata_file, "w") as f:
            await f.write(metadata.model_dump_json(indent=2))

        # Copy specification
        spec_copy = subdirs["artifacts"] / "original_specification.md"
        shutil.copy2(spec_path, spec_copy)

        # Calculate spec hash
        spec_hash = await self._calculate_file_hash(spec_path)

        # Create initial state
        initial_state = ProjectState(
            metadata=metadata,
            spec_hash=spec_hash,
        )

        # Save initial state
        state_file = subdirs["checkpoints"] / "initial_state.json"
        async with aiofiles.open(state_file, "w") as f:
            await f.write(initial_state.model_dump_json(indent=2))

        # Create .gitignore
        gitignore_path = path / ".gitignore"
        async with aiofiles.open(gitignore_path, "w") as f:
            await f.write("""# Claude Code Builder
.checkpoints/
.memory/
logs/
*.tmp
*.bak
""")

        # Initialize git repository
        import subprocess
        try:
            subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial project structure"],
                cwd=path,
                check=True,
                capture_output=True,
            )
        except Exception:
            # Git not available or failed, continue anyway
            pass

        return ProjectDirectory(
            path=path,
            metadata=metadata,
            subdirs=subdirs,
        )

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()


class ProjectResumer:
    """Handles project resume operations."""

    def __init__(self, output_manager: OutputManager) -> None:
        """Initialize the resumer."""
        self.output_manager = output_manager

    async def check_resume_capability(self, project_dir: Path) -> ResumeStatus:
        """Check if a project can be resumed."""
        try:
            # Load project directory
            project = await ProjectDirectory.load(project_dir)
            
            # Load latest state
            state_file = project.subdirs["checkpoints"] / "latest_state.json"
            if not state_file.exists():
                return ResumeStatus(
                    can_resume=False,
                    reason="No checkpoint found",
                )

            async with aiofiles.open(state_file, "r") as f:
                state_data = json.loads(await f.read())
                state = ProjectState(**state_data)

            # Validate state integrity
            validation = await self._validate_state(state, project)
            if not validation["is_valid"]:
                return ResumeStatus(
                    can_resume=False,
                    reason=validation["reason"],
                    corruption_details=validation.get("details"),
                )

            # Check spec hasn't changed
            current_spec_hash = await self.output_manager._calculate_file_hash(
                Path(state.metadata.specification_path)
            )
            spec_unchanged = current_spec_hash == state.spec_hash

            if not spec_unchanged:
                return ResumeStatus(
                    can_resume=True,
                    reason="Specification has changed",
                    requires_confirmation=True,
                    last_phase=str(state.current_phase) if state.current_phase else None,
                    completed_phases=[str(p) for p in state.completed_phases],
                    completed_tasks=len(state.completed_tasks),
                    last_checkpoint=state.last_checkpoint,
                )

            return ResumeStatus(
                can_resume=True,
                last_phase=str(state.current_phase) if state.current_phase else None,
                completed_phases=[str(p) for p in state.completed_phases],
                completed_tasks=len(state.completed_tasks),
                last_checkpoint=state.last_checkpoint,
            )

        except Exception as e:
            return ResumeStatus(
                can_resume=False,
                reason=f"Error checking resume status: {str(e)}",
            )

    async def _validate_state(
        self, state: ProjectState, project: ProjectDirectory
    ) -> Dict[str, Any]:
        """Validate project state integrity."""
        try:
            # Check required directories exist
            for key, subdir in project.subdirs.items():
                if not subdir.exists():
                    return {
                        "is_valid": False,
                        "reason": f"Missing required directory: {key}",
                        "details": {"missing_dir": str(subdir)},
                    }

            # Check artifacts exist
            artifacts_dir = project.subdirs["artifacts"]
            required_artifacts = ["original_specification.md"]
            
            for artifact in required_artifacts:
                if not (artifacts_dir / artifact).exists():
                    return {
                        "is_valid": False,
                        "reason": f"Missing required artifact: {artifact}",
                        "details": {"missing_artifact": artifact},
                    }

            # Validate state consistency
            if state.current_phase and state.current_phase in state.completed_phases:
                return {
                    "is_valid": False,
                    "reason": "Inconsistent state: current phase marked as completed",
                    "details": {
                        "current_phase": str(state.current_phase),
                        "completed_phases": [str(p) for p in state.completed_phases],
                    },
                }

            return {"is_valid": True}

        except Exception as e:
            return {
                "is_valid": False,
                "reason": f"Validation error: {str(e)}",
                "details": {"error": str(e)},
            }


async def generate_build_summary(project_dir: ProjectDirectory) -> str:
    """Generate a summary of the build."""
    summary_lines = [
        "## Build Summary\n",
        f"**Project**: {project_dir.metadata.project_name}",
        f"**Output Directory**: {project_dir.path}",
        f"**Model Used**: {project_dir.metadata.model_used}",
        f"**Claude Code Version**: {project_dir.metadata.claude_code_version}",
        "",
        "### Generated Artifacts:",
    ]

    # List key artifacts
    artifacts_dir = project_dir.subdirs["artifacts"]
    if artifacts_dir.exists():
        for artifact in sorted(artifacts_dir.glob("*.json")):
            if artifact.name != "original_specification.md":
                summary_lines.append(f"- {artifact.stem}")

    # Check for generated source
    src_dir = project_dir.subdirs["source"]
    if src_dir.exists():
        file_count = sum(1 for _ in src_dir.rglob("*") if _.is_file())
        summary_lines.append(f"\n### Source Files: {file_count}")

    # Check for documentation
    docs_dir = project_dir.subdirs["documentation"]
    if docs_dir.exists():
        doc_count = sum(1 for _ in docs_dir.glob("*.md"))
        summary_lines.append(f"### Documentation Files: {doc_count}")

    return "\n".join(summary_lines)


__all__ = [
    "ProjectDirectory",
    "OutputManager",
    "ProjectResumer",
    "generate_build_summary",
]