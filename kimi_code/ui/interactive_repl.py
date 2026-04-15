"""Interactive REPL with streaming visualization and session management."""

import asyncio
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from kimi_code.agent_streaming import StreamingAgent
from kimi_code.session_manager import SessionManager
from kimi_code.ui.stream_display import StreamingDisplay


class InteractiveREPL:
    """Interactive REPL for agent conversations with streaming and persistence."""

    def __init__(
        self,
        agent_factory,
        model: str = "unknown",
        auto_save: bool = True,
    ):
        """Initialize interactive REPL.

        Args:
            agent_factory: Callable that returns a StreamingAgent
            model: LLM model name
            auto_save: Whether to auto-save sessions
        """
        self.agent_factory = agent_factory
        self.model = model
        self.auto_save = auto_save

        self.console = Console()
        self.display = StreamingDisplay(self.console)
        self.session_manager = SessionManager()
        self.current_session_id = str(uuid.uuid4())[:8]
        self.current_agent: Optional[StreamingAgent] = None

    def run(self) -> None:
        """Start the interactive REPL loop."""
        self._print_banner()
        self.console.print("", style="")

        # Initialize agent
        self.current_agent = self.agent_factory(display=self.display)

        try:
            while True:
                try:
                    # Get user input
                    user_input = self.console.input("\n[cyan]You[/cyan]: ")

                    if not user_input.strip():
                        continue

                    # Handle special commands
                    if user_input.startswith("/"):
                        self._handle_command(user_input)
                        continue

                    # Run agent with streaming display
                    asyncio.run(self._run_agent(user_input))

                except KeyboardInterrupt:
                    self.console.print("\n\n⏹️  Interrupted by user", style="yellow")
                    break
                except EOFError:
                    break

        finally:
            self._print_goodbye()

    async def _run_agent(self, user_input: str) -> None:
        """Run agent with user input.

        Args:
            user_input: The user's input
        """
        try:
            result = await self.current_agent.run(user_input)

            # Auto-save if enabled
            if self.auto_save:
                self._save_current_session()

        except Exception as e:
            self.display.show_error(f"Error: {type(e).__name__}: {e}")

    def _save_current_session(self) -> None:
        """Save current session to disk."""
        if not self.current_agent:
            return

        try:
            cost = self.current_agent.get_cost_summary()
            self.session_manager.save_session(
                session_id=self.current_session_id,
                messages=self.current_agent.messages,
                agent_name=self.current_agent.name,
                model=self.model,
                cost_summary=cost,
            )
        except Exception as e:
            self.console.print(f"Warning: Could not save session: {e}", style="yellow")

    def _handle_command(self, command: str) -> None:
        """Handle special commands.

        Args:
            command: The command string
        """
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == "/help":
            self._print_help()
        elif cmd == "/clear":
            self._handle_clear()
        elif cmd == "/history":
            self._handle_history()
        elif cmd == "/cost":
            self._handle_cost()
        elif cmd == "/sessions":
            self._handle_list_sessions()
        elif cmd == "/load":
            self._handle_load_session(parts[1] if len(parts) > 1 else None)
        elif cmd == "/save":
            self._handle_save_session()
        elif cmd == "/export":
            self._handle_export()
        elif cmd == "/tools":
            self._handle_list_tools()
        elif cmd == "/model":
            self._handle_show_model()
        elif cmd == "/exit" or cmd == "/quit":
            raise KeyboardInterrupt()
        else:
            self.console.print(f"Unknown command: {cmd}. Type /help for available commands.", style="red")

    def _handle_clear(self) -> None:
        """Clear conversation history."""
        self.current_agent.clear_history()
        self.current_session_id = str(uuid.uuid4())[:8]
        self.console.print("✅ Conversation cleared", style="green")

    def _handle_history(self) -> None:
        """Show conversation history."""
        if not self.current_agent.messages:
            self.console.print("No messages in history", style="yellow")
            return

        self.console.print("\n📝 Conversation History:\n", style="cyan")
        for i, msg in enumerate(self.current_agent.messages, 1):
            role = "[cyan]User[/cyan]" if msg.role == "user" else "[yellow]Assistant[/yellow]"
            content = msg.content
            if isinstance(content, list):
                content = f"[Tool Results: {len(content)} items]"
            elif len(str(content)) > 200:
                content = str(content)[:200] + "..."

            self.console.print(f"{i}. {role}: {content}\n")

    def _handle_cost(self) -> None:
        """Show cost summary."""
        cost = self.current_agent.get_cost_summary()

        table = Table(title="💰 Cost Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value")

        table.add_row("Input Tokens", f"{cost.total_input_tokens:,}")
        table.add_row("Output Tokens", f"{cost.total_output_tokens:,}")
        if cost.total_cache_read_tokens > 0:
            table.add_row("Cache Read Tokens", f"{cost.total_cache_read_tokens:,}")
        if cost.total_cache_write_tokens > 0:
            table.add_row("Cache Write Tokens", f"{cost.total_cache_write_tokens:,}")

        table.add_row("Total Tokens", f"{cost.total_tokens:,}", style="bold")
        table.add_row("Total Cost", cost.format_cost(cost.total_cost), style="bold cyan")

        self.console.print(table)

    def _handle_list_sessions(self) -> None:
        """List saved sessions."""
        sessions = self.session_manager.list_sessions()

        if not sessions:
            self.console.print("No saved sessions", style="yellow")
            return

        self.console.print("\n📋 Saved Sessions:\n", style="cyan")
        for session in sessions[:10]:  # Show last 10
            self.console.print(self.session_manager.format_session_info(session))

        if len(sessions) > 10:
            self.console.print(f"\n... and {len(sessions) - 10} more sessions", style="dim")

    def _handle_load_session(self, session_id: Optional[str]) -> None:
        """Load a saved session.

        Args:
            session_id: Session ID to load
        """
        if not session_id:
            self.console.print("Usage: /load <session_id>", style="yellow")
            return

        session_data = self.session_manager.load_session(session_id)
        if not session_data:
            self.console.print(f"Session not found: {session_id}", style="red")
            return

        # Restore messages
        messages = self.session_manager.restore_messages(session_data)
        self.current_agent._messages = messages
        self.current_session_id = session_id

        self.console.print(f"✅ Loaded session: {session_id}", style="green")
        self.console.print(f"Messages: {len(messages)}", style="cyan")

    def _handle_save_session(self) -> None:
        """Save current session with custom ID."""
        custom_id = self.console.input("Enter session ID (or press Enter for auto): ").strip()
        if custom_id:
            self.current_session_id = custom_id

        self._save_current_session()
        self.console.print(f"✅ Session saved: {self.current_session_id}", style="green")

    def _handle_export(self) -> None:
        """Export conversation to markdown."""
        if not self.current_agent.messages:
            self.console.print("No messages to export", style="yellow")
            return

        # Create markdown content
        lines = [
            f"# Conversation Export",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Model**: {self.model}",
            f"**Total Tokens**: {self.current_agent.get_cost_summary().total_tokens:,}",
            "",
        ]

        for msg in self.current_agent.messages:
            role = "User" if msg.role == "user" else "Assistant"
            lines.append(f"## {role}")
            if isinstance(msg.content, str):
                lines.append(msg.content)
            else:
                lines.append(f"[Tool Result: {len(msg.content)} items]")
            lines.append("")

        # Save to file
        export_file = Path.home() / f"conversation_{self.current_session_id}.md"
        export_file.write_text("\n".join(lines))

        self.console.print(f"✅ Exported to: {export_file}", style="green")

    def _handle_list_tools(self) -> None:
        """List available tools."""
        if not self.current_agent.tools:
            self.console.print("No tools available", style="yellow")
            return

        table = Table(title="🔧 Available Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description")

        for tool in self.current_agent.tools:
            table.add_row(tool.name, tool.description[:60] + "..." if len(tool.description) > 60 else tool.description)

        self.console.print(table)

    def _handle_show_model(self) -> None:
        """Show current model."""
        self.console.print(f"Current Model: {self.model}", style="cyan")
        self.console.print(f"Agent: {self.current_agent.name}", style="cyan")
        self.console.print(f"Tools: {len(self.current_agent.tools)}", style="cyan")

    def _print_banner(self) -> None:
        """Print welcome banner."""
        self.console.print("\n" + "=" * 70, style="cyan")
        self.console.print("🚀 kimi-code: Interactive Agent REPL", style="bold cyan")
        self.console.print("=" * 70, style="cyan")
        self.console.print(f"Model: {self.model}", style="dim")
        self.console.print("Type /help for available commands", style="dim")
        self.console.print("")

    def _print_help(self) -> None:
        """Print help message."""
        help_text = """
📚 Available Commands:

General:
  /help          Show this help message
  /exit, /quit   Exit the REPL

Conversation:
  /clear         Clear conversation history
  /history       Show conversation history
  /cost          Show token usage and costs

Session Management:
  /sessions      List saved sessions
  /load <id>     Load a saved session
  /save          Save current session with custom ID
  /export        Export conversation to markdown

Information:
  /tools         List available tools
  /model         Show current model and agent info

Tips:
  • Sessions are auto-saved after each message
  • Use /load to resume previous conversations
  • Use /export to save conversations as markdown
  • Costs are tracked automatically
"""
        self.console.print(help_text, style="cyan")

    def _print_goodbye(self) -> None:
        """Print goodbye message."""
        self.console.print("\n" + "=" * 70, style="cyan")
        self.console.print("👋 Goodbye!", style="cyan")
        self.console.print("=" * 70, style="cyan")
        self.console.print("")
