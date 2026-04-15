# Architecture — kimi-code

## Overview

kimi-code is a Python implementation of Claude Code with a focus on **parallel multi-agent execution** via asyncio. The system is designed to:

1. Support multiple LLM providers (Kimi k2.5z, Claude)
2. Enable parallel task execution through sub-agents
3. Maintain clean separation of concerns
4. Provide an interactive REPL and CLI interface

## Core Design Principles

### 1. **Provider Abstraction**
- Providers implement a common protocol (`LLMProvider`)
- Both Kimi and Claude use the same internal `Message` format
- Providers handle translation to/from their native APIs

### 2. **Tool Composition**
- All tools inherit from `BaseTool`
- Tool definitions are provider-agnostic (JSON Schema)
- Providers translate schemas to their format at request time

### 3. **Parallel-First Architecture**
- All tool calls within a single LLM turn run in parallel
- The `task` tool enables explicit sub-agent spawning
- Nested parallelism with depth control prevents infinite recursion

### 4. **Dependency Injection**
- TaskTool receives its `agent_factory` at runtime
- Breaks circular imports between Agent and TaskTool
- Allows agents to create sub-agents with proper context

## Component Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLI / REPL                       │
│          (kimi_code.cli, kimi_code.ui.repl)         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                 Agent Core Loop                     │
│            (kimi_code.agent.Agent)                  │
│  • Manages conversation history (messages)          │
│  • Executes tools in parallel (asyncio.gather)      │
│  • Loops until no more tool calls                   │
└──────────────┬──────────────────────────────────────┘
               │
       ┌───────┴──────────┬──────────────────┐
       │                  │                  │
┌──────▼──────┐  ┌────────▼────────┐  ┌─────▼──────┐
│  Providers  │  │      Tools      │  │   Models   │
│             │  │                 │  │            │
│ • Kimi      │  │ • bash          │  │ • Message  │
│ • Claude    │  │ • read/write    │  │ • ToolCall │
│ • (custom)  │  │ • edit          │  │ • Usage    │
│             │  │ • glob/grep     │  │ • Responses│
│ Translate   │  │ • task (agents) │  │ (Canonical │
│ messages &  │  │                 │  │ format)    │
│ tool schemas│  │ BaseTool ABC    │  │            │
└─────────────┘  └─────────────────┘  └────────────┘
```

## Parallel Multi-Agent Execution

### How It Works

When a user asks for multiple independent tasks:

```
"Count files, lines, deps, and TODOs — do in parallel"
```

**Flow:**
1. Agent calls LLM with user input
2. LLM recognizes independent tasks → returns tool_call to `task` tool
3. Agent executes tool_call to TaskTool
4. TaskTool creates 4 sub-agents with fresh context
5. All 4 sub-agents run simultaneously via `asyncio.gather()`
6. Results aggregated and returned
7. Parent agent synthesizes response

### Asyncio Structure

```python
# In Agent._loop()
await asyncio.gather(
    *[self._execute_tool(tc) for tc in response.tool_calls]
)

# In TaskTool.execute()
await asyncio.gather(
    *[self._run_single_task(spec, i) for i, spec in enumerate(tasks)]
)
```

Two levels of parallelism:
- **Level 1**: Multiple tools in one LLM response run in parallel
- **Level 2**: Multiple sub-agents run in parallel (via task tool)

### Sub-Agent Context Isolation

Each sub-agent:
- Gets its own `_messages` list (fresh conversation)
- Shares the provider instance (async clients are thread-safe)
- Inherits parent's tools (configurable per-agent)
- Can themselves spawn sub-agents (up to depth 3)

```python
# Parent agent message history
[user: "query", assistant: "Using task tool", user: results]

# Sub-agent A message history (isolated)
[user: "task 1 description", assistant: "response A"]

# Sub-agent B message history (isolated)
[user: "task 2 description", assistant: "response B"]
```

## Provider Integration

### Message Flow

Internal format (provider-agnostic):
```python
Message(
    role="assistant",
    content="some text",
    tool_calls=[
        ToolCall(id="call_1", name="bash", arguments={"command": "ls"})
    ]
)
```

### Kimi Provider (OpenAI-Compatible)
```python
# Translation: Message → OpenAI format
{
    "role": "assistant",
    "content": "some text",
    "tool_calls": [{
        "id": "call_1",
        "type": "function",
        "function": {
            "name": "bash",
            "arguments": '{"command": "ls"}'  # JSON string!
        }
    }]
}
```

### Claude Provider (Anthropic)
```python
# Translation: Message → Anthropic format
{
    "role": "assistant",
    "content": [
        {"type": "text", "text": "some text"},
        {
            "type": "tool_use",
            "id": "call_1",
            "name": "bash",
            "input": {"command": "ls"}  # Direct dict
        }
    ]
}
```

### Tool Schema Translation

Internal schema (provider-agnostic JSON Schema):
```python
tool.input_schema = {
    "type": "object",
    "properties": {
        "command": {"type": "string"}
    },
    "required": ["command"]
}
```

**Kimi** converts to OpenAI format:
```python
{
    "type": "function",
    "function": {
        "name": "bash",
        "description": "...",
        "parameters": {...}  # Same JSON Schema
    }
}
```

**Claude** converts to Anthropic format:
```python
{
    "name": "bash",
    "description": "...",
    "input_schema": {...}  # Same JSON Schema, diff key
}
```

## Tool Execution

### Async Execution

All tools are async:
```python
class BashTool(BaseTool):
    async def execute(self, command: str, timeout: int = 30) -> ToolResult:
        proc = await asyncio.create_subprocess_shell(...)
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return ToolResult(content=output, is_error=failed)
```

### Error Handling

Tools return `ToolResult` with:
- `content`: Output (success or error message)
- `is_error`: Boolean flag

Errors are gracefully returned, not raised.

### Output Truncation

Large outputs are truncated to prevent context overflow:
- Bash: 50KB max
- Grep: 50KB max
- Combined output is capped

## Configuration System

### Settings Dataclass
```python
@dataclass
class Settings:
    provider: str = "kimi"
    kimi_model: str = "moonshot-v1-8k"
    moonshot_api_key: str = ""  # From env
    claude_model: str = "claude-opus-4-6"
    anthropic_api_key: str = ""  # From env
    # ...
```

### Validation
```python
settings.validate()  # Raises if required keys missing
```

### Environment Loading
```python
from dotenv import load_dotenv
load_dotenv()  # Reads .env file

# Settings automatically pulls from os.environ
```

## CLI Architecture

### Typer-Based CLI
```
kimi-code [OPTIONS] COMMAND [ARGS]

Global options:
  --provider      (kimi|claude)
  --model         (override default)
  --system        (custom prompt)
  --tools         (all|minimal|none)
  --debug

Commands:
  (default REPL)  Interactive mode
  run             Single prompt execution
  demo            Run demonstrations
```

### Command Structure
```python
@app.callback(invoke_without_command=True)  # Default: REPL
def main(...): ...

@app.command()
def run(...): ...                            # Non-interactive

@app.command()
def demo(...): ...                           # Run demos
```

## Testing Strategy

### Unit Tests (Future)
- Individual tools (bash, read, write, etc.)
- Provider message translation
- Config validation
- Tool schema validation

### Integration Tests (Future)
- Full agent loop with mock provider
- Parallel execution correctness
- Message history management
- Error handling and recovery

### Demo/Smoke Tests (Current)
- `test_smoke.py`: Basic structure and tools
- `test_parallel_structure.py`: Parallel agent wiring
- `demos/parallel_agents.py`: Full end-to-end with real provider

## Extensibility

### Adding a New Tool

1. Create `kimi_code/tools/mytool.py`:
```python
class MyTool(BaseTool):
    name = "mytool"
    description = "..."
    input_schema = {"type": "object", "properties": {...}}
    
    async def execute(self, **kwargs) -> ToolResult:
        ...
```

2. Register in `kimi_code/tools/__init__.py`:
```python
def get_default_tools():
    return [..., MyTool()]
```

3. Available to all agents immediately.

### Adding a New Provider

1. Create `kimi_code/providers/newprovider.py`
2. Implement `chat()` and `stream()` methods
3. Handle message translation (to/from internal format)
4. Handle tool schema translation
5. Register in `kimi_code/providers/__init__.py`

### Custom System Prompts

```bash
kimi-code --system "You are a Python expert"
```

Or programmatically:
```python
agent = Agent(..., system="Your prompt")
```

## Performance Considerations

### Parallelism Benefits
- 4 tasks in parallel: 4x speedup (max)
- Real speedup depends on I/O vs CPU
- Network requests: excellent parallelism
- CPU-bound tasks: no speedup

### Memory Usage
- Each sub-agent has separate message history
- Provider connection is shared
- Token usage grows with parallel tasks

### Depth Limits
- Max depth: 3 (configurable)
- Prevents infinite recursion
- Discourages impractical nesting

## Future Improvements

### Streaming Responses
- Currently all responses are non-streaming
- Could implement streaming for live feedback

### Prompt Caching
- Claude: Use prompt caching for repeated contexts
- Kimi: Use if similar feature available

### Better Error Recovery
- Retry failed tasks
- Graceful degradation
- Comprehensive error reporting

### Advanced Orchestration
- Task priorities/ordering
- Conditional branching
- Loop constructs
- State management between tasks

## References

- [Claude API Docs](https://docs.anthropic.com)
- [Moonshot AI Docs](https://platform.moonshot.cn)
- [Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Rich Documentation](https://rich.readthedocs.io)
