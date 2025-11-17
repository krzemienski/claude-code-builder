"""SDK Client Manager for Claude Code Builder v2.

This module manages interactions with the real Claude Agent SDK.
"""

from typing import Any, AsyncIterator, Dict, List, Optional

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    UserMessage,
    query,
)

from claude_code_builder_v2.core.config import ExecutorConfig
from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


class SDKClientManager:
    """Manages Claude SDK client instances and interactions."""

    def __init__(
        self,
        config: ExecutorConfig,
        logger: ComprehensiveLogger,
        hooks: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize SDK client manager.

        Args:
            config: Executor configuration
            logger: Comprehensive logger instance
            hooks: Optional hooks for SDK events
        """
        self.config = config
        self.logger = logger
        self.hooks = hooks or {}

        # Create SDK client options
        self.options = ClaudeAgentOptions(
            system_prompt=config.system_prompt or "",
            model=config.model,
            max_turns=config.max_turns or 10,
            allowed_tools=config.allowed_tools or [],
            permission_mode=config.permission_mode or "auto",
            cwd=config.cwd,
        )

        # Initialize SDK client for bidirectional conversations
        self.client: Optional[ClaudeSDKClient] = None

    async def query_simple(self, prompt: str, **kwargs: Any) -> str:
        """Execute simple query using SDK query() function.

        Args:
            prompt: User prompt
            **kwargs: Additional options (model, max_turns, etc.)

        Returns:
            Response text from Claude
        """
        try:
            # Merge options
            options = {
                "model": kwargs.get("model", self.config.model),
                "max_turns": kwargs.get("max_turns", self.config.max_turns),
                "system_prompt": kwargs.get("system_prompt", self.config.system_prompt),
            }

            # Log query start
            self.logger.info(
                "sdk_query_start",
                msg="Starting SDK query",
                model=options["model"],
                max_turns=options["max_turns"],
            )

            # Execute query
            response_text = ""
            async for chunk in query(prompt, **options):
                response_text += chunk

            # Log completion
            self.logger.info(
                "sdk_query_complete",
                msg="SDK query completed",
                response_length=len(response_text),
            )

            return response_text

        except Exception as e:
            self.logger.error(
                "sdk_query_error",
                msg=f"SDK query failed: {e}",
                error=str(e),
            )
            raise

    async def query_streaming(
        self, prompt: str, **kwargs: Any
    ) -> AsyncIterator[str]:
        """Execute streaming query using SDK query() function.

        Args:
            prompt: User prompt
            **kwargs: Additional options

        Yields:
            Response chunks from Claude
        """
        try:
            options = {
                "model": kwargs.get("model", self.config.model),
                "max_turns": kwargs.get("max_turns", self.config.max_turns),
                "system_prompt": kwargs.get("system_prompt", self.config.system_prompt),
            }

            self.logger.info(
                "sdk_streaming_start",
                msg="Starting SDK streaming query",
                model=options["model"],
            )

            chunk_count = 0
            async for chunk in query(prompt, **options):
                chunk_count += 1
                yield chunk

            self.logger.info(
                "sdk_streaming_complete",
                msg="SDK streaming completed",
                chunks=chunk_count,
            )

        except Exception as e:
            self.logger.error(
                "sdk_streaming_error",
                msg=f"SDK streaming failed: {e}",
                error=str(e),
            )
            raise

    async def create_conversation(
        self,
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
    ) -> ClaudeSDKClient:
        """Create bidirectional conversation client.

        Args:
            system_prompt: Optional system prompt override
            allowed_tools: Optional tools override

        Returns:
            ClaudeSDKClient instance
        """
        try:
            # Update options if provided
            options = ClaudeAgentOptions(
                system_prompt=system_prompt or self.options.system_prompt,
                model=self.options.model,
                max_turns=self.options.max_turns,
                allowed_tools=allowed_tools or self.options.allowed_tools,
                permission_mode=self.options.permission_mode,
                cwd=self.options.cwd,
            )

            # Create client
            client = ClaudeSDKClient()

            self.logger.info(
                "sdk_conversation_created",
                msg="Created SDK conversation client",
                model=options.model,
                tools_count=len(options.allowed_tools),
            )

            self.client = client
            return client

        except Exception as e:
            self.logger.error(
                "sdk_conversation_error",
                msg=f"Failed to create conversation: {e}",
                error=str(e),
            )
            raise

    async def send_message(
        self, message: str, conversation_id: Optional[str] = None
    ) -> AssistantMessage:
        """Send message in bidirectional conversation.

        Args:
            message: User message
            conversation_id: Optional conversation ID

        Returns:
            Assistant response message
        """
        if not self.client:
            raise RuntimeError("Conversation client not initialized")

        try:
            # Create user message
            user_msg = UserMessage(content=message)

            # Send message
            response = await self.client.send_message(user_msg)

            self.logger.info(
                "sdk_message_sent",
                msg="Message sent to SDK",
                message_length=len(message),
            )

            return response

        except Exception as e:
            self.logger.error(
                "sdk_message_error",
                msg=f"Failed to send message: {e}",
                error=str(e),
            )
            raise

    async def close(self) -> None:
        """Close SDK client and cleanup."""
        if self.client:
            # Cleanup if needed
            self.client = None
            self.logger.info("sdk_client_closed", msg="SDK client closed")

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get SDK usage statistics.

        Returns:
            Dictionary with usage stats
        """
        # This will be populated by hooks/cost tracker
        return {
            "total_queries": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "model": self.config.model,
        }
