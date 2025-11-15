"""Tool Registry for SDK."""

from typing import Dict, List, Callable, Any, Optional, get_type_hints
import inspect
from functools import wraps

from claude_code_builder_v2.core.logging_system import ComprehensiveLogger


def tool(description: Optional[str] = None) -> Callable:
    """
    Decorator to mark a function as an SDK tool.

    Usage:
        @tool("Description of what this tool does")
        async def my_tool(arg1: str, arg2: int) -> dict:
            return {"result": "..."}
    """
    def decorator(func: Callable) -> Callable:
        # Extract function signature
        sig = inspect.signature(func)

        # Build JSON schema from type hints
        schema = _build_schema_from_signature(func, sig)

        # Add metadata
        func._is_tool = True  # type: ignore
        func._tool_description = description or func.__doc__ or ""  # type: ignore
        func._tool_schema = schema  # type: ignore

        return func

    return decorator


def _build_schema_from_signature(func: Callable, sig: inspect.Signature) -> Dict[str, Any]:
    """Build JSON schema from function signature."""
    properties = {}
    required = []

    # Get type hints
    try:
        type_hints = get_type_hints(func)
    except Exception:
        type_hints = {}

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        # Get type hint
        param_type = type_hints.get(param_name, param.annotation)

        # Convert to JSON schema type
        json_type = _python_type_to_json_type(param_type)

        properties[param_name] = {"type": json_type}

        # Check if required (no default)
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _python_type_to_json_type(py_type: Any) -> str:
    """Convert Python type to JSON schema type."""
    # Handle string representations
    if isinstance(py_type, str):
        py_type_str = py_type.lower()
        if py_type_str == "str":
            return "string"
        elif py_type_str == "int":
            return "integer"
        elif py_type_str == "float":
            return "number"
        elif py_type_str == "bool":
            return "boolean"
        elif py_type_str == "list":
            return "array"
        elif py_type_str == "dict":
            return "object"
        return "string"

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    # Handle actual types
    return type_map.get(py_type, "string")


class ToolRegistry:
    """Registry for SDK tools."""

    def __init__(self, logger: ComprehensiveLogger) -> None:
        """Initialize tool registry."""
        self.logger = logger
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool function.

        Args:
            name: Tool name
            func: Tool function (should be @tool decorated)
        """
        if not getattr(func, "_is_tool", False):
            raise ValueError(f"Function {name} is not decorated with @tool")

        self.tools[name] = func
        self.tool_metadata[name] = {
            "description": func._tool_description,  # type: ignore
            "schema": func._tool_schema,  # type: ignore
        }

        self.logger.logger.debug(
            "tool_registered",
            tool=name,
        )

    def get_tool_definitions(self, tool_names: List[str]) -> List[Dict[str, Any]]:
        """
        Get tool definitions for SDK.

        Args:
            tool_names: List of tool names

        Returns:
            List of tool definitions in SDK format
        """
        definitions = []

        for name in tool_names:
            if name in self.tool_metadata:
                metadata = self.tool_metadata[name]
                definitions.append({
                    "name": name,
                    "description": metadata["description"],
                    "input_schema": metadata["schema"],
                })

        return definitions

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """
        Execute a tool.

        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        tool_func = self.tools[tool_name]

        # Execute tool
        try:
            if inspect.iscoroutinefunction(tool_func):
                result = await tool_func(**arguments)
            else:
                result = tool_func(**arguments)

            return result

        except Exception as e:
            self.logger.logger.error(
                "tool_execution_error",
                tool=tool_name,
                error=str(e),
                exc_info=True,
            )
            raise
