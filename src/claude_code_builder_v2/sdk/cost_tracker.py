"""Cost tracking for Claude SDK usage."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class UsageRecord:
    """Single API usage record."""

    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class CostTracker:
    """Tracks costs and usage for Claude SDK calls."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-opus-20240229": {
            "input": 15.00,  # per 1M tokens
            "output": 75.00,
        },
        "claude-3-sonnet-20240229": {
            "input": 3.00,
            "output": 15.00,
        },
        "claude-3-5-sonnet-20241022": {
            "input": 3.00,
            "output": 15.00,
        },
        "claude-3-haiku-20240307": {
            "input": 0.25,
            "output": 1.25,
        },
    }

    def __init__(self) -> None:
        """Initialize cost tracker."""
        self.records: List[UsageRecord] = []
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate cost for API call.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        pricing = self.PRICING.get(model, self.PRICING["claude-3-sonnet-20240229"])

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Track API usage and return cost.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Optional metadata

        Returns:
            Cost for this call
        """
        cost = self.calculate_cost(model, input_tokens, output_tokens)

        record = UsageRecord(
            timestamp=datetime.utcnow(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata=metadata or {},
        )

        self.records.append(record)
        self.total_cost += cost
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        return cost

    def get_summary(self) -> Dict[str, Any]:
        """Get usage summary.

        Returns:
            Summary dictionary with totals and breakdowns
        """
        by_model: Dict[str, Dict[str, Any]] = {}

        for record in self.records:
            if record.model not in by_model:
                by_model[record.model] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0.0,
                }

            by_model[record.model]["calls"] += 1
            by_model[record.model]["input_tokens"] += record.input_tokens
            by_model[record.model]["output_tokens"] += record.output_tokens
            by_model[record.model]["cost"] += record.cost

        return {
            "total_cost": self.total_cost,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "api_calls": len(self.records),
            "by_model": by_model,
            "records": len(self.records),
        }

    def get_records(
        self, limit: Optional[int] = None, model: Optional[str] = None
    ) -> List[UsageRecord]:
        """Get usage records.

        Args:
            limit: Optional limit on number of records
            model: Optional filter by model

        Returns:
            List of usage records
        """
        records = self.records

        if model:
            records = [r for r in records if r.model == model]

        if limit:
            records = records[-limit:]

        return records

    def reset(self) -> None:
        """Reset all tracking data."""
        self.records = []
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def check_budget(self, max_cost: float) -> bool:
        """Check if total cost is within budget.

        Args:
            max_cost: Maximum allowed cost

        Returns:
            True if within budget, False otherwise
        """
        return self.total_cost <= max_cost

    def get_remaining_budget(self, max_cost: float) -> float:
        """Get remaining budget.

        Args:
            max_cost: Maximum allowed cost

        Returns:
            Remaining budget amount
        """
        return max(0.0, max_cost - self.total_cost)
