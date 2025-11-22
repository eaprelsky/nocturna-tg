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
Твоя задача — дать краткую, но содержательную интерпретацию текущего транзита планет, ориентированную на повседневную жизнь людей.

Это анализ энергий дня, он не учитывает влияние на конкретного человека, поэтому избегай использования личных местоимений. Говори об энергиях дня в целом.

Твой анализ должен:
- Быть написан на русском языке.
- Быть понятным для обычного человека (избегай сложной терминологии).
- Фокусироваться на практических аспектах и влиянии на повседневную жизнь.
- Быть позитивным, но реалистичным.
- Быть кратким (максимум 400-500 слов).
- Выделять наиболее важные влияния.
- НЕ ИСПОЛЬЗОВАТЬ ЗАГОЛОВКИ ИЛИ MARKDOWN форматирование (например, #, ##, ***, ---). Используй только абзацы и обычный текст.

Структура ответа:
1. Общая энергия дня (1-2 предложения, ключевая тема).
2. Влияние на отношения и общение (как планетарные энергии могут отразиться на взаимодействии с окружающими).
3. Влияние на работу, карьеру и финансы (какие возможности или вызовы могут возникнуть в этих сферах).
4. Влияние на эмоциональное состояние и внутренний мир (как текущие транзиты сказываются на чувствах и самочувствии).
5. Практические рекомендации (что благоприятно делать, чего стоит избегать, на что обратить внимание).
6. Совет дня (краткое вдохновляющее заключение).

Используй эмодзи для визуального акцента (но умеренно и только в начале абзацев)."""

            user_prompt = f"""Проанализируй следующую астрологическую картину дня:

Текущие позиции планет:
{positions_text}

Текущие аспекты:
{aspects_text}

На основе этих данных, пожалуйста, предоставь краткую интерпретацию, следуя указанной выше структуре и правилам форматирования. """

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

