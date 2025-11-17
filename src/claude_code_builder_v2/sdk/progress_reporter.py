"""Streaming progress reporter for Claude SDK."""

from typing import AsyncIterator, Callable, Optional

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class StreamingProgressReporter:
    """Reports streaming progress from SDK queries."""

    def __init__(
        self,
        logger: ComprehensiveLogger,
        callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Initialize progress reporter.

        Args:
            logger: Comprehensive logger
            callback: Optional callback for each chunk
        """
        self.logger = logger
        self.callback = callback
        self.chunks_received = 0
        self.total_chars = 0

    async def report_progress(self, stream: AsyncIterator[str]) -> str:
        """Report progress from a streaming response.

        Args:
            stream: AsyncIterator yielding response chunks

        Returns:
            Complete response text
        """
        self.chunks_received = 0
        self.total_chars = 0
        response_parts = []

        try:
            async for chunk in stream:
                self.chunks_received += 1
                self.total_chars += len(chunk)
                response_parts.append(chunk)

                # Call callback if provided
                if self.callback:
                    self.callback(chunk)

                # Log progress periodically
                if self.chunks_received % 10 == 0:
                    self.logger.debug(
                        "streaming_progress",
                        msg="Streaming progress",
                        chunks=self.chunks_received,
                        chars=self.total_chars,
                    )

            response_text = "".join(response_parts)

            self.logger.info(
                "streaming_complete",
                msg="Streaming completed",
                total_chunks=self.chunks_received,
                total_chars=self.total_chars,
            )

            return response_text

        except Exception as e:
            self.logger.error(
                "streaming_error",
                msg=f"Streaming error: {e}",
                error=str(e),
                chunks_before_error=self.chunks_received,
            )
            raise

    def reset(self) -> None:
        """Reset progress tracking."""
        self.chunks_received = 0
        self.total_chars = 0
