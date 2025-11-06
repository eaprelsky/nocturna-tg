"""Service for LLM-based astrological interpretation."""

import logging
from typing import List, Dict, Any

from src.api.openrouter_client import OpenRouterClient


logger = logging.getLogger(__name__)


class InterpretationService:
    """
    Service for generating astrological interpretations using LLM.

    Analyzes planetary positions and aspects to provide
    meaningful insights in Russian language.
    """

    def __init__(self, openrouter_client: OpenRouterClient):
        """
        Initialize interpretation service.

        Args:
            openrouter_client: Client for OpenRouter API
        """
        self.openrouter_client = openrouter_client

    def interpret_transit(
        self, positions: List[Dict[str, Any]], aspects: List[Dict[str, Any]]
    ) -> str:
        """
        Generate interpretation of current transit.

        Args:
            positions: Planetary positions data
            aspects: Aspects data

        Returns:
            Interpretation text in Russian
        """
        try:
            # Format positions for prompt
            positions_text = self._format_positions_for_prompt(positions)
            aspects_text = self._format_aspects_for_prompt(aspects)

            # Create prompt
            system_prompt = """Ты — опытный астролог с глубокими знаниями западной астрологии. 
Твоя задача — дать краткую, но содержательную интерпретацию текущего транзита планет.

Твой анализ должен:
- Быть написан на русском языке
- Быть понятным для обычного человека (избегай слишком сложной терминологии)
- Фокусироваться на практических аспектах и влиянии на повседневную жизнь
- Быть позитивным, но реалистичным
- Быть кратким (максимум 300-400 слов)
- Выделять наиболее важные влияния

Структура ответа:
1. Общая картина дня (1-2 предложения)
2. Ключевые планетарные влияния (2-3 самых важных)
3. Практические рекомендации (что благоприятно, чего стоит избегать)

Используй эмодзи для визуального акцента (но умеренно)."""

            user_prompt = f"""Текущие позиции планет:
{positions_text}

Текущие аспекты:
{aspects_text}

Пожалуйста, проанализируй эту астрологическую картину и дай краткую интерпретацию."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # Generate interpretation
            interpretation = self.openrouter_client.generate_completion(
                messages=messages, temperature=0.7, max_tokens=1500
            )

            return interpretation

        except Exception as e:
            logger.error(f"Error generating interpretation: {str(e)}")
            return (
                "⚠️ К сожалению, не удалось сгенерировать интерпретацию. "
                "Пожалуйста, попробуйте позже."
            )

    def _format_positions_for_prompt(self, positions: List[Dict[str, Any]]) -> str:
        """Format positions data for LLM prompt."""
        lines = []
        for pos in positions:
            planet = pos.get("planet", "")
            sign = pos.get("sign", "")
            degree = int(pos.get("degree", 0))
            minute = int(pos.get("minute", 0))
            retrograde = " (ретроградный)" if pos.get("is_retrograde") else ""

            lines.append(f"- {planet} в {sign} {degree}°{minute:02d}'{retrograde}")

        return "\n".join(lines)

    def _format_aspects_for_prompt(self, aspects: List[Dict[str, Any]]) -> str:
        """Format aspects data for LLM prompt."""
        if not aspects:
            return "Нет значимых аспектов."

        lines = []
        for asp in aspects:
            planet1 = asp.get("planet1", "")
            planet2 = asp.get("planet2", "")
            aspect_type = asp.get("aspect_type", "")
            orb = asp.get("orb", 0)
            applying = asp.get("applying")

            applying_text = (
                " (сходящийся)"
                if applying
                else " (расходящийся)" if applying is False else ""
            )

            lines.append(
                f"- {planet1} {aspect_type} {planet2} (орб {orb:.1f}°){applying_text}"
            )

        return "\n".join(lines)

