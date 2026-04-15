"""Anthropic provider for Claude models."""

import anthropic

from kimi_code.models import LLMResponse, Message, ToolCall, Usage
from kimi_code.tools.base import BaseTool


class AnthropicProvider:
    """LLM provider for Claude models via Anthropic API."""

    def __init__(self, api_key: str, model: str):
        """Initialize AnthropicProvider.

        Args:
            api_key: Anthropic API key
            model: Model name (e.g., claude-opus-4-6)
        """
        self.model = model
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    def _tools_to_anthropic(self, tools: list[BaseTool]) -> list[dict]:
        """Convert tools to Anthropic format."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in tools
        ]

    def _messages_to_anthropic(self, messages: list[Message]) -> list[dict]:
        """Convert Message objects to Anthropic format."""
        result = []
        for msg in messages:
            if msg.role == "assistant":
                content = []
                if msg.content and isinstance(msg.content, str) and msg.content.strip():
                    content.append({"type": "text", "text": msg.content})
                for tc in msg.tool_calls:
                    content.append(
                        {
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.name,
                            "input": tc.arguments,
                        }
                    )
                result.append({"role": "assistant", "content": content})

            elif msg.role == "user":
                # Tool results as separate user message
                if msg.tool_results:
                    content = []
                    for tr in msg.tool_results:
                        content.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tr.tool_call_id,
                                "content": tr.content,
                                "is_error": tr.is_error,
                            }
                        )
                    result.append({"role": "user", "content": content})
                else:
                    content = msg.content if isinstance(msg.content, str) else ""
                    if content.strip():
                        result.append({"role": "user", "content": content})

            else:  # system
                # Anthropic system messages are handled separately in the API call
                pass

        return result

    def _parse_response(self, response) -> LLMResponse:
        """Parse Anthropic response into LLMResponse."""
        tool_calls = []
        text_parts = []

        for block in response.content:
            if block.type == "tool_use":
                tool_calls.append(
                    ToolCall(id=block.id, name=block.name, arguments=block.input)
                )
            elif block.type == "text":
                text_parts.append(block.text)

        usage = Usage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cache_read_tokens=getattr(response.usage, "cache_read_input_tokens", 0),
            cache_write_tokens=getattr(response.usage, "cache_creation_input_tokens", 0),
        )

        stop_reason = "tool_use" if tool_calls else "end_turn"

        return LLMResponse(
            text=" ".join(text_parts),
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
        """Send a chat request to Claude."""
        anthropic_messages = self._messages_to_anthropic(messages)

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": anthropic_messages,
        }

        if system:
            kwargs["system"] = system

        if tools:
            kwargs["tools"] = self._tools_to_anthropic(tools)

        response = await self._client.messages.create(**kwargs)
        return self._parse_response(response)

    async def stream(
        self,
        messages: list[Message],
        tools: list[BaseTool] | None = None,
        system: str | None = None,
        max_tokens: int = 8192,
    ):
        """Stream a chat response from Claude (not yet fully implemented)."""
        raise NotImplementedError("Streaming is not yet implemented for AnthropicProvider")
