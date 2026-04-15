"""File content search tool."""

import asyncio
from pathlib import Path
from typing import Any

from kimi_code.tools.base import BaseTool, ToolResult


class GrepTool(BaseTool):
    """Search file contents using grep/ripgrep."""

    name = "grep"
    description = (
        "Search for patterns in files using regex (like grep). "
        "Returns matching lines with file paths and line numbers."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Regex pattern to search for",
            },
            "path": {
                "type": "string",
                "description": "File or directory to search (default: current directory)",
                "default": ".",
            },
            "type": {
                "type": "string",
                "description": "File type filter (e.g., 'py', 'js', 'txt')",
            },
        },
        "required": ["pattern"],
    }

    async def execute(
        self, pattern: str, path: str = ".", type: str | None = None
    ) -> ToolResult:
        """Search files for a pattern.

        Args:
            pattern: Regex pattern to search for
            path: File or directory to search
            type: Optional file type filter

        Returns:
            ToolResult with matching lines
        """
        try:
            search_path = Path(path)
            if not search_path.exists():
                return ToolResult(
                    content=f"Path not found: {path}",
                    is_error=True,
                )

            # Build command - prefer rg (ripgrep) if available, fall back to grep
            try:
                cmd = ["rg", "--color=never", "-n"]
                if type:
                    cmd.extend(["--type", type])
                cmd.extend([pattern, str(search_path)])
            except:
                cmd = ["grep", "-r", "-n", pattern, str(search_path)]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

            output = stdout.decode("utf-8", errors="replace").strip()
            if not output:
                return ToolResult(content=f"No matches found for pattern: {pattern}")

            # Truncate very long output
            if len(output) > 50_000:
                output = output[:50_000] + "\n... [output truncated]"

            return ToolResult(content=output)

        except asyncio.TimeoutError:
            return ToolResult(
                content="Search timed out",
                is_error=True,
            )
        except Exception as e:
            return ToolResult(
                content=f"Error searching files: {type(e).__name__}: {e}",
                is_error=True,
            )
