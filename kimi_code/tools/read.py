"""File reading tool."""

from pathlib import Path
from typing import Any

import aiofiles

from kimi_code.tools.base import BaseTool, ToolResult


class ReadTool(BaseTool):
    """Read file contents."""

    name = "read"
    description = "Read the contents of a file. Returns up to 2000 lines by default."
    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of lines to read (default: 2000)",
                "default": 2000,
            },
        },
        "required": ["file_path"],
    }

    async def execute(self, file_path: str, limit: int = 2000) -> ToolResult:
        """Read a file.

        Args:
            file_path: Path to read
            limit: Max lines to read

        Returns:
            ToolResult with file contents
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return ToolResult(content=f"File not found: {file_path}", is_error=True)

            async with aiofiles.open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = []
                i = 0
                async for line in f:
                    if i >= limit:
                        lines.append(f"... [truncated after {limit} lines]")
                        break
                    lines.append(line.rstrip())
                    i += 1

            content = "\n".join(lines)
            return ToolResult(content=content)

        except Exception as e:
            return ToolResult(
                content=f"Error reading file: {type(e).__name__}: {e}",
                is_error=True,
            )
