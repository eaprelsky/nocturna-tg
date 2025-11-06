"""Client for OpenRouter API."""

import logging
from typing import List, Dict, Optional

from openai import OpenAI


logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Client for interacting with OpenRouter API.

    Uses OpenAI SDK with custom base URL for OpenRouter.
    """

    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key
            model: Model to use (default: Claude 3.5 Sonnet)
        """
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise

