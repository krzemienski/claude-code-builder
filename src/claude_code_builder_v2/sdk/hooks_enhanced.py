"""Enhanced SDK hooks for tracking and monitoring."""

from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class CostTracker:
    """Tracks API costs and usage."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
    }

    def __init__(self):
        """Initialize cost tracker."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.api_calls = 0
        self.calls_by_model: Dict[str, int] = defaultdict(int)
        self.tokens_by_model: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"input": 0, "output": 0}
        )
        self.cost_by_model: Dict[str, float] = defaultdict(float)

    def track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Track API usage and calculate cost.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost for this call
        """
        self.api_calls += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        # Track by model
        self.calls_by_model[model] += 1
        self.tokens_by_model[model]["input"] += input_tokens
        self.tokens_by_model[model]["output"] += output_tokens

        # Calculate cost
        pricing = self.PRICING.get(model, {"input": 3.0, "output": 15.0})
        cost = (input_tokens / 1_000_000 * pricing["input"]) + (
            output_tokens / 1_000_000 * pricing["output"]
        )

        self.total_cost += cost
        self.cost_by_model[model] += cost

        return cost

    def get_summary(self) -> Dict[str, Any]:
        """Get usage summary.

        Returns:
            Dictionary of usage statistics
        """
        return {
            "api_calls": self.api_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": round(self.total_cost, 4),
            "by_model": {
                model: {
                    "calls": self.calls_by_model[model],
                    "input_tokens": self.tokens_by_model[model]["input"],
                    "output_tokens": self.tokens_by_model[model]["output"],
                    "cost": round(self.cost_by_model[model], 4),
                }
                for model in self.calls_by_model.keys()
            },
        }


class ToolUsageTracker:
    """Tracks tool usage statistics."""

    def __init__(self):
        """Initialize tool usage tracker."""
        self.tool_calls: Dict[str, int] = defaultdict(int)
        self.tool_errors: Dict[str, int] = defaultdict(int)
        self.tool_latency: Dict[str, list] = defaultdict(list)

    def track_call(
        self,
        tool_name: str,
        success: bool,
        latency_ms: float,
    ) -> None:
        """Track tool call.

        Args:
            tool_name: Name of tool
            success: Whether call succeeded
            latency_ms: Latency in milliseconds
        """
        self.tool_calls[tool_name] += 1
        self.tool_latency[tool_name].append(latency_ms)

        if not success:
            self.tool_errors[tool_name] += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get tool usage summary.

        Returns:
            Dictionary of tool statistics
        """
        summary = {}

        for tool_name in self.tool_calls.keys():
            latencies = self.tool_latency[tool_name]
            avg_latency = sum(latencies) / len(latencies) if latencies else 0

            summary[tool_name] = {
                "calls": self.tool_calls[tool_name],
                "errors": self.tool_errors[tool_name],
                "error_rate": (
                    self.tool_errors[tool_name] / self.tool_calls[tool_name]
                    if self.tool_calls[tool_name] > 0
                    else 0
                ),
                "avg_latency_ms": round(avg_latency, 2),
            }

        return summary


class EnhancedSDKHooks:
    """Enhanced SDK hooks for comprehensive tracking."""

    def __init__(
        self,
        logger: ComprehensiveLogger,
        cost_tracker: Optional[CostTracker] = None,
        tool_tracker: Optional[ToolUsageTracker] = None,
    ):
        """Initialize enhanced SDK hooks.

        Args:
            logger: Logger instance
            cost_tracker: Optional cost tracker
            tool_tracker: Optional tool usage tracker
        """
        self.logger = logger
        self.cost_tracker = cost_tracker or CostTracker()
        self.tool_tracker = tool_tracker or ToolUsageTracker()
        self.active_tools: Dict[str, datetime] = {}

    async def pre_query(
        self,
        prompt: str,
        model: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Hook called before query execution.

        Args:
            prompt: Query prompt
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Context dictionary
        """
        context = {
            "start_time": datetime.utcnow(),
            "model": model,
            "prompt_length": len(prompt),
        }

        self.logger.logger.info(
            "sdk_query_start",
            model=model,
            prompt_length=len(prompt),
            **kwargs,
        )

        return context

    async def post_query(
        self,
        context: Dict[str, Any],
        response: Any,
        error: Optional[Exception] = None,
    ) -> None:
        """Hook called after query execution.

        Args:
            context: Context from pre_query
            response: Query response
            error: Error if query failed
        """
        duration = (datetime.utcnow() - context["start_time"]).total_seconds()

        if error:
            self.logger.print_error(f"Query failed: {error}")
            self.logger.logger.error(
                "sdk_query_error",
                model=context["model"],
                duration=duration,
                error=str(error),
            )
            return

        # Extract token usage if available
        input_tokens = getattr(response, "input_tokens", 0)
        output_tokens = getattr(response, "output_tokens", 0)

        # Track cost
        if input_tokens > 0 or output_tokens > 0:
            cost = self.cost_tracker.track_usage(
                context["model"],
                input_tokens,
                output_tokens,
            )
        else:
            cost = 0.0

        # Log query completion
        self.logger.logger.info(
            "sdk_query_complete",
            model=context["model"],
            duration=duration,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=round(cost, 6),
        )

    async def pre_tool_use(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Hook called before tool execution.

        Args:
            tool_name: Name of tool
            arguments: Tool arguments

        Returns:
            Context dictionary
        """
        start_time = datetime.utcnow()
        self.active_tools[tool_name] = start_time

        self.logger.logger.info(
            "sdk_tool_use",
            tool=tool_name,
            arguments=arguments,
        )

        return {
            "tool_name": tool_name,
            "start_time": start_time,
        }

    async def post_tool_use(
        self,
        context: Dict[str, Any],
        result: Any,
        error: Optional[Exception] = None,
    ) -> None:
        """Hook called after tool execution.

        Args:
            context: Context from pre_tool_use
            result: Tool result
            error: Error if tool failed
        """
        tool_name = context["tool_name"]
        start_time = context["start_time"]

        # Calculate latency
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Remove from active
        if tool_name in self.active_tools:
            del self.active_tools[tool_name]

        # Track usage
        success = error is None
        self.tool_tracker.track_call(tool_name, success, latency_ms)

        # Log result
        if error:
            self.logger.print_error(f"Tool {tool_name} failed: {error}")
            self.logger.logger.error(
                "sdk_tool_error",
                tool=tool_name,
                latency_ms=latency_ms,
                error=str(error),
            )
        else:
            self.logger.logger.info(
                "sdk_tool_complete",
                tool=tool_name,
                latency_ms=round(latency_ms, 2),
                success=success,
            )

    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """Get comprehensive tracking summary.

        Returns:
            Dictionary of all statistics
        """
        return {
            "cost": self.cost_tracker.get_summary(),
            "tools": self.tool_tracker.get_summary(),
            "active_tools": list(self.active_tools.keys()),
        }


__all__ = [
    "CostTracker",
    "ToolUsageTracker",
    "EnhancedSDKHooks",
]
