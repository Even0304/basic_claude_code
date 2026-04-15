"""File globbing/pattern matching tool."""

from pathlib import Path
from typing import Any

from kimi_code.tools.base import BaseTool, ToolResult


class GlobTool(BaseTool):
    """Find files by glob pattern."""

    name = "glob"
    description = (
        "Find files matching a glob pattern (e.g., '**/*.py' for all Python files). "
        "Returns a list of matching file paths."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob pattern (e.g., '*.py', '**/*.txt')",
            },
            "path": {
                "type": "string",
                "description": "Directory to search (default: current directory)",
                "default": ".",
            },
        },
        "required": ["pattern"],
    }

    async def execute(self, pattern: str, path: str = ".") -> ToolResult:
        """Find files matching a pattern.

        Args:
            pattern: Glob pattern
            path: Root directory to search from

        Returns:
            ToolResult with list of matching files
        """
        try:
            root = Path(path)
            if not root.exists():
                return ToolResult(
                    content=f"Path not found: {path}",
                    is_error=True,
                )

            matches = list(root.glob(pattern))
            matches.sort()

            if not matches:
                return ToolResult(content=f"No files matching pattern: {pattern}")

            result_lines = [str(m.relative_to(root)) for m in matches]
            content = "\n".join(result_lines)

            return ToolResult(content=content)

        except Exception as e:
            return ToolResult(
                content=f"Error globbing files: {type(e).__name__}: {e}",
                is_error=True,
            )
