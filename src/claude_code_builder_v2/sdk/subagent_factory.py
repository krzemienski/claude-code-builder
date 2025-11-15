"""Subagent Factory for SDK."""

from typing import Dict, List, Optional
from pydantic import BaseModel

from claude_code_builder_v2.core.enums import AgentType
from claude_code_builder_v2.core.config import ExecutorConfig


class AgentDefinition(BaseModel):
    """SDK Agent Definition."""
    name: str
    description: str
    system_prompt: str
    allowed_tools: List[str]
    model: str


class SubagentFactory:
    """Factory for creating subagent definitions."""

    def __init__(self, config: ExecutorConfig) -> None:
        """Initialize subagent factory."""
        self.config = config
        self.definitions: Dict[AgentType, AgentDefinition] = {}

    def create_definition(
        self,
        agent_type: AgentType,
        system_prompt: str,
        allowed_tools: List[str],
        model: Optional[str] = None,
    ) -> AgentDefinition:
        """Create agent definition."""
        definition = AgentDefinition(
            name=agent_type.value,
            description=self._get_description(agent_type),
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            model=model or self.config.model,
        )

        self.definitions[agent_type] = definition
        return definition

    def _get_description(self, agent_type: AgentType) -> str:
        """Get agent description."""
        descriptions = {
            AgentType.SPEC_ANALYZER: "Analyzes project specifications",
            AgentType.TASK_GENERATOR: "Generates task breakdowns",
            AgentType.INSTRUCTION_BUILDER: "Builds implementation instructions",
            AgentType.CODE_GENERATOR: "Generates production code",
            AgentType.TEST_GENERATOR: "Creates test suites",
            AgentType.ACCEPTANCE_GENERATOR: "Generates acceptance criteria",
            AgentType.ERROR_HANDLER: "Handles and recovers from errors",
            AgentType.DOCUMENTATION_AGENT: "Generates documentation",
        }
        return descriptions.get(agent_type, "Agent")
