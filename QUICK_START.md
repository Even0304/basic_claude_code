# kimi-code 快速启动指南

## 🚀 5 分钟入门

### 1️⃣ 安装
```bash
pip install -e .
```

### 2️⃣ 配置 API
创建 `.env` 文件:
```bash
# 方式 1: Kimi k2.5 (推荐)
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.miromind.site/v1
LLM_MODEL=moonshotai/kimi-k2.5

# 方式 2: Claude Opus
ANTHROPIC_API_KEY=sk-ant-xxx
```

### 3️⃣ 启动
```bash
# 流式交互模式（推荐）
kimi-code streaming

# 或传统模式
kimi-code
```

---

## 🎯 核心功能速览

### 功能 1️⃣: 流式响应 & 可视化
```bash
kimi-code streaming
```

输入提示词，实时看到：
- 🔧 工具调用过程
- ⏱️ 执行时间
- ✅ 完成状态
- 💰 成本统计

### 功能 2️⃣: 会话管理
```
在 REPL 中输入:
/sessions       列出所有保存的会话
/load abc123    加载某个会话
/save           保存当前会话
/export         导出为 Markdown
```

### 功能 3️⃣: 成本追踪
```
在 REPL 中输入:
/cost           显示 Token 和成本统计
```

### 功能 4️⃣: 帮助和工具
```
在 REPL 中输入:
/help           显示所有命令
/tools          列出可用工具
/history        查看对话历史
```

---

## 📊 演示脚本

### 基础演示（验证安装）
```bash
python demos/simple_demo.py
```
**输出**: 顺序 vs 并行执行对比 (预期: 2.7x 加速)

### 基准测试
```bash
python demos/benchmark.py kimi . 4
```
**输出**: 详细的性能指标对比

### 流式和会话演示
```bash
python demos/streaming_demo.py
```
**选项**:
1. 流式执行演示
2. 成本跟踪演示
3. 交互式 REPL

### 综合功能展示
```bash
python demos/comprehensive_demo.py
```
**展示**: Web 获取 + 并行 + 成本 + 工具组合

---

## 💡 常见用法

### 用法 1: 单次分析
```bash
kimi-code run "分析项目中的 async 代码"
```

### 用法 2: 交互式对话
```bash
kimi-code streaming
# 或
kimi-code
```

### 用法 3: 恢复上次对话
```bash
# 启动时会显示最近的会话
kimi-code streaming
# 在 REPL 中
/sessions        # 查看列表
/load abc123     # 加载某个会话
```

### 用法 4: 导出对话
```bash
kimi-code streaming
# 在 REPL 中
/export          # 生成 conversation_<session-id>.md
```

---

## 🔧 REPL 命令参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `/help` | 显示帮助 | `/help` |
| `/clear` | 清空对话 | `/clear` |
| `/history` | 查看历史 | `/history` |
| `/cost` | 成本统计 | `/cost` |
| `/sessions` | 列出会话 | `/sessions` |
| `/load <id>` | 加载会话 | `/load abc123` |
| `/save` | 保存会话 | `/save` |
| `/export` | 导出对话 | `/export` |
| `/tools` | 列出工具 | `/tools` |
| `/model` | 显示模型 | `/model` |
| `/exit` | 退出 | `/exit` |

---

## 🎮 交互式例子

```bash
$ kimi-code streaming

======================================================================
🚀 kimi-code: Interactive Agent REPL
======================================================================
Model: moonshotai/kimi-k2.5
Type /help for available commands

You: 有多少个 Python 文件在这个项目里？

[实时显示工具调用...]
✅ glob: 找到 45 个 Python 文件

[实时显示工具结果...]
✅ 分析完成

📊 Execution Summary
  Total Time: 12.3s
  Tools Used: 1
  Tool Time: 2.1s
  Tokens: 1,245
  Cost: $0.0034

You: /cost
[显示详细成本统计...]

You: /export
✅ Exported to: /Users/user/conversation_abc123.md

You: /exit
👋 Goodbye!
```

---

## 📈 性能期望

### 并行执行
- **顺序执行**: ~135s (4 个任务)
- **并行执行**: ~50s (4 个任务)
- **加速比**: **2.7x** ✅

### 成本示例 (Opus 4.6)
- 简单分析: $0.001 - $0.005
- 中等复杂: $0.005 - $0.02
- 复杂任务: $0.02 - $0.10

### Token 使用
- 简单问题: 500 - 1,000 tokens
- 中等问题: 1,000 - 3,000 tokens
- 复杂问题: 3,000 - 8,000 tokens

---

## 🔗 常见问题

### Q: 如何切换模型？
```bash
kimi-code --model claude-opus-4-6 streaming
```

### Q: 如何使用 Claude 而不是 Kimi？
```bash
kimi-code --provider claude streaming
```

### Q: 会话保存在哪里？
```bash
~/.kimi/sessions/     # JSON 格式
```

### Q: 如何清空所有会话？
```bash
rm -rf ~/.kimi/sessions/*
```

### Q: 如何看到完整的帮助？
在 REPL 中输入:
```
/help
```

### Q: 工具超时怎么办？
工具有内置超时保护（默认 30 秒），超时会自动返回错误。

### Q: 如何禁用自动保存？
目前自动保存无法禁用，但可以手动使用 `/clear` 清空历史。

---

## 📚 下一步阅读

1. **FEATURES_COMPARISON.md** — 详细功能对比
2. **FINAL_IMPLEMENTATION_REPORT.md** — 完整实现报告
3. **SESSION_SUMMARY.md** — 第一阶段总结
4. **demos/*.py** — 查看源代码示例

---

## 🆘 故障排查

### 问题: ImportError 找不到模块
**解决**: 确保安装了所有依赖
```bash
pip install -e .
```

### 问题: API 连接失败
**检查**:
1. `.env` 文件配置正确
2. API key 有效
3. 网络连接正常

### 问题: 工具执行失败
**检查**:
1. 输入参数格式
2. 文件路径存在
3. 权限设置正确

### 问题: 会话无法加载
**解决**:
1. 检查会话 ID 正确
2. 会话文件未损坏
3. 如有问题删除 `~/.kimi/sessions/` 重新开始

---

## ⚡ 高级用法

### 以编程方式使用
```python
from kimi_code.agent_streaming import StreamingAgent
from kimi_code.ui.stream_display import StreamingDisplay
from kimi_code.config import Settings
from kimi_code.providers import get_provider
from kimi_code.tools import get_default_tools

# 设置
settings = Settings(provider='kimi')
provider = get_provider(settings)
tools = get_default_tools()

# 创建 Agent
display = StreamingDisplay()
agent = StreamingAgent(
    provider=provider,
    tools=tools,
    display=display,
)

# 运行
result = await agent.run("Your prompt")

# 获取成本
cost = agent.get_cost_summary()
print(f"Cost: {cost.format_cost(cost.total_cost)}")
```

### 自定义系统提示
```bash
kimi-code streaming --system "你是一个Python专家"
```

### 使用最小工具集
```bash
kimi-code --tools minimal streaming
```

---

## 📞 获取帮助

- **命令行帮助**: `kimi-code --help`
- **REPL 帮助**: 输入 `/help`
- **文档**: 查看 `*.md` 文件
- **源代码**: `kimi_code/` 目录有完整注释

---

## ✨ 核心特性总结

✅ **流式响应** — 实时看到 Agent 执行过程  
✅ **可视化界面** — 彩色输出，执行进度展示  
✅ **会话管理** — 自动保存/加载对话  
✅ **成本追踪** — 实时 Token 和成本计算  
✅ **强大工具集** — 9 个工具，支持并行执行  
✅ **多 LLM 支持** — Kimi k2.5 + Claude + OpenAI 兼容  
✅ **完全异步** — 高效的并发执行  

---

**开始使用**:
```bash
kimi-code streaming
```

**祝编码愉快！** 🚀
