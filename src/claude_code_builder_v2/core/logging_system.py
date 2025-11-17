"""Comprehensive logging system for Claude Code Builder v2."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from claude_code_builder_v2.core.config import LoggingConfig


class ComprehensiveLogger:
    """Multi-stream structured logger."""

    def __init__(
        self, project_dir: Path, config: Optional[LoggingConfig] = None
    ) -> None:
        """Initialize comprehensive logger.

        Args:
            project_dir: Project directory for log files
            config: Logging configuration
        """
        self.project_dir = project_dir
        self.config = config or LoggingConfig()
        self.log_dir = project_dir / "logs"
        self.log_dir.mkdir(exist_ok=True, parents=True)

        # Setup structlog
        self._setup_structlog()

        # Get logger
        self.logger = structlog.get_logger()

    def _setup_structlog(self) -> None:
        """Setup structlog configuration."""
        processors = [
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]

        if self.config.json_logs:
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def _log_to_file(self, level: str, event: str, **kwargs: Any) -> None:
        """Log to file.

        Args:
            level: Log level
            event: Event name
            **kwargs: Additional context
        """
        if not self.config.log_to_file:
            return

        log_file = self.log_dir / f"build_{datetime.utcnow().strftime('%Y%m%d')}.log"

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "event": event,
            **kwargs,
        }

        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Failed to write log: {e}", file=sys.stderr)

    def debug(self, event: str, **kwargs: Any) -> None:
        """Log debug message.

        Args:
            event: Event name
            **kwargs: Additional context
        """
        if self.config.log_to_console:
            self.logger.debug(event, **kwargs)
        self._log_to_file("DEBUG", event, **kwargs)

    def info(self, event_type: str, msg: str = "", **kwargs: Any) -> None:
        """Log info message.

        Args:
            event_type: Event type/name
            msg: Message
            **kwargs: Additional context
        """
        if self.config.log_to_console:
            self.logger.info(event_type, msg=msg, **kwargs)
        self._log_to_file("INFO", event_type, msg=msg, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        """Log warning message.

        Args:
            event: Event name
            **kwargs: Additional context
        """
        if self.config.log_to_console:
            self.logger.warning(event, **kwargs)
        self._log_to_file("WARNING", event, **kwargs)

    def error(self, event_type: str, msg: str = "", **kwargs: Any) -> None:
        """Log error message.

        Args:
            event_type: Event type/name
            msg: Message
            **kwargs: Additional context
        """
        if self.config.log_to_console:
            self.logger.error(event_type, msg=msg, **kwargs)
        self._log_to_file("ERROR", event_type, msg=msg, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> None:
        """Log critical message.

        Args:
            event: Event name
            **kwargs: Additional context
        """
        if self.config.log_to_console:
            self.logger.critical(event, **kwargs)
        self._log_to_file("CRITICAL", event, **kwargs)

    def log_api_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        duration_ms: float,
        **kwargs: Any,
    ) -> None:
        """Log API call details.

        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
            cost: Cost in USD
            duration_ms: Duration in milliseconds
            **kwargs: Additional context
        """
        self.info(
            "api_call",
            msg="API call completed",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost=cost,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_phase_start(self, phase_name: str, **kwargs: Any) -> None:
        """Log phase start.

        Args:
            phase_name: Phase name
            **kwargs: Additional context
        """
        self.info(
            "phase_start",
            msg=f"Starting phase: {phase_name}",
            phase=phase_name,
            **kwargs,
        )

    def log_phase_complete(
        self, phase_name: str, duration_seconds: float, cost: float, **kwargs: Any
    ) -> None:
        """Log phase completion.

        Args:
            phase_name: Phase name
            duration_seconds: Duration in seconds
            cost: Phase cost
            **kwargs: Additional context
        """
        self.info(
            "phase_complete",
            msg=f"Phase completed: {phase_name}",
            phase=phase_name,
            duration_seconds=duration_seconds,
            cost=cost,
            **kwargs,
        )

    def log_agent_execution(
        self, agent_type: str, success: bool, **kwargs: Any
    ) -> None:
        """Log agent execution.

        Args:
            agent_type: Agent type
            success: Whether execution succeeded
            **kwargs: Additional context
        """
        level = "info" if success else "error"
        event = "agent_success" if success else "agent_failure"

        getattr(self, level)(
            event,
            msg=f"Agent execution: {agent_type}",
            agent=agent_type,
            success=success,
            **kwargs,
        )

    def get_log_path(self) -> Path:
        """Get path to log directory.

        Returns:
            Path to log directory
        """
        return self.log_dir
