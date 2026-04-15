"""Core Agent class with agentic loop."""

import asyncio
import uuid
from typing import Any, Callable

from kimi_code.cost_tracker import CostTracker, CostSummary
from kimi_code.models import LLMResponse, Message, ToolCall, ToolResult as ModelToolResult
from kimi_code.providers.base import LLMProvider
from kimi_code.tools.base import BaseTool, ToolResult as ToolResultBase


class Agent:
    """AI agent with tool use and agentic loop."""

    def __init__(
        self,
        provider: LLMProvider,
        tools: list[BaseTool] | None = None,
        system: str | None = None,
        max_turns: int = 50,
        name: str = "agent",
    ):
        """Initialize an Agent.

        Args:
            provider: LLM provider instance
            tools: List of tools available to the agent
            system: System prompt
            max_turns: Maximum conversation turns before stopping
            name: Agent name (for debugging)
        """
        self.provider = provider
        self.tools = tools or []
        self.system = system
        self.max_turns = max_turns
        self.name = name

        self._messages: list[Message] = []
        self._tool_map: dict[str, BaseTool] = {t.name: t for t in self.tools}
        self._cost_tracker = CostTracker(provider.model)

        # Wire up TaskTool if it exists (dependency injection)
        self._wire_task_tools()

    def _wire_task_tools(self) -> None:
        """Inject agent factory into TaskTool instances."""
        from kimi_code.tools.task import TaskTool

        for tool in self.tools:
            if isinstance(tool, TaskTool):
                tool._agent_factory = self.create_subagent
                tool._available_tools = [t for t in self.tools]

    def create_subagent(
        self,
        tools: list[BaseTool] | None = None,
        system: str | None = None,
    ) -> "Agent":
        """Create a fresh sub-agent with isolated message history.

        Args:
            tools: Tools for the sub-agent (or inherit parent's)
            system: System prompt (or inherit parent's)

        Returns:
            New Agent instance with isolated context
        """
        return Agent(
            provider=self.provider,
            tools=tools if tools is not None else list(self.tools),
            system=system or self.system,
            max_turns=self.max_turns,
            name=f"{self.name}/sub-{uuid.uuid4().hex[:6]}",
        )

    @property
    def messages(self) -> list[Message]:
        """Get conversation history."""
        return list(self._messages)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._messages.clear()

    def get_cost_summary(self) -> CostSummary:
        """Get the current cost summary.

        Returns:
            CostSummary with usage and cost information
        """
        return self._cost_tracker.get_summary()

    def reset_costs(self) -> None:
        """Reset the cost tracker."""
        self._cost_tracker.reset()

    async def _execute_tool(self, tool_call: ToolCall) -> ModelToolResult:
        """Execute a single tool call.

        Args:
            tool_call: The tool call to execute

        Returns:
            ToolResult with output or error
        """
        tool = self._tool_map.get(tool_call.name)
        if tool is None:
            return ModelToolResult(
                tool_call_id=tool_call.id,
                content=f"Unknown tool: {tool_call.name}. "
                f"Available: {list(self._tool_map.keys())}",
                is_error=True,
            )

        try:
            result = await tool.execute(**tool_call.arguments)
            return ModelToolResult(
                tool_call_id=tool_call.id,
                content=result.content,
                is_error=result.is_error,
            )
        except Exception as e:
            return ModelToolResult(
                tool_call_id=tool_call.id,
                content=f"Error executing tool {tool_call.name}: {type(e).__name__}: {e}",
                is_error=True,
            )

    async def run(self, user_input: str) -> str:
        """Process user input and run the agentic loop.

        Args:
            user_input: The user's input/prompt

        Returns:
            The final response text
        """
        self._messages.append(Message(role="user", content=user_input))
        return await self._loop()

    async def _loop(self) -> str:
        """Main agentic loop: call LLM, execute tools, repeat.

        Returns:
            Final response text when loop terminates
        """
        for turn in range(self.max_turns):
            # Call the LLM
            response: LLMResponse = await self.provider.chat(
                messages=self._messages,
                tools=self.tools if self.tools else None,
                system=self.system,
            )

            # Track costs
            self._cost_tracker.add_usage(response.usage)

            # Append assistant response to history
            assistant_msg = Message(
                role="assistant",
                content=response.text,
                tool_calls=response.tool_calls,
            )
            self._messages.append(assistant_msg)

            # If no tool calls or explicit end, we're done
            if not response.tool_calls or response.stop_reason == "end_turn":
                return response.text

            # Execute all tool calls in parallel
            tool_results: list[ModelToolResult] = await asyncio.gather(
                *[self._execute_tool(tc) for tc in response.tool_calls]
            )

            # Add tool results to history
            user_msg = Message(
                role="user",
                content="",
                tool_results=tool_results,
            )
            self._messages.append(user_msg)

        return f"[Agent {self.name}: max turns ({self.max_turns}) reached]"
