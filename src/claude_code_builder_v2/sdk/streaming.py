"""Streaming progress reporting for SDK queries."""

import asyncio
from typing import AsyncIterator, Callable, Optional, Dict, Any
from datetime import datetime

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class StreamChunk:
    """Represents a chunk of streamed content."""

    def __init__(
        self,
        chunk_type: str,
        content: str,
        tool_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize stream chunk.

        Args:
            chunk_type: Type of chunk (thinking, tool_use, text, etc.)
            content: Content of the chunk
            tool_name: Name of tool being used (if applicable)
            metadata: Additional metadata
        """
        self.type = chunk_type
        self.content = content
        self.tool_name = tool_name
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()


class StreamingProgressReporter:
    """Reports real-time progress via SDK streaming."""

    def __init__(
        self,
        logger: ComprehensiveLogger,
        progress_callback: Optional[Callable[[str], None]] = None,
    ):
        """Initialize streaming progress reporter.

        Args:
            logger: Logger instance
            progress_callback: Optional callback for progress updates
        """
        self.logger = logger
        self.progress_callback = progress_callback
        self.chunks_received = 0
        self.total_content_length = 0
        self.start_time: Optional[datetime] = None

    async def report_progress(
        self,
        query_iterator: AsyncIterator,
    ) -> str:
        """Monitor SDK query stream and report progress.

        Args:
            query_iterator: Async iterator from SDK query

        Returns:
            Complete assembled response text
        """
        self.start_time = datetime.utcnow()
        response_parts = []

        try:
            async for chunk in query_iterator:
                self.chunks_received += 1

                # Process different chunk types
                if hasattr(chunk, "type"):
                    await self._process_chunk(chunk)

                    # Collect text content
                    if hasattr(chunk, "content"):
                        response_parts.append(chunk.content)
                        self.total_content_length += len(chunk.content)
                elif isinstance(chunk, str):
                    # Simple string chunk
                    response_parts.append(chunk)
                    self.total_content_length += len(chunk)
                    await self._report("text", chunk)

        except Exception as e:
            self.logger.print_error(f"Streaming error: {e}")
            raise

        # Assemble complete response
        complete_response = "".join(response_parts)

        # Log final statistics
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        self.logger.logger.info(
            "streaming_complete",
            chunks=self.chunks_received,
            content_length=self.total_content_length,
            duration=duration,
        )

        return complete_response

    async def _process_chunk(self, chunk: Any) -> None:
        """Process a single stream chunk.

        Args:
            chunk: Chunk from stream
        """
        chunk_type = getattr(chunk, "type", "unknown")
        content = getattr(chunk, "content", "")
        tool_name = getattr(chunk, "tool_name", None)

        # Report based on chunk type
        if chunk_type == "thinking":
            await self._report(
                "thinking",
                f"Thinking: {content[:50]}..." if len(content) > 50 else content,
            )
        elif chunk_type == "tool_use":
            await self._report(
                "tool_use", f"Using tool: {tool_name or 'unknown'}"
            )
        elif chunk_type == "text":
            await self._report(
                "text",
                f"Response: {content[:50]}..." if len(content) > 50 else content,
            )
        elif chunk_type == "error":
            await self._report("error", f"Error: {content}")

        # Log chunk
        self.logger.logger.debug(
            "streaming_chunk",
            type=chunk_type,
            content_length=len(content),
            tool=tool_name,
        )

    async def _report(self, event_type: str, message: str) -> None:
        """Report progress event.

        Args:
            event_type: Type of event
            message: Progress message
        """
        # Call callback if provided
        if self.progress_callback:
            try:
                if asyncio.iscoroutinefunction(self.progress_callback):
                    await self.progress_callback(message)
                else:
                    self.progress_callback(message)
            except Exception as e:
                self.logger.logger.warning(
                    "progress_callback_error",
                    error=str(e),
                )

        # Always log
        self.logger.logger.info(
            "streaming_progress",
            event_type=event_type,
            msg=message,
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get streaming statistics.

        Returns:
            Dictionary of statistics
        """
        duration = 0.0
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()

        return {
            "chunks_received": self.chunks_received,
            "total_content_length": self.total_content_length,
            "duration": duration,
            "avg_chunk_size": (
                self.total_content_length / self.chunks_received
                if self.chunks_received > 0
                else 0
            ),
        }


class StreamingQueryWrapper:
    """Wrapper for SDK queries with streaming support."""

    def __init__(
        self,
        logger: ComprehensiveLogger,
        progress_callback: Optional[Callable[[str], None]] = None,
    ):
        """Initialize streaming query wrapper.

        Args:
            logger: Logger instance
            progress_callback: Optional progress callback
        """
        self.logger = logger
        self.progress_callback = progress_callback

    async def query_with_streaming(
        self,
        query_func: Callable,
        *args,
        **kwargs,
    ) -> str:
        """Execute query with streaming progress reporting.

        Args:
            query_func: Async query function that returns iterator
            *args: Positional arguments for query
            **kwargs: Keyword arguments for query

        Returns:
            Complete response text
        """
        reporter = StreamingProgressReporter(
            logger=self.logger,
            progress_callback=self.progress_callback,
        )

        # Execute query
        query_iterator = await query_func(*args, **kwargs)

        # Monitor and report progress
        response = await reporter.report_progress(query_iterator)

        # Log statistics
        stats = reporter.get_statistics()
        self.logger.logger.info(
            "query_streaming_stats",
            **stats,
        )

        return response


__all__ = [
    "StreamChunk",
    "StreamingProgressReporter",
    "StreamingQueryWrapper",
]
