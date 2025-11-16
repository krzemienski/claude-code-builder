"""SDK-based Build Orchestrator for managing the complete build process."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from claude_code_builder_v2.sdk import SDKClientManager
from claude_code_builder_v2.executor.phase_executor import SDKPhaseExecutor
from claude_code_builder_v2.agents import SpecAnalyzer, TaskGenerator
from claude_code_builder_v2.core.config import BuildConfig, ExecutorConfig
from claude_code_builder_v2.core.context_manager import ContextManager, SpecificationChunker
from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.exceptions import ClaudeCodeBuilderError, SpecificationError
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
from claude_code_builder_v2.core.models import (
    BuildMetrics,
    ExecutionContext,
    Phase,
    ProjectState,
    SpecAnalysis,
    TaskBreakdown,
)
from claude_code_builder_v2.core.output_manager import OutputManager, ProjectDirectory


class SDKBuildOrchestrator:
    """Orchestrates complete build using Claude Agent SDK."""

    def __init__(
        self,
        spec_path: Path,
        output_dir: Optional[Path] = None,
        build_config: Optional[BuildConfig] = None,
        resume_from: Optional[Path] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the SDK build orchestrator."""
        self.spec_path = spec_path
        self.output_dir = output_dir
        self.build_config = build_config or BuildConfig()
        self.resume_from = resume_from
        self.api_key = api_key

        # Will be initialized in setup
        self.project_dir: Optional[ProjectDirectory] = None
        self.logger: Optional[ComprehensiveLogger] = None
        self.sdk_manager: Optional[SDKClientManager] = None
        self.context_manager: Optional[ContextManager] = None
        self.phase_executor: Optional[SDKPhaseExecutor] = None

        # Build state
        self.project_state: Optional[ProjectState] = None
        self.spec_analysis: Optional[SpecAnalysis] = None
        self.task_breakdown: Optional[TaskBreakdown] = None
        self.build_start_time: Optional[datetime] = None
        self.session_id: str = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    async def setup(self) -> None:
        """Set up the build environment with SDK."""
        # Create output directory
        output_manager = OutputManager()

        if self.resume_from:
            self.project_dir = await ProjectDirectory.load(self.resume_from)
            self.logger = ComprehensiveLogger(
                self.project_dir.path,
                self.build_config.default_logging_config,
            )
            await self.logger.start_session(self.session_id)
            self.logger.print_info("Resuming build from checkpoint")
        else:
            self.project_dir = await output_manager.create_project_directory(
                project_name=self.spec_path.stem,
                spec_path=self.spec_path,
                user_specified_dir=self.output_dir,
                max_cost=self.build_config.max_cost,
            )
            self.logger = ComprehensiveLogger(
                self.project_dir.path,
                self.build_config.default_logging_config,
            )
            await self.logger.start_session(self.session_id)

        # Initialize SDK components
        exec_config = self.build_config.default_executor_config
        self.sdk_manager = SDKClientManager(
            exec_config, self.logger, api_key=self.api_key
        )
        self.sdk_manager.initialize_registries()

        self.context_manager = ContextManager(
            max_context_tokens=150000,
            chunker=SpecificationChunker(),
        )

        # Initialize phase executor with SDK
        self.phase_executor = SDKPhaseExecutor(
            self.sdk_manager,
            self.context_manager,
            self.logger,
            self.project_dir.path,
        )

        # Load or create project state
        if self.resume_from:
            await self._load_project_state()
        else:
            await self._initialize_project_state()

    async def _initialize_project_state(self) -> None:
        """Initialize new project state."""
        self.project_state = ProjectState(
            metadata=self.project_dir.metadata,
            spec_hash=await self._calculate_spec_hash(),
        )

    async def _load_project_state(self) -> None:
        """Load existing project state."""
        state_file = self.project_dir.subdirs["checkpoints"] / "latest_state.json"
        if state_file.exists():
            with open(state_file) as f:
                state_data = json.load(f)
            self.project_state = ProjectState(**state_data)
        else:
            await self._initialize_project_state()

    async def _calculate_spec_hash(self) -> str:
        """Calculate specification file hash."""
        import hashlib

        content = self.spec_path.read_bytes()
        return hashlib.sha256(content).hexdigest()

    async def build(self) -> BuildMetrics:
        """Execute the complete build process using SDK."""
        self.build_start_time = datetime.utcnow()

        try:
            self.logger.print_info("Starting Claude Code Builder (SDK-based)")

            # Phase 1: Load specification
            await self._load_specification()

            # Phase 2: Analyze specification
            await self._analyze_specification()

            # Phase 3: Generate task breakdown
            await self._generate_tasks()

            # Phase 4: Execute phases
            await self._execute_phases()

            # Phase 5: Finalize build
            await self._finalize_build()

            # Generate metrics
            metrics = await self._generate_build_metrics()

            self.logger.print_success("Build completed successfully!")

            return metrics

        except Exception as e:
            self.logger.print_error(f"Build failed: {e}")

            # Save error state
            if self.project_state:
                self.project_state.add_error(e, "build_failed")
                await self.project_dir.save_state(self.project_state)

            raise ClaudeCodeBuilderError(f"Build failed: {e}")

        finally:
            # Cleanup SDK resources
            if self.sdk_manager:
                await self._cleanup_sdk()

    async def _load_specification(self) -> None:
        """Load and validate specification."""
        self.logger.print_info("Loading specification")

        if not self.spec_path.exists():
            raise SpecificationError(
                self.spec_path, "Specification file not found"
            )

        spec_content = self.spec_path.read_text()

        if not spec_content.strip():
            raise SpecificationError(
                self.spec_path, "Specification file is empty"
            )

        # Load into context manager
        spec_data = await self.context_manager.load_specification(
            self.spec_path, spec_content
        )

        self.logger.print_success(
            f"Specification loaded: {spec_data['total_tokens']} tokens"
        )

        # Copy spec to project directory
        project_spec = self.project_dir.path / "specification.md"
        project_spec.write_text(spec_content)

    async def _analyze_specification(self) -> None:
        """Analyze specification using SDK agent."""
        self.logger.print_info("Analyzing specification")

        # Create analyzer agent
        spec_analyzer = SpecAnalyzer(
            sdk_manager=self.sdk_manager,
            context_manager=self.context_manager,
            logger=self.logger,
        )

        # Create execution context
        context = ExecutionContext(
            session_id=self.session_id,
            full_context=self.spec_path.read_text(),
        )

        # Analyze
        response = await spec_analyzer.run(
            context, specification=self.spec_path.read_text()
        )

        if not response.success:
            raise SpecificationError(
                self.spec_path,
                f"Specification analysis failed: {response.error}",
            )

        # Store analysis
        self.spec_analysis = SpecAnalysis(**response.result)

        # Save to project directory
        analysis_file = self.project_dir.subdirs["analysis"] / "spec_analysis.json"
        analysis_file.write_text(json.dumps(self.spec_analysis.model_dump(), indent=2))

        self.logger.print_success(
            f"Specification analyzed: {self.spec_analysis.project_type} project"
        )

    async def _generate_tasks(self) -> None:
        """Generate task breakdown using SDK agent."""
        self.logger.print_info("Generating task breakdown")

        # Create task generator agent
        task_generator = TaskGenerator(
            sdk_manager=self.sdk_manager,
            context_manager=self.context_manager,
            logger=self.logger,
        )

        # Create execution context
        context = ExecutionContext(
            session_id=self.session_id,
            full_context=json.dumps(self.spec_analysis.model_dump()),
        )

        # Generate tasks
        response = await task_generator.run(
            context, spec_analysis=self.spec_analysis.model_dump()
        )

        if not response.success:
            raise ClaudeCodeBuilderError(
                f"Task generation failed: {response.error}"
            )

        # Store breakdown
        self.task_breakdown = TaskBreakdown(**response.result)

        # Save to project directory
        tasks_file = self.project_dir.subdirs["planning"] / "task_breakdown.json"
        tasks_file.write_text(json.dumps(self.task_breakdown.model_dump(), indent=2))

        self.logger.print_success(
            f"Task breakdown generated: {len(self.task_breakdown.tasks)} tasks across {len(self.task_breakdown.phases)} phases"
        )

    async def _execute_phases(self) -> None:
        """Execute all phases using SDK phase executor."""
        self.logger.print_info("Executing build phases")

        if not self.task_breakdown or not self.task_breakdown.phases:
            raise ClaudeCodeBuilderError("No phases to execute")

        for phase in self.task_breakdown.phases:
            self.logger.print_info(f"Starting phase: {phase.name}")

            result = await self.phase_executor.execute_phase(
                phase,
                self.task_breakdown,
                self.project_state,
                self.spec_analysis,
            )

            if not result["success"]:
                raise ClaudeCodeBuilderError(
                    f"Phase {phase.name} failed: {result.get('tasks_failed', 0)} tasks failed"
                )

            self.logger.print_success(
                f"Phase {phase.name} completed: {result['tasks_completed']} tasks in {result['duration']:.2f}s"
            )

            # Update project state
            if self.project_state:
                self.project_state.completed_phases.add(phase.id)
                await self.project_dir.save_state(self.project_state)

    async def _finalize_build(self) -> None:
        """Finalize the build."""
        self.logger.print_info("Finalizing build")

        # Mark build as complete
        if self.project_state:
            self.project_state.build_completed = True
            self.project_state.build_end_time = datetime.utcnow()
            await self.project_dir.save_state(self.project_state)

        self.logger.print_success("Build finalized")

    async def _generate_build_metrics(self) -> BuildMetrics:
        """Generate build metrics."""
        build_duration = (datetime.utcnow() - self.build_start_time).total_seconds()

        metrics = BuildMetrics(
            total_duration=build_duration,
            phases_completed=len(
                self.project_state.completed_phases
                if self.project_state
                else []
            ),
            tasks_completed=len(
                self.phase_executor.completed_tasks
                if self.phase_executor
                else []
            ),
            total_api_calls=0,  # Would need to track from SDK manager
            total_cost=0.0,  # Would need to track from SDK manager
        )

        # Save metrics
        metrics_file = self.project_dir.subdirs["logs"] / "build_metrics.json"
        metrics_file.write_text(json.dumps(metrics.model_dump(), indent=2))

        return metrics

    async def _cleanup_sdk(self) -> None:
        """Cleanup SDK resources."""
        if self.sdk_manager:
            # Close all active sessions
            for session_id in list(self.sdk_manager.active_sessions.keys()):
                try:
                    await self.sdk_manager.close_session(session_id)
                except Exception as e:
                    self.logger.print_warning(f"Failed to close session {session_id}: {e}")

        self.logger.print_info("SDK resources cleaned up")


__all__ = ["SDKBuildOrchestrator"]
