#!/usr/bin/env python3
"""Benchmark - compare sequential vs parallel task execution performance.

This demo shows how TaskTool enables parallel sub-agent execution for
significant performance improvements.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Callable

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kimi_code.agent import Agent
from kimi_code.config import Settings
from kimi_code.providers import get_provider
from kimi_code.tools import get_default_tools


async def benchmark_sequential(agent: Agent, tasks: list[str], task_name: str) -> tuple[str, float]:
    """Run tasks sequentially (one by one).

    Args:
        agent: The agent to run tasks with
        tasks: List of task descriptions
        task_name: Name of the benchmark

    Returns:
        Tuple of (result, elapsed_time)
    """
    print(f"\n📝 {task_name} (Sequential):")
    for i, task in enumerate(tasks, 1):
        print(f"   Task {i}: {task[:50]}...")
    print("\n🔄 Running sequentially...")

    start = time.monotonic()

    prompt = "Execute these tasks ONE BY ONE (not in parallel):\n\n"
    for i, task in enumerate(tasks, 1):
        prompt += f"{i}. {task}\n"
    prompt += "\nDo them sequentially and report results."

    result = await agent.run(prompt)
    elapsed = time.monotonic() - start

    print(f"✅ Completed in {elapsed:.1f}s")
    return result, elapsed


async def benchmark_parallel(agent: Agent, tasks: list[str], task_name: str) -> tuple[str, float]:
    """Run tasks in parallel using TaskTool.

    Args:
        agent: The agent to run tasks with
        tasks: List of task descriptions
        task_name: Name of the benchmark

    Returns:
        Tuple of (result, elapsed_time)
    """
    print(f"\n📝 {task_name} (Parallel):")
    for i, task in enumerate(tasks, 1):
        print(f"   Task {i}: {task[:50]}...")
    print("\n🔄 Running in PARALLEL using task tool...")

    agent.clear_history()
    start = time.monotonic()

    prompt = "Use the task tool to run these tasks IN PARALLEL (all at the same time):\n\n"
    for i, task in enumerate(tasks, 1):
        prompt += f"{i}. {task}\n"
    prompt += "\nUse the task tool to execute them simultaneously."

    result = await agent.run(prompt)
    elapsed = time.monotonic() - start

    print(f"✅ Completed in {elapsed:.1f}s")
    return result, elapsed


async def run_benchmark(
    provider_name: str = "kimi",
    target_dir: str = ".",
    num_tasks: int = 3,
) -> None:
    """Run the benchmark suite.

    Args:
        provider_name: "kimi" or "claude"
        target_dir: Directory to analyze
        num_tasks: Number of parallel tasks (3-5)
    """
    print("\n" + "=" * 70)
    print("📊 kimi-code: Parallel Execution Benchmark")
    print("=" * 70)
    print(f"\nComparing sequential vs parallel task execution")
    print(f"Provider: {provider_name}")
    print(f"Target directory: {target_dir}")
    print(f"Number of tasks: {num_tasks}")
    print("-" * 70)

    # Setup
    settings = Settings(provider=provider_name)
    settings.validate()
    provider = get_provider(settings)
    tools = get_default_tools()

    agent = Agent(
        provider=provider,
        tools=tools,
        system="You are a code analysis assistant. Execute all requested analyses completely.",
        name="benchmark-agent",
    )

    # Define benchmark suites
    benchmarks = {
        "Code Analysis Suite": [
            "Count the total number of Python files in this directory",
            "Find all TODO and FIXME comments in the code",
            "List the dependencies from any requirements files",
            "Calculate total lines of code across all Python files",
            "Find the largest Python file by line count",
        ][:num_tasks],

        "Search Suite": [
            "List all files matching the pattern '*.py' in the current directory",
            "Find all Python files that contain 'async' or 'await' keywords",
            "Search for all imports of 'asyncio' or 'aiohttp' in the codebase",
            "Find all test files (files named test_*.py or *_test.py)",
            "Count how many files contain the word 'agent' or 'Agent'",
        ][:num_tasks],
    }

    results = {}
    total_seq = 0.0
    total_par = 0.0

    for suite_name, tasks in benchmarks.items():
        print(f"\n\n🔬 Benchmark Suite: {suite_name}")
        print("=" * 70)

        # Sequential run
        seq_result, seq_time = await benchmark_sequential(agent, tasks, suite_name)
        total_seq += seq_time

        # Parallel run
        par_result, par_time = await benchmark_parallel(agent, tasks, suite_name)
        total_par += par_time

        # Calculate speedup
        speedup = seq_time / par_time if par_time > 0 else 0
        improvement = ((seq_time - par_time) / seq_time * 100) if seq_time > 0 else 0

        results[suite_name] = {
            "sequential": seq_time,
            "parallel": par_time,
            "speedup": speedup,
            "improvement": improvement,
        }

        print(f"\n📊 Results for {suite_name}:")
        print(f"   Sequential: {seq_time:.1f}s")
        print(f"   Parallel:   {par_time:.1f}s")
        print(f"   Speedup:    {speedup:.2f}x faster")
        print(f"   Time saved: {improvement:.1f}%")

    # Summary
    print("\n\n" + "=" * 70)
    print("📈 Summary")
    print("=" * 70)

    for suite_name, metrics in results.items():
        print(f"\n{suite_name}:")
        print(f"  Sequential: {metrics['sequential']:.1f}s")
        print(f"  Parallel:   {metrics['parallel']:.1f}s")
        print(f"  Speedup:    {metrics['speedup']:.2f}x")
        print(f"  Improvement: {metrics['improvement']:.1f}%")

    print(f"\n{'Total Sequential:':<25} {total_seq:.1f}s")
    print(f"{'Total Parallel:':<25} {total_par:.1f}s")

    if total_par > 0:
        overall_speedup = total_seq / total_par
        overall_improvement = ((total_seq - total_par) / total_seq * 100)
        print(f"{'Overall Speedup:':<25} {overall_speedup:.2f}x")
        print(f"{'Overall Time Saved:':<25} {overall_improvement:.1f}%")

        print(f"\n🎉 Parallel execution is {overall_speedup:.2f}x faster overall!")

        if overall_speedup >= 2.0:
            print("   Excellent parallelization - TaskTool is very effective!")
        elif overall_speedup >= 1.5:
            print("   Good parallelization - Parallel tasks provide clear benefit")
        else:
            print("   Modest parallelization - Network/API latency may be the bottleneck")

    print("\n" + "=" * 70)
    print("✅ Benchmark completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    import sys

    provider = sys.argv[1] if len(sys.argv) > 1 else "kimi"
    target = sys.argv[2] if len(sys.argv) > 2 else "."
    num_tasks = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    asyncio.run(run_benchmark(provider_name=provider, target_dir=target, num_tasks=num_tasks))
