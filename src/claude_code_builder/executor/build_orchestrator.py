"""Build Orchestrator for managing the complete build process."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from claude_code_builder.core.config import BuildConfig
from claude_code_builder.core.context_manager import ContextManager, SpecificationChunker
from claude_code_builder.core.enums import Complexity, MCPCheckpoint, MCPServer
from claude_code_builder.core.exceptions import (
    ClaudeCodeBuilderError,
    PhaseExecutionError,
    ResourceLimitExceeded,
    SpecificationError,
)
from claude_code_builder.core.logging_system import ComprehensiveLogger
from claude_code_builder.core.models import (
    BuildMetrics,
    Phase,
    ProjectState,
    SpecAnalysis,
    TaskBreakdown,
)
from claude_code_builder.core.output_manager import OutputManager, ProjectDirectory
from claude_code_builder.executor.executor import ClaudeCodeExecutor
from claude_code_builder.executor.phase_executor import PhaseExecutor
from claude_code_builder.mcp.checkpoints import MCPCheckpointManager
from claude_code_builder.mcp.orchestrator import MCPOrchestrator


class BuildOrchestrator:
    """Orchestrates the complete Claude Code Builder process."""
    
    def __init__(
        self,
        spec_path: Path,
        output_dir: Optional[Path] = None,
        build_config: Optional[BuildConfig] = None,
        resume_from: Optional[Path] = None,
    ) -> None:
        """Initialize the build orchestrator."""
        self.spec_path = spec_path
        self.output_dir = output_dir
        self.build_config = build_config or BuildConfig()
        self.resume_from = resume_from
        
        # Will be initialized in setup
        self.project_dir: Optional[ProjectDirectory] = None
        self.logger: Optional[ComprehensiveLogger] = None
        self.executor: Optional[ClaudeCodeExecutor] = None
        self.context_manager: Optional[ContextManager] = None
        self.mcp_orchestrator: Optional[MCPOrchestrator] = None
        self.phase_executor: Optional[PhaseExecutor] = None
        self.checkpoint_manager: Optional[MCPCheckpointManager] = None
        
        # Build state
        self.project_state: Optional[ProjectState] = None
        self.spec_analysis: Optional[SpecAnalysis] = None
        self.task_breakdown: Optional[TaskBreakdown] = None
        self.build_start_time: Optional[datetime] = None
        self.session_id: str = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    async def setup(self) -> None:
        """Set up the build environment."""
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
        
        # Initialize components
        self.executor = ClaudeCodeExecutor(
            logger=self.logger,
        )
        
        self.context_manager = ContextManager(
            max_context_tokens=150000,
            chunker=SpecificationChunker(),
        )
        
        # Initialize MCP
        from claude_code_builder.core.config import settings
        
        self.mcp_orchestrator = MCPOrchestrator(
            settings.default_mcp_config,
            self.project_dir.path,
            self.logger,
        )
        
        await self.mcp_orchestrator.initialize()
        
        self.checkpoint_manager = MCPCheckpointManager(
            self.project_dir.subdirs["checkpoints"],
            self.mcp_orchestrator,
        )
        self.mcp_orchestrator.checkpoint_manager = self.checkpoint_manager
        
        # Initialize phase executor
        self.phase_executor = PhaseExecutor(
            self.executor,
            self.context_manager,
            self.mcp_orchestrator,
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
        
        # Record initialization checkpoint
        await self.checkpoint_manager.record_checkpoint(
            MCPCheckpoint.PROJECT_INITIALIZED,
            [MCPServer.FILESYSTEM, MCPServer.MEMORY],
            {"project_metadata": self.project_dir.metadata.model_dump()},
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
        """Execute the complete build process."""
        self.build_start_time = datetime.utcnow()
        
        try:
            self.logger.print_info("Starting Claude Code Builder")
            
            # Phase 1: Load specification
            await self._load_specification()
            
            # Phase 2: Analyze specification
            await self._analyze_specification()
            
            # Phase 3: Generate task breakdown
            await self._generate_tasks()
            
            # Phase 4: Execute phases
            await self._execute_phases()
            
            # Phase 5: Validate and finalize
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
            
            # Record failure checkpoint
            await self.checkpoint_manager.record_checkpoint(
                MCPCheckpoint.BUILD_COMPLETED,
                list(self.mcp_orchestrator.server_manager.connections.keys()),
                error=str(e),
            )
            
            raise
        
        finally:
            # Cleanup
            await self.cleanup()

    async def _load_specification(self) -> None:
        """Load and process the specification."""
        self.logger.print_info("Loading specification...")
        
        # Load spec content
        spec_content = self.spec_path.read_text()
        
        # Load into context manager
        load_result = await self.context_manager.load_specification(
            self.spec_path,
            spec_content,
        )
        
        self.logger.print_info(
            f"Specification loaded: {load_result['total_tokens']} tokens, "
            f"{load_result['chunks']} chunks"
        )
        
        # Record checkpoint
        await self.checkpoint_manager.record_checkpoint(
            MCPCheckpoint.CONTEXT_LOADED,
            [MCPServer.FILESYSTEM, MCPServer.MEMORY],
            {"load_result": load_result},
        )

    async def _analyze_specification(self) -> None:
        """Analyze the specification."""
        if self.project_state and self.project_state.spec_analysis:
            self.spec_analysis = self.project_state.spec_analysis
            self.logger.print_info("Using cached specification analysis")
            return
        
        self.logger.print_info("Analyzing specification...")
        
        # Get spec analyzer agent
        from claude_code_builder.agents import SpecAnalyzer
        
        spec_analyzer = SpecAnalyzer(
            executor=self.executor,
            context_manager=self.context_manager,
            mcp_orchestrator=self.mcp_orchestrator,
            logger=self.logger,
        )
        
        # Create context
        from claude_code_builder.core.models import ExecutionContext
        from uuid import uuid4
        
        context = ExecutionContext(
            session_id=self.session_id,
        )
        
        # Analyze
        spec_content = self.spec_path.read_text()
        
        # LOG SPEC CONTENT BEING ANALYZED
        self.logger.logger.info(
            "spec_analysis_input",
            spec_path=str(self.spec_path),
            spec_length=len(spec_content),
            spec_preview=spec_content[:1000] + "..." if len(spec_content) > 1000 else spec_content,
            spec_lines=spec_content.count('\n'),
        )
        
        result = await spec_analyzer.run(
            context,
            spec_content=spec_content,
            spec_path=self.spec_path,
        )
        
        if not result.success:
            raise SpecificationError(
                f"Specification analysis failed: {result.error}"
            )
        
        self.spec_analysis = result.result
        
        # Update project state
        self.project_state.spec_analysis = self.spec_analysis
        self.project_state.project_type = self.spec_analysis.project_type
        # Estimate tokens based on complexity
        complexity_tokens = {
            Complexity.SIMPLE: 500000,
            Complexity.MODERATE: 1000000,
            Complexity.COMPLEX: 2000000,
            Complexity.VERY_COMPLEX: 3000000,
        }
        self.project_state.estimated_tokens = complexity_tokens.get(self.spec_analysis.complexity, 1000000)
        
        await self.project_dir.save_state(self.project_state)
        
        self.logger.print_success(
            f"Analysis complete: {self.spec_analysis.project_name} "
            f"({self.spec_analysis.complexity if isinstance(self.spec_analysis.complexity, str) else self.spec_analysis.complexity.value} complexity)"
        )

    async def _generate_tasks(self) -> None:
        """Generate task breakdown."""
        if self.project_state and self.project_state.task_breakdown:
            self.task_breakdown = self.project_state.task_breakdown
            self.logger.print_info("Using cached task breakdown")
            return
        
        self.logger.print_info("Generating task breakdown...")
        
        # Get task generator agent
        from claude_code_builder.agents import TaskGenerator
        
        task_generator = TaskGenerator(
            executor=self.executor,
            context_manager=self.context_manager,
            mcp_orchestrator=self.mcp_orchestrator,
            logger=self.logger,
        )
        
        # Create context
        from claude_code_builder.core.models import ExecutionContext
        
        context = ExecutionContext(
            session_id=self.session_id,
        )
        
        # Generate tasks
        result = await task_generator.run(
            context,
            spec_analysis=self.spec_analysis,
        )
        
        if not result.success:
            raise ClaudeCodeBuilderError(
                f"Task generation failed: {result.error}"
            )
        
        self.task_breakdown = result.result
        
        # Update project state
        self.project_state.task_breakdown = self.task_breakdown
        await self.project_dir.save_state(self.project_state)
        
        self.logger.print_success(
            f"Generated {len(self.task_breakdown.tasks)} tasks "
            f"across {len(self.task_breakdown.phases)} phases"
        )

    async def _execute_phases(self) -> None:
        """Execute all phases."""
        phases_to_execute = self._get_phases_to_execute()
        
        self.logger.print_info(
            f"Executing {len(phases_to_execute)} phases..."
        )
        
        for i, phase in enumerate(phases_to_execute, 1):
            self.logger.print_info(
                f"\n{'='*60}\n"
                f"Phase {i}/{len(phases_to_execute)}: {phase.name}\n"
                f"{'='*60}"
            )
            
            # Check resource limits
            if self.executor.total_tokens_used > self.build_config.max_tokens:
                raise ResourceLimitExceeded(
                    "Token limit exceeded",
                    "tokens",
                    self.executor.total_tokens_used,
                    self.build_config.max_tokens,
                )
            
            if self.executor.total_cost > self.build_config.max_cost:
                raise ResourceLimitExceeded(
                    "Cost limit exceeded",
                    "cost",
                    self.executor.total_cost,
                    self.build_config.max_cost,
                )
            
            # Execute phase
            result = await self.phase_executor.execute_phase(
                phase,
                self.task_breakdown,
                self.project_state,
                self.spec_analysis,
            )
            
            # Update state
            self.project_state.current_phase = phase.id
            self.project_state.completed_phases.append(phase.id)
            self.project_state.completed_tasks.extend(
                self.phase_executor.completed_tasks
            )
            self.project_state.api_calls_made = self.executor.api_calls_made
            self.project_state.tokens_used = self.executor.total_tokens_used
            self.project_state.cost_incurred = self.executor.total_cost
            self.project_state.last_checkpoint = datetime.utcnow()
            
            # Save checkpoint
            await self.project_dir.save_state(self.project_state)
            
            # Auto-commit if enabled
            if self.build_config.auto_commit:
                await self._commit_changes(phase)
            
            self.logger.print_info(
                f"Phase complete: {result['tasks_completed']} tasks completed"
            )
            
            # Check for phase failure
            if not result["success"] and not self.build_config.continue_on_error:
                raise PhaseExecutionError(
                    phase.name,
                    f"Phase failed with {result['tasks_failed']} failed tasks",
                )

    def _get_phases_to_execute(self) -> List[Phase]:
        """Get phases that need to be executed."""
        if not self.task_breakdown:
            return []
        
        # Filter based on configuration
        phases = self.task_breakdown.phases
        
        if self.build_config.phases_to_execute:
            phases = [
                p for p in phases
                if p.name in self.build_config.phases_to_execute
            ]
        
        # Filter out completed phases if resuming
        if self.project_state:
            completed_ids = set(self.project_state.completed_phases)
            phases = [p for p in phases if p.id not in completed_ids]
        
        return phases

    async def _commit_changes(self, phase: Phase) -> None:
        """Commit changes for a phase."""
        try:
            await self.mcp_orchestrator.git.add(
                str(self.project_dir.path),
                ["."],
            )
            
            message = self.build_config.commit_message_format.format(
                type="feat",
                scope=phase.name.lower().replace(" ", "-"),
                description=f"Complete {phase.name}",
            )
            
            await self.mcp_orchestrator.git.commit(
                str(self.project_dir.path),
                message,
            )
            
            self.logger.print_info("Changes committed")
            
        except Exception as e:
            self.logger.print_warning(f"Failed to commit: {e}")

    async def _finalize_build(self) -> None:
        """Finalize the build process."""
        self.logger.print_info("Finalizing build...")
        
        # Save final state
        self.project_state.build_completed = True
        self.project_state.completed_at = datetime.utcnow()
        
        await self.project_dir.save_final_state()
        await self.project_dir.save_state(self.project_state)
        
        # Export logs
        await self.logger.export_logs(
            self.project_dir.subdirs["artifacts"]
        )
        
        # Export MCP usage report
        await self.mcp_orchestrator.export_usage_report(
            self.project_dir.subdirs["artifacts"]
        )
        
        # Export checkpoint report
        await self.checkpoint_manager.export_checkpoint_report(
            self.project_dir.subdirs["artifacts"] / "checkpoint_report.json"
        )
        
        # Record completion
        await self.checkpoint_manager.record_checkpoint(
            MCPCheckpoint.BUILD_COMPLETED,
            list(self.mcp_orchestrator.server_manager.connections.keys()),
            {
                "success": True,
                "duration": (
                    datetime.utcnow() - self.build_start_time
                ).total_seconds(),
                "metrics": {
                    "phases_completed": len(self.project_state.completed_phases),
                    "tasks_completed": len(self.project_state.completed_tasks),
                    "total_cost": self.project_state.cost_incurred,
                    "total_tokens": self.project_state.tokens_used,
                },
            },
        )

    async def _generate_build_metrics(self) -> BuildMetrics:
        """Generate build metrics."""
        duration = datetime.utcnow() - self.build_start_time
        
        return BuildMetrics(
            total_phases=len(self.task_breakdown.phases) if self.task_breakdown else 0,
            completed_phases=len(self.project_state.completed_phases),
            total_tasks=len(self.task_breakdown.tasks) if self.task_breakdown else 0,
            completed_tasks=len(self.project_state.completed_tasks),
            failed_tasks=0,  # Would need to track this
            total_tokens_used=self.project_state.tokens_used,
            total_cost=self.project_state.cost_incurred,
            total_api_calls=self.project_state.api_calls_made,
            build_duration_seconds=duration.total_seconds(),
            files_generated=await self._count_generated_files(),
            lines_of_code=await self._count_lines_of_code(),
            test_coverage=0.0,  # Would need to calculate
            mcp_servers_used=len(self.mcp_orchestrator.server_calls),
            checkpoints_created=len(self.checkpoint_manager.checkpoints),
        )

    async def _count_generated_files(self) -> int:
        """Count generated files."""
        src_dir = self.project_dir.subdirs["source"]
        count = 0
        
        for path in src_dir.rglob("*.py"):
            count += 1
        
        return count

    async def _count_lines_of_code(self) -> int:
        """Count lines of code."""
        src_dir = self.project_dir.subdirs["source"]
        total_lines = 0
        
        for path in src_dir.rglob("*.py"):
            try:
                content = path.read_text()
                total_lines += len(content.split('\n'))
            except Exception:
                pass
        
        return total_lines

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Shutdown MCP
            if self.mcp_orchestrator:
                await self.mcp_orchestrator.shutdown()
            
            # Final logging
            if self.logger:
                summary = self.executor.get_usage_summary() if self.executor else {}
                self.logger.print_info(
                    f"\nBuild Summary:\n"
                    f"- API Calls: {summary.get('api_calls', 0)}\n"
                    f"- Total Tokens: {summary.get('total_tokens', 0)}\n"
                    f"- Total Cost: ${summary.get('total_cost', 0):.2f}"
                )
                
        except Exception as e:
            print(f"Cleanup error: {e}")


__all__ = ["BuildOrchestrator"]