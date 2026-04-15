"""kimi-code: AI-powered coding assistant (Claude Code in Python)."""

__version__ = "0.1.0"

from kimi_code.agent import Agent
from kimi_code.config import Settings, get_settings
from kimi_code.providers import get_provider

__all__ = [
    "Agent",
    "Settings",
    "get_settings",
    "get_provider",
]
