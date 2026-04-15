"""Base LLM provider protocol."""

from typing import AsyncIterator, Protocol, runtime_checkable

from kimi_code.models import LLMResponse
from kimi_code.tools.base import BaseTool


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers (Kimi, Claude, etc)."""

    model: str

    async def chat(
        self,
        messages: list,
        tools: list[BaseTool] | None = None,
        system: str | None = None,
        max_tokens: int = 8192,
    ) -> LLMResponse:
        """Send a chat request to the LLM.

        Args:
            messages: List of Message objects
            tools: Optional list of tools the LLM can call
            system: Optional system prompt
            max_tokens: Maximum tokens in response

        Returns:
            LLMResponse with text, tool_calls, stop_reason, and usage
        """
        ...

    async def stream(
        self,
        messages: list,
        tools: list[BaseTool] | None = None,
        system: str | None = None,
        max_tokens: int = 8192,
    ) -> AsyncIterator[dict]:
        """Stream a chat response from the LLM.

        Args:
            messages: List of Message objects
            tools: Optional list of tools the LLM can call
            system: Optional system prompt
            max_tokens: Maximum tokens in response

        Yields:
            Chunks of the response (text, tool_calls, etc)
        """
        ...
