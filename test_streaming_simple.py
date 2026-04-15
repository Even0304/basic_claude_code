#!/usr/bin/env python3
"""Simple test for StreamingAgent - debug version."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kimi_code.agent_streaming import StreamingAgent
from kimi_code.config import Settings
from kimi_code.providers import get_provider
from kimi_code.tools import get_default_tools
from kimi_code.ui.stream_display import StreamingDisplay


async def main():
    print("\n" + "=" * 70)
    print("🔧 StreamingAgent Debug Test")
    print("=" * 70)

    # Setup
    print("\n📋 Setting up...")
    try:
        settings = Settings(provider="kimi")
        settings.validate()
        print(f"✅ Settings valid")
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return

    try:
        provider = get_provider(settings)
        print(f"✅ Provider: {provider.model}")
    except Exception as e:
        print(f"❌ Provider error: {e}")
        return

    try:
        tools = get_default_tools()
        print(f"✅ Tools loaded: {[t.name for t in tools]}")
    except Exception as e:
        print(f"❌ Tools error: {e}")
        return

    # Create agent
    try:
        display = StreamingDisplay()
        agent = StreamingAgent(
            provider=provider,
            tools=tools,
            system="你是一个有帮助的编程助手。分析 Python 项目。",
            name="debug-agent",
            display=display,
            show_thinking=True,
        )
        print(f"✅ Agent created: {agent.name}")
    except Exception as e:
        print(f"❌ Agent error: {e}")
        return

    # Simple test prompts
    test_prompts = [
        "当前工作目录是什么？",
        "这个目录中有多少个 Python 文件？",
        "列出 kimi_code 目录中的文件。",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'=' * 70}")
        print(f"TEST {i}: {prompt}")
        print("=" * 70)

        try:
            result = await agent.run(prompt)
            print(f"\n✅ Success!")
            print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")

            # Show cost
            cost = agent.get_cost_summary()
            print(f"💰 Cost: {cost.format_cost(cost.total_cost)}")
            print(f"📊 Tokens: {cost.total_tokens:,}")

            # Clear for next test
            agent.clear_history()

        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("✅ Debug test complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
