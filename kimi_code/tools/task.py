"""Task tool for spawning parallel sub-agents."""

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from kimi_code.tools.base import BaseTool, ToolResult

if TYPE_CHECKING:
    from kimi_code.agent import Agent


@dataclass
class TaskSpec:
    """Specification for a single task."""

    description: str
    context: str | None = None
    tools: list[str] | None = None


class TaskTool(BaseTool):
    """Spawn one or more sub-agents to execute tasks in parallel."""

    name = "task"
    description = (
        "Spawn one or more sub-agents to execute tasks IN PARALLEL. "
        "Each sub-agent runs independently with its own conversation context. "
        "Use this for parallelizable work: searching multiple files, running multiple analyses, etc. "
        "All tasks run simultaneously and their results are returned together."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "What this sub-agent should do",
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context or data to pass to this sub-agent",
                        },
                        "tools": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tool names the sub-agent can use. Omit to inherit all tools.",
                        },
                    },
                    "required": ["description"],
                },
                "description": "List of tasks to execute in parallel",
                "minItems": 1,
            }
        },
        "required": ["tasks"],
    }

    def __init__(
        self,
        agent_factory: Callable[..., "Agent"] | None = None,
        available_tools: list[BaseTool] | None = None,
        max_depth: int = 3,
        current_depth: int = 0,
    ):
        """Initialize TaskTool.

        Args:
            agent_factory: Callable to create sub-agents (injected by Agent)
            available_tools: Available tools (injected by Agent)
            max_depth: Maximum nesting depth for TaskTools
            current_depth: Current nesting depth
        """
        self._agent_factory = agent_factory
        self._available_tools = available_tools or []
        self._max_depth = max_depth
        self._current_depth = current_depth

    def _get_tools_for_subagent(self, tool_names: list[str] | None) -> list[BaseTool]:
        """Get tools for a sub-agent, respecting depth limits.

        Args:
            tool_names: Specific tool names to use, or None for all

        Returns:
            List of BaseTool instances
        """
        # Exclude TaskTool (to avoid infinite nesting at max depth)
        non_recursive_tools = [t for t in self._available_tools if t.name != "task"]

        if tool_names is None:
            tools = non_recursive_tools
        else:
            name_set = set(tool_names)
            tools = [t for t in non_recursive_tools if t.name in name_set]

        # Add TaskTool back if depth allows
        if self._current_depth < self._max_depth - 1:
            sub_task_tool = TaskTool(
                agent_factory=self._agent_factory,
                available_tools=self._available_tools,
                max_depth=self._max_depth,
                current_depth=self._current_depth + 1,
            )
            tools.append(sub_task_tool)

        return tools

    async def _run_single_task(self, spec: TaskSpec, index: int) -> tuple[int, str]:
        """Run a single task in a sub-agent.

        Args:
            spec: Task specification
            index: Task index (for ordering results)

        Returns:
            Tuple of (index, result_text)
        """
        if self._agent_factory is None:
            return index, "ERROR: Agent factory not initialized"

        tools = self._get_tools_for_subagent(spec.tools)

        # Build the prompt from description and optional context
        prompt = spec.description
        if spec.context:
            prompt = f"Context:\n{spec.context}\n\nTask:\n{spec.description}"

        # Create sub-agent with fresh history
        agent = self._agent_factory(tools, None)

        try:
            result = await agent.run(prompt)
            return index, result
        except Exception as e:
            return index, f"ERROR: {type(e).__name__}: {e}"

    async def execute(self, tasks: list[dict[str, Any]]) -> ToolResult:
        """Execute multiple tasks in parallel.

        Args:
            tasks: List of task dictionaries

        Returns:
            ToolResult with aggregated results
        """
        # Parse task specs
        task_specs = [
            TaskSpec(
                description=t["description"],
                context=t.get("context"),
                tools=t.get("tools"),
            )
            for t in tasks
        ]

        # Run all tasks in parallel
        coroutines = [
            self._run_single_task(spec, i) for i, spec in enumerate(task_specs)
        ]
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Aggregate results
        output_parts = []
        has_error = False

        for i, result in enumerate(results):
            task_desc = task_specs[i].description[:80]
            if isinstance(result, Exception):
                output_parts.append(f"Task {i + 1} ({task_desc}):\n[ERROR] {result}")
                has_error = True
            else:
                idx, text = result
                output_parts.append(f"Task {i + 1} ({task_desc}):\n{text}")

        combined = "\n\n---\n\n".join(output_parts)
        return ToolResult(content=combined, is_error=has_error)
