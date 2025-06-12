"""Claude Code Executor - Main execution engine."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, AsyncIterator

import anthropic
from anthropic import AsyncAnthropic

from claude_code_builder.core.config import ExecutorConfig, settings
from claude_code_builder.core.enums import OutputFormat
from claude_code_builder.core.exceptions import APIError, ExecutionTimeoutError
from claude_code_builder.core.logging_system import ComprehensiveLogger


class ClaudeCodeExecutor:
    """Main Claude Code execution engine."""
    
    def __init__(
        self,
        config: Optional[ExecutorConfig] = None,
        logger: Optional[ComprehensiveLogger] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the executor."""
        self.config = config or ExecutorConfig()
        self.logger = logger
        self.api_key = api_key or settings.anthropic_api_key
        
        # Initialize Anthropic client
        self.client = AsyncAnthropic(api_key=self.api_key)
        
        # Track usage
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.api_calls_made = 0
        
        # Tool definitions cache
        self._tool_definitions: Dict[str, Dict[str, Any]] = {}
        self._load_tool_definitions()

    def _load_tool_definitions(self) -> None:
        """Load tool definitions for Claude Code SDK."""
        # These would be the actual tool definitions from Claude Code SDK
        # Simplified for implementation
        self._tool_definitions = {
            "Agent": {
                "name": "Agent",
                "description": "Launch a new agent for complex tasks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "context": {"type": "string"},
                    },
                    "required": ["task"],
                },
            },
            "Read": {
                "name": "Read",
                "description": "Read a file from the filesystem",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "offset": {"type": "integer"},
                        "limit": {"type": "integer"},
                    },
                    "required": ["file_path"],
                },
            },
            "Write": {
                "name": "Write",
                "description": "Write content to a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["file_path", "content"],
                },
            },
            "Edit": {
                "name": "Edit",
                "description": "Edit a file by replacing text",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "old_string": {"type": "string"},
                        "new_string": {"type": "string"},
                        "replace_all": {"type": "boolean"},
                    },
                    "required": ["file_path", "old_string", "new_string"],
                },
            },
            "MultiEdit": {
                "name": "MultiEdit",
                "description": "Make multiple edits to a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "edits": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "old_string": {"type": "string"},
                                    "new_string": {"type": "string"},
                                },
                                "required": ["old_string", "new_string"],
                            },
                        },
                    },
                    "required": ["file_path", "edits"],
                },
            },
            "Bash": {
                "name": "Bash",
                "description": "Execute a bash command",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "timeout": {"type": "integer"},
                    },
                    "required": ["command"],
                },
            },
            "Glob": {
                "name": "Glob",
                "description": "Find files matching a pattern",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string"},
                    },
                    "required": ["pattern"],
                },
            },
            "Grep": {
                "name": "Grep",
                "description": "Search for patterns in files",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string"},
                        "include": {"type": "string"},
                    },
                    "required": ["pattern"],
                },
            },
            "TodoWrite": {
                "name": "TodoWrite",
                "description": "Update the todo list",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "todos": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "content": {"type": "string"},
                                    "status": {"type": "string"},
                                    "priority": {"type": "string"},
                                    "id": {"type": "string"},
                                },
                                "required": ["content", "status", "priority", "id"],
                            },
                        },
                    },
                    "required": ["todos"],
                },
            },
            "WebFetch": {
                "name": "WebFetch",
                "description": "Fetch content from a URL",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "prompt": {"type": "string"},
                    },
                    "required": ["url", "prompt"],
                },
            },
            "WebSearch": {
                "name": "WebSearch",
                "description": "Search the web",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "allowed_domains": {"type": "array", "items": {"type": "string"}},
                        "blocked_domains": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["query"],
                },
            },
        }

    def get_tool_definitions(self, tool_names: List[str]) -> List[Dict[str, Any]]:
        """Get tool definitions for specified tools."""
        tools = []
        for name in tool_names:
            if name in self._tool_definitions:
                tools.append(self._tool_definitions[name])
        return tools

    async def call_claude(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        stream: bool = False,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make a call to Claude API."""
        timeout = timeout or self.config.timeout_seconds
        
        # LOG THE RAW REQUEST BEING SENT TO CLAUDE
        if self.logger:
            self.logger.logger.info(
                "claude_api_raw_request",
                model=self.config.model,
                system_prompt_length=len(system_prompt),
                system_prompt_preview=system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt,
                messages_count=len(messages),
                messages=[{
                    "role": msg.get("role"),
                    "content_length": len(msg.get("content", "")),
                    "content_preview": msg.get("content", "")[:500] + "..." if len(msg.get("content", "")) > 500 else msg.get("content", ""),
                    "tool_calls": msg.get("tool_calls", []) if "tool_calls" in msg else None,
                } for msg in messages],
                tools_count=len(tools) if tools else 0,
                tool_names=[tool.get("name") for tool in tools] if tools else [],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
        
        try:
            # Prepare request
            request_params = {
                "model": self.config.model,
                "messages": messages,
                "system": system_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if tools:
                request_params["tools"] = tools
            
            # Make API call with timeout
            start_time = asyncio.get_event_loop().time()
            
            try:
                response = await asyncio.wait_for(
                    self.client.messages.create(**request_params),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                elapsed = asyncio.get_event_loop().time() - start_time
                if self.logger:
                    self.logger.logger.error(
                        "claude_api_timeout",
                        timeout=timeout,
                        elapsed=elapsed,
                        model=self.config.model,
                    )
                raise ExecutionTimeoutError(
                    "Claude API call timed out",
                    timeout,
                    elapsed,
                )
            
            # LOG THE RAW RESPONSE FROM CLAUDE
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if self.logger:
                self.logger.logger.info(
                    "claude_api_raw_response",
                    model=self.config.model,
                    elapsed_seconds=elapsed_time,
                    content_length=len(response.content[0].text) if response.content else 0,
                    content_preview=response.content[0].text[:1000] + "..." if response.content and len(response.content[0].text) > 1000 else response.content[0].text if response.content else "",
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    stop_reason=response.stop_reason,
                    has_tool_calls=hasattr(response.content[0], "tool_calls") if response.content else False,
                )
            
            # Process response
            result = {
                "content": response.content[0].text if response.content else "",
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "stop_reason": response.stop_reason,
            }
            
            # Extract tool calls if present
            if hasattr(response.content[0], "tool_calls"):
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "arguments": tc.input,
                    }
                    for tc in response.content[0].tool_calls
                ]
                
                # LOG TOOL CALLS
                if self.logger:
                    self.logger.logger.info(
                        "claude_api_tool_calls",
                        tool_calls=[{
                            "id": tc.id,
                            "name": tc.name,
                            "arguments": tc.input,
                        } for tc in response.content[0].tool_calls],
                    )
            
            # Update usage tracking
            self.total_tokens_used += (
                response.usage.input_tokens + response.usage.output_tokens
            )
            self.api_calls_made += 1
            
            # Estimate cost (rough estimates)
            input_cost = response.usage.input_tokens * 0.000015  # $15/1M tokens
            output_cost = response.usage.output_tokens * 0.000075  # $75/1M tokens
            self.total_cost += input_cost + output_cost
            
            # LOG COST AND USAGE
            if self.logger:
                self.logger.logger.info(
                    "claude_api_usage",
                    api_calls_total=self.api_calls_made,
                    tokens_total=self.total_tokens_used,
                    cost_total=self.total_cost,
                    cost_this_call=input_cost + output_cost,
                )
            
            return result
            
        except anthropic.APIError as e:
            if self.logger:
                self.logger.logger.error(
                    "claude_api_error",
                    error_type="anthropic_api_error",
                    error_message=str(e),
                    status_code=getattr(e, "status_code", None),
                    model=self.config.model,
                    exc_info=True,
                )
            raise APIError(
                f"Anthropic API error: {str(e)}",
                status_code=getattr(e, "status_code", None),
                response_body=getattr(e, "response", None),
            )
        except Exception as e:
            if self.logger:
                self.logger.logger.error(
                    "claude_api_error",
                    error_type="unexpected_error",
                    error_message=str(e),
                    model=self.config.model,
                    exc_info=True,
                )
            raise APIError(f"Unexpected error calling Claude: {str(e)}")

    async def execute_with_tools(
        self,
        initial_message: str,
        system_prompt: str,
        allowed_tools: Optional[List[str]] = None,
        max_iterations: int = 10,
        callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Execute a task using Claude with tools."""
        allowed_tools = allowed_tools or self.config.allowed_tools
        tools = self.get_tool_definitions(allowed_tools)
        
        messages = [{"role": "user", "content": initial_message}]
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            
            # Call Claude
            response = await self.call_claude(
                messages=messages,
                system_prompt=system_prompt,
                tools=tools,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            
            # Add assistant response to messages
            assistant_message = {
                "role": "assistant",
                "content": response["content"],
            }
            
            if "tool_calls" in response:
                assistant_message["tool_calls"] = response["tool_calls"]
            
            messages.append(assistant_message)
            
            # Check if we have tool calls to execute
            if "tool_calls" not in response:
                # No more tool calls, we're done
                break
            
            # Execute tool calls
            for tool_call in response["tool_calls"]:
                tool_result = await self._execute_tool_call(tool_call, callback)
                
                # Add tool result to messages
                messages.append({
                    "role": "user",
                    "content": json.dumps(tool_result),
                    "tool_call_id": tool_call["id"],
                })
            
            # Check stop reason
            if response.get("stop_reason") == "stop_sequence":
                break
        
        return {
            "final_response": response.get("content", ""),
            "messages": messages,
            "iterations": iterations,
            "total_tokens": self.total_tokens_used,
            "total_cost": self.total_cost,
        }

    async def _execute_tool_call(
        self,
        tool_call: Dict[str, Any],
        callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Execute a tool call."""
        tool_name = tool_call["name"]
        arguments = tool_call.get("arguments", {})
        
        # LOG TOOL EXECUTION START
        if self.logger:
            self.logger.logger.info(
                "tool_execution_start",
                tool_name=tool_name,
                tool_id=tool_call.get("id"),
                arguments=arguments,
                has_callback=callback is not None,
            )
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # In a real implementation, this would execute actual tools
            # For now, return mock results
            if callback:
                result = await callback(tool_name, arguments)
            else:
                result = {
                    "tool": tool_name,
                    "status": "success",
                    "result": f"Executed {tool_name} with {arguments}",
                }
            
            elapsed = asyncio.get_event_loop().time() - start_time
            
            # LOG TOOL EXECUTION SUCCESS
            if self.logger:
                self.logger.logger.info(
                    "tool_execution_complete",
                    tool_name=tool_name,
                    tool_id=tool_call.get("id"),
                    elapsed_seconds=elapsed,
                    result_preview=str(result)[:500] + "..." if len(str(result)) > 500 else str(result),
                    status=result.get("status", "unknown"),
                )
            
            return result
            
        except Exception as e:
            elapsed = asyncio.get_event_loop().time() - start_time
            
            # LOG TOOL EXECUTION ERROR
            if self.logger:
                self.logger.logger.error(
                    "tool_execution_error",
                    tool_name=tool_name,
                    tool_id=tool_call.get("id"),
                    elapsed_seconds=elapsed,
                    error=str(e),
                    exc_info=True,
                )
            
            return {
                "tool": tool_name,
                "status": "error",
                "error": str(e),
            }

    async def stream_execution(
        self,
        initial_message: str,
        system_prompt: str,
        allowed_tools: Optional[List[str]] = None,
        output_callback: Optional[Any] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream execution results as they happen."""
        allowed_tools = allowed_tools or self.config.allowed_tools
        tools = self.get_tool_definitions(allowed_tools)
        
        messages = [{"role": "user", "content": initial_message}]
        
        # Stream response
        stream = await self.client.messages.create(
            model=self.config.model,
            messages=messages,
            system=system_prompt,
            tools=tools,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
        )
        
        async for chunk in stream:
            if output_callback:
                await output_callback(chunk)
            
            yield {
                "type": "stream_chunk",
                "content": chunk,
            }

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary."""
        return {
            "api_calls": self.api_calls_made,
            "total_tokens": self.total_tokens_used,
            "total_cost": self.total_cost,
            "average_tokens_per_call": (
                self.total_tokens_used / self.api_calls_made
                if self.api_calls_made > 0
                else 0
            ),
        }

    async def validate_api_key(self) -> bool:
        """Validate the API key works."""
        try:
            # Make a simple test call
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use cheapest model
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
            )
            return True
        except Exception:
            return False


from typing import AsyncIterator  # Add this import


__all__ = ["ClaudeCodeExecutor"]