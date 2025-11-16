"""SDK-based Phase Executor for managing phase-by-phase execution."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from claude_code_builder_v2.agents import (
    SpecAnalyzer,
    TaskGenerator,
    InstructionBuilder,
    CodeGenerator,
    TestGenerator,
    AcceptanceGenerator,
    ErrorHandler,
    DocumentationAgent,
    BaseAgent,
    AgentResponse,
)
from claude_code_builder_v2.sdk import SDKClientManager
from claude_code_builder_v2.core.context_manager import ContextManager
from claude_code_builder_v2.core.enums import AgentType, TaskStatus
from claude_code_builder_v2.core.exceptions import PhaseExecutionError
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
from claude_code_builder_v2.core.models import (
    ExecutionContext,
    Phase,
    ProjectState,
    Task,
    TaskBreakdown,
)


class SDKPhaseExecutor:
    """Executes build phases using SDK-based agents."""

    def __init__(
        self,
        sdk_manager: SDKClientManager,
        context_manager: ContextManager,
        logger: ComprehensiveLogger,
        project_dir: Path,
    ) -> None:
        """Initialize the SDK phase executor."""
        self.sdk_manager = sdk_manager
        self.context_manager = context_manager
        self.logger = logger
        self.project_dir = project_dir

        # Initialize agents with SDK
        self.agents = self._initialize_agents()

        # Track execution state
        self.current_phase: Optional[Phase] = None
        self.completed_tasks: Set[str] = set()

    def _initialize_agents(self) -> Dict[AgentType, BaseAgent]:
        """Initialize all SDK-based agents."""
        agents = {}

        # Create each agent with SDK manager
        agent_classes = {
            AgentType.SPEC_ANALYZER: SpecAnalyzer,
            AgentType.TASK_GENERATOR: TaskGenerator,
            AgentType.INSTRUCTION_BUILDER: InstructionBuilder,
            AgentType.CODE_GENERATOR: CodeGenerator,
            AgentType.TEST_GENERATOR: TestGenerator,
            AgentType.ACCEPTANCE_GENERATOR: AcceptanceGenerator,
            AgentType.ERROR_HANDLER: ErrorHandler,
            AgentType.DOCUMENTATION_AGENT: DocumentationAgent,
        }

        for agent_type, agent_class in agent_classes.items():
            agents[agent_type] = agent_class(
                sdk_manager=self.sdk_manager,
                context_manager=self.context_manager,
                logger=self.logger,
            )

        return agents

    async def execute_phase(
        self,
        phase: Phase,
        task_breakdown: TaskBreakdown,
        project_state: ProjectState,
        spec_analysis: Any,
    ) -> Dict[str, Any]:
        """Execute a complete phase using SDK."""
        self.current_phase = phase
        phase_start = datetime.utcnow()

        try:
            self.logger.print_info(f"Executing phase: {phase.name}")

            # Get phase tasks
            phase_tasks = [
                task for task in task_breakdown.tasks if task.phase_id == phase.id
            ]

            if not phase_tasks:
                self.logger.print_warning(f"No tasks found for phase: {phase.name}")
                return {"tasks_completed": 0, "success": True}

            # Sort tasks by dependencies
            sorted_tasks = await self._sort_tasks_by_dependencies(phase_tasks)

            # Execute tasks
            completed = 0
            failed = 0

            for task in sorted_tasks:
                if await self._can_execute_task(task, task_breakdown.tasks):
                    result = await self._execute_task(
                        task,
                        task_breakdown,
                        project_state,
                        spec_analysis,
                    )

                    if result["success"]:
                        completed += 1
                        self.completed_tasks.add(str(task.id))
                        task.status = TaskStatus.COMPLETED
                    else:
                        failed += 1
                        task.status = TaskStatus.FAILED

                        # Handle failure based on priority
                        if task.priority == "high" and not result.get("recovered"):
                            raise PhaseExecutionError(
                                phase.name,
                                f"Critical task failed: {task.name}",
                                task.name,
                            )

            return {
                "tasks_completed": completed,
                "tasks_failed": failed,
                "success": failed == 0,
                "duration": (datetime.utcnow() - phase_start).total_seconds(),
            }

        except Exception as e:
            self.logger.print_error(f"Phase execution failed: {e}")
            raise PhaseExecutionError(
                phase.name,
                str(e),
                details={"phase": phase.model_dump()},
            )

    async def _sort_tasks_by_dependencies(
        self,
        tasks: List[Task],
    ) -> List[Task]:
        """Sort tasks respecting dependencies."""
        sorted_tasks = []
        remaining = tasks.copy()
        task_ids = {str(task.id) for task in tasks}

        while remaining:
            # Find tasks with no pending dependencies
            ready_tasks = []
            for task in remaining:
                # Check if all dependencies are completed or not in this phase
                deps_satisfied = all(
                    str(dep_id) in self.completed_tasks
                    or str(dep_id) not in task_ids
                    for dep_id in task.dependencies
                )

                if deps_satisfied:
                    ready_tasks.append(task)

            if not ready_tasks:
                # Circular dependency or missing dependency
                self.logger.print_warning(
                    f"Dependency issue: {len(remaining)} tasks cannot be scheduled"
                )
                # Add remaining tasks anyway
                sorted_tasks.extend(remaining)
                break

            # Sort ready tasks by priority
            ready_tasks.sort(key=lambda t: (t.priority, t.estimated_hours))

            sorted_tasks.extend(ready_tasks)
            for task in ready_tasks:
                remaining.remove(task)

        return sorted_tasks

    async def _can_execute_task(
        self,
        task: Task,
        all_tasks: List[Task],
    ) -> bool:
        """Check if a task can be executed."""
        # Check if already completed
        if str(task.id) in self.completed_tasks:
            return False

        # Check dependencies
        for dep_id in task.dependencies:
            if str(dep_id) not in self.completed_tasks:
                # Check if dependency is in a different phase
                dep_task = next((t for t in all_tasks if t.id == dep_id), None)
                if dep_task and dep_task.phase_id == task.phase_id:
                    # Same phase dependency not completed
                    return False

        return True

    async def _execute_task(
        self,
        task: Task,
        task_breakdown: TaskBreakdown,
        project_state: ProjectState,
        spec_analysis: Any,
    ) -> Dict[str, Any]:
        """Execute a single task using SDK agents."""
        task_start = datetime.utcnow()

        try:
            self.logger.print_info(f"Executing task: {task.name}")

            # Create execution context
            context = ExecutionContext(
                session_id=f"task_{task.id}",
                current_phase=self.current_phase.id if self.current_phase else None,
                current_task=task.id,
                completed_phases=set(),
                completed_tasks={
                    UUID(int=int(tid))
                    for tid in self.completed_tasks
                    if tid.replace("-", "").isdigit()
                }
                if self.completed_tasks
                else set(),
            )

            # Get agent for task
            agent = self._get_agent_for_task(task)

            if not agent:
                self.logger.print_warning(f"No agent found for task: {task.name}")
                return {
                    "success": False,
                    "error": "No suitable agent",
                    "duration": (datetime.utcnow() - task_start).total_seconds(),
                }

            # Execute task with agent
            try:
                response = await self._run_agent_for_task(
                    agent, task, context, spec_analysis
                )

                if not response.success:
                    # Try error recovery
                    recovery_response = await self._recover_from_error(
                        task, context, response.error or "Unknown error"
                    )

                    if recovery_response and recovery_response.success:
                        # Retry with recovery strategy
                        response = await self._run_agent_for_task(
                            agent, task, context, spec_analysis
                        )

                return {
                    "success": response.success,
                    "duration": (datetime.utcnow() - task_start).total_seconds(),
                    "result": response.result,
                    "recovered": not response.success and recovery_response is not None,
                }

            except Exception as e:
                self.logger.print_error(f"Agent execution error: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "duration": (datetime.utcnow() - task_start).total_seconds(),
                }

        except Exception as e:
            self.logger.print_error(f"Task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.utcnow() - task_start).total_seconds(),
            }

    def _get_agent_for_task(self, task: Task) -> Optional[BaseAgent]:
        """Get appropriate agent for a task."""
        task_lower = task.name.lower()

        # Determine agent based on task type
        if "analy" in task_lower or "spec" in task_lower:
            return self.agents.get(AgentType.SPEC_ANALYZER)
        elif "generat" in task_lower and "task" in task_lower:
            return self.agents.get(AgentType.TASK_GENERATOR)
        elif "instruct" in task_lower or "plan" in task_lower:
            return self.agents.get(AgentType.INSTRUCTION_BUILDER)
        elif "implement" in task_lower or "code" in task_lower:
            return self.agents.get(AgentType.CODE_GENERATOR)
        elif "test" in task_lower:
            return self.agents.get(AgentType.TEST_GENERATOR)
        elif "accept" in task_lower or "criteria" in task_lower:
            return self.agents.get(AgentType.ACCEPTANCE_GENERATOR)
        elif "document" in task_lower or "doc" in task_lower:
            return self.agents.get(AgentType.DOCUMENTATION_AGENT)
        else:
            # Default to code generator
            return self.agents.get(AgentType.CODE_GENERATOR)

    async def _run_agent_for_task(
        self,
        agent: BaseAgent,
        task: Task,
        context: ExecutionContext,
        spec_analysis: Any,
    ) -> AgentResponse:
        """Run agent with appropriate parameters for task."""
        agent_type = agent.agent_type

        # Build parameters based on agent type
        if agent_type == AgentType.SPEC_ANALYZER:
            spec_content = await self._get_spec_content()
            return await agent.run(context, specification=spec_content)

        elif agent_type == AgentType.TASK_GENERATOR:
            return await agent.run(context, spec_analysis=spec_analysis)

        elif agent_type == AgentType.INSTRUCTION_BUILDER:
            return await agent.run(context, task=task)

        elif agent_type == AgentType.CODE_GENERATOR:
            return await agent.run(
                context, task=task, project_dir=str(self.project_dir)
            )

        elif agent_type == AgentType.TEST_GENERATOR:
            return await agent.run(context, task=task, project_dir=str(self.project_dir))

        elif agent_type == AgentType.ACCEPTANCE_GENERATOR:
            return await agent.run(context, feature_description=task.name)

        elif agent_type == AgentType.DOCUMENTATION_AGENT:
            return await agent.run(context, project_dir=str(self.project_dir))

        else:
            # Generic execution
            return await agent.run(context, task=task)

    async def _recover_from_error(
        self,
        task: Task,
        context: ExecutionContext,
        error: str,
    ) -> Optional[AgentResponse]:
        """Attempt error recovery using ErrorHandler agent."""
        try:
            error_handler = self.agents.get(AgentType.ERROR_HANDLER)
            if not error_handler:
                return None

            error_details = f"""Task: {task.name}
Error: {error}
Context: Phase {context.current_phase}, Task {context.current_task}"""

            response = await error_handler.run(context, error_details=error_details)
            return response

        except Exception as e:
            self.logger.print_error(f"Error recovery failed: {e}")
            return None

    async def _get_spec_content(self) -> str:
        """Get specification content."""
        spec_path = self.project_dir / "specification.md"
        if spec_path.exists():
            return spec_path.read_text()
        return ""

    def get_phase_summary(self) -> Dict[str, Any]:
        """Get summary of phase execution."""
        return {
            "current_phase": self.current_phase.name if self.current_phase else None,
            "completed_tasks": len(self.completed_tasks),
            "agents_available": list(self.agents.keys()),
        }


__all__ = ["SDKPhaseExecutor"]
