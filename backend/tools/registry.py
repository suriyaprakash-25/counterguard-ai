import logging
from typing import Dict

from backend.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Centralized registry for discovering and accessing investigation tools.
    Maintains loose coupling between agents and tool implementations.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Registers a tool by its unique name."""
        if tool.name in self._tools:
            logger.warning(f"Tool {tool.name} is already registered. Overwriting.")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> BaseTool:
        """Retrieves a tool by name. Raises ValueError if not found."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered in the ToolRegistry.")
        return self._tools[name]

    def get_all_tools(self) -> list[BaseTool]:
        """Returns all registered tools."""
        return list(self._tools.values())
