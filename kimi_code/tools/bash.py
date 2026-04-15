"""Bash/shell tool for executing commands."""

import asyncio
from pathlib import Path
from typing import Any

from kimi_code.tools.base import BaseTool, ToolResult


class BashTool(BaseTool):
    """Execute shell commands asynchronously."""

    name = "bash"
    description = (
        "Execute a shell command. Returns stdout, stderr, and exit code. "
        "Use for running scripts, searching files, git operations, etc."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 30, max: 120)",
                "default": 30,
            },
            "working_dir": {
                "type": "string",
                "description": "Working directory for the command (optional)",
            },
        },
        "required": ["command"],
    }

    def __init__(self, working_dir: str | Path | None = None):
        """Initialize BashTool.

        Args:
            working_dir: Default working directory for commands
        """
        self._default_working_dir = (
            Path(working_dir) if working_dir else Path.cwd()
        )

    async def execute(
        self,
        command: str,
        timeout: int = 30,
        working_dir: str | None = None,
    ) -> ToolResult:
        """Execute a shell command.

        Args:
            command: The shell command to run
            timeout: Maximum execution time in seconds (capped at 120)
            working_dir: Optional working directory override

        Returns:
            ToolResult with command output or error message
        """
        cwd = Path(working_dir) if working_dir else self._default_working_dir
        timeout = min(max(timeout, 1), 120)  # Clamp between 1 and 120 seconds

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(cwd),
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return ToolResult(
                    content=f"Command timed out after {timeout}s: {command}",
                    is_error=True,
                )

            stdout_text = stdout.decode("utf-8", errors="replace").strip()
            stderr_text = stderr.decode("utf-8", errors="replace").strip()
            exit_code = proc.returncode

            # Truncate very long output to avoid overwhelming the context
            MAX_OUTPUT = 50_000
            if len(stdout_text) > MAX_OUTPUT:
                stdout_text = stdout_text[:MAX_OUTPUT] + "\n... [output truncated]"
            if len(stderr_text) > MAX_OUTPUT:
                stderr_text = stderr_text[:MAX_OUTPUT] + "\n... [error truncated]"

            # Build output
            parts = []
            if stdout_text:
                parts.append(stdout_text)
            if stderr_text:
                parts.append(f"[stderr]\n{stderr_text}")
            if exit_code != 0:
                parts.append(f"[exit code: {exit_code}]")

            content = "\n".join(parts) if parts else "(no output)"
            is_error = exit_code != 0

            return ToolResult(content=content, is_error=is_error)

        except Exception as e:
            return ToolResult(
                content=f"Error executing command: {type(e).__name__}: {e}",
                is_error=True,
            )
