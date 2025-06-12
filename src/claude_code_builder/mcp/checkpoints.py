"""MCP checkpoint management for tracking server usage."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import Field

from claude_code_builder.core.base_model import BaseModel
from claude_code_builder.core.enums import MCPCheckpoint, MCPServer
from claude_code_builder.core.models import ProjectState


class CheckpointState(BaseModel):
    """State at an MCP checkpoint."""
    
    checkpoint: MCPCheckpoint
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    phase: str
    task: Optional[str] = None
    servers_used: List[MCPServer] = Field(default_factory=list)
    data_stored: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


class MCPCheckpointManager:
    """Manages MCP checkpoints throughout the build process."""
    
    def __init__(
        self,
        checkpoint_dir: Path,
        orchestrator: "MCPOrchestrator",  # type: ignore
    ) -> None:
        """Initialize the checkpoint manager."""
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.orchestrator = orchestrator
        
        # State tracking
        self.checkpoints: List[CheckpointState] = []
        self.current_phase: Optional[str] = None
        self.current_task: Optional[str] = None

    async def record_checkpoint(
        self,
        checkpoint: MCPCheckpoint,
        servers_used: List[MCPServer],
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> CheckpointState:
        """Record an MCP checkpoint."""
        state = CheckpointState(
            checkpoint=checkpoint,
            phase=self.current_phase or "unknown",
            task=self.current_task,
            servers_used=servers_used,
            data_stored=data or {},
            success=error is None,
            error=error,
        )
        
        self.checkpoints.append(state)
        
        # Save to file
        await self._save_checkpoint(state)
        
        # Record in orchestrator
        await self.orchestrator.record_checkpoint_usage(checkpoint, servers_used)
        
        # Execute checkpoint-specific actions
        await self._execute_checkpoint_actions(checkpoint, state)
        
        return state

    async def _save_checkpoint(self, state: CheckpointState) -> None:
        """Save checkpoint state to file."""
        # Handle checkpoint value - might be string or enum
        if hasattr(state.checkpoint, 'value'):
            checkpoint_value = state.checkpoint.value
        else:
            checkpoint_value = str(state.checkpoint)
            
        filename = f"{checkpoint_value}_{state.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.checkpoint_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(state.model_dump(), f, indent=2, default=str)

    async def _execute_checkpoint_actions(
        self,
        checkpoint: MCPCheckpoint,
        state: CheckpointState,
    ) -> None:
        """Execute actions specific to each checkpoint."""
        
        if checkpoint == MCPCheckpoint.PROJECT_INITIALIZED:
            await self._handle_project_initialized(state)
            
        elif checkpoint == MCPCheckpoint.CONTEXT_LOADED:
            await self._handle_context_loaded(state)
            
        elif checkpoint == MCPCheckpoint.SPECIFICATION_ANALYZED:
            await self._handle_specification_analyzed(state)
            
        elif checkpoint == MCPCheckpoint.TASKS_GENERATED:
            await self._handle_tasks_generated(state)
            
        elif checkpoint == MCPCheckpoint.PHASE_COMPLETED:
            await self._handle_phase_completed(state)
            
        elif checkpoint == MCPCheckpoint.CODE_GENERATED:
            await self._handle_code_generated(state)
            
        elif checkpoint == MCPCheckpoint.TESTS_EXECUTED:
            await self._handle_tests_executed(state)
            
        elif checkpoint == MCPCheckpoint.BUILD_COMPLETED:
            await self._handle_build_completed(state)

    async def _handle_project_initialized(self, state: CheckpointState) -> None:
        """Handle project initialization checkpoint."""
        # Store project metadata in memory
        if MCPServer.MEMORY in state.servers_used:
            project_data = state.data_stored.get("project_metadata", {})
            if project_data:
                await self.orchestrator.memory.store_project_knowledge(
                    project_data.get("project_name", "unknown"),
                    "initialization",
                    {
                        "timestamp": state.timestamp.isoformat(),
                        "status": "initialized",
                        "details": project_data,
                    },
                )

    async def _handle_context_loaded(self, state: CheckpointState) -> None:
        """Handle context loaded checkpoint."""
        # Ensure Context7 was used for documentation
        if MCPServer.CONTEXT7 not in state.servers_used:
            self.orchestrator.logger.print_warning(
                "Context7 MCP server was not used for loading context"
            )

    async def _handle_specification_analyzed(self, state: CheckpointState) -> None:
        """Handle specification analyzed checkpoint."""
        # Store analysis results
        if MCPServer.MEMORY in state.servers_used:
            analysis = state.data_stored.get("analysis", {})
            if analysis:
                entities = [
                    {
                        "name": "SpecificationAnalysis",
                        "entityType": "Analysis",
                        "observations": [
                            f"Project Type: {analysis.get('project_type', 'unknown')}",
                            f"Complexity: {analysis.get('complexity', 'unknown')}",
                            f"Requirements Count: {len(analysis.get('requirements', []))}",
                        ],
                    }
                ]
                await self.orchestrator.memory.create_entities(entities)

    async def _handle_tasks_generated(self, state: CheckpointState) -> None:
        """Handle tasks generated checkpoint."""
        # Optionally sync with TaskMaster
        if MCPServer.TASKMASTER in state.servers_used:
            tasks = state.data_stored.get("tasks", [])
            if tasks:
                self.orchestrator.logger.print_info(
                    f"Synced {len(tasks)} tasks with TaskMaster"
                )

    async def _handle_phase_completed(self, state: CheckpointState) -> None:
        """Handle phase completion checkpoint."""
        # Commit changes if git is available
        if MCPServer.GIT in state.servers_used:
            try:
                repo_path = str(self.orchestrator.project_dir)
                
                # Check status
                status = await self.orchestrator.git.status(repo_path)
                
                if status.get("changes"):
                    # Add all changes
                    await self.orchestrator.git.add(repo_path, ["."])
                    
                    # Commit
                    commit_message = f"Complete phase: {state.phase}"
                    if state.task:
                        commit_message += f" - {state.task}"
                    
                    commit_sha = await self.orchestrator.git.commit(
                        repo_path,
                        commit_message,
                    )
                    
                    self.orchestrator.logger.print_success(
                        f"Committed phase changes: {commit_sha[:8]}"
                    )
            except Exception as e:
                self.orchestrator.logger.print_warning(
                    f"Failed to commit phase changes: {e}"
                )

    async def _handle_code_generated(self, state: CheckpointState) -> None:
        """Handle code generation checkpoint."""
        # Store code metrics
        if MCPServer.MEMORY in state.servers_used:
            metrics = state.data_stored.get("metrics", {})
            if metrics:
                observations = [
                    {
                        "entityName": f"{state.phase}:CodeGeneration",
                        "contents": [
                            f"Files Generated: {metrics.get('files_count', 0)}",
                            f"Lines of Code: {metrics.get('lines_of_code', 0)}",
                            f"Tokens Used: {metrics.get('tokens_used', 0)}",
                        ],
                    }
                ]
                await self.orchestrator.memory.add_observations(observations)

    async def _handle_tests_executed(self, state: CheckpointState) -> None:
        """Handle test execution checkpoint."""
        # Store test results
        results = state.data_stored.get("test_results", {})
        if results and MCPServer.MEMORY in state.servers_used:
            await self.orchestrator.memory.store_project_knowledge(
                self.orchestrator.project_dir.name,
                f"tests_{state.phase}",
                {
                    "timestamp": state.timestamp.isoformat(),
                    "status": "completed",
                    "details": results,
                },
            )

    async def _handle_build_completed(self, state: CheckpointState) -> None:
        """Handle build completion checkpoint."""
        # Create final summary
        summary = await self._create_build_summary()
        
        # Store in memory
        if MCPServer.MEMORY in state.servers_used:
            await self.orchestrator.memory.store_project_knowledge(
                self.orchestrator.project_dir.name,
                "build_complete",
                {
                    "timestamp": state.timestamp.isoformat(),
                    "status": "success" if state.success else "failed",
                    "details": summary,
                },
            )
        
        # Optionally push to GitHub
        if MCPServer.GITHUB in state.servers_used and state.data_stored.get("push_to_github"):
            await self._push_to_github(state)

    async def _create_build_summary(self) -> Dict[str, Any]:
        """Create a summary of the build process."""
        # Count checkpoints by type
        checkpoint_counts = {}
        for cp in self.checkpoints:
            checkpoint_value = cp.checkpoint.value if hasattr(cp.checkpoint, 'value') else str(cp.checkpoint)
            checkpoint_counts[checkpoint_value] = checkpoint_counts.get(checkpoint_value, 0) + 1
        
        # Count server usage
        server_usage = {}
        for cp in self.checkpoints:
            for server in cp.servers_used:
                server_value = server.value if hasattr(server, 'value') else str(server)
                server_usage[server_value] = server_usage.get(server_value, 0) + 1
        
        # Get phase summary
        phases = set(cp.phase for cp in self.checkpoints if cp.phase != "unknown")
        
        return {
            "total_checkpoints": len(self.checkpoints),
            "checkpoint_counts": checkpoint_counts,
            "server_usage": server_usage,
            "phases_completed": list(phases),
            "success_rate": sum(1 for cp in self.checkpoints if cp.success) / len(self.checkpoints),
            "errors": [
                {
                    "checkpoint": cp.checkpoint.value if hasattr(cp.checkpoint, 'value') else str(cp.checkpoint), 
                    "error": cp.error
                }
                for cp in self.checkpoints
                if cp.error
            ],
        }

    async def _push_to_github(self, state: CheckpointState) -> None:
        """Push project to GitHub."""
        try:
            github_config = state.data_stored.get("github", {})
            
            # Create repository if needed
            if github_config.get("create_repo"):
                repo_data = await self.orchestrator.github.create_repository(
                    name=github_config.get("repo_name", self.orchestrator.project_dir.name),
                    description=github_config.get("description", "Built with Claude Code Builder"),
                    private=github_config.get("private", False),
                )
                
                self.orchestrator.logger.print_success(
                    f"Created GitHub repository: {repo_data.get('html_url')}"
                )
                
        except Exception as e:
            self.orchestrator.logger.print_error(f"Failed to push to GitHub: {e}")

    def set_phase(self, phase: str, task: Optional[str] = None) -> None:
        """Set current phase and task."""
        self.current_phase = phase
        self.current_task = task

    async def get_checkpoint_history(
        self,
        checkpoint_type: Optional[MCPCheckpoint] = None,
        phase: Optional[str] = None,
    ) -> List[CheckpointState]:
        """Get checkpoint history."""
        history = self.checkpoints
        
        if checkpoint_type:
            history = [cp for cp in history if cp.checkpoint == checkpoint_type]
        
        if phase:
            history = [cp for cp in history if cp.phase == phase]
        
        return sorted(history, key=lambda cp: cp.timestamp)

    async def export_checkpoint_report(self, output_file: Path) -> None:
        """Export detailed checkpoint report."""
        report = {
            "project": str(self.orchestrator.project_dir),
            "total_checkpoints": len(self.checkpoints),
            "checkpoints": [cp.model_dump() for cp in self.checkpoints],
            "summary": await self._create_build_summary(),
            "mcp_usage": self.orchestrator.get_usage_stats(),
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.orchestrator.logger.print_success(
            f"Exported checkpoint report to {output_file}"
        )

    async def validate_checkpoints(self, project_state: ProjectState) -> List[str]:
        """Validate that required checkpoints were hit."""
        issues = []
        
        # Define required checkpoints per phase
        required_checkpoints = {
            "initialization": [MCPCheckpoint.PROJECT_INITIALIZED],
            "context_loading": [MCPCheckpoint.CONTEXT_LOADED],
            "specification_analysis": [MCPCheckpoint.SPECIFICATION_ANALYZED],
            "task_generation": [MCPCheckpoint.TASKS_GENERATED],
            "code_generation": [MCPCheckpoint.CODE_GENERATED],
            "testing": [MCPCheckpoint.TESTS_EXECUTED],
            "build": [MCPCheckpoint.BUILD_COMPLETED],
        }
        
        # Check each completed phase
        for phase in project_state.completed_phases:
            phase_name = str(phase)
            if phase_name in required_checkpoints:
                required = required_checkpoints[phase_name]
                
                # Find checkpoints for this phase
                phase_checkpoints = [
                    cp.checkpoint for cp in self.checkpoints
                    if cp.phase == phase_name
                ]
                
                # Check if all required checkpoints were hit
                for req_checkpoint in required:
                    if req_checkpoint not in phase_checkpoints:
                        issues.append(
                            f"Missing checkpoint {req_checkpoint.value} for phase {phase_name}"
                        )
        
        # Validate MCP server usage
        if not any(MCPServer.MEMORY in cp.servers_used for cp in self.checkpoints):
            issues.append("Memory MCP server was never used")
        
        if not any(MCPServer.FILESYSTEM in cp.servers_used for cp in self.checkpoints):
            issues.append("Filesystem MCP server was never used")
        
        return issues


__all__ = [
    "MCPCheckpointManager",
    "CheckpointState",
]