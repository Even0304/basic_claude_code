#!/usr/bin/env python3
"""
Simple demo showing parallel multi-agent execution.
Much simpler than parallel_agents.py, easier to debug.
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
    print("🚀 kimi-code: Parallel Multi-Agent Demo")
    print("=" * 70)

    # Setup
    print("\n📋 Setting up...")
    settings = Settings(provider='kimi')
    settings.validate()
    provider = get_provider(settings)
    tools = get_default_tools()

    print(f"✓ Provider: {provider.model}")
    print(f"✓ Tools: {[t.name for t in tools]}")

    agent = Agent(
        provider=provider,
        tools=tools,
        system="You are a helpful code analysis assistant. Use the task tool to run analyses in parallel when possible.",
        name="parallel-demo",
    )

    print(f"✓ Agent ready: {agent.name}\n")

    # Simple test
    print("=" * 70)
    print("TEST 1: Single analysis (baseline)")
    print("=" * 70)

    prompt1 = "How many Python files are in this directory? Count them for me."

    print(f"\n📝 Prompt: {prompt1}\n")
    print("🔄 Running agent...")

    start = time.monotonic()
    result1 = await agent.run(prompt1)
    elapsed1 = time.monotonic() - start

    print(f"\n✅ Result:\n{result1}")
    print(f"\n⏱️  Time: {elapsed1:.1f}s")

    # Parallel test
    print("\n" + "=" * 70)
    print("TEST 2: Parallel analysis (using task tool)")
    print("=" * 70)

    prompt2 = """
    Please use the task tool to run these analyses in PARALLEL:
    1. Count the number of Python files
    2. Find all TODO comments
    3. Count total lines of code

    Do them at the same time using the task tool, not one by one.
    """

    print(f"\n📝 Prompt: {prompt2}\n")
    print("🔄 Running agent with parallel tasks...")

    agent.clear_history()  # Start fresh

    start = time.monotonic()
    result2 = await agent.run(prompt2)
    elapsed2 = time.monotonic() - start

    print(f"\n✅ Result:\n{result2}")
    print(f"\n⏱️  Time: {elapsed2:.1f}s")

    # Summary
    print("\n" + "=" * 70)
    print("📊 Summary")
    print("=" * 70)

    print(f"\nTest 1 (single): {elapsed1:.1f}s")
    print(f"Test 2 (parallel): {elapsed2:.1f}s")

    if elapsed2 < elapsed1:
        speedup = elapsed1 / elapsed2
        print(f"\n🎉 Parallel is {speedup:.1f}x faster!")
    else:
        print(f"\n(Times may vary due to network conditions)")

    print("\n" + "=" * 70)
    print("✅ Demo completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
