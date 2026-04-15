"""Streaming agent with real-time visualization."""

import asyncio
import time
import uuid
from typing import Any, Callable, Optional

from kimi_code.cost_tracker import CostTracker, CostSummary
from kimi_code.models import LLMResponse, Message, ToolCall, ToolResult as ModelToolResult
from kimi_code.providers.base import LLMProvider
from kimi_code.tools.base import BaseTool, ToolResult as ToolResultBase
from kimi_code.ui.stream_display import StreamingDisplay


class StreamingAgent:
    """AI agent with streaming visualization support."""

    def __init__(
        self,
        provider: LLMProvider,
        tools: list[BaseTool] | None = None,
        system: str | None = None,
        max_turns: int = 50,
        name: str = "agent",
        display: Optional[StreamingDisplay] = None,
        show_thinking: bool = True,
    ):
        """Initialize streaming agent.

        Args:
            provider: LLM provider instance
            tools: List of tools available to the agent
            system: System prompt
            max_turns: Maximum conversation turns
            name: Agent name
            display: StreamingDisplay instance (creates default if None)
            show_thinking: Whether to show thinking/intermediate steps
        """
        self.provider = provider
        self.tools = tools or []
        self.system = system
        self.max_turns = max_turns
        self.name = name
        self.show_thinking = show_thinking

        self.display = display or StreamingDisplay()

        self._messages: list[Message] = []
        self._tool_map: dict[str, BaseTool] = {t.name: t for t in self.tools}
        self._cost_tracker = CostTracker(provider.model)

        # Wire up TaskTool
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
    ) -> "StreamingAgent":
        """Create a fresh sub-agent.

        Args:
            tools: Tools for the sub-agent
            system: System prompt

        Returns:
            New StreamingAgent instance
        """
        return StreamingAgent(
            provider=self.provider,
            tools=tools if tools is not None else list(self.tools),
            system=system or self.system,
            max_turns=self.max_turns,
            name=f"{self.name}/sub-{uuid.uuid4().hex[:6]}",
            display=self.display,
            show_thinking=self.show_thinking,
        )

    @property
    def messages(self) -> list[Message]:
        """Get conversation history."""
        return list(self._messages)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._messages.clear()

    def get_cost_summary(self) -> CostSummary:
        """Get cost summary."""
        return self._cost_tracker.get_summary()

    async def _execute_tool(self, tool_call: ToolCall) -> ModelToolResult:
        """Execute a single tool call with timing.

        Args:
            tool_call: The tool call to execute

        Returns:
            ToolResult with output or error
        """
        tool = self._tool_map.get(tool_call.name)
        if tool is None:
            return ModelToolResult(
                tool_call_id=tool_call.id,
                content=f"Unknown tool: {tool_call.name}",
                is_error=True,
            )

        # Show tool call
        self.display.show_tool_call(tool_call.name, tool_call.arguments)

        start = time.time()
        try:
            result = await tool.execute(**tool_call.arguments)
            elapsed = time.time() - start

            # Show result
            self.display.show_tool_result(
                tool_call.name,
                result.content,
                elapsed,
                result.is_error,
            )

            return ModelToolResult(
                tool_call_id=tool_call.id,
                content=result.content,
                is_error=result.is_error,
            )
        except Exception as e:
            elapsed = time.time() - start
            error_msg = f"Error: {type(e).__name__}: {e}"
            self.display.show_tool_result(
                tool_call.name,
                error_msg,
                elapsed,
                is_error=True,
            )
            return ModelToolResult(
                tool_call_id=tool_call.id,
                content=error_msg,
                is_error=True,
            )

    async def run(self, user_input: str) -> str:
        """Process user input with streaming display.

        Args:
            user_input: The user's input

        Returns:
            The final response text
        """
        # Display execution start
        self.display.start_execution(user_input, self.name)

        self._messages.append(Message(role="user", content=user_input))
        result = await self._loop()

        # Display summary
        elapsed = time.time() - self.display.start_time
        cost = self.get_cost_summary()
        self.display.show_summary(
            elapsed,
            tokens=cost.total_tokens,
            cost=cost.format_cost(cost.total_cost) if cost.total_cost > 0 else None,
        )

        return result

    async def _loop(self) -> str:
        """Main agentic loop with streaming visualization.

        Returns:
            Final response text
        """
        for turn in range(self.max_turns):
            # Show status
            self.display.update_status(f"Turn {turn + 1}/{self.max_turns}: Calling LLM")

            start = time.time()
            # Call the LLM
            response: LLMResponse = await self.provider.chat(
                messages=self._messages,
                tools=self.tools if self.tools else None,
                system=self.system,
            )
            elapsed = time.time() - start

            # Track costs
            self._cost_tracker.add_usage(response.usage)

            # Show thinking (if enabled)
            if self.show_thinking and elapsed > 0.5:
                self.display.show_thinking(
                    f"Processing with {response.usage.total_tokens} tokens",
                    elapsed,
                )

            # Append assistant response
            assistant_msg = Message(
                role="assistant",
                content=response.text,
                tool_calls=response.tool_calls,
            )
            self._messages.append(assistant_msg)

            # If no tool calls, we're done
            if not response.tool_calls or response.stop_reason == "end_turn":
                elapsed_total = time.time() - self.display.start_time
                self.display.show_response(response.text, elapsed_total)
                return response.text

            # Show parallel execution
            if len(response.tool_calls) > 1:
                self.display.show_parallel_execution(len(response.tool_calls))

            # Execute all tools in parallel
            tool_results: list[ModelToolResult] = await asyncio.gather(
                *[self._execute_tool(tc) for tc in response.tool_calls]
            )

            # Add results to history
            user_msg = Message(
                role="user",
                content="",
                tool_results=tool_results,
            )
            self._messages.append(user_msg)

        return f"[Agent {self.name}: max turns reached]"
