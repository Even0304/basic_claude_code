"""LLM provider implementations."""

from kimi_code.config import Settings
from kimi_code.providers.base import LLMProvider


def get_provider(settings: Settings | None = None) -> LLMProvider:
    """Get an LLM provider based on settings.

    Args:
        settings: Settings instance (uses global settings if None)

    Returns:
        An LLMProvider instance
    """
    if settings is None:
        from kimi_code.config import get_settings

        settings = get_settings()

    settings.validate()

    if settings.provider == "kimi":
        from kimi_code.providers.kimi_provider import KimiProvider

        # Use new OpenAI-compatible API settings, with fallback to old Moonshot settings
        api_key = settings.openai_api_key or settings.moonshot_api_key
        base_url = settings.openai_base_url or settings.moonshot_base_url
        model = settings.llm_model or settings.kimi_model

        return KimiProvider(
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
    elif settings.provider == "claude":
        from kimi_code.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.claude_model,
        )
    else:
        raise ValueError(f"Unknown provider: {settings.provider}")


__all__ = ["LLMProvider", "get_provider"]
