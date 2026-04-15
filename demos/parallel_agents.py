"""
Demo: Parallel Multi-Agent Execution via TaskTool

This demo shows the TaskTool spawning 4 sub-agents in parallel to:
  - Count Python files
  - Count total lines of code
  - List dependencies (if they exist)
  - Find TODO comments

The parent agent orchestrates all 4 analyses simultaneously and synthesizes results.
"""

import asyncio
import time

from kimi_code.agent import Agent
from kimi_code.config import Settings, get_settings
from kimi_code.providers import get_provider
from kimi_code.tools.bash import BashTool
from kimi_code.tools.glob_tool import GlobTool
from kimi_code.tools.grep_tool import GrepTool
from kimi_code.tools.read import ReadTool
from kimi_code.tools.task import TaskTool


SYSTEM_PROMPT = """You are a code analysis assistant. When asked to analyze a project,
use the task tool to run multiple analyses IN PARALLEL for efficiency.
Always use the task tool for operations that can be parallelized.
Provide clear, concise summaries of your findings."""

DEMO_PROMPT = """
Analyze the current Python project by doing ALL of the following simultaneously using the task tool:

1. Count the total number of Python (.py) files in the project
2. Count the total lines of code across all Python files
3. List any dependencies found (from requirements.txt, pyproject.toml, or setup.py if they exist)
4. Find all TODO and FIXME comments in the codebase

Use the task tool to run these 4 analyses in parallel. Then provide a concise project summary.
"""


async def run_demo(provider_name: str = "kimi", target_dir: str = ".") -> None:
    """Run the parallel agents demo.

    Args:
        provider_name: "kimi" or "claude"
        target_dir: Directory to analyze
    """
    print("\n" + "=" * 70)
    print("kimi-code: Parallel Multi-Agent Demo")
    print("=" * 70)
    print(
        f"\nThis demo shows {len(['a', 'b', 'c', 'd'])} tasks running in parallel "
        "using the task tool."
    )
    print(f"Target directory: {target_dir}")
    print(f"Provider: {provider_name}")
    print("-" * 70 + "\n")

    # Setup
    settings = Settings(provider=provider_name)
    provider = get_provider(settings)

    tools = [
        BashTool(working_dir=target_dir),
        ReadTool(),
        GlobTool(),
        GrepTool(),
        TaskTool(),
    ]

    agent = Agent(
        provider=provider,
        tools=tools,
        system=SYSTEM_PROMPT,
        name="demo-agent",
    )

    # Run demo
    print(f"[INFO] Starting analysis...")
    print(f"[INFO] Running on provider: {provider.model}")
    print(f"[INFO] Tools available: {[t.name for t in agent.tools]}\n")

    start = time.monotonic()
    try:
        result = await agent.run(DEMO_PROMPT)
        elapsed = time.monotonic() - start

        print("\n" + "=" * 70)
        print("✅ ANALYSIS RESULTS:")
        print("=" * 70)

        if result:
            print(result)
        else:
            print("[WARNING] No results returned from agent")
            print("Agent messages:", len(agent.messages))
            for i, msg in enumerate(agent.messages[-3:]):  # Show last 3 messages
                print(f"\nMessage {i}:")
                print(f"  Role: {msg.role}")
                print(f"  Content: {str(msg.content)[:200]}...")

        print("=" * 70)
        print(f"\n[INFO] Analysis completed in {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print("[INFO] Demo finished successfully!\n")

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    import sys

    provider = sys.argv[1] if len(sys.argv) > 1 else "kimi"
    target = sys.argv[2] if len(sys.argv) > 2 else "."

    asyncio.run(run_demo(provider_name=provider, target_dir=target))
