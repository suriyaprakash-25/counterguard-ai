"""
Base tool abstraction for CounterGuard Tool Framework.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """
    Abstract base class for all external tools in CounterGuard.

    Each tool exposes a common interface consisting of a name, description,
    parameter schema, and an abstract `run` method.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The unique identifier name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A detailed explanation of what the tool does and when to use it."""
        pass

    @property
    def parameters(self) -> Dict[str, Any]:
        """
        Optional JSON schema-like dictionary describing expected argument inputs.
        Defaults to an empty object schema.
        """
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """
        Execute the tool logic with the provided arguments.

        Args:
            **kwargs: Keyword arguments matching the tool's expected parameter schema.

        Returns:
            The output result of the tool execution.

        Raises:
            ToolExecutionError: If tool execution fails or validation fails.
        """
        pass

    def to_schema(self) -> Dict[str, Any]:
        """
        Export the tool definition as a standard metadata schema suitable
        for AI agents or function calling interfaces.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
