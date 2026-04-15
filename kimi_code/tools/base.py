"""Base tool abstraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    """Result from executing a tool."""

    content: str
    is_error: bool = False


class BaseTool(ABC):
    """Abstract base class for all tools."""

    name: str
    description: str
    input_schema: dict[str, Any]  # JSON Schema format

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with the given arguments.

        Args:
            **kwargs: Arguments matching the input_schema

        Returns:
            ToolResult with the output and error status
        """
        pass
