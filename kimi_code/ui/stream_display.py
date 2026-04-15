"""Streaming display UI for agent execution visualization."""

import time
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text


class StreamingDisplay:
    """Real-time visualization of agent execution with streaming support."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize streaming display.

        Args:
            console: Rich console instance (creates default if None)
        """
        self.console = console or Console()
        self.live: Optional[Live] = None
        self.start_time = 0.0
        self.current_status = ""
        self.tool_executions: list[dict] = []
        self.token_count = 0

    def start_execution(self, prompt: str, agent_name: str = "Agent") -> None:
        """Start displaying agent execution.

        Args:
            prompt: The user prompt being executed
            agent_name: Name of the agent
        """
        self.start_time = time.time()
        self.tool_executions.clear()
        self.token_count = 0

        # Display initial prompt
        self.console.print(f"\n🚀 {agent_name}", style="bold cyan")
        self.console.print(f"📝 Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"📝 Prompt: {prompt}")
        self.console.print("")

    def update_status(self, status: str) -> None:
        """Update current execution status.

        Args:
            status: Status message
        """
        self.current_status = status
        elapsed = time.time() - self.start_time
        self.console.print(f"⏳ {status} ({elapsed:.1f}s)", style="yellow")

    def show_tool_call(
        self,
        tool_name: str,
        arguments: dict,
        execution_start: float = 0.0,
    ) -> None:
        """Display a tool call.

        Args:
            tool_name: Name of the tool being called
            arguments: Tool arguments
            execution_start: Time the tool started executing
        """
        # Format arguments
        args_str = ", ".join(f"{k}={str(v)[:30]}" for k, v in arguments.items())
        self.console.print(f"  🔧 {tool_name}({args_str})", style="dim cyan")

    def show_tool_result(
        self,
        tool_name: str,
        result: str,
        elapsed: float,
        is_error: bool = False,
    ) -> None:
        """Display tool execution result.

        Args:
            tool_name: Name of the tool
            result: Result output
            elapsed: Time taken to execute
            is_error: Whether result is an error
        """
        style = "red" if is_error else "green"
        icon = "❌" if is_error else "✅"

        # Truncate long results
        display_result = result if len(result) < 200 else result[:200] + "..."
        self.console.print(
            f"  {icon} {tool_name} completed in {elapsed:.2f}s",
            style=style,
        )

        if is_error:
            self.console.print(f"     Error: {display_result}", style="red dim")
        elif len(display_result) > 0:
            self.console.print(f"     {display_result}", style="dim")

        self.tool_executions.append(
            {"tool": tool_name, "elapsed": elapsed, "is_error": is_error}
        )

    def show_thinking(self, thought: str, elapsed: float = 0.0) -> None:
        """Display LLM thinking/reasoning.

        Args:
            thought: The thought content
            elapsed: Time taken
        """
        # Truncate long thoughts
        display_thought = thought if len(thought) < 300 else thought[:300] + "..."
        self.console.print(f"💭 Thinking ({elapsed:.1f}s):", style="dim magenta")
        self.console.print(f"  {display_thought}", style="dim magenta")

    def show_streaming_response(self, token: str) -> None:
        """Display a token from streaming response.

        Args:
            token: The token to display
        """
        # Print without newline for streaming effect
        self.console.print(token, end="", highlight=False)

    def show_response(self, response: str, elapsed: float) -> None:
        """Display final response.

        Args:
            response: The response text
            elapsed: Time taken
        """
        self.console.print("\n")
        self.console.print(
            Panel(
                response,
                title="📤 Response",
                border_style="green",
                padding=(1, 2),
            )
        )
        self.console.print(f"⏱️  Response time: {elapsed:.1f}s\n", style="dim")

    def show_summary(
        self,
        total_time: float,
        tokens: int = 0,
        cost: Optional[str] = None,
    ) -> None:
        """Display execution summary.

        Args:
            total_time: Total execution time
            tokens: Total tokens used
            cost: Cost information
        """
        # Create summary table
        table = Table(title="📊 Execution Summary", show_header=False)
        table.add_row("Total Time", f"{total_time:.1f}s")
        table.add_row("Tools Used", str(len(self.tool_executions)))

        if self.tool_executions:
            tool_time = sum(t["elapsed"] for t in self.tool_executions)
            table.add_row("Tool Time", f"{tool_time:.1f}s")
            errors = sum(1 for t in self.tool_executions if t["is_error"])
            if errors > 0:
                table.add_row("Errors", str(errors), style="red")

        if tokens > 0:
            table.add_row("Tokens", f"{tokens:,}")

        if cost:
            table.add_row("Cost", cost, style="cyan")

        self.console.print(table)

    def show_error(self, error: str) -> None:
        """Display an error.

        Args:
            error: Error message
        """
        self.console.print(
            Panel(
                error,
                title="❌ Error",
                border_style="red",
                padding=(1, 2),
            ),
            style="red",
        )

    def show_parallel_execution(self, task_count: int) -> None:
        """Display parallel task execution indicator.

        Args:
            task_count: Number of parallel tasks
        """
        self.console.print(
            f"⚡ Executing {task_count} tasks in parallel...", style="yellow"
        )

    def show_progress_bar(
        self,
        current: int,
        total: int,
        description: str = "Progress",
    ) -> None:
        """Show a progress bar (simplified).

        Args:
            current: Current progress
            total: Total items
            description: Description
        """
        percentage = (current / total * 100) if total > 0 else 0
        bar_length = 20
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        self.console.print(
            f"{description} [{bar}] {percentage:.0f}%", style="cyan"
        )


class StreamingConsole:
    """Enhanced console for streaming agent responses."""

    def __init__(self):
        """Initialize streaming console."""
        self.console = Console()
        self.display = StreamingDisplay(self.console)
        self.buffer = ""

    def add_token(self, token: str) -> None:
        """Add a token to the streaming display.

        Args:
            token: The token to add
        """
        self.buffer += token
        # Print immediately for real-time effect
        self.console.print(token, end="", highlight=False)

    def flush(self) -> str:
        """Flush and return the buffered content.

        Returns:
            The complete buffered text
        """
        result = self.buffer
        self.buffer = ""
        return result

    def print_section(self, title: str, content: str, style: str = "cyan") -> None:
        """Print a section with title.

        Args:
            title: Section title
            content: Section content
            style: Text style
        """
        self.console.print(f"\n{title}", style=f"bold {style}")
        self.console.print(content)

    def print_success(self, message: str) -> None:
        """Print success message.

        Args:
            message: Success message
        """
        self.console.print(f"✅ {message}", style="green")

    def print_warning(self, message: str) -> None:
        """Print warning message.

        Args:
            message: Warning message
        """
        self.console.print(f"⚠️  {message}", style="yellow")

    def print_error(self, message: str) -> None:
        """Print error message.

        Args:
            message: Error message
        """
        self.console.print(f"❌ {message}", style="red")

    def print_info(self, message: str) -> None:
        """Print info message.

        Args:
            message: Info message
        """
        self.console.print(f"ℹ️  {message}", style="blue")
