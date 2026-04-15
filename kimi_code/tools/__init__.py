"""Tools available to agents."""

from kimi_code.tools.base import BaseTool, ToolResult
from kimi_code.tools.bash import BashTool
from kimi_code.tools.task import TaskTool

__all__ = [
    "BaseTool",
    "ToolResult",
    "BashTool",
    "TaskTool",
]


def get_minimal_tools() -> list[BaseTool]:
    """Get minimal tool set (bash only)."""
    return [BashTool()]


def get_default_tools() -> list[BaseTool]:
    """Get default tool set (all basic tools, but not task tool - added by agent)."""
    from kimi_code.tools.read import ReadTool
    from kimi_code.tools.write import WriteTool
    from kimi_code.tools.edit import EditTool
    from kimi_code.tools.glob_tool import GlobTool
    from kimi_code.tools.grep_tool import GrepTool
    from kimi_code.tools.web_fetch import WebFetchTool

    return [
        BashTool(),
        ReadTool(),
        WriteTool(),
        EditTool(),
        GlobTool(),
        GrepTool(),
        WebFetchTool(),
    ]
