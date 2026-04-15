"""Console UI helpers with Rich."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from kimi_code.models import LLMResponse, ToolCall, ToolResult


class AgentConsole:
    """Display helper with Rich for agent output."""

    def __init__(self, console: Console | None = None, verbose: bool = True):
        """Initialize AgentConsole.

        Args:
            console: Rich Console instance
            verbose: Whether to print detailed output
        """
        self._console = console or Console()
        self.verbose = verbose

    def sub_console(self, parent_name: str = "") -> "AgentConsole":
        """Create a sub-console for nested agents."""
        return AgentConsole(console=self._console, verbose=self.verbose)

    def print(self, *args, **kwargs) -> None:
        """Print to console."""
        self._console.print(*args, **kwargs)

    def on_tool_start(self, agent_name: str, tool_call: ToolCall) -> None:
        """Display when a tool starts executing."""
        if not self.verbose:
            return

        if tool_call.name == "bash":
            cmd = tool_call.arguments.get("command", "")
            self._console.print(
                Panel(
                    Syntax(cmd, "bash", theme="monokai", line_numbers=False),
                    title=f"[bold cyan]bash[/]",
                    border_style="cyan",
                    expand=False,
                )
            )
        elif tool_call.name == "task":
            tasks = tool_call.arguments.get("tasks", [])
            lines = [f"  {i + 1}. {t.get('description', '?')[:60]}" for i, t in enumerate(tasks)]
            self._console.print(
                Panel(
                    "\n".join(lines),
                    title=f"[bold magenta]task ({len(tasks)} parallel)[/]",
                    border_style="magenta",
                )
            )
        else:
            self._console.print(f"  [dim]{tool_call.name}[/]", end="")

    def on_tool_end(self, agent_name: str, tool_call: ToolCall, result: ToolResult) -> None:
        """Display when a tool finishes."""
        if not self.verbose:
            return
        if result.is_error:
            self._console.print(f"[red]  ✗ Error[/]", end="")

    def on_llm_response(self, agent_name: str, response: LLMResponse) -> None:
        """Display LLM response."""
        if response.text:
            self._console.print(Markdown(response.text))

    def print_welcome(self, model: str, tools: list[str]) -> None:
        """Print welcome banner."""
        tools_str = ", ".join(tools) if tools else "(no tools)"
        self._console.print(
            Panel(
                f"[bold]kimi-code[/] — AI coding assistant\n"
                f"Model: [cyan]{model}[/]\n"
                f"Tools: [yellow]{tools_str}[/]\n\n"
                f"Type [cyan]/help[/] for commands or [cyan]/exit[/] to quit.",
                border_style="green",
                title="[bold green]Welcome[/]",
            )
        )

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self._console.print(f"[red]Error:[/] {message}")

    def print_info(self, message: str) -> None:
        """Print an info message."""
        self._console.print(f"[blue]Info:[/] {message}")

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self._console.print(f"[green]✓[/] {message}")
