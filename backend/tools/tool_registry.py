"""
Registry module for managing and discovering external CounterGuard tools.
"""

from typing import Any, Dict, List, Optional, Type

from backend.exceptions import ToolNotFoundError
from backend.tools.base_tool import BaseTool


class ToolRegistry:
    """
    Registry for all available tools in the CounterGuard Tool Framework.
    """

    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, name: Optional[str] = None):
        """
        Decorator to register a BaseTool subclass into the registry.
        If name is not provided, it will attempt to instantiate or access the class's name property.

        Usage:
            @ToolRegistry.register("google_search")
            class GoogleSearchTool(BaseTool):
                ...
        """

        def decorator(tool_class: Type[BaseTool]) -> Type[BaseTool]:
            if not issubclass(tool_class, BaseTool):
                raise TypeError(
                    f"Cannot register '{tool_class.__name__}'; must inherit from BaseTool."
                )

            tool_name = name
            if not tool_name:
                try:
                    tool_name = tool_class().name
                except Exception as exc:
                    raise ValueError(
                        f"Could not determine name for tool '{tool_class.__name__}'. "
                        "Please pass an explicit name to @ToolRegistry.register(name)."
                    ) from exc

            cls._tools[tool_name] = tool_class
            return tool_class

        return decorator

    @classmethod
    def register_tool(
        cls, tool_class: Type[BaseTool], name: Optional[str] = None
    ) -> None:
        """
        Procedural method to register a BaseTool subclass without a decorator.
        """
        cls.register(name=name)(tool_class)

    @classmethod
    def get_tool(cls, name: str) -> Type[BaseTool]:
        """
        Retrieve the class definition of a registered tool by its name.

        Raises:
            ToolNotFoundError: If the requested tool name is not in the registry.
        """
        if name not in cls._tools:
            raise ToolNotFoundError(f"Tool '{name}' not found in ToolRegistry.")
        return cls._tools[name]

    @classmethod
    def create_tool(cls, name: str, *args: Any, **kwargs: Any) -> BaseTool:
        """
        Instantiate and return a registered tool by name with optional constructor arguments.

        Raises:
            ToolNotFoundError: If the requested tool name is not in the registry.
        """
        tool_class = cls.get_tool(name)
        return tool_class(*args, **kwargs)

    @classmethod
    def list_tools(cls) -> List[str]:
        """
        Return a sorted list of all registered tool names.
        """
        return sorted(cls._tools.keys())

    @classmethod
    def get_tool_schemas(cls) -> List[Dict[str, Any]]:
        """
        Return metadata schemas for all registered tools to empower AI agents
        with dynamic tool discovery.
        """
        schemas = []
        for name in cls.list_tools():
            tool_instance = cls.create_tool(name)
            schemas.append(tool_instance.to_schema())
        return schemas

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered tools from the registry. Mostly used for testing or resets.
        """
        cls._tools.clear()
