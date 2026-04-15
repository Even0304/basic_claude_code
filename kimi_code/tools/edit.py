"""File editing tool for exact string replacement."""

from pathlib import Path
from typing import Any

import aiofiles

from kimi_code.tools.base import BaseTool, ToolResult


class EditTool(BaseTool):
    """Edit files by exact string replacement."""

    name = "edit"
    description = (
        "Replace exact strings in a file. Useful for surgical edits. "
        "The old_string must match exactly (including whitespace)."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to edit",
            },
            "old_string": {
                "type": "string",
                "description": "Exact string to find and replace",
            },
            "new_string": {
                "type": "string",
                "description": "String to replace it with",
            },
        },
        "required": ["file_path", "old_string", "new_string"],
    }

    async def execute(self, file_path: str, old_string: str, new_string: str) -> ToolResult:
        """Edit a file by replacing text.

        Args:
            file_path: Path to edit
            old_string: Exact string to find
            new_string: Replacement string

        Returns:
            ToolResult confirming the edit
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return ToolResult(content=f"File not found: {file_path}", is_error=True)

            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                content = await f.read()

            if old_string not in content:
                return ToolResult(
                    content=f"Old string not found in {file_path}",
                    is_error=True,
                )

            new_content = content.replace(old_string, new_string, 1)

            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(new_content)

            return ToolResult(content=f"Successfully edited {file_path}")

        except Exception as e:
            return ToolResult(
                content=f"Error editing file: {type(e).__name__}: {e}",
                is_error=True,
            )
