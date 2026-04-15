"""Configuration and settings management."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Settings:
    """Global settings for the agent system."""

    # Provider selection
    provider: str = field(default_factory=lambda: os.getenv("PROVIDER", "kimi"))

    # OpenAI-compatible API (for Kimi, Claude, or any compatible service)
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_base_url: str = field(
        default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.moonshot.cn/v1")
    )
    llm_model: str = field(
        default_factory=lambda: os.getenv("LLM_MODEL", "moonshot-v1-8k")
    )

    # Legacy Moonshot-specific (deprecated, use openai_* above)
    moonshot_api_key: str = field(
        default_factory=lambda: os.getenv("MOONSHOT_API_KEY", "")
    )
    moonshot_base_url: str = "https://api.moonshot.cn/v1"
    kimi_model: str = field(
        default_factory=lambda: os.getenv("KIMI_MODEL", "moonshot-v1-8k")
    )

    # Anthropic
    anthropic_api_key: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "")
    )
    claude_model: str = field(
        default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-opus-4-6")
    )

    # Agent configuration
    max_turns: int = 50
    max_tokens: int = 16384
    temperature: float = 0.0
    stream: bool = False

    # UI
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    show_token_usage: bool = False
    working_dir: Path = field(default_factory=Path.cwd)

    def validate(self) -> None:
        """Validate settings and raise if critical values are missing."""
        if self.provider == "kimi":
            # Accept either new OPENAI_API_KEY or legacy MOONSHOT_API_KEY
            if not self.openai_api_key and not self.moonshot_api_key:
                raise ValueError(
                    "OPENAI_API_KEY or MOONSHOT_API_KEY environment variable is required for Kimi provider"
                )
        if self.provider == "claude" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required for Claude provider"
            )


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def set_settings(settings: Settings) -> None:
    """Set the global settings instance."""
    global _settings
    _settings = settings
