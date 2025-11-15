"""Hook Registry for SDK events."""

from typing import Dict, Any, Callable, List
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class HookRegistry:
    """Registry for SDK hooks."""

    def __init__(self, logger: ComprehensiveLogger) -> None:
        """Initialize hook registry."""
        self.logger = logger
        self.hooks: Dict[str, List[Callable]] = {
            "pre_tool_use": [],
            "post_tool_use": [],
            "user_prompt_submit": [],
        }

    def register_hook(self, event: str, callback: Callable) -> None:
        """Register a hook callback."""
        if event not in self.hooks:
            raise ValueError(f"Unknown hook event: {event}")

        self.hooks[event].append(callback)

    async def pre_tool_use(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Hook called before tool execution."""
        self.logger.logger.info(
            "hook_pre_tool_use",
            tool=tool_name,
            arguments=arguments,
        )

        # Execute registered callbacks
        for callback in self.hooks["pre_tool_use"]:
            arguments = await callback(tool_name, arguments, context)

        return arguments

    async def post_tool_use(
        self,
        tool_name: str,
        result: Any,
        context: Dict[str, Any],
    ) -> None:
        """Hook called after tool execution."""
        self.logger.logger.info(
            "hook_post_tool_use",
            tool=tool_name,
            success=not isinstance(result, Exception),
        )

        # Execute registered callbacks
        for callback in self.hooks["post_tool_use"]:
            await callback(tool_name, result, context)

    async def user_prompt_submit(
        self,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """Hook called before prompt submission."""
        self.logger.logger.info(
            "hook_user_prompt",
            prompt_length=len(prompt),
        )

        # Execute registered callbacks
        for callback in self.hooks["user_prompt_submit"]:
            prompt = await callback(prompt, context)

        return prompt
