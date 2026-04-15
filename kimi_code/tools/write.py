"""File writing tool."""

from pathlib import Path
from typing import Any

import aiofiles

from kimi_code.tools.base import BaseTool, ToolResult


class WriteTool(BaseTool):
    """Write or create files."""

    name = "write"
    description = "Write content to a file. Creates the file or overwrites existing content."
    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to write",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file",
            },
        },
        "required": ["file_path", "content"],
    }

    async def execute(self, file_path: str, content: str) -> ToolResult:
        """Write to a file.

        Args:
            file_path: Path to write to
            content: Content to write

        Returns:
            ToolResult confirming write
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(content)

            return ToolResult(
                content=f"Successfully wrote {len(content)} bytes to {file_path}"
            )

        except Exception as e:
            return ToolResult(
                content=f"Error writing file: {type(e).__name__}: {e}",
                is_error=True,
            )
