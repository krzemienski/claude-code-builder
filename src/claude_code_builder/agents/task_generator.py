"""Task Generator agent for Claude Code Builder."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

from claude_code_builder.agents.base import BaseAgent, AgentResponse
from claude_code_builder.core.enums import (
    AgentType,
    Complexity,
    MCPCheckpoint,
    MCPServer,
    Priority,
    TaskStatus,
)
from claude_code_builder.core.models import (
    ExecutionContext,
    Phase,
    SpecAnalysis,
    Task,
    TaskBreakdown,
)


class TaskGenerator(BaseAgent):
    """Generates comprehensive task breakdown from specification analysis."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskGenerator."""
        super().__init__(AgentType.TASK_GENERATOR, *args, **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for task generation."""
        return """You are a Task Generator for Claude Code Builder.

Your role is to create a comprehensive task breakdown from the specification analysis:
1. Define clear phases of development
2. Break down each phase into specific, actionable tasks
3. Establish task dependencies and ordering
4. Estimate complexity and effort for each task
5. Define acceptance criteria for task completion
6. Identify required tools and resources
7. Flag critical path tasks

You must:
- Create tasks that are specific and measurable
- Ensure all requirements are covered by tasks
- Maintain logical task dependencies
- Balance task granularity (not too large, not too small)
- Consider parallel execution opportunities
- Include testing and documentation tasks
- Use MCP servers for enhanced task management

Output structured task breakdown following the TaskBreakdown model."""

    def get_tools(self) -> List[str]:
        """Get tools available to this agent."""
        return [
            "Read",
            "Write",
            "TodoWrite",
        ]

    async def execute(
        self,
        context: ExecutionContext,
        spec_analysis: SpecAnalysis,
        custom_phases: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> AgentResponse:
        """Generate task breakdown from specification analysis."""
        try:
            await self.log_progress("Starting task generation")
            
            # Check for existing task breakdown
            existing_breakdown = await self._check_existing_breakdown(
                spec_analysis.project_name
            )
            if existing_breakdown and not kwargs.get("force_regenerate"):
                await self.log_progress("Found existing task breakdown")
                return AgentResponse(
                    agent_type=self.agent_type,
                    success=True,
                    result=existing_breakdown,
                    metadata={"cached": True},
                )
            
            # Generate phases
            phases = await self._generate_phases(spec_analysis, custom_phases)
            
            # Generate tasks for each phase
            all_tasks = []
            for phase in phases:
                phase_tasks = await self._generate_phase_tasks(
                    phase,
                    spec_analysis,
                    all_tasks,
                )
                phase.tasks = phase_tasks  # Assign tasks to the phase
                all_tasks.extend(phase_tasks)
            
            # Resolve task dependencies from names to UUIDs
            all_tasks = await self._resolve_task_dependencies(all_tasks)
            
            # Optimize task dependencies
            all_tasks = await self._optimize_dependencies(all_tasks)
            
            # Calculate totals
            total_hours = sum(task.estimated_hours for task in all_tasks)
            total_cost = total_hours * 50  # Assuming $50/hour rate
            
            # Create task breakdown
            breakdown = TaskBreakdown(
                phases=phases,
                total_estimated_hours=total_hours,
                total_estimated_cost=total_cost,
                critical_path=await self._identify_critical_path(all_tasks),
                parallel_phases=[]  # Will be calculated if needed
            )
            
            # Validate breakdown
            breakdown = await self._validate_breakdown(breakdown, spec_analysis)
            
            # Store in memory
            await self._store_breakdown(breakdown, spec_analysis)
            
            # Optionally sync with TaskMaster
            if MCPServer.TASKMASTER in self.mcp_orchestrator.mcp_config.servers:
                await self._sync_with_taskmaster(breakdown)
            
            # Calculate metrics
            metrics = self._calculate_breakdown_metrics(breakdown)
            
            await self.log_progress("Task generation completed successfully")
            
            # Record checkpoint
            await self.mcp_orchestrator.checkpoint_manager.record_checkpoint(
                MCPCheckpoint.TASKS_GENERATED,
                self.mcp_servers_used,
                {"tasks": [t.model_dump(mode='json') for t in all_tasks[:10]]},  # Sample
            )
            
            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                result=breakdown,
                metadata=metrics,
                tokens_used=sum(call.tokens_total for call in self.api_calls),
                cost=sum(call.estimated_cost for call in self.api_calls),
            )
            
        except Exception as e:
            return await self.handle_error(e, "task generation", recoverable=False)

    async def _check_existing_breakdown(
        self,
        project_name: str,
    ) -> Optional[TaskBreakdown]:
        """Check for existing task breakdown in memory."""
        try:
            results = await self.search_memory(f"TaskBreakdown:{project_name}")
            if results:
                # Parse stored breakdown
                for node in results:
                    for obs in node.get("observations", []):
                        if obs.startswith("{") and "phases" in obs:
                            data = json.loads(obs)
                            # Reconstruct objects
                            phases = [Phase(**p) for p in data["phases"]]
                            # Assign tasks to phases
                            for phase in phases:
                                phase_tasks = [Task(**t) for t in data["tasks"] if t.get("phase_id") == str(phase.id)]
                                phase.tasks = phase_tasks
                            
                            return TaskBreakdown(
                                phases=phases,
                                total_estimated_hours=data.get("total_estimated_hours", 0.0),
                                total_estimated_cost=data.get("total_estimated_cost", 0.0),
                                critical_path=[UUID(id) for id in data.get("critical_path", [])],
                                parallel_phases=[[UUID(id) for id in track] for track in data.get("parallel_phases", [])],
                            )
            return None
        except Exception:
            return None

    async def _generate_phases(
        self,
        spec_analysis: SpecAnalysis,
        custom_phases: Optional[List[str]] = None,
    ) -> List[Phase]:
        """Generate development phases."""
        if custom_phases:
            # Use custom phases
            phases = []
            for i, phase_name in enumerate(custom_phases):
                phases.append(
                    Phase(
                        name=phase_name,
                        description=f"Custom phase: {phase_name}",
                        order=i + 1,
                        dependencies=[],
                    )
                )
            return phases
        
        # Generate phases based on project type and complexity
        messages = [
            {
                "role": "user",
                "content": f"""Generate development phases for this project:

Project: {spec_analysis.project_name}
Type: {spec_analysis.project_type if isinstance(spec_analysis.project_type, str) else spec_analysis.project_type.value}
Complexity: {spec_analysis.complexity if isinstance(spec_analysis.complexity, str) else spec_analysis.complexity.value}
Estimated Hours: {spec_analysis.estimated_hours}

Technical Requirements:
{chr(10).join(spec_analysis.technical_requirements[:10])}

Generate approximately 10-15 phases that cover:
1. Project setup and initialization
2. Core functionality implementation
3. Integration and interfaces
4. Testing and validation
5. Documentation and deployment

For each phase provide:
- name
- description
- dependencies on other phases
- key deliverables

Format as JSON array of Phase objects."""
            }
        ]
        
        response = await self.call_claude(messages, max_tokens=4000)
        content = response.get("content", "")
        
        # Parse response
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
            phases_data = json.loads(json_str)
        else:
            # Fallback to default phases
            phases_data = self._get_default_phases(spec_analysis)
        
        # Create Phase objects
        phases = []
        
        for i, phase_data in enumerate(phases_data):
            phases.append(
                Phase(
                    name=phase_data["name"],
                    description=phase_data.get("description", ""),
                    order=i + 1,
                    dependencies=[],  # Will be set after all phases created
                )
            )
        
        # Create phase_map after phases are created (so they have IDs)
        phase_map = {phase.name: phase.id for phase in phases}
        
        # Set dependencies
        for i, phase_data in enumerate(phases_data):
            if "depends_on" in phase_data:
                dep_names = phase_data["depends_on"]
                if isinstance(dep_names, str):
                    dep_names = [dep_names]
                
                dep_ids = [
                    phase_map[name] for name in dep_names
                    if name in phase_map
                ]
                phases[i].dependencies = dep_ids
        
        return phases

    async def _generate_phase_tasks(
        self,
        phase: Phase,
        spec_analysis: SpecAnalysis,
        existing_tasks: List[Task],
    ) -> List[Task]:
        """Generate tasks for a specific phase."""
        # Get relevant requirements for this phase
        relevant_reqs = await self._get_phase_requirements(
            phase,
            spec_analysis.technical_requirements,
        )
        
        messages = [
            {
                "role": "user",
                "content": f"""Generate detailed tasks for this development phase:

Phase: {phase.name}
Description: {phase.description}

Relevant Requirements:
{chr(10).join(relevant_reqs)}

Project Context:
- Type: {spec_analysis.project_type if isinstance(spec_analysis.project_type, str) else spec_analysis.project_type.value}
- Stack: {', '.join(spec_analysis.suggested_technologies)}
- Complexity: {spec_analysis.complexity if isinstance(spec_analysis.complexity, str) else spec_analysis.complexity.value}

Generate specific, actionable tasks that:
1. Cover all requirements for this phase
2. Include clear acceptance criteria
3. Have realistic time estimates
4. Identify dependencies on other tasks
5. Specify required tools/resources

For each task provide:
- title
- description
- acceptance_criteria (list)
- estimated_hours
- complexity (low/medium/high)
- priority (low/medium/high)
- required_tools (list)
- dependencies (task titles)

Format as JSON array of Task objects."""
            }
        ]
        
        response = await self.call_claude(messages, max_tokens=6000)
        content = response.get("content", "")
        
        # Parse tasks
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
            tasks_data = json.loads(json_str)
        else:
            # Generate default tasks
            tasks_data = self._get_default_phase_tasks(phase)
        
        # Create Task objects
        tasks = []
        task_name_to_deps = {}  # Store dependencies by task name
        
        for task_data in tasks_data:
            task_name = task_data.get("title", task_data.get("name", "Unnamed Task"))
            task = Task(
                phase_id=phase.id,
                name=task_name,
                description=task_data.get("description", ""),
                estimated_hours=task_data.get("estimated_hours", 4),
                priority=Priority[task_data.get("priority", "MEDIUM").upper()],
                dependencies=[],  # Will be set after all tasks created
                context_required=task_data.get("context_required", []),
                outputs=task_data.get("outputs", []),
            )
            tasks.append(task)
            
            # Store the dependency names for later resolution
            if "dependencies" in task_data:
                deps = task_data["dependencies"]
                if isinstance(deps, str):
                    deps = [deps]
                task_name_to_deps[task_name] = deps
        
        # Now resolve dependencies by name to UUIDs
        # This needs to be done after all tasks in the project are created
        # Store the dependency info for later resolution
        for task in tasks:
            if task.name in task_name_to_deps:
                task._dependency_names = task_name_to_deps[task.name]
        
        return tasks

    async def _get_phase_requirements(
        self,
        phase: Phase,
        all_requirements: List[str],
    ) -> List[str]:
        """Get requirements relevant to a phase."""
        # Simple keyword matching - could be enhanced with NLP
        phase_keywords = {
            "setup": ["install", "configure", "initialize", "structure"],
            "core": ["implement", "create", "build", "develop"],
            "integration": ["integrate", "connect", "interface", "api"],
            "testing": ["test", "validate", "verify", "check"],
            "documentation": ["document", "readme", "guide", "tutorial"],
            "deployment": ["deploy", "package", "release", "publish"],
        }
        
        relevant_reqs = []
        phase_lower = phase.name.lower()
        
        # Find matching keywords
        keywords = []
        for key, words in phase_keywords.items():
            if key in phase_lower:
                keywords.extend(words)
        
        # Match requirements
        for req in all_requirements:
            req_lower = req.lower()
            if any(keyword in req_lower for keyword in keywords):
                relevant_reqs.append(req)
        
        # If no matches, take a portion based on phase order
        if not relevant_reqs:
            chunk_size = len(all_requirements) // 5  # Assume ~5 phases
            start_idx = (phase.order - 1) * chunk_size
            end_idx = start_idx + chunk_size
            relevant_reqs = all_requirements[start_idx:end_idx]
        
        return relevant_reqs[:20]  # Limit to 20 requirements

    async def _resolve_task_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Resolve task dependencies from names to UUIDs."""
        # Create a mapping of task names to task objects
        task_by_name = {task.name: task for task in tasks}
        
        # Resolve dependencies
        for task in tasks:
            if hasattr(task, '_dependency_names'):
                resolved_deps = []
                for dep_name in task._dependency_names:
                    if dep_name in task_by_name:
                        resolved_deps.append(task_by_name[dep_name].id)
                    else:
                        # Log warning about missing dependency
                        self.logger.warning(
                            f"Task '{task.name}' has dependency on '{dep_name}' which was not found"
                        )
                task.dependencies = resolved_deps
                delattr(task, '_dependency_names')
        
        return tasks

    async def _optimize_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Optimize task dependencies."""
        # Build task lookup
        task_lookup = {task.name: task for task in tasks}
        
        # Remove circular dependencies
        visited = set()
        rec_stack = set()
        
        def has_cycle(task: Task) -> bool:
            visited.add(task.id)
            rec_stack.add(task.id)
            
            for dep_id in task.dependencies:
                dep_task = next((t for t in tasks if t.id == dep_id), None)
                if dep_task:
                    if dep_task.id not in visited:
                        if has_cycle(dep_task):
                            return True
                    elif dep_task.id in rec_stack:
                        return True
            
            rec_stack.remove(task.id)
            return False
        
        # Check each task
        for task in tasks:
            if task.id not in visited:
                if has_cycle(task):
                    # Remove the last dependency to break cycle
                    if task.dependencies:
                        task.dependencies.pop()
        
        return tasks

    async def _identify_critical_path(self, tasks: List[Task]) -> List[UUID]:
        """Identify the critical path through tasks."""
        # Simple implementation - find longest dependency chain
        task_map = {task.id: task for task in tasks}
        
        def get_path_length(task_id: UUID, memo: Dict[UUID, int]) -> int:
            if task_id in memo:
                return memo[task_id]
            
            task = task_map.get(task_id)
            if not task or not task.dependencies:
                memo[task_id] = task.estimated_hours if task else 0
                return memo[task_id]
            
            max_dep_length = 0
            for dep_id in task.dependencies:
                dep_length = get_path_length(dep_id, memo)
                max_dep_length = max(max_dep_length, dep_length)
            
            memo[task_id] = task.estimated_hours + max_dep_length
            return memo[task_id]
        
        # Calculate path lengths
        memo = {}
        path_lengths = {
            task.id: get_path_length(task.id, memo)
            for task in tasks
        }
        
        # Find the longest path
        if not path_lengths:
            return []
        
        end_task_id = max(path_lengths, key=path_lengths.get)
        
        # Reconstruct path
        path = []
        current_id = end_task_id
        
        while current_id:
            path.append(current_id)
            task = task_map.get(current_id)
            
            if not task or not task.dependencies:
                break
            
            # Find dependency with longest path
            next_id = None
            max_length = -1
            
            for dep_id in task.dependencies:
                if dep_id in path_lengths and path_lengths[dep_id] > max_length:
                    max_length = path_lengths[dep_id]
                    next_id = dep_id
            
            current_id = next_id
        
        return list(reversed(path))

    async def _identify_parallel_tracks(
        self,
        tasks: List[Task],
    ) -> List[List[UUID]]:
        """Identify tasks that can be executed in parallel."""
        # Group tasks by phase
        phase_tasks = {}
        for task in tasks:
            if task.phase_id not in phase_tasks:
                phase_tasks[task.phase_id] = []
            phase_tasks[task.phase_id].append(task)
        
        parallel_tracks = []
        
        # Find independent tasks within each phase
        for phase_id, phase_task_list in phase_tasks.items():
            independent_groups = []
            
            for task in phase_task_list:
                # Check if task can be added to any existing group
                added = False
                for group in independent_groups:
                    # Check if task depends on any task in group
                    group_ids = [t.id for t in group]
                    if not any(dep_id in group_ids for dep_id in task.dependencies):
                        # Check if any task in group depends on this task
                        if not any(task.id in t.dependencies for t in group):
                            group.append(task)
                            added = True
                            break
                
                if not added:
                    independent_groups.append([task])
            
            # Convert to track IDs
            for group in independent_groups:
                if len(group) > 1:
                    parallel_tracks.append([t.id for t in group])
        
        return parallel_tracks

    async def _define_milestones(
        self,
        phases: List[Phase],
        tasks: List[Task],
    ) -> Dict[str, Any]:
        """Define project milestones."""
        milestones = {}
        
        # Create milestone for each phase completion
        for phase in phases:
            phase_tasks = [t for t in tasks if t.phase_id == phase.id]
            if phase_tasks:
                milestone_name = f"{phase.name} Complete"
                milestones[milestone_name] = {
                    "phase_id": str(phase.id),
                    "task_count": len(phase_tasks),
                    "total_hours": sum(t.estimated_hours for t in phase_tasks),
                    "criteria": [
                        f"All {len(phase_tasks)} tasks in {phase.name} completed",
                        "All acceptance criteria met",
                        "Phase deliverables validated",
                    ],
                }
        
        # Add overall project milestones
        milestones["Project Kickoff"] = {
            "phase_id": str(phases[0].id) if phases else "",
            "criteria": ["Project setup complete", "Development environment ready"],
        }
        
        milestones["Project Completion"] = {
            "phase_id": str(phases[-1].id) if phases else "",
            "criteria": [
                "All phases completed",
                "All tests passing",
                "Documentation complete",
                "Ready for deployment",
            ],
        }
        
        return milestones

    async def _validate_breakdown(
        self,
        breakdown: TaskBreakdown,
        spec_analysis: SpecAnalysis,
    ) -> TaskBreakdown:
        """Validate and enhance task breakdown."""
        issues = []
        
        # Check requirement coverage
        uncovered_reqs = await self._check_requirement_coverage(
            breakdown.tasks,
            spec_analysis.technical_requirements,
        )
        if uncovered_reqs:
            issues.append(f"Uncovered requirements: {len(uncovered_reqs)}")
        
        # Check for orphan tasks
        orphan_tasks = [
            t for t in breakdown.tasks
            if not any(t.id in other.dependencies for other in breakdown.tasks)
            and t.dependencies  # Has dependencies but nothing depends on it
        ]
        if orphan_tasks:
            issues.append(f"Orphan tasks found: {len(orphan_tasks)}")
        
        # Check time estimates
        total_hours = sum(t.estimated_hours for t in breakdown.tasks)
        if total_hours < 40:  # Less than a week
            issues.append("Total estimated time seems too low")
        elif total_hours > 2000:  # More than a year
            issues.append("Total estimated time seems too high")
        
        if issues:
            await self.log_progress(f"Validating breakdown: {', '.join(issues)}")
        
        return breakdown

    async def _check_requirement_coverage(
        self,
        tasks: List[Task],
        requirements: List[str],
    ) -> List[str]:
        """Check which requirements are not covered by tasks."""
        # Build requirement coverage map
        covered_keywords = set()
        
        for task in tasks:
            # Extract keywords from task
            text = f"{task.name} {task.description}"
            words = text.lower().split()
            covered_keywords.update(words)
        
        # Check each requirement
        uncovered = []
        for req in requirements:
            req_words = set(req.lower().split())
            # If less than 30% of requirement words are covered, consider it uncovered
            coverage = len(req_words & covered_keywords) / len(req_words)
            if coverage < 0.3:
                uncovered.append(req)
        
        return uncovered

    async def _store_breakdown(
        self,
        breakdown: TaskBreakdown,
        spec_analysis: SpecAnalysis,
    ) -> None:
        """Store task breakdown in memory."""
        # Store main breakdown
        await self.store_in_memory(
            entity_name=f"TaskBreakdown:{spec_analysis.project_name}",
            entity_type="TaskBreakdown",
            observations=[
                f"Total Tasks: {len(breakdown.tasks)}",
                f"Total Phases: {len(breakdown.phases)}",
                f"Total Estimated Hours: {breakdown.total_estimated_hours}",
                f"Total Estimated Cost: ${breakdown.total_estimated_cost:,.2f}",
                f"Critical Path Length: {len(breakdown.critical_path)}",
                f"Parallel Phases: {len(breakdown.parallel_phases)}",
                json.dumps({
                    "phases": [p.model_dump(mode='json') for p in breakdown.phases],
                    "tasks": [t.model_dump(mode='json') for t in breakdown.tasks],
                    "total_estimated_hours": breakdown.total_estimated_hours,
                    "total_estimated_cost": breakdown.total_estimated_cost,
                    "critical_path": [str(id) for id in breakdown.critical_path],
                    "parallel_phases": [[str(id) for id in phase] for phase in breakdown.parallel_phases],
                }),
            ],
        )
        
        # Store individual phases
        for phase in breakdown.phases[:10]:  # Limit to 10
            await self.store_in_memory(
                entity_name=f"Phase:{phase.name}",
                entity_type="Phase",
                observations=[
                    f"Order: {phase.order}",
                    f"Description: {phase.description}",
                    f"Dependencies: {len(phase.dependencies)}",
                ],
            )

    async def _sync_with_taskmaster(self, breakdown: TaskBreakdown) -> None:
        """Sync tasks with TaskMaster MCP server."""
        try:
            await self.use_mcp_server(MCPServer.TASKMASTER)
            
            # Initialize TaskMaster project
            await self.mcp_orchestrator.taskmaster.initialize_project(
                str(self.mcp_orchestrator.project_dir)
            )
            
            # Convert tasks to TaskMaster format
            # This is simplified - real implementation would be more sophisticated
            for phase in breakdown.phases:
                phase_tasks = [t for t in breakdown.tasks if t.phase_id == phase.id]
                
                for task in phase_tasks[:20]:  # Limit to prevent overload
                    # TaskMaster uses different format
                    await self.log_progress(
                        f"Synced {phase.name} tasks with TaskMaster"
                    )
                    
        except Exception as e:
            await self.log_progress(
                f"TaskMaster sync failed: {e}",
                level="warning"
            )

    def _calculate_breakdown_metrics(self, breakdown: TaskBreakdown) -> Dict[str, Any]:
        """Calculate metrics from task breakdown."""
        total_hours = sum(t.estimated_hours for t in breakdown.tasks)
        
        # Complexity distribution - Task model doesn't have complexity field
        # Using estimated hours as a proxy for complexity
        complexity_distribution = {
            "low": sum(1 for t in breakdown.tasks if t.estimated_hours <= 4),
            "medium": sum(1 for t in breakdown.tasks if 4 < t.estimated_hours <= 8),
            "high": sum(1 for t in breakdown.tasks if 8 < t.estimated_hours <= 16),
            "very_high": sum(1 for t in breakdown.tasks if t.estimated_hours > 16),
        }
        
        priority_distribution = {
            "high": sum(1 for t in breakdown.tasks if t.priority == Priority.HIGH),
            "medium": sum(1 for t in breakdown.tasks if t.priority == Priority.MEDIUM),
            "low": sum(1 for t in breakdown.tasks if t.priority == Priority.LOW),
        }
        
        return {
            "total_tasks": len(breakdown.tasks),
            "total_phases": len(breakdown.phases),
            "total_hours": total_hours,
            "estimated_days": total_hours / 8,
            "estimated_weeks": total_hours / 40,
            "complexity_distribution": complexity_distribution,
            "priority_distribution": priority_distribution,
            "average_task_hours": total_hours / len(breakdown.tasks) if breakdown.tasks else 0,
            "critical_path_hours": sum(
                t.estimated_hours for t in breakdown.tasks
                if t.id in breakdown.critical_path
            ),
            "parallelization_factor": len(breakdown.parallel_phases) / len(breakdown.phases) if breakdown.phases else 0,
        }

    def _calculate_total_complexity(self, tasks: List[Task]) -> int:
        """Calculate total complexity score based on estimated hours."""
        # Using estimated hours as a proxy for complexity
        complexity_score = 0
        for t in tasks:
            if t.estimated_hours <= 4:
                complexity_score += 1  # Low
            elif t.estimated_hours <= 8:
                complexity_score += 3  # Medium
            elif t.estimated_hours <= 16:
                complexity_score += 5  # High
            else:
                complexity_score += 8  # Very High
        return complexity_score

    def _get_default_phases(self, spec_analysis: SpecAnalysis) -> List[Dict[str, Any]]:
        """Get default phases based on project type."""
        # Simplified default phases
        return [
            {
                "name": "Project Setup",
                "description": "Initialize project structure and development environment",
                "depends_on": [],
            },
            {
                "name": "Core Implementation",
                "description": "Implement core functionality and features",
                "depends_on": ["Project Setup"],
            },
            {
                "name": "Integration",
                "description": "Integrate components and external services",
                "depends_on": ["Core Implementation"],
            },
            {
                "name": "Testing",
                "description": "Comprehensive testing and validation",
                "depends_on": ["Integration"],
            },
            {
                "name": "Documentation",
                "description": "Create documentation and deployment guides",
                "depends_on": ["Testing"],
            },
        ]

    def _get_default_phase_tasks(self, phase: Phase) -> List[Dict[str, Any]]:
        """Get default tasks for a phase."""
        # Simplified default tasks
        return [
            {
                "title": f"Setup {phase.name}",
                "description": f"Initial setup for {phase.name}",
                "acceptance_criteria": [f"{phase.name} environment ready"],
                "estimated_hours": 4,
                "complexity": "medium",
                "priority": "high",
                "required_tools": [],
            },
            {
                "title": f"Implement {phase.name}",
                "description": f"Main implementation for {phase.name}",
                "acceptance_criteria": [f"{phase.name} functionality complete"],
                "estimated_hours": 16,
                "complexity": "high",
                "priority": "high",
                "required_tools": [],
            },
            {
                "title": f"Test {phase.name}",
                "description": f"Testing for {phase.name}",
                "acceptance_criteria": [f"{phase.name} tests passing"],
                "estimated_hours": 8,
                "complexity": "medium",
                "priority": "medium",
                "required_tools": [],
            },
        ]


__all__ = ["TaskGenerator"]