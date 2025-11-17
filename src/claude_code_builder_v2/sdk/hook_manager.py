"""Hook manager for Claude SDK events."""

from typing import Any, Callable, Dict, List, Optional

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger
from claude_code_builder_v2.sdk.cost_tracker import CostTracker


class SDKHookManager:
    """Manages hooks for SDK events like permission checks, tool calls, etc."""

    def __init__(
        self,
        logger: ComprehensiveLogger,
        cost_tracker: Optional[CostTracker] = None,
    ) -> None:
        """Initialize hook manager.

        Args:
            logger: Comprehensive logger
            cost_tracker: Optional cost tracker
        """
        self.logger = logger
        self.cost_tracker = cost_tracker or CostTracker()
        self.hooks: Dict[str, List[Callable]] = {
            "before_request": [],
            "after_request": [],
            "on_tool_call": [],
            "on_permission_check": [],
            "on_error": [],
        }

    def register_hook(self, event: str, callback: Callable) -> None:
        """Register a hook callback.

        Args:
            event: Event name (before_request, after_request, etc.)
            callback: Callback function
        """
        if event not in self.hooks:
            self.hooks[event] = []

        self.hooks[event].append(callback)
        self.logger.debug(
            "hook_registered",
            msg=f"Registered hook for {event}",
            event=event,
        )

    def unregister_hook(self, event: str, callback: Callable) -> None:
        """Unregister a hook callback.

        Args:
            event: Event name
            callback: Callback function to remove
        """
        if event in self.hooks and callback in self.hooks[event]:
            self.hooks[event].remove(callback)
            self.logger.debug(
                "hook_unregistered",
                msg=f"Unregistered hook for {event}",
                event=event,
            )

    async def trigger_before_request(self, prompt: str, options: Dict[str, Any]) -> None:
        """Trigger before_request hooks.

        Args:
            prompt: User prompt
            options: Request options
        """
        for callback in self.hooks["before_request"]:
            try:
                await callback(prompt=prompt, options=options)
            except Exception as e:
                self.logger.error(
                    "hook_error",
                    msg=f"Error in before_request hook: {e}",
                    error=str(e),
                )

    async def trigger_after_request(
        self,
        prompt: str,
        response: str,
        usage: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Trigger after_request hooks.

        Args:
            prompt: User prompt
            response: Assistant response
            usage: Optional usage statistics
        """
        # Track cost if usage provided
        if usage and self.cost_tracker:
            model = usage.get("model", "claude-3-sonnet-20240229")
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

            cost = self.cost_tracker.track_usage(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

            self.logger.info(
                "sdk_usage_tracked",
                msg="Tracked SDK usage",
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
            )

        # Trigger hooks
        for callback in self.hooks["after_request"]:
            try:
                await callback(prompt=prompt, response=response, usage=usage)
            except Exception as e:
                self.logger.error(
                    "hook_error",
                    msg=f"Error in after_request hook: {e}",
                    error=str(e),
                )

    async def trigger_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> bool:
        """Trigger on_tool_call hooks.

        Args:
            tool_name: Name of tool being called
            arguments: Tool arguments

        Returns:
            True if tool call is allowed, False otherwise
        """
        allowed = True

        for callback in self.hooks["on_tool_call"]:
            try:
                result = await callback(tool_name=tool_name, arguments=arguments)
                if result is False:
                    allowed = False
            except Exception as e:
                self.logger.error(
                    "hook_error",
                    msg=f"Error in on_tool_call hook: {e}",
                    error=str(e),
                )

        if not allowed:
            self.logger.warning(
                "tool_call_blocked",
                msg=f"Tool call blocked by hook: {tool_name}",
                tool=tool_name,
            )

        return allowed

    async def trigger_permission_check(
        self, action: str, context: Dict[str, Any]
    ) -> bool:
        """Trigger on_permission_check hooks.

        Args:
            action: Action requiring permission
            context: Context information

        Returns:
            True if action is allowed, False otherwise
        """
        allowed = True

        for callback in self.hooks["on_permission_check"]:
            try:
                result = await callback(action=action, context=context)
                if result is False:
                    allowed = False
            except Exception as e:
                self.logger.error(
                    "hook_error",
                    msg=f"Error in on_permission_check hook: {e}",
                    error=str(e),
                )

        if not allowed:
            self.logger.warning(
                "permission_denied",
                msg=f"Permission denied by hook: {action}",
                action=action,
            )

        return allowed

    async def trigger_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Trigger on_error hooks.

        Args:
            error: Exception that occurred
            context: Context information
        """
        for callback in self.hooks["on_error"]:
            try:
                await callback(error=error, context=context)
            except Exception as e:
                self.logger.error(
                    "hook_error",
                    msg=f"Error in on_error hook: {e}",
                    error=str(e),
                )

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary.

        Returns:
            Cost summary dictionary
        """
        return self.cost_tracker.get_summary()

    def reset_cost_tracking(self) -> None:
        """Reset cost tracking."""
        self.cost_tracker.reset()
        self.logger.info("cost_tracking_reset", msg="Cost tracking reset")
