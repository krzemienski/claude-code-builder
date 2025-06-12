"""Agent Orchestrator for coordinating multi-agent workflows."""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from claude_code_builder.agents.base import AgentResponse
from claude_code_builder.core.enums import AgentType, MCPCheckpoint
from claude_code_builder.core.exceptions import PhaseExecutionError
from claude_code_builder.core.logging_system import ComprehensiveLogger
from claude_code_builder.core.models import ExecutionContext

if TYPE_CHECKING:
    from claude_code_builder.agents.base import BaseAgent


class AgentOrchestrator:
    """Orchestrates multi-agent workflows."""
    
    def __init__(
        self,
        agents: Dict[AgentType, "BaseAgent"],
        logger: ComprehensiveLogger,
    ) -> None:
        """Initialize the orchestrator."""
        self.agents = agents
        self.logger = logger
        self.execution_history: List[AgentResponse] = []

    async def execute_workflow(
        self,
        workflow: List[Dict[str, Any]],
        context: ExecutionContext,
    ) -> List[AgentResponse]:
        """Execute a multi-agent workflow."""
        results = []
        
        for step in workflow:
            agent_type = AgentType[step["agent"]]
            agent = self.agents.get(agent_type)
            
            if not agent:
                raise PhaseExecutionError(
                    context.current_phase,
                    f"Agent not found: {agent_type}",
                )
            
            # Execute agent
            self.logger.print_info(f"Executing {agent_type.value}...")
            response = await agent.run(context, **step.get("params", {}))
            
            results.append(response)
            self.execution_history.append(response)
            
            # Check for failure
            if not response.success:
                if step.get("required", True):
                    raise PhaseExecutionError(
                        context.current_phase,
                        f"Agent failed: {agent_type.value}",
                        details={"error": response.error},
                    )
        
        return results

    async def execute_parallel(
        self,
        agents: List[Dict[str, Any]],
        context: ExecutionContext,
    ) -> List[AgentResponse]:
        """Execute multiple agents in parallel."""
        import asyncio
        
        tasks = []
        for agent_info in agents:
            agent_type = AgentType[agent_info["agent"]]
            agent = self.agents.get(agent_type)
            
            if agent:
                task = agent.run(context, **agent_info.get("params", {}))
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        responses = []
        for result in results:
            if isinstance(result, Exception):
                response = AgentResponse(
                    agent_type=AgentType.ERROR_HANDLER,
                    success=False,
                    result=None,
                    error=str(result),
                )
            else:
                response = result
            
            responses.append(response)
            self.execution_history.append(response)
        
        return responses

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of agent executions."""
        total_calls = len(self.execution_history)
        successful_calls = sum(1 for r in self.execution_history if r.success)
        
        agent_stats = {}
        for response in self.execution_history:
            agent = response.agent_type.value
            if agent not in agent_stats:
                agent_stats[agent] = {
                    "calls": 0,
                    "successes": 0,
                    "tokens": 0,
                    "cost": 0.0,
                }
            
            agent_stats[agent]["calls"] += 1
            if response.success:
                agent_stats[agent]["successes"] += 1
            agent_stats[agent]["tokens"] += response.tokens_used
            agent_stats[agent]["cost"] += response.cost
        
        return {
            "total_executions": total_calls,
            "successful_executions": successful_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "agent_statistics": agent_stats,
            "total_tokens": sum(r.tokens_used for r in self.execution_history),
            "total_cost": sum(r.cost for r in self.execution_history),
        }


__all__ = ["AgentOrchestrator"]