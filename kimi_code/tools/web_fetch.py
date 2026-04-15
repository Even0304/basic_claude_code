"""Web fetch tool - retrieve and clean HTML content from URLs."""

import asyncio
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from .base import BaseTool, ToolResult


class WebFetchTool(BaseTool):
    """Fetch and clean HTML content from URLs."""

    name = "web_fetch"
    description = "Fetch content from a URL and clean HTML to markdown-like text"
    input_schema = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch (must start with http:// or https://)",
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds",
                "default": 10,
            },
        },
        "required": ["url"],
    }

    async def execute(self, url: str, timeout: int = 10, **kwargs: Any) -> ToolResult:
        """Fetch and clean content from a URL.

        Args:
            url: The URL to fetch
            timeout: Request timeout in seconds (max 30)
            **kwargs: Additional arguments (ignored)

        Returns:
            ToolResult with cleaned content or error message
        """
        # Validate URL
        if not isinstance(url, str):
            return ToolResult(content="URL must be a string", is_error=True)

        if not (url.startswith("http://") or url.startswith("https://")):
            return ToolResult(
                content="URL must start with http:// or https://", is_error=True
            )

        # Clamp timeout
        timeout = max(1, min(timeout, 30))

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; kimi-code/1.0)"
                    },
                ) as resp:
                    if resp.status != 200:
                        return ToolResult(
                            content=f"HTTP {resp.status}: Failed to fetch {url}",
                            is_error=True,
                        )

                    html = await resp.text()
                    content = await asyncio.get_event_loop().run_in_executor(
                        None, self._clean_html, html
                    )

                    if not content.strip():
                        return ToolResult(
                            content="No readable content found on page",
                            is_error=True,
                        )

                    # Truncate if too long
                    max_chars = 50000
                    if len(content) > max_chars:
                        content = content[:max_chars] + f"\n\n[...truncated {len(content) - max_chars} chars]"

                    return ToolResult(content=content)

        except asyncio.TimeoutError:
            return ToolResult(
                content=f"Request timeout (>{timeout}s) for {url}",
                is_error=True,
            )
        except aiohttp.ClientError as e:
            return ToolResult(
                content=f"Network error: {str(e)}", is_error=True
            )
        except Exception as e:
            return ToolResult(
                content=f"Error fetching {url}: {str(e)}", is_error=True
            )

    @staticmethod
    def _clean_html(html: str) -> str:
        """Clean HTML to readable text.

        Args:
            html: Raw HTML content

        Returns:
            Cleaned text content
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style
            for tag in soup(["script", "style", "meta", "link", "noscript"]):
                tag.decompose()

            # Get text
            text = soup.get_text(separator="\n")

            # Clean up whitespace
            lines = [line.strip() for line in text.split("\n")]
            lines = [line for line in lines if line]  # Remove empty lines

            # Remove excessive blank lines
            cleaned = "\n".join(lines)
            cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

            return cleaned
        except Exception:
            # Fallback to basic text extraction
            return re.sub(r"<[^>]+>", "", html)
