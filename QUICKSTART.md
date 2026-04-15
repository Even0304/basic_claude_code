# Quickstart Guide — kimi-code

Get started with kimi-code in 5 minutes.

## 1. Installation

```bash
# Clone and install
git clone <repo-url>
cd kimi-code
pip install -e .
```

## 2. Configuration

Create `.env` with your API keys:

```bash
# Option A: Use Kimi via third-party API relay (recommended)
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.miromind.site/v1
LLM_MODEL=moonshotai/kimi-k2.5
PROVIDER=kimi

# Option B: Use Kimi directly from Moonshot AI
OPENAI_API_KEY=your-moonshot-api-key
OPENAI_BASE_URL=https://api.moonshot.cn/v1
LLM_MODEL=moonshot-v1-8k
PROVIDER=kimi

# Option C: Use Claude (Anthropic)
ANTHROPIC_API_KEY=your-api-key-here
PROVIDER=claude
```

## 3. Run Your First Demo

See the parallel agent system in action:

```bash
kimi-code demo parallel
```

This runs 4 analyses simultaneously:
- Count Python files
- Count lines of code
- List dependencies
- Find TODO comments

**Expected output:**
```
Task 1 (Count the total number of Python files):
...found 15 Python files...

Task 2 (Count the total lines of code):
...8,234 total lines...

Task 3 (List dependencies):
...anthropic, openai, rich...

Task 4 (Find all TODO comments):
...3 TODO comments found...
```

## 4. Interactive Mode

Try the interactive REPL:

```bash
kimi-code
```

You're now in an interactive session. Try:

```
> Analyze this directory structure

> Count the Python files

> /tools           # See available tools

> /help            # See all commands

> /exit            # Exit
```

## 5. Single Command Mode

Execute queries without interactive mode:

```bash
kimi-code run "List all Python files and summarize"

kimi-code run "Find all TODO comments" --provider claude

kimi-code run "Count lines of code" --tools minimal
```

## Understanding Parallel Agents

The key feature is the **task tool**. When you ask for multiple independent analyses:

```
"Count files, count lines, list deps, find TODOs — do all in parallel"
```

Behind the scenes:
1. The agent recognizes these are independent
2. Uses the `task` tool to spawn 4 sub-agents
3. All 4 run **simultaneously** (not sequentially)
4. Results aggregated and presented

This is 4x faster than doing them one-by-one!

## Key Concepts

### Tools
- **bash**: Run shell commands (`bash find . -type f -name '*.py'`)
- **read**: Read file contents
- **write**: Create/overwrite files
- **edit**: Replace specific text in files
- **glob**: Find files by pattern
- **grep**: Search file contents
- **task**: Spawn parallel sub-agents

### Providers
- **Kimi (Moonshot AI)**: OpenAI-compatible API
- **Claude (Anthropic)**: Native Anthropic API

Both work the same way; just change `PROVIDER` or use `--provider claude`.

### System Prompts
The agent has a default system prompt. Customize it:

```bash
kimi-code --system "You are a Python expert analyzing code quality"
```

## Common Tasks

### Count Python files
```
> Count the number of .py files in this directory
```

### Find patterns
```
> Find all function definitions in Python files
```

### Analyze code
```
> What's the most commonly used module in this project?
```

### Parallel analysis
```
> Analyze this project by counting files, finding TODOs, listing dependencies, and calculating lines of code — do all in parallel
```

## Slash Commands in REPL

```
/help       Show available commands
/tools      List available tools
/model      Show current model
/history    Show conversation
/clear      Clear conversation
/exit       Exit
```

## Troubleshooting

### "API key not found"
Make sure `.env` file exists with `MOONSHOT_API_KEY` or `ANTHROPIC_API_KEY`

### "Tool not found"
Use `--tools all` to get all tools (default)

### "Timeout"
Bash commands default to 30s timeout, max 120s. Use:
```bash
kimi-code run "long command" --max-turns 1
```

## Next Steps

1. **Read** [README.md](README.md) for full documentation
2. **Explore** the demo code in `demos/parallel_agents.py`
3. **Build** custom tools by extending `BaseTool`
4. **Integrate** into your workflow

## Examples

### Speed up analysis with parallelism

Instead of:
```bash
find . -name '*.py' | wc -l        # 10 seconds
find . -name '*.py' | xargs wc -l  # 10 seconds
cat requirements.txt                # 2 seconds
grep -r TODO .                      # 10 seconds
# Total: ~32 seconds
```

Use:
```bash
kimi-code run "Count files, count lines, list deps, find TODOs in parallel"
# Total: ~10 seconds (all parallel!)
```

### Analyze multiple modules independently

```
kimi-code run "In parallel: analyze module A, analyze module B, test module C"
```

All three happen simultaneously.

## Get Help

```bash
kimi-code --help
kimi-code run --help
kimi-code demo --help
```

---

**Ready to code?** Start with `kimi-code` and explore!
