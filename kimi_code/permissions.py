"""Permission and safety system for agent operations."""

import re
from enum import Enum
from typing import Optional

from kimi_code.models import ToolCall


class PermissionMode(Enum):
    """Permission modes for agent execution."""

    DEFAULT = "default"  # Ask for dangerous operations
    PLAN = "plan"  # Read-only mode
    ACCEPT_EDITS = "acceptEdits"  # Auto-approve file edits
    BYPASS = "bypassPermissions"  # Skip all confirmations
    DONT_ASK = "dontAsk"  # Auto-reject confirmations


class DangerLevel(Enum):
    """Danger level of an operation."""

    SAFE = "safe"  # No concerns
    WARNING = "warning"  # Should ask user
    DANGEROUS = "dangerous"  # Requires explicit approval
    FORBIDDEN = "forbidden"  # Never allow


# Patterns for dangerous shell commands
DANGEROUS_PATTERNS = [
    r"rm\s+(-[rfR]+\s+)?/",  # rm -rf /
    r"git\s+reset\s+--hard",  # git reset --hard
    r"git\s+clean",  # git clean
    r"sudo\s+",  # sudo commands
    r"mkfs",  # Format filesystem
    r"dd\s+",  # Low-level disk operations
    r"killall",  # Kill all processes
    r"chmod\s+777",  # Dangerous permissions
    r"chown\s+",  # Change ownership
    r"halt|shutdown|reboot",  # System shutdown
    r"rm\s+-rf",  # Recursive forced delete
    r"git\s+push\s+--force",  # Force git push
]

# Patterns for operations that write files
WRITE_PATTERNS = [
    r"write_file|WriteTool",
    r"edit_file|EditTool",
    r">>\s*[a-zA-Z]",  # Append redirection
    r">\s*[a-zA-Z]",  # Write redirection
]


class PermissionChecker:
    """Checks if operations are allowed based on permission mode."""

    def __init__(self, mode: PermissionMode = PermissionMode.DEFAULT) -> None:
        """Initialize permission checker.

        Args:
            mode: The permission mode
        """
        self.mode = mode
        self.denied_operations: list[str] = []
        self.allowed_operations: list[str] = []

    def should_ask_for_tool(self, tool_call: ToolCall) -> bool:
        """Determine if user should be asked about this tool call.

        Args:
            tool_call: The tool call to check

        Returns:
            True if user should be asked, False otherwise
        """
        danger_level = self.assess_tool_danger(tool_call)

        if self.mode == PermissionMode.PLAN:
            # Plan mode: only allow read tools
            return not self._is_read_tool(tool_call.name)

        if self.mode == PermissionMode.BYPASS:
            # Bypass mode: never ask
            return False

        if self.mode == PermissionMode.DONT_ASK:
            # Auto-reject mode: ask (then reject)
            return danger_level == DangerLevel.DANGEROUS

        if self.mode == PermissionMode.ACCEPT_EDITS:
            # Auto-approve edits: only ask for shell commands
            return tool_call.name == "bash" and danger_level == DangerLevel.DANGEROUS

        # DEFAULT mode: ask for dangerous/warning operations
        return danger_level in (DangerLevel.DANGEROUS, DangerLevel.WARNING)

    def assess_tool_danger(self, tool_call: ToolCall) -> DangerLevel:
        """Assess the danger level of a tool call.

        Args:
            tool_call: The tool call to assess

        Returns:
            DangerLevel enum value
        """
        tool_name = tool_call.name

        # Read-only tools are always safe
        if self._is_read_tool(tool_name):
            return DangerLevel.SAFE

        # Shell commands need detailed analysis
        if tool_name == "bash":
            return self._assess_shell_command(tool_call.arguments.get("command", ""))

        # File write operations
        if tool_name in ("write_file", "edit_file"):
            return DangerLevel.WARNING  # Ask before overwriting

        # Other tools are generally safe
        return DangerLevel.SAFE

    def _is_read_tool(self, tool_name: str) -> bool:
        """Check if a tool is read-only.

        Args:
            tool_name: Name of the tool

        Returns:
            True if tool only reads
        """
        read_tools = {"read", "read_file", "glob", "list_files", "grep", "grep_search", "web_fetch"}
        return tool_name in read_tools

    def _assess_shell_command(self, command: str) -> DangerLevel:
        """Assess danger level of a shell command.

        Args:
            command: The shell command to assess

        Returns:
            DangerLevel enum value
        """
        # Check against dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return DangerLevel.DANGEROUS

        # Common write operations are warnings
        if any(keyword in command.lower() for keyword in ["rm", "mv", "cp", "dd"]):
            return DangerLevel.DANGEROUS

        # Most other commands are just warnings
        if any(keyword in command.lower() for keyword in ["chmod", "chown", "sudo"]):
            return DangerLevel.WARNING

        return DangerLevel.SAFE

    def get_permission_message(
        self, tool_call: ToolCall, danger_level: DangerLevel
    ) -> str:
        """Get a message for asking permission.

        Args:
            tool_call: The tool call
            danger_level: The assessed danger level

        Returns:
            A message to display to the user
        """
        if tool_call.name == "bash":
            cmd = tool_call.arguments.get("command", "").strip()
            if len(cmd) > 100:
                cmd = cmd[:100] + "..."
            return f"Execute shell command?\n\n$ {cmd}\n\nContinue? (y/n): "

        if tool_call.name in ("write_file", "edit_file"):
            filepath = tool_call.arguments.get("file_path", "unknown")
            return f"Modify file?\n\n{filepath}\n\nContinue? (y/n): "

        return f"Execute {tool_call.name}? (y/n): "

    def add_permission_rule(
        self, pattern: str, allow: bool = True
    ) -> None:
        """Add a permission rule (allow/deny pattern).

        Args:
            pattern: Regex pattern to match against commands
            allow: Whether to allow matching commands
        """
        if allow:
            self.allowed_operations.append(pattern)
        else:
            self.denied_operations.append(pattern)

    def check_against_rules(self, command: str) -> Optional[bool]:
        """Check a command against permission rules.

        Args:
            command: The command to check

        Returns:
            True if allowed, False if denied, None if no rule matches
        """
        # Check deny rules first (higher priority)
        for pattern in self.denied_operations:
            if re.search(pattern, command, re.IGNORECASE):
                return False

        # Check allow rules
        for pattern in self.allowed_operations:
            if re.search(pattern, command, re.IGNORECASE):
                return True

        # No rule matched
        return None
