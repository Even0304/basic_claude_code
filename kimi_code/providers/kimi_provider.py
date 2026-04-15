"""Kimi/Moonshot AI provider using OpenAI-compatible API."""

import json
from typing import Any

from openai import AsyncOpenAI

from kimi_code.models import LLMResponse, Message, ToolCall, Usage
from kimi_code.tools.base import BaseTool


class KimiProvider:
    """LLM provider for Kimi (Moonshot AI) via OpenAI-compatible API."""

    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize KimiProvider.

        Args:
            api_key: Moonshot API key
            base_url: Moonshot API base URL (https://api.moonshot.cn/v1)
            model: Model name (e.g., kimi-k2.5z)
        """
        self.model = model
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def _tools_to_openai(self, tools: list[BaseTool]) -> list[dict[str, Any]]:
        """Convert tools to OpenAI function-calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in tools
        ]

    def _messages_to_openai(self, messages: list[Message]) -> list[dict[str, Any]]:
        """Convert Message objects to OpenAI message format."""
        result = []
        for msg in messages:
            if msg.role == "assistant":
                content = msg.content if isinstance(msg.content, str) else ""
                tool_calls = None
                if msg.tool_calls:
                    tool_calls = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments),
                            },
                        }
                        for tc in msg.tool_calls
                    ]
                result.append(
                    {"role": "assistant", "content": content, "tool_calls": tool_calls}
                )
            elif msg.role == "user":
                # Tool results come as separate "tool" messages
                if msg.tool_results:
                    for tr in msg.tool_results:
                        result.append(
                            {
                                "role": "tool",
                                "tool_call_id": tr.tool_call_id,
                                "content": tr.content,
                            }
                        )
                else:
                    content = msg.content if isinstance(msg.content, str) else ""
                    if content:
                        result.append({"role": "user", "content": content})
            else:  # system
                result.append({"role": "system", "content": msg.content})
        return result

    def _parse_response(self, response: Any) -> LLMResponse:
        """Parse OpenAI response into LLMResponse."""
        choice = response.choices[0]
        msg = choice.message

        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {"raw_arguments": tc.function.arguments}
                tool_calls.append(
                    ToolCall(id=tc.id, name=tc.function.name, arguments=args)
                )

        usage = Usage(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
        )

        stop_reason = "tool_use" if tool_calls else "end_turn"

        return LLMResponse(
            text=msg.content or "",
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            usage=usage,
        )

    async def chat(
        self,
        messages: list[Message],
        tools: list[BaseTool] | None = None,
        system: str | None = None,
        max_tokens: int = 8192,
    ) -> LLMResponse:
        """Send a chat request to Kimi."""
        oai_messages = []

        # Add system message if provided
        if system:
            oai_messages.append({"role": "system", "content": system})

        # Convert Message objects to OpenAI format
        oai_messages.extend(self._messages_to_openai(messages))

        # Prepare request kwargs
        kwargs = {
            "model": self.model,
            "messages": oai_messages,
            "max_tokens": max_tokens,
        }

        # Add tools if provided
        if tools:
            kwargs["tools"] = self._tools_to_openai(tools)
            kwargs["tool_choice"] = "auto"

        # Make API call
        response = await self._client.chat.completions.create(**kwargs)

        return self._parse_response(response)

    async def stream(
        self,
        messages: list[Message],
        tools: list[BaseTool] | None = None,
        system: str | None = None,
        max_tokens: int = 8192,
    ):
        """Stream a chat response from Kimi (not yet fully implemented)."""
        # Streaming support would be added here
        raise NotImplementedError("Streaming is not yet implemented for KimiProvider")
