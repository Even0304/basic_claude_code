"""Cost tracking for LLM API usage."""

from dataclasses import dataclass, field
from typing import Optional

from kimi_code.models import Usage


@dataclass
class PricingInfo:
    """Pricing information for a model.

    Prices are in USD per 1M tokens.
    """

    model: str
    input_price: float  # USD per 1M input tokens
    output_price: float  # USD per 1M output tokens
    cache_read_price: Optional[float] = None  # USD per 1M cache read tokens (optional)
    cache_write_price: Optional[float] = None  # USD per 1M cache write tokens (optional)


# Pricing data (as of 2024-2025)
PRICING_DATABASE = {
    # Anthropic Claude models
    "claude-opus-4-6": PricingInfo(
        "claude-opus-4-6",
        input_price=15.0,
        output_price=75.0,
        cache_read_price=1.5,  # 90% discount
        cache_write_price=18.75,  # 25% premium
    ),
    "claude-sonnet-4-6": PricingInfo(
        "claude-sonnet-4-6",
        input_price=3.0,
        output_price=15.0,
        cache_read_price=0.3,  # 90% discount
        cache_write_price=7.5,  # 50% premium
    ),
    "claude-haiku-4-5": PricingInfo(
        "claude-haiku-4-5-20251001",
        input_price=0.8,
        output_price=4.0,
        cache_read_price=0.08,  # 90% discount
        cache_write_price=1.0,  # 25% premium
    ),

    # OpenAI GPT-4 models
    "gpt-4o": PricingInfo(
        "gpt-4o",
        input_price=5.0,
        output_price=15.0,
    ),
    "gpt-4o-mini": PricingInfo(
        "gpt-4o-mini",
        input_price=0.15,
        output_price=0.6,
    ),
    "gpt-4-turbo": PricingInfo(
        "gpt-4-turbo",
        input_price=10.0,
        output_price=30.0,
    ),

    # Moonshot Kimi models (via OpenAI-compatible endpoint)
    "moonshot-v1-8k": PricingInfo(
        "moonshot-v1-8k",
        input_price=2.0,  # Estimate based on public pricing
        output_price=6.0,
    ),
    "moonshot-v1-32k": PricingInfo(
        "moonshot-v1-32k",
        input_price=3.0,  # Estimate
        output_price=9.0,
    ),
    "moonshot-v1-128k": PricingInfo(
        "moonshot-v1-128k",
        input_price=5.0,  # Estimate
        output_price=15.0,
    ),
    "moonshotai/kimi-k2.5": PricingInfo(
        "moonshotai/kimi-k2.5",
        input_price=0.0,  # Assumption: free tier or test
        output_price=0.0,
    ),
}


@dataclass
class CostSummary:
    """Summary of costs for a conversation."""

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cache_read_tokens: int = 0
    total_cache_write_tokens: int = 0
    total_input_cost: float = 0.0
    total_output_cost: float = 0.0
    total_cache_read_cost: float = 0.0
    total_cache_write_cost: float = 0.0

    @property
    def total_tokens(self) -> int:
        return (
            self.total_input_tokens
            + self.total_output_tokens
            + self.total_cache_read_tokens
            + self.total_cache_write_tokens
        )

    @property
    def total_cost(self) -> float:
        return (
            self.total_input_cost
            + self.total_output_cost
            + self.total_cache_read_cost
            + self.total_cache_write_cost
        )

    def format_cost(self, cost: float) -> str:
        """Format cost as a readable string.

        Args:
            cost: Cost in USD

        Returns:
            Formatted cost string
        """
        if cost < 0.00001:
            return "~$0.00"
        elif cost < 0.001:
            return f"${cost*1000:.3f}m"  # millidollars
        else:
            return f"${cost:.4f}"

    def __str__(self) -> str:
        """Return a formatted summary string."""
        return (
            f"Tokens: {self.total_tokens:,} "
            f"(input: {self.total_input_tokens:,}, "
            f"output: {self.total_output_tokens:,}, "
            f"cache_read: {self.total_cache_read_tokens:,}, "
            f"cache_write: {self.total_cache_write_tokens:,}) | "
            f"Cost: {self.format_cost(self.total_cost)}"
        )


class CostTracker:
    """Tracks costs for API calls."""

    def __init__(self, model: str) -> None:
        """Initialize cost tracker for a specific model.

        Args:
            model: The model name (e.g., 'claude-opus-4-6', 'gpt-4o')
        """
        self.model = model
        self.pricing = self._get_pricing(model)
        self.summary = CostSummary()

    def add_usage(self, usage: Usage) -> None:
        """Add usage statistics from an API call.

        Args:
            usage: Usage object with token counts
        """
        self.summary.total_input_tokens += usage.input_tokens
        self.summary.total_output_tokens += usage.output_tokens
        self.summary.total_cache_read_tokens += usage.cache_read_tokens
        self.summary.total_cache_write_tokens += usage.cache_write_tokens

        # Calculate costs
        if self.pricing:
            self.summary.total_input_cost += (
                usage.input_tokens / 1_000_000 * self.pricing.input_price
            )
            self.summary.total_output_cost += (
                usage.output_tokens / 1_000_000 * self.pricing.output_price
            )

            if self.pricing.cache_read_price:
                self.summary.total_cache_read_cost += (
                    usage.cache_read_tokens / 1_000_000 * self.pricing.cache_read_price
                )

            if self.pricing.cache_write_price:
                self.summary.total_cache_write_cost += (
                    usage.cache_write_tokens / 1_000_000 * self.pricing.cache_write_price
                )

    def get_summary(self) -> CostSummary:
        """Get the current cost summary.

        Returns:
            CostSummary object
        """
        return self.summary

    def reset(self) -> None:
        """Reset the cost summary."""
        self.summary = CostSummary()

    def _get_pricing(self, model: str) -> Optional[PricingInfo]:
        """Get pricing info for a model.

        Args:
            model: Model name

        Returns:
            PricingInfo if found, None otherwise
        """
        # Try exact match first
        if model in PRICING_DATABASE:
            return PRICING_DATABASE[model]

        # Try prefix match (e.g., "claude-opus" matches "claude-opus-4-6")
        for key, pricing in PRICING_DATABASE.items():
            if key.startswith(model) or model.startswith(key):
                return pricing

        # Model not found
        return None
