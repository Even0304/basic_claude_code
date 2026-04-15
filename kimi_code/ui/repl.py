"""Interactive REPL for kimi-code."""

import asyncio

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from kimi_code.agent import Agent
from kimi_code.config import Settings
from kimi_code.models import Message
from kimi_code.ui.console import AgentConsole


SLASH_COMMANDS = {
    "/exit": "Exit kimi-code",
    "/quit": "Exit kimi-code",
    "/clear": "Clear conversation history",
    "/history": "Show conversation history",
    "/model": "Show current model",
    "/tools": "List available tools",
    "/tokens": "Show token usage",
    "/help": "Show this help message",
}


class REPL:
    """Interactive REPL for the agent."""

    def __init__(self, agent: Agent, settings: Settings, console: Console | None = None):
        """Initialize REPL.

        Args:
            agent: Agent instance
            settings: Settings instance
            console: Rich Console instance
        """
        self.agent = agent
        self.settings = settings
        self.console = console or Console()
        self.ui = AgentConsole(console=self.console)

    async def run(self) -> None:
        """Run the interactive REPL loop."""
        self.ui.print_welcome(self.agent.provider.model, [t.name for t in self.agent.tools])

        while True:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: Prompt.ask("\n[bold green]>[/]")
                )
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[dim]Goodbye.[/]")
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            # Handle slash commands
            if user_input.startswith("/"):
                if not await self._handle_command(user_input):
                    break
                continue

            # Run agent
            try:
                self.console.print()
                await self.agent.run(user_input)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted.[/]")
            except Exception as e:
                self.ui.print_error(f"{type(e).__name__}: {e}")

    async def _handle_command(self, cmd_str: str) -> bool:
        """Handle a slash command. Returns False to signal exit.

        Args:
            cmd_str: Command string (e.g., "/exit")

        Returns:
            False to exit REPL, True to continue
        """
        parts = cmd_str.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd in ("/exit", "/quit"):
            self.console.print("[dim]Goodbye.[/]")
            return False

        elif cmd == "/clear":
            self.agent.clear_history()
            self.ui.print_success("Conversation history cleared")

        elif cmd == "/history":
            self._show_history()

        elif cmd == "/model":
            self.console.print(f"Model: [cyan]{self.agent.provider.model}[/]")

        elif cmd == "/tools":
            self._show_tools()

        elif cmd == "/tokens":
            # Could show total tokens used if we track them
            self.console.print("[dim]Token tracking not yet implemented[/]")

        elif cmd == "/help":
            self._show_help()

        else:
            self.ui.print_error(f"Unknown command: {cmd}. Type /help for available commands.")

        return True

    def _show_history(self) -> None:
        """Display conversation history."""
        messages = self.agent.messages
        if not messages:
            self.console.print("[dim]No conversation history[/]")
            return

        for i, msg in enumerate(messages):
            role_color = (
                "green" if msg.role == "user" else "blue" if msg.role == "assistant" else "dim"
            )
            content = str(msg.content)[:100]
            if len(str(msg.content)) > 100:
                content += "..."
            self.console.print(f"  {i+1}. [{role_color}]{msg.role}[/]: {content}")

    def _show_tools(self) -> None:
        """Display available tools."""
        table = Table(title="Available Tools")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="dim")

        for tool in self.agent.tools:
            desc = tool.description[:60] + ("..." if len(tool.description) > 60 else "")
            table.add_row(tool.name, desc)

        self.console.print(table)

    def _show_help(self) -> None:
        """Display help message."""
        self.console.print("\nAvailable slash commands:")
        for cmd, desc in SLASH_COMMANDS.items():
            self.console.print(f"  [cyan]{cmd:15}[/] {desc}")
        self.console.print()
