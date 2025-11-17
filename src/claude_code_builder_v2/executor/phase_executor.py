"""Phase executor using Claude SDK."""

import time
from pathlib import Path
from typing import Any, Dict, Optional

from claude_code_builder_v2.agents import (
    AcceptanceGenerator,
    CodeReviewer,
    DocumentationAgent,
    InstructionBuilder,
    SpecAnalyzer,
    TaskGenerator,
    TestGenerator,
)
from claude_code_builder_v2.core.config import ExecutorConfig
from claude_code_builder_v2.core.enums import PhaseStatus
from claude_code_builder_v2.core.exceptions import PhaseError
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
from claude_code_builder_v2.core.models import ExecutionContext, PhaseResult
from claude_code_builder_v2.sdk.client_manager import SDKClientManager
from claude_code_builder_v2.sdk.cost_tracker import CostTracker


class SDKPhaseExecutor:
    """Executes build phases using SDK-based agents."""

    def __init__(
        self,
        config: ExecutorConfig,
        logger: ComprehensiveLogger,
        client_manager: SDKClientManager,
        cost_tracker: CostTracker,
        project_dir: Path,
    ) -> None:
        """Initialize phase executor.

        Args:
            config: Executor configuration
            logger: Comprehensive logger
            client_manager: SDK client manager
            cost_tracker: Cost tracker
            project_dir: Project directory
        """
        self.config = config
        self.logger = logger
        self.client_manager = client_manager
        self.cost_tracker = cost_tracker
        self.project_dir = project_dir

        # Initialize agents
        self._init_agents()

    def _init_agents(self) -> None:
        """Initialize all agents."""
        agent_args = (self.config, self.logger, self.client_manager)

        self.spec_analyzer = SpecAnalyzer(*agent_args)
        self.task_generator = TaskGenerator(*agent_args)
        self.instruction_builder = InstructionBuilder(*agent_args)
        self.documentation_agent = DocumentationAgent(*agent_args)
        self.test_generator = TestGenerator(*agent_args)
        self.code_reviewer = CodeReviewer(*agent_args)
        self.acceptance_generator = AcceptanceGenerator(*agent_args)

        self.logger.info(
            "agents_initialized",
            msg="All agents initialized",
            agent_count=7,
        )

    async def execute_phase(
        self,
        phase_name: str,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> PhaseResult:
        """Execute a build phase.

        Args:
            phase_name: Name of phase
            context: Execution context
            **kwargs: Phase-specific arguments

        Returns:
            PhaseResult
        """
        self.logger.log_phase_start(phase_name)
        start_time = time.time()
        start_cost = self.cost_tracker.total_cost

        try:
            # Execute phase based on name
            if phase_name == "analyze_specification":
                result = await self._execute_analyze_phase(context, **kwargs)
            elif phase_name == "generate_tasks":
                result = await self._execute_task_generation_phase(context, **kwargs)
            elif phase_name == "build_instructions":
                result = await self._execute_instruction_phase(context, **kwargs)
            elif phase_name == "generate_documentation":
                result = await self._execute_documentation_phase(context, **kwargs)
            elif phase_name == "generate_tests":
                result = await self._execute_test_generation_phase(context, **kwargs)
            elif phase_name == "review_code":
                result = await self._execute_code_review_phase(context, **kwargs)
            elif phase_name == "create_acceptance_criteria":
                result = await self._execute_acceptance_phase(context, **kwargs)
            else:
                raise PhaseError(f"Unknown phase: {phase_name}")

            duration = time.time() - start_time
            cost = self.cost_tracker.total_cost - start_cost

            self.logger.log_phase_complete(phase_name, duration, cost)

            return PhaseResult(
                phase_name=phase_name,
                status=PhaseStatus.COMPLETED,
                agent_responses=[result],
                duration_seconds=duration,
                cost=cost,
            )

        except Exception as e:
            duration = time.time() - start_time
            cost = self.cost_tracker.total_cost - start_cost

            self.logger.error(
                "phase_failed",
                msg=f"Phase {phase_name} failed: {e}",
                phase=phase_name,
                error=str(e),
            )

            return PhaseResult(
                phase_name=phase_name,
                status=PhaseStatus.FAILED,
                duration_seconds=duration,
                cost=cost,
                error=str(e),
            )

    async def _execute_analyze_phase(
        self, context: ExecutionContext, **kwargs: Any
    ) -> Any:
        """Execute specification analysis phase."""
        return await self.spec_analyzer.execute(context, **kwargs)

    async def _execute_task_generation_phase(
        self, context: ExecutionContext, **kwargs: Any
    ) -> Any:
        """Execute task generation phase."""
        analysis = kwargs.get("analysis", "")
        return await self.task_generator.execute(context, analysis=analysis, **kwargs)

    async def _execute_instruction_phase(
        self, context: ExecutionContext, **kwargs: Any
    ) -> Any:
        """Execute instruction building phase."""
        tasks = kwargs.get("tasks", "")
        return await self.instruction_builder.execute(context, tasks=tasks, **kwargs)

    async def _execute_documentation_phase(
        self, context: ExecutionContext, **kwargs: Any
    ) -> Any:
        """Execute documentation generation phase."""
        project_details = kwargs.get("project_details", context.specification)
        return await self.documentation_agent.execute(
            context, project_details=project_details, **kwargs
        )

    async def _execute_test_generation_phase(
        self, context: ExecutionContext, **kwargs: Any
    ) -> Any:
        """Execute test generation phase."""
        code_to_test = kwargs.get("code", "")
        return await self.test_generator.execute(
            context, code_to_test=code_to_test, **kwargs
        )

    async def _execute_code_review_phase(
        self, context: ExecutionContext, **kwargs: Any
    ) -> Any:
        """Execute code review phase."""
        code = kwargs.get("code", "")
        return await self.code_reviewer.execute(context, code=code, **kwargs)

    async def _execute_acceptance_phase(
        self, context: ExecutionContext, **kwargs: Any
    ) -> Any:
        """Execute acceptance criteria generation phase."""
        requirements = kwargs.get("requirements", context.specification)
        return await self.acceptance_generator.execute(
            context, requirements=requirements, **kwargs
        )
