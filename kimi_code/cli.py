"""CLI interface for kimi-code."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from kimi_code import __version__
from kimi_code.agent import Agent
from kimi_code.agent_streaming import StreamingAgent
from kimi_code.config import Settings, get_settings
from kimi_code.providers import get_provider
from kimi_code.tools import get_default_tools, get_minimal_tools
from kimi_code.ui.interactive_repl import InteractiveREPL
from kimi_code.ui.stream_display import StreamingDisplay
from kimi_code.ui.console import AgentConsole
from kimi_code.ui.repl import REPL

app = typer.Typer(name="kimi-code", help="AI-powered coding assistant")
console = Console()


def _get_default_system_prompt() -> str:
    """Get default system prompt."""
    return """You are an AI coding assistant. Help the user with programming tasks.
You have access to tools to read files, write code, search, run commands, and parallelize tasks.
Be helpful, clear, and concise. When appropriate, use the task tool to parallelize independent work."""


def _make_agent(
    provider: str,
    model: Optional[str],
    tools_set: str,
    system: Optional[str],
    debug: bool,
) -> Agent:
    """Create an agent with given configuration."""
    settings = Settings(provider=provider, debug=debug)

    if model:
        if provider == "kimi":
            settings.kimi_model = model
        else:
            settings.claude_model = model

    settings.validate()
    provider_instance = get_provider(settings)

    if tools_set == "none":
        tools = []
    elif tools_set == "minimal":
        tools = get_minimal_tools()
    else:
        tools = get_default_tools()
        # Add TaskTool for parallel agent support
        from kimi_code.tools.task import TaskTool
        tools.append(TaskTool())

    agent_console = AgentConsole(console=console, verbose=not debug)

    return Agent(
        provider=provider_instance,
        tools=tools,
        system=system or _get_default_system_prompt(),
        name="main",
    )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    provider: str = typer.Option("kimi", "--provider", "-p", help="Provider: kimi|claude"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name to use"),
    system: Optional[str] = typer.Option(None, "--system", "-s", help="Custom system prompt"),
    tools: str = typer.Option("all", "--tools", help="Tool set: all|minimal|none"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug output"),
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
) -> None:
    """Launch interactive REPL (default)."""
    if ctx.invoked_subcommand is not None:
        return

    if version:
        console.print(f"kimi-code {__version__}")
        raise typer.Exit()

    agent = _make_agent(provider, model, tools, system, debug)
    settings = get_settings()

    repl = REPL(agent=agent, settings=settings, console=console)
    asyncio.run(repl.run())


@app.command()
def run(
    prompt: str = typer.Argument(..., help="Prompt to execute"),
    provider: str = typer.Option("kimi", "--provider", help="Provider: kimi|claude"),
    model: Optional[str] = typer.Option(None, "--model", help="Model name"),
    tools: str = typer.Option("all", "--tools", help="Tool set: all|minimal|none"),
    max_turns: int = typer.Option(20, "--max-turns", help="Maximum turns"),
) -> None:
    """Execute a single prompt non-interactively."""
    agent = _make_agent(provider, model, tools, None, False)
    agent.max_turns = max_turns

    async def _run():
        try:
            result = await agent.run(prompt)
            if result:
                console.print(result)
        except Exception as e:
            console.print(f"[red]Error: {type(e).__name__}: {e}[/]")
            raise typer.Exit(1)

    asyncio.run(_run())


@app.command()
def streaming(
    provider: str = typer.Option("kimi", "--provider", "-p", help="Provider: kimi|claude"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name"),
    tools: str = typer.Option("all", "--tools", help="Tool set: all|minimal|none"),
) -> None:
    """Launch streaming interactive REPL with visualization."""
    settings = Settings(provider=provider)

    if model:
        if provider == "kimi":
            settings.kimi_model = model
        else:
            settings.claude_model = model

    settings.validate()
    provider_instance = get_provider(settings)

    if tools == "none":
        tool_list = []
    elif tools == "minimal":
        tool_list = get_minimal_tools()
    else:
        tool_list = get_default_tools()
        from kimi_code.tools.task import TaskTool
        tool_list.append(TaskTool())

    def create_agent(display: Optional[StreamingDisplay] = None):
        return StreamingAgent(
            provider=provider_instance,
            tools=tool_list,
            system=_get_default_system_prompt(),
            display=display,
            show_thinking=True,
        )

    repl = InteractiveREPL(
        agent_factory=create_agent,
        model=settings.llm_model,
        auto_save=True,
    )
    repl.run()


@app.command()
def demo(
    demo_name: str = typer.Argument("parallel", help="Demo: parallel|coding|streaming"),
    provider: str = typer.Option("kimi", "--provider", help="Provider to use"),
    target: str = typer.Option(".", "--target", help="Target directory for analysis"),
) -> None:
    """Run demo scripts."""
    import sys
    from pathlib import Path

    # Add the project root to sys.path so we can import demos
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    if demo_name == "parallel":
        try:
            from demos.parallel_agents import run_demo
        except ImportError:
            console.print("[red]Error: Could not import demo. Make sure demos/parallel_agents.py exists.[/]")
            raise typer.Exit(1)
        asyncio.run(run_demo(provider_name=provider, target_dir=target))
    elif demo_name == "streaming":
        try:
            from demos.streaming_demo import main as streaming_main
        except ImportError:
            console.print("[red]Error: Could not import streaming demo[/]")
            raise typer.Exit(1)
        asyncio.run(streaming_main())
    elif demo_name == "coding":
        console.print("[yellow]Coding demo not yet implemented[/]")
        raise typer.Exit(1)
    else:
        console.print(f"[red]Unknown demo: {demo_name}. Choose: parallel|coding|streaming[/]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
