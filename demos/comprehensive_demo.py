#!/usr/bin/env python3
"""Comprehensive demo showcasing all major features.

This demo shows:
1. Web fetch tool
2. Cost tracking
3. Parallel execution
4. Tool composition
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kimi_code.agent import Agent
from kimi_code.config import Settings
from kimi_code.providers import get_provider
from kimi_code.tools import get_default_tools


async def main():
    print("\n" + "=" * 70)
    print("🚀 kimi-code: Comprehensive Feature Demo")
    print("=" * 70)

    # Setup
    print("\n📋 Setting up...")
    settings = Settings(provider="kimi")
    settings.validate()
    provider = get_provider(settings)
    tools = get_default_tools()

    print(f"✓ Provider: {provider.model}")
    print(f"✓ Tools ({len(tools)}): {[t.name for t in tools]}")

    agent = Agent(
        provider=provider,
        tools=tools,
        system="You are a helpful code analysis assistant.",
        name="comprehensive-demo",
    )

    print(f"✓ Agent ready: {agent.name}\n")

    # Feature 1: Web Fetch
    print("=" * 70)
    print("FEATURE 1: Web Fetch Tool")
    print("=" * 70)

    prompt1 = """
    Demonstrate the web_fetch tool:
    1. Fetch content from a public website
    2. Extract key information
    3. Summarize what you found

    Try to fetch the GitHub README or any other website you can access.
    """

    print(f"\n📝 Prompt: {prompt1.strip()}\n")
    print("🔄 Running agent...\n")

    start = time.monotonic()
    try:
        result1 = await agent.run(prompt1)
        elapsed1 = time.monotonic() - start
        print(f"\n✅ Result:\n{result1}")
        print(f"\n⏱️  Time: {elapsed1:.1f}s")

        # Show cost
        cost = agent.get_cost_summary()
        print(f"💰 Cost: {cost.format_cost(cost.total_cost)}")
        print(f"📊 Tokens: {cost.total_tokens:,}")
    except Exception as e:
        print(f"⚠️  Feature skipped (network/API unavailable): {e}")

    # Feature 2: Parallel Analysis with Cost Tracking
    print("\n\n" + "=" * 70)
    print("FEATURE 2: Parallel Analysis + Cost Tracking")
    print("=" * 70)

    prompt2 = """
    Use the task tool to run these analyses IN PARALLEL:
    1. Count Python files in this directory
    2. Find all TODO comments
    3. Count total lines of code

    Execute them simultaneously for speed.
    """

    print(f"\n📝 Prompt: {prompt2.strip()}\n")
    print("🔄 Running agent with parallel tasks...\n")

    agent.clear_history()
    cost_before = agent.get_cost_summary().total_cost
    start = time.monotonic()
    result2 = await agent.run(prompt2)
    elapsed2 = time.monotonic() - start

    print(f"\n✅ Result:\n{result2}")
    print(f"\n⏱️  Time: {elapsed2:.1f}s")

    # Show cost for this operation
    cost_after = agent.get_cost_summary().total_cost
    operation_cost = cost_after - cost_before
    cost_summary = agent.get_cost_summary()
    print(f"💰 Cost (this operation): {cost_summary.format_cost(operation_cost)}")
    print(f"💰 Total cost (session): {cost_summary.format_cost(cost_summary.total_cost)}")
    print(f"📊 Total tokens: {cost_summary.total_tokens:,}")

    # Feature 3: Tool Composition
    print("\n\n" + "=" * 70)
    print("FEATURE 3: Tool Composition (File Reading + Pattern Matching)")
    print("=" * 70)

    prompt3 = """
    Analyze the codebase:
    1. List all Python files using glob
    2. Read a few of them using read_file
    3. Search for 'async' pattern in the code using grep
    4. Report what you find
    """

    print(f"\n📝 Prompt: {prompt3.strip()}\n")
    print("🔄 Running agent...\n")

    agent.clear_history()
    start = time.monotonic()
    result3 = await agent.run(prompt3)
    elapsed3 = time.monotonic() - start

    print(f"\n✅ Result:\n{result3[:500]}..." if len(result3) > 500 else f"\n✅ Result:\n{result3}")
    print(f"\n⏱️  Time: {elapsed3:.1f}s")

    # Summary with costs
    print("\n\n" + "=" * 70)
    print("📊 Summary")
    print("=" * 70)

    final_cost = agent.get_cost_summary()
    print(f"\n✅ All features demonstrated successfully!")
    print(f"\nTotal Session Metrics:")
    print(f"  • Total tokens used: {final_cost.total_tokens:,}")
    print(f"  • Input tokens: {final_cost.total_input_tokens:,}")
    print(f"  • Output tokens: {final_cost.total_output_tokens:,}")
    print(f"  • Total cost: {final_cost.format_cost(final_cost.total_cost)}")
    print(f"  • Model: {provider.model}")

    print(f"\nFeatures demonstrated:")
    print(f"  ✓ Web fetch tool (HTTP + HTML cleaning)")
    print(f"  ✓ Parallel multi-task execution")
    print(f"  ✓ Cost tracking (tokens + USD)")
    print(f"  ✓ Tool composition and orchestration")
    print(f"  ✓ Async agent loop with streaming support")

    print("\n" + "=" * 70)
    print("✅ Comprehensive demo completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
