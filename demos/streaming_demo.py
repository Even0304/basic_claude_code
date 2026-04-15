#!/usr/bin/env python3
"""Streaming demo showcasing real-time visualization and session management.

This demo shows:
1. Streaming visualization during agent execution
2. Real-time tool execution display
3. Session persistence
4. Interactive REPL interface
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kimi_code.agent_streaming import StreamingAgent
from kimi_code.config import Settings
from kimi_code.providers import get_provider
from kimi_code.tools import get_default_tools
from kimi_code.ui.interactive_repl import InteractiveREPL
from kimi_code.ui.stream_display import StreamingDisplay


async def demo_streaming_execution():
    """Demo 1: Streaming execution with visualization."""
    print("\n" + "=" * 70)
    print("DEMO 1: Streaming Execution with Real-Time Visualization")
    print("=" * 70)

    # Setup
    settings = Settings(provider="kimi")
    settings.validate()
    provider = get_provider(settings)
    tools = get_default_tools()

    display = StreamingDisplay()
    agent = StreamingAgent(
        provider=provider,
        tools=tools,
        system="You are a helpful code analysis assistant.",
        name="streaming-demo",
        display=display,
        show_thinking=True,
    )

    # Run with streaming
    prompt = """
    Analyze the Python project:
    1. Count total Python files
    2. Find files with 'async' keyword
    3. List any configuration files

    Execute these tasks in parallel.
    """

    print(f"\n📝 Running with streaming visualization...\n")
    result = await agent.run(prompt)

    # Show final result
    print("\n" + "-" * 70)
    print("Final Analysis Complete ✅\n")


async def demo_cost_tracking():
    """Demo 2: Real-time cost tracking."""
    print("\n" + "=" * 70)
    print("DEMO 2: Real-Time Cost Tracking")
    print("=" * 70)

    settings = Settings(provider="kimi")
    settings.validate()
    provider = get_provider(settings)
    tools = get_default_tools()

    display = StreamingDisplay()
    agent = StreamingAgent(
        provider=provider,
        tools=tools,
        name="cost-tracking-demo",
        display=display,
    )

    print("\n💰 Tracking costs in real-time...\n")

    prompt = "Count the Python files and list the largest ones."
    result = await agent.run(prompt)

    # Display cost breakdown
    cost = agent.get_cost_summary()
    print("\n💵 Detailed Cost Breakdown:")
    print(f"  Input Tokens:  {cost.total_input_tokens:,}")
    print(f"  Output Tokens: {cost.total_output_tokens:,}")
    print(f"  Total Tokens:  {cost.total_tokens:,}")
    print(f"  Total Cost:    {cost.format_cost(cost.total_cost)}")


def demo_interactive_repl():
    """Demo 3: Interactive REPL with persistence."""
    print("\n" + "=" * 70)
    print("DEMO 3: Interactive REPL (Type /help for commands)")
    print("=" * 70)

    def create_agent(display=None):
        settings = Settings(provider="kimi")
        settings.validate()
        provider = get_provider(settings)
        tools = get_default_tools()

        return StreamingAgent(
            provider=provider,
            tools=tools,
            system="You are a helpful assistant analyzing a Python project.",
            display=display,
        )

    settings = Settings(provider="kimi")
    repl = InteractiveREPL(
        agent_factory=create_agent,
        model=settings.llm_model,
        auto_save=True,
    )

    # Run REPL
    repl.run()


async def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("🚀 kimi-code: Streaming & Visualization Demo Suite")
    print("=" * 70)

    # Choose demo
    print("\nChoose a demo to run:")
    print("1. Streaming Execution (real-time visualization)")
    print("2. Cost Tracking (token usage display)")
    print("3. Interactive REPL (persistent sessions)")
    print("0. Run all demos in sequence")

    choice = input("\nSelect (0-3): ").strip()

    if choice == "1":
        await demo_streaming_execution()
    elif choice == "2":
        await demo_cost_tracking()
    elif choice == "3":
        demo_interactive_repl()
    elif choice == "0":
        await demo_streaming_execution()
        await demo_cost_tracking()
        demo_interactive_repl()
    else:
        print("Invalid choice")

    print("\n" + "=" * 70)
    print("✅ Demo completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
