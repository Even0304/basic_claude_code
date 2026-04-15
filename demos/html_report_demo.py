#!/usr/bin/env python3
"""Generate beautiful HTML reports from agent analysis.

This demo shows how to create interactive HTML visualizations
of agent execution results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from kimi_code.ui.html_report import HTMLReportGenerator


def generate_project_analysis_report():
    """Generate an HTML report of project analysis."""

    # Create report
    report = HTMLReportGenerator(title="kimi-code 项目分析报告")

    # Add metadata
    report.add_metadata("项目名称", "kimi-code")
    report.add_metadata("分析日期", "2025-04-15")
    report.add_metadata("分析工具", "AI Agent")
    report.add_metadata("状态", "✅ 完成")

    # Add statistics
    report.add_stats(
        {
            "Python 文件": "53",
            "包含 Async": "30",
            "总代码行数": "5,300+",
            "项目完整度": "95%",
        }
    )

    # Add analysis sections
    report.add_section(
        "📊 项目概览",
        """kimi-code 是 Claude Code 的 Python 实现。

核心特性：
• 流式响应 - 实时看到 Agent 执行过程
• 可视化界面 - Rich 彩色输出
• 会话管理 - 自动保存/加载对话
• 成本跟踪 - Token 和美元计算
• 9 个工具 - 支持并行执行
• 多 LLM 支持 - Kimi + Claude + OpenAI

实现完整度：95% ✅""",
        "text",
    )

    # Add file statistics table
    report.add_table(
        "📁 文件统计",
        ["目录", "Python 文件", "包含 Async", "用途"],
        [
            ["kimi_code/", "21", "18", "核心代码"],
            ["kimi_code/tools/", "9", "6", "工具集"],
            ["kimi_code/ui/", "4", "3", "用户界面"],
            ["demos/", "6", "5", "演示脚本"],
            ["tests/", "3", "2", "测试代码"],
            ["其他", "10", "5", "辅助文件"],
        ],
    )

    # Add code example
    report.add_code_block(
        "💻 使用示例",
        '''from kimi_code.agent_streaming import StreamingAgent
from kimi_code.ui.stream_display import StreamingDisplay
from kimi_code.config import Settings
from kimi_code.providers import get_provider
from kimi_code.tools import get_default_tools

# 设置
settings = Settings(provider='kimi')
provider = get_provider(settings)
tools = get_default_tools()

# 创建带可视化的 Agent
display = StreamingDisplay()
agent = StreamingAgent(
    provider=provider,
    tools=tools,
    display=display,
    show_thinking=True,
)

# 运行
result = await agent.run("分析项目结构")
cost = agent.get_cost_summary()
print(f"成本: {cost.format_cost(cost.total_cost)}")''',
        "python",
    )

    # Add feature comparison
    report.add_section(
        "✨ 核心特性",
        """✅ 流式响应 - 实时 token 输出
✅ 可视化展示 - Rich 执行过程显示
✅ 会话持久化 - 自动保存和恢复
✅ 成本跟踪 - 14 种模型定价库
✅ 权限系统 - 5 种模式，危险检测
✅ 并行执行 - 2.7x 加速验证
✅ 多工具支持 - 9 个工具，完全异步
✅ 多提供商 - Kimi + Claude + OpenAI
✅ 交互式 REPL - 8 种强大命令""",
        "text",
    )

    # Add performance section
    report.add_section(
        "⚡ 性能指标",
        """并行执行：
  • 顺序执行: 135.8s
  • 并行执行: 50.8s
  • 加速比: 2.7x ✅

成本跟踪（Opus 4.6）：
  • 简单问题: $0.001 - $0.005
  • 中等问题: $0.005 - $0.02
  • 复杂问题: $0.02 - $0.10

Token 使用：
  • 简单问题: 500 - 1,000 tokens
  • 中等问题: 1,000 - 3,000 tokens
  • 复杂问题: 3,000 - 8,000 tokens""",
        "text",
    )

    # Add REPL commands
    report.add_table(
        "🎮 REPL 命令",
        ["命令", "说明", "示例"],
        [
            ["/help", "显示帮助信息", "/help"],
            ["/cost", "显示成本统计", "/cost"],
            ["/history", "查看对话历史", "/history"],
            ["/sessions", "列出保存的会话", "/sessions"],
            ["/load <id>", "加载某个会话", "/load abc123"],
            ["/save", "保存当前会话", "/save"],
            ["/export", "导出为 Markdown", "/export"],
            ["/clear", "清空对话历史", "/clear"],
        ],
    )

    # Add usage section
    report.add_section(
        "🚀 快速开始",
        """安装：
  pip install -e .

配置 .env：
  OPENAI_API_KEY=sk-xxx
  OPENAI_BASE_URL=https://api.miromind.site/v1
  LLM_MODEL=moonshotai/kimi-k2.5

启动流式模式（推荐）：
  kimi-code streaming

传统 REPL：
  kimi-code

单次执行：
  kimi-code run "分析项目结构"

运行演示：
  python demos/streaming_demo.py
  python demos/benchmark.py kimi . 4
  python demos/html_report_demo.py""",
        "text",
    )

    # Generate and save
    output_file = Path.home() / "kimi_analysis_report.html"
    html_content = report.generate(str(output_file))

    print("\n" + "=" * 70)
    print("✅ HTML 报告生成成功!")
    print("=" * 70)
    print(f"\n📄 报告已保存: {output_file}")
    print(f"📊 文件大小: {len(html_content) / 1024:.1f} KB")
    print(f"\n在浏览器中打开:\n  open '{output_file}'")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    generate_project_analysis_report()
