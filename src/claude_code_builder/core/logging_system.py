"""Comprehensive logging system for Claude Code Builder."""

import asyncio
import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO

import structlog
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn
from rich.table import Table

from claude_code_builder.core.config import LoggingConfig
from claude_code_builder.core.enums import LogLevel
from claude_code_builder.core.models import APICall, GeneratedCode


class RichConsoleHandler(RichHandler):
    """Enhanced Rich handler with custom formatting."""

    def __init__(self, console: Console, **kwargs: Any) -> None:
        """Initialize the handler."""
        super().__init__(console=console, show_path=False, **kwargs)
        self.console = console

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record with enhanced formatting."""
        # Add custom formatting for specific log types
        if hasattr(record, "api_call"):
            self._format_api_call(record)
        elif hasattr(record, "code_generated"):
            self._format_code_generated(record)
        else:
            super().emit(record)

    def _format_api_call(self, record: logging.LogRecord) -> None:
        """Format API call logs."""
        api_call = record.api_call
        self.console.print(
            f"[cyan]API Call[/cyan] → [yellow]{api_call['model']}[/yellow] "
            f"({api_call['tokens_in']}↓ {api_call['tokens_out']}↑) "
            f"[dim]{api_call['latency_ms']}ms[/dim]"
        )

    def _format_code_generated(self, record: logging.LogRecord) -> None:
        """Format code generation logs."""
        code_info = record.code_generated
        self.console.print(
            f"[green]Code Generated[/green] → [blue]{code_info['file_path']}[/blue] "
            f"({code_info['lines']} lines) [dim]{code_info['language']}[/dim]"
        )


class StructuredFileHandler(logging.Handler):
    """Handler for structured JSON logging."""

    def __init__(self, filename: Path) -> None:
        """Initialize the handler."""
        super().__init__()
        self.filename = filename
        self.filename.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record as structured JSON."""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            # Add extra fields
            for key, value in record.__dict__.items():
                if key not in [
                    "name", "msg", "args", "created", "filename", "funcName",
                    "levelname", "levelno", "lineno", "module", "msecs",
                    "pathname", "process", "processName", "relativeCreated",
                    "thread", "threadName", "getMessage"
                ]:
                    log_entry[key] = value

            with open(self.filename, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception:
            self.handleError(record)


class APICallLogger:
    """Specialized logger for API calls."""

    def __init__(self, api_log_dir: Path) -> None:
        """Initialize the logger."""
        self.api_log_dir = api_log_dir
        self.api_log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_dir: Optional[Path] = None
        self.call_counter = 0
        self.logger = structlog.get_logger()

    async def start_session(self, session_id: Optional[str] = None) -> None:
        """Start a new API logging session."""
        if session_id:
            # Use provided session ID
            self.current_session_dir = self.api_log_dir / session_id
        else:
            # Generate new session ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_session_dir = self.api_log_dir / f"session_{timestamp}"
        
        self.current_session_dir.mkdir(parents=True, exist_ok=True)
        self.call_counter = 0
        
        self.logger.info("api_session_started", session_dir=str(self.current_session_dir))

    async def log_call(self, api_call: APICall) -> None:
        """Log an API call with full details."""
        if not self.current_session_dir:
            await self.start_session()
        
        # Ensure the session directory still exists
        if not self.current_session_dir.exists():
            self.current_session_dir.mkdir(parents=True, exist_ok=True)

        self.call_counter += 1
        
        # Create detailed log file
        call_file = self.current_session_dir / f"call_{self.call_counter:04d}.json"
        
        # Convert Pydantic models to dicts for serialization
        messages = []
        for msg in api_call.request_messages:
            if hasattr(msg, 'model_dump'):
                messages.append(msg.model_dump())
            else:
                messages.append(msg)
        
        tools = []
        for tool in api_call.tools:
            if hasattr(tool, 'model_dump'):
                tools.append(tool.model_dump())
            else:
                tools.append(tool)
        
        tool_calls = []
        for tc in api_call.tool_calls:
            if hasattr(tc, 'model_dump'):
                tool_calls.append(tc.model_dump())
            else:
                tool_calls.append(tc)
        
        call_data = {
            "timestamp": api_call.created_at.isoformat(),
            "call_id": str(api_call.call_id),
            "call_number": self.call_counter,
            "endpoint": api_call.endpoint,
            "model": api_call.model,
            "agent_type": api_call.agent_type.value if hasattr(api_call.agent_type, 'value') else str(api_call.agent_type),
            "phase": api_call.phase,
            "task": api_call.task,
            "request": {
                "messages": messages,
                "system_prompt": api_call.system_prompt,
                "temperature": api_call.temperature,
                "max_tokens": api_call.max_tokens,
                "tools": tools,
            },
            "response": {
                "content": api_call.response_content,
                "tool_calls": tool_calls,
                "error": api_call.error,
            },
            "usage": {
                "input_tokens": api_call.tokens_in,
                "output_tokens": api_call.tokens_out,
                "total_tokens": api_call.tokens_total,
            },
            "performance": {
                "latency_ms": api_call.latency_ms,
                "stream_chunks": api_call.stream_chunks,
            },
            "cost": {
                "estimated": api_call.estimated_cost,
            },
        }

        # Write detailed log
        with open(call_file, "w") as f:
            json.dump(call_data, f, indent=2, default=str)

        # Update session summary
        await self._update_session_summary(api_call)

        # Log to structured logger
        self.logger.info(
            "api_call_logged",
            call_number=self.call_counter,
            model=api_call.model,
            tokens=api_call.tokens_total,
            cost=api_call.estimated_cost,
            latency_ms=api_call.latency_ms,
        )

    async def _update_session_summary(self, api_call: APICall) -> None:
        """Update the session summary file."""
        summary_file = self.current_session_dir / "session_summary.json"
        
        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)
        else:
            summary = {
                "session_start": datetime.now().isoformat(),
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "models_used": {},
                "agents_used": {},
                "errors": 0,
            }

        # Update summary
        summary["total_calls"] += 1
        summary["total_tokens"] += api_call.tokens_total
        summary["total_cost"] += api_call.estimated_cost
        
        model = api_call.model
        if model not in summary["models_used"]:
            summary["models_used"][model] = {"calls": 0, "tokens": 0, "cost": 0.0}
        summary["models_used"][model]["calls"] += 1
        summary["models_used"][model]["tokens"] += api_call.tokens_total
        summary["models_used"][model]["cost"] += api_call.estimated_cost
        
        agent = api_call.agent_type
        if agent not in summary["agents_used"]:
            summary["agents_used"][agent] = {"calls": 0, "tokens": 0}
        summary["agents_used"][agent]["calls"] += 1
        summary["agents_used"][agent]["tokens"] += api_call.tokens_total
        
        if api_call.error:
            summary["errors"] += 1

        # Write updated summary
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)


class GeneratedCodeLogger:
    """Logger for tracking generated code."""

    def __init__(self, code_log_dir: Path) -> None:
        """Initialize the logger."""
        self.code_log_dir = code_log_dir
        self.code_log_dir.mkdir(parents=True, exist_ok=True)
        self.code_index: List[Dict[str, Any]] = []
        self.logger = structlog.get_logger()

    async def log_code(self, code_block: GeneratedCode) -> None:
        """Log generated code with metadata."""
        # Create phase-specific directory
        phase_dir = self.code_log_dir / code_block.phase
        phase_dir.mkdir(exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = code_block.file_path.name if hasattr(code_block.file_path, 'name') else code_block.file_path
        code_file = phase_dir / f"{timestamp}_{filename}"

        # Create header
        header = f"""# Generated by Claude Code Builder
# Phase: {code_block.phase}
# Task: {code_block.task}
# Timestamp: {code_block.timestamp}
# Model: {code_block.model}
# Tokens: {code_block.tokens_used}
# Original Path: {code_block.file_path}
# {'=' * 60}

"""

        # Write code with header
        with open(code_file, "w") as f:
            f.write(header + code_block.content)

        # Update index
        index_entry = {
            "timestamp": code_block.timestamp.isoformat(),
            "phase": code_block.phase,
            "task": code_block.task,
            "file_path": str(code_block.file_path),
            "language": code_block.language,
            "lines": code_block.line_count,
            "tokens": code_block.tokens_used,
            "log_path": str(code_file.relative_to(self.code_log_dir)),
        }
        
        self.code_index.append(index_entry)

        # Save index
        index_file = self.code_log_dir / "code_index.json"
        with open(index_file, "w") as f:
            json.dump(self.code_index, f, indent=2)

        self.logger.info(
            "code_logged",
            file_path=str(code_block.file_path),
            lines=code_block.line_count,
            phase=code_block.phase,
        )


class ComprehensiveLogger:
    """Main logging orchestrator."""

    def __init__(self, project_dir: Path, config: LoggingConfig) -> None:
        """Initialize the comprehensive logger."""
        self.project_dir = project_dir
        self.log_dir = project_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.config = config
        
        # Initialize console
        self.console = Console(record=True)
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )
        
        # Initialize handlers
        self._setup_logging()
        
        # Initialize specialized loggers
        self.api_logger = APICallLogger(self.log_dir / "api_calls")
        self.code_logger = GeneratedCodeLogger(self.log_dir / "generated_code")
        
        self.logger = structlog.get_logger()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer() if self.config.json_enabled else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self._get_log_level())

        # Remove existing handlers
        root_logger.handlers = []

        # Add console handler
        if self.config.console_enabled:
            console_handler = RichConsoleHandler(
                console=self.console,
                show_time=self.config.include_timestamps,
            )
            console_handler.setLevel(self._get_log_level())
            root_logger.addHandler(console_handler)

        # Add file handler
        if self.config.file_enabled:
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / "claude_code_builder.log",
                maxBytes=self.config.log_rotation_size,
                backupCount=5,
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s"
                )
            )
            file_handler.setLevel(self._get_log_level())
            root_logger.addHandler(file_handler)

        # Add JSON handler
        if self.config.json_enabled:
            json_handler = StructuredFileHandler(self.log_dir / "structured.jsonl")
            json_handler.setLevel(self._get_log_level())
            root_logger.addHandler(json_handler)

    def _get_log_level(self) -> int:
        """Convert LogLevel enum to logging level."""
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return level_map.get(self.config.level, logging.INFO)

    async def start_session(self, session_id: Optional[str] = None) -> None:
        """Start a new logging session."""
        await self.api_logger.start_session(session_id)
        self.logger.info("logging_session_started", project_dir=str(self.project_dir))

    async def log_api_call(self, api_call: APICall) -> None:
        """Log an API call."""
        await self.api_logger.log_call(api_call)
        
        # Also log to main logger with custom formatting
        self.logger.info(
            "api_call",
            api_call={
                "model": api_call.model,
                "tokens_in": api_call.tokens_in,
                "tokens_out": api_call.tokens_out,
                "latency_ms": api_call.latency_ms,
            },
        )

    async def log_generated_code(self, code_block: GeneratedCode) -> None:
        """Log generated code."""
        await self.code_logger.log_code(code_block)
        
        # Also log to main logger
        self.logger.info(
            "code_generated",
            code_generated={
                "file_path": str(code_block.file_path),
                "lines": code_block.line_count,
                "language": code_block.language,
            },
        )

    def start_progress(self, description: str) -> TaskID:
        """Start a progress indicator."""
        return self.progress.add_task(description)

    def update_progress(self, task_id: TaskID, description: Optional[str] = None) -> None:
        """Update progress indicator."""
        self.progress.update(task_id, description=description)

    def stop_progress(self, task_id: TaskID) -> None:
        """Stop progress indicator."""
        self.progress.remove_task(task_id)

    def print_table(self, title: str, headers: List[str], rows: List[List[str]]) -> None:
        """Print a formatted table."""
        table = Table(title=title)
        for header in headers:
            table.add_column(header)
        for row in rows:
            table.add_row(*row)
        self.console.print(table)

    def print_success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"[green]✓[/green] {message}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"[red]✗[/red] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {message}")

    def print_info(self, message: str) -> None:
        """Print info message."""
        self.console.print(f"[cyan]ℹ[/cyan] {message}")

    async def export_logs(self, export_path: Path) -> None:
        """Export all logs to a directory."""
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Copy log files
        import shutil
        shutil.copytree(self.log_dir, export_path / "logs", dirs_exist_ok=True)
        
        # Export console recording
        console_export = export_path / "console_output.html"
        self.console.save_html(str(console_export))
        
        self.logger.info("logs_exported", export_path=str(export_path))


# GeneratedCode model is now imported from claude_code_builder.core.models


__all__ = [
    "ComprehensiveLogger",
    "APICallLogger",
    "GeneratedCodeLogger",
    "RichConsoleHandler",
    "StructuredFileHandler",
    "GeneratedCode",
]