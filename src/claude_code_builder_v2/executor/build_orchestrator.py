"""Build orchestrator using Claude SDK."""

import hashlib
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles

from claude_code_builder_v2.core.config import BuildConfig, ExecutorConfig, LoggingConfig
from claude_code_builder_v2.core.enums import BuildStatus
from claude_code_builder_v2.core.exceptions import SpecificationError
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
from claude_code_builder_v2.core.models import BuildMetrics, ExecutionContext, PhaseResult
from claude_code_builder_v2.executor.phase_executor import SDKPhaseExecutor
from claude_code_builder_v2.sdk.client_manager import SDKClientManager
from claude_code_builder_v2.sdk.cost_tracker import CostTracker
from claude_code_builder_v2.sdk.hook_manager import SDKHookManager


class SDKBuildOrchestrator:
    """Orchestrates complete build process using SDK."""

    def __init__(
        self,
        spec_path: Path,
        build_config: Optional[BuildConfig] = None,
        output_dir: Optional[Path] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize build orchestrator.

        Args:
            spec_path: Path to specification file
            build_config: Build configuration
            output_dir: Output directory
            api_key: Anthropic API key
        """
        self.spec_path = spec_path
        self.build_config = build_config or BuildConfig()
        self.output_dir = output_dir or Path.cwd() / "output"
        self.api_key = api_key

        # Will be initialized in setup()
        self.project_dir: Optional[Path] = None
        self.logger: Optional[ComprehensiveLogger] = None
        self.cost_tracker: Optional[CostTracker] = None
        self.hook_manager: Optional[SDKHookManager] = None
        self.client_manager: Optional[SDKClientManager] = None
        self.phase_executor: Optional[SDKPhaseExecutor] = None

        # Build state
        self.build_id = str(uuid.uuid4())
        self.phase_results: List[PhaseResult] = []
        self.specification: Optional[str] = None

    async def setup(self) -> None:
        """Setup build environment."""
        # Create project directory
        self.project_dir = self.output_dir / f"build_{self.build_id[:8]}"
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logger
        logging_config = self.build_config.default_logging_config or LoggingConfig()
        self.logger = ComprehensiveLogger(self.project_dir, logging_config)

        self.logger.info(
            "build_setup_start",
            msg="Starting build setup",
            build_id=self.build_id,
            spec_path=str(self.spec_path),
        )

        # Initialize cost tracking and hooks
        self.cost_tracker = CostTracker()
        self.hook_manager = SDKHookManager(self.logger, self.cost_tracker)

        # Initialize SDK client manager
        executor_config = self.build_config.default_executor_config or ExecutorConfig()
        self.client_manager = SDKClientManager(
            config=executor_config,
            logger=self.logger,
            hooks={},
        )

        # Initialize phase executor
        self.phase_executor = SDKPhaseExecutor(
            config=executor_config,
            logger=self.logger,
            client_manager=self.client_manager,
            cost_tracker=self.cost_tracker,
            project_dir=self.project_dir,
        )

        self.logger.info(
            "build_setup_complete",
            msg="Build setup completed",
            project_dir=str(self.project_dir),
        )

    async def build(self) -> BuildMetrics:
        """Execute complete build process.

        Returns:
            BuildMetrics
        """
        if not self.logger or not self.phase_executor:
            raise RuntimeError("Build not setup. Call setup() first.")

        self.logger.info(
            "build_start",
            msg="Starting build process",
            build_id=self.build_id,
        )

        start_time = time.time()
        status = BuildStatus.IN_PROGRESS

        try:
            # Load specification
            await self._load_specification()

            # Execute build phases
            await self._execute_build_phases()

            # Mark build as completed
            status = BuildStatus.COMPLETED

        except SpecificationError:
            # Re-raise specification errors
            raise
        except Exception as e:
            status = BuildStatus.FAILED
            self.logger.error(
                "build_failed",
                msg=f"Build failed: {e}",
                build_id=self.build_id,
                error=str(e),
            )

        duration = time.time() - start_time

        # Create metrics
        metrics = BuildMetrics(
            build_id=self.build_id,
            status=status,
            phases_completed=len([p for p in self.phase_results if p.status == "completed"]),
            phases_failed=len([p for p in self.phase_results if p.status == "failed"]),
            total_duration=duration,
            total_cost=self.cost_tracker.total_cost if self.cost_tracker else 0.0,
            total_tokens=self.cost_tracker.total_input_tokens + self.cost_tracker.total_output_tokens if self.cost_tracker else 0,
        )

        self.logger.info(
            "build_complete",
            msg="Build completed",
            build_id=self.build_id,
            status=status.value,
            duration=duration,
            cost=metrics.total_cost,
        )

        return metrics

    async def _load_specification(self) -> None:
        """Load specification from file."""
        if not self.logger:
            raise RuntimeError("Logger not initialized")

        try:
            async with aiofiles.open(self.spec_path, "r") as f:
                self.specification = await f.read()

            if not self.specification or not self.specification.strip():
                raise SpecificationError("Specification file is empty")

            self.logger.info(
                "specification_loaded",
                msg="Specification loaded",
                length=len(self.specification),
            )

        except Exception as e:
            self.logger.error(
                "specification_load_error",
                msg=f"Failed to load specification: {e}",
                error=str(e),
            )
            raise

    async def _execute_build_phases(self) -> None:
        """Execute all build phases."""
        if not self.specification or not self.phase_executor or not self.project_dir:
            raise RuntimeError("Build not properly initialized")

        # Create execution context
        context = ExecutionContext(
            phase="build",
            specification=self.specification,
            project_dir=self.project_dir,
        )

        # Phase 1: Analyze specification
        result = await self.phase_executor.execute_phase(
            "analyze_specification", context
        )
        self.phase_results.append(result)

        if not result.agent_responses or not result.agent_responses[0].success:
            raise Exception("Specification analysis failed")

        analysis = result.agent_responses[0].result.get("analysis", "")

        # Phase 2: Generate tasks
        result = await self.phase_executor.execute_phase(
            "generate_tasks", context, analysis=analysis
        )
        self.phase_results.append(result)

        if result.agent_responses and result.agent_responses[0].success:
            tasks = result.agent_responses[0].result.get("tasks", "")

            # Phase 3: Build instructions
            result = await self.phase_executor.execute_phase(
                "build_instructions", context, tasks=tasks
            )
            self.phase_results.append(result)

    async def _calculate_spec_hash(self) -> str:
        """Calculate hash of specification.

        Returns:
            SHA-256 hash of specification
        """
        # Always reload from file to ensure fresh content
        async with aiofiles.open(self.spec_path, "r") as f:
            content = await f.read()

        return hashlib.sha256(content.encode()).hexdigest()

    def get_metrics(self) -> Dict[str, Any]:
        """Get current build metrics.

        Returns:
            Metrics dictionary
        """
        return {
            "build_id": self.build_id,
            "phases_completed": len([p for p in self.phase_results if p.status == "completed"]),
            "phases_failed": len([p for p in self.phase_results if p.status == "failed"]),
            "total_cost": self.cost_tracker.total_cost if self.cost_tracker else 0.0,
        }
