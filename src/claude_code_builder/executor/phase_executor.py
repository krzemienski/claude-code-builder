"""Phase Executor for managing phase-by-phase execution."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from claude_code_builder.agents import (
    AgentOrchestrator,
    BaseAgent,
    CodeGenerator,
    ErrorHandler,
    InstructionBuilder,
    SpecAnalyzer,
    TaskGenerator,
    TestGenerator,
)
from claude_code_builder.core.context_manager import ContextManager
from claude_code_builder.core.enums import AgentType, MCPCheckpoint, TaskStatus
from claude_code_builder.core.exceptions import PhaseExecutionError
from claude_code_builder.core.logging_system import ComprehensiveLogger
from claude_code_builder.core.models import (
    ExecutionContext,
    Phase,
    ProjectState,
    Task,
    TaskBreakdown,
)
from claude_code_builder.executor.executor import ClaudeCodeExecutor
from claude_code_builder.mcp.orchestrator import MCPOrchestrator


class PhaseExecutor:
    """Executes individual phases of the build process."""
    
    def __init__(
        self,
        executor: ClaudeCodeExecutor,
        context_manager: ContextManager,
        mcp_orchestrator: MCPOrchestrator,
        logger: ComprehensiveLogger,
        project_dir: Path,
    ) -> None:
        """Initialize the phase executor."""
        self.executor = executor
        self.context_manager = context_manager
        self.mcp_orchestrator = mcp_orchestrator
        self.logger = logger
        self.project_dir = project_dir
        
        # Initialize agents
        self.agents = self._initialize_agents()
        self.agent_orchestrator = AgentOrchestrator(self.agents, logger)
        
        # Track execution state
        self.current_phase: Optional[Phase] = None
        self.completed_tasks: Set[str] = set()

    def _initialize_agents(self) -> Dict[AgentType, BaseAgent]:
        """Initialize all agents."""
        agents = {}
        
        # Create each agent
        agent_classes = {
            AgentType.SPEC_ANALYZER: SpecAnalyzer,
            AgentType.TASK_GENERATOR: TaskGenerator,
            AgentType.INSTRUCTION_BUILDER: InstructionBuilder,
            AgentType.CODE_GENERATOR: CodeGenerator,
            AgentType.TEST_GENERATOR: TestGenerator,
            AgentType.ERROR_HANDLER: ErrorHandler,
        }
        
        for agent_type, agent_class in agent_classes.items():
            agents[agent_type] = agent_class(
                executor=self.executor,
                context_manager=self.context_manager,
                mcp_orchestrator=self.mcp_orchestrator,
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
        """Execute a complete phase."""
        self.current_phase = phase
        phase_start = datetime.utcnow()
        
        try:
            self.logger.print_info(f"Executing phase: {phase.name}")
            
            # Update MCP checkpoint manager
            self.mcp_orchestrator.checkpoint_manager.set_phase(
                phase.name,
                None,
            )
            
            # Get phase tasks
            phase_tasks = [
                task for task in task_breakdown.tasks
                if task.phase_id == phase.id
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
                        # Note: priority is already a string due to use_enum_values=True
                        if task.priority == "high" and not result.get("recovered"):
                            raise PhaseExecutionError(
                                phase.name,
                                f"Critical task failed: {task.name}",
                                task.name,
                            )
            
            # Record phase completion
            await self.mcp_orchestrator.checkpoint_manager.record_checkpoint(
                MCPCheckpoint.PHASE_COMPLETED,
                list(self.mcp_orchestrator.server_manager.connections.keys()),
                {
                    "phase": phase.name,
                    "tasks_completed": completed,
                    "tasks_failed": failed,
                    "duration": (datetime.utcnow() - phase_start).total_seconds(),
                },
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
                    str(dep_id) in self.completed_tasks or str(dep_id) not in task_ids
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
            # Note: priority and complexity are already strings due to use_enum_values=True
            # Since Task model doesn't have complexity field, use estimated_hours
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
                dep_task = next(
                    (t for t in all_tasks if t.id == dep_id),
                    None
                )
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
        """Execute a single task."""
        task_start = datetime.utcnow()
        
        try:
            self.logger.print_info(f"Executing task: {task.name}")
            
            # Update checkpoint manager
            self.mcp_orchestrator.checkpoint_manager.set_phase(
                self.current_phase.name if self.current_phase else "unknown",
                task.name,
            )
            
            # Create execution context
            context = ExecutionContext(
                session_id=self.executor.session_id if hasattr(self.executor, 'session_id') else "default",
                current_phase=self.current_phase.id if self.current_phase else None,
                current_task=task.id,
                completed_phases=set(),  # Would need to track this
                completed_tasks={UUID(int=int(tid)) for tid in self.completed_tasks if tid.isdigit()} if self.completed_tasks else set(),
            )
            
            # Define workflow based on task type
            workflow = await self._get_task_workflow(task)
            
            # Execute workflow
            results = await self.agent_orchestrator.execute_workflow(
                workflow,
                context,
            )
            
            # Check results
            success = all(r.success for r in results)
            
            if not success:
                # Try error recovery
                error_handler = self.agents[AgentType.ERROR_HANDLER]
                recovery_result = await error_handler.run(
                    context,
                    error=results[-1].error if results else "Unknown error",
                )
                
                if recovery_result.success:
                    # Retry with recovery strategy
                    results = await self.agent_orchestrator.execute_workflow(
                        workflow,
                        context,
                    )
                    success = all(r.success for r in results)
            
            return {
                "success": success,
                "duration": (datetime.utcnow() - task_start).total_seconds(),
                "results": [r.model_dump() for r in results],
                "recovered": not all(r.success for r in results[:1]) and success,
            }
            
        except Exception as e:
            self.logger.print_error(f"Task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.utcnow() - task_start).total_seconds(),
            }

    async def _get_task_workflow(self, task: Task) -> List[Dict[str, Any]]:
        """Get workflow for a task."""
        task_lower = task.name.lower()
        
        # Determine workflow based on task type
        if "analy" in task_lower or "spec" in task_lower:
            return [
                {
                    "agent": "SPEC_ANALYZER",
                    "params": {
                        "spec_content": await self._get_spec_content(),
                        "spec_path": self.project_dir / "specification.md",
                    },
                    "required": True,
                },
            ]
        
        elif "generat" in task_lower and "task" in task_lower:
            return [
                {
                    "agent": "TASK_GENERATOR",
                    "params": {
                        "spec_analysis": await self._get_spec_analysis(),
                    },
                    "required": True,
                },
            ]
        
        elif "instruct" in task_lower or "plan" in task_lower:
            return [
                {
                    "agent": "INSTRUCTION_BUILDER",
                    "params": {
                        "task": task,
                        "task_breakdown": await self._get_task_breakdown(),
                        "project_context": await self._get_project_context(),
                    },
                    "required": True,
                },
            ]
        
        elif "implement" in task_lower or "code" in task_lower:
            return [
                {
                    "agent": "INSTRUCTION_BUILDER",
                    "params": {
                        "task": task,
                        "task_breakdown": await self._get_task_breakdown(),
                        "project_context": await self._get_project_context(),
                    },
                    "required": True,
                },
                {
                    "agent": "CODE_GENERATOR",
                    "params": {
                        "task": task,
                        "instructions": "{{previous.result}}",  # From instruction builder
                        "project_dir": self.project_dir,
                    },
                    "required": True,
                },
            ]
        
        elif "test" in task_lower:
            return [
                {
                    "agent": "TEST_GENERATOR",
                    "params": {
                        "task": task,
                        "project_dir": self.project_dir,
                    },
                    "required": True,
                },
            ]
        
        else:
            # Default workflow
            return [
                {
                    "agent": "CODE_GENERATOR",
                    "params": {
                        "task": task,
                        "instructions": {"instructions": [f"Implement {task.name}"]},
                        "project_dir": self.project_dir,
                    },
                    "required": True,
                },
            ]

    async def _get_spec_content(self) -> str:
        """Get specification content."""
        spec_path = self.project_dir / "specification.md"
        if spec_path.exists():
            return spec_path.read_text()
        return ""

    async def _get_spec_analysis(self) -> Any:
        """Get specification analysis from memory."""
        # Would retrieve from memory MCP
        return None

    async def _get_task_breakdown(self) -> TaskBreakdown:
        """Get task breakdown from memory."""
        # Would retrieve from memory MCP
        return TaskBreakdown(phases=[], tasks=[])

    async def _get_project_context(self) -> Dict[str, Any]:
        """Get project context."""
        return {
            "project_name": self.project_dir.name,
            "project_type": "python_package",
            "technology_stack": ["python", "asyncio", "pydantic"],
        }

    def get_phase_summary(self) -> Dict[str, Any]:
        """Get summary of phase execution."""
        return {
            "current_phase": self.current_phase.name if self.current_phase else None,
            "completed_tasks": len(self.completed_tasks),
            "agent_summary": self.agent_orchestrator.get_execution_summary(),
        }


__all__ = ["PhaseExecutor"]