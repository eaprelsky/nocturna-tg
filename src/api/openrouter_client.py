"""Client for OpenRouter API."""

import logging
from typing import List, Dict, Optional

from openai import OpenAI
import httpx


logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Client for interacting with OpenRouter API.

    Uses OpenAI SDK with custom base URL for OpenRouter.
    """

    def __init__(self, api_key: str, model: str = "anthropic/claude-haiku-4.5"):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key
            model: Model to use (default: Claude Haiku 4.5)
        """
        self.model = model
        
        # Create HTTP client without proxies to avoid conflicts
        http_client = httpx.Client(
            timeout=60.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            http_client=http_client,
        )

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate completion using OpenRouter.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        try:
            logger.info(f"Calling OpenRouter API with model {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            logger.info(f"Received response: {len(content)} characters")
            return content

        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}", exc_info=True)
            raise

