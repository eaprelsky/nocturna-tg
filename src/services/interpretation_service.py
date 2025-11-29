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

    def interpret_natal_chart(
        self, positions: List[Dict[str, Any]], houses: List[Dict[str, Any]]
    ) -> str:
        """
        Generate interpretation of natal chart.

        Args:
            positions: Planetary positions data
            houses: Houses data

        Returns:
            Interpretation text in Russian
        """
        try:
            # Format positions for prompt
            positions_text = self._format_positions_for_prompt(positions)
            houses_text = self._format_houses_for_prompt(houses)

            # Create prompt
            system_prompt = """Ты — опытный астролог с глубокими знаниями западной астрологии. 
Твоя задача — дать краткую, но содержательную интерпретацию натальной карты.

Твой анализ должен:
- Быть написан на русском языке.
- Быть понятным для обычного человека (избегай сложной терминологии).
- Фокусироваться на ключевых характеристиках личности.
- Быть позитивным, но реалистичным.
- Быть кратким (максимум 500-600 слов).
- Выделять наиболее важные аспекты карты.
- НЕ ИСПОЛЬЗОВАТЬ ЗАГОЛОВКИ ИЛИ MARKDOWN форматирование (например, #, ##, ***, ---). Используй только абзацы и обычный текст.

Структура ответа:
1. Общая характеристика личности (2-3 предложения о ключевых чертах, основанных на положении Солнца, Луны и Асцендента).
2. Эмоциональная сфера и внутренний мир (как человек чувствует, какие у него эмоциональные потребности).
3. Стиль общения и мышления (особенности коммуникации и восприятия информации).
4. Отношения и любовь (как проявляется в романтических отношениях, что важно в партнерстве).
5. Карьера и самореализация (профессиональные склонности и способы достижения целей).
6. Сильные стороны и потенциал (на что важно опираться).
7. Области роста (над чем можно поработать для гармоничного развития).

Используй эмодзи для визуального акцента (но умеренно и только в начале абзацев)."""

            user_prompt = f"""Проанализируй следующую натальную карту:

Позиции планет:
{positions_text}

Дома:
{houses_text}

На основе этих данных, пожалуйста, предоставь краткую интерпретацию натальной карты, следуя указанной выше структуре и правилам форматирования."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # Generate interpretation
            interpretation = self.openrouter_client.generate_completion(
                messages=messages, temperature=0.7, max_tokens=2000
            )

            return interpretation

        except Exception as e:
            logger.error(f"Error generating natal interpretation: {str(e)}")
            return (
                "⚠️ К сожалению, не удалось сгенерировать интерпретацию. "
                "Пожалуйста, попробуйте позже."
            )

    def _format_houses_for_prompt(self, houses: List[Dict[str, Any]]) -> str:
        """Format houses data for LLM prompt."""
        if not houses:
            return "Дома не указаны."

        lines = []
        for house in houses:
            house_num = house.get("number", 0)
            sign = house.get("sign", "")
            degree = int(house.get("degree", 0))
            minute = int(house.get("minute", 0))

            # Special names for main angles
            if house_num == 1:
                house_name = "1 дом (Асцендент)"
            elif house_num == 4:
                house_name = "4 дом (IC)"
            elif house_num == 7:
                house_name = "7 дом (Десцендент)"
            elif house_num == 10:
                house_name = "10 дом (MC)"
            else:
                house_name = f"{house_num} дом"

            lines.append(f"- {house_name}: {sign} {degree}°{minute:02d}'")

        return "\n".join(lines)

    def interpret_personal_transits(
        self,
        natal_positions: List[Dict[str, Any]],
        transit_aspects: List[Dict[str, Any]],
    ) -> str:
        """
        Generate interpretation of personal transits (transits to natal chart).

        Args:
            natal_positions: Natal planetary positions
            transit_aspects: Aspects between transiting and natal planets

        Returns:
            Interpretation text in Russian
        """
        try:
            # Format natal positions
            natal_text = self._format_positions_for_prompt(natal_positions)
            
            # Format transit aspects (synastry format: planet1=natal, planet2=transit)
            transit_aspects_text = self._format_transit_aspects_for_prompt(transit_aspects)

            # Create prompt
            system_prompt = """Ты — опытный астролог с глубокими знаниями западной астрологии. 
Твоя задача — дать краткую, но содержательную интерпретацию персональных транзитов, т.е. текущих планет в аспектах к натальной карте конкретного человека.

Твой анализ должен:
- Быть написан на русском языке.
- Обращаться к читателю на "ты" (это персональный прогноз для конкретного человека).
- Быть понятным для обычного человека (избегай сложной терминологии).
- Фокусироваться на практических аспектах и влиянии на повседневную жизнь.
- Быть позитивным, но реалистичным.
- Быть кратким (максимум 400-500 слов).
- Выделять наиболее важные транзитные влияния.
- НЕ ИСПОЛЬЗОВАТЬ ЗАГОЛОВКИ ИЛИ MARKDOWN форматирование (например, #, ##, ***, ---). Используй только абзацы и обычный текст.

Структура ответа:
1. Общая энергия периода (1-2 предложения о ключевых транзитных влияниях).
2. Влияние на твои отношения и общение (как транзиты влияют на взаимодействие с окружающими).
3. Влияние на работу, карьеру и финансы (какие возможности или вызовы могут возникнуть).
4. Влияние на эмоциональное состояние и внутренний мир (как транзиты сказываются на чувствах).
5. Практические рекомендации (что благоприятно делать, чего стоит избегать).
6. Персональный совет (краткое вдохновляющее заключение).

Используй эмодзи для визуального акцента (но умеренно и только в начале абзацев)."""

            user_prompt = f"""Проанализируй следующие персональные транзиты:

Натальные позиции планет:
{natal_text}

Транзитные аспекты к натальной карте:
{transit_aspects_text}

На основе этих данных, пожалуйста, предоставь краткую интерпретацию персональных транзитов, следуя указанной выше структуре и правилам форматирования."""

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
            logger.error(f"Error generating personal transit interpretation: {str(e)}")
            return (
                "⚠️ К сожалению, не удалось сгенерировать интерпретацию. "
                "Пожалуйста, попробуйте позже."
            )

    def _format_transit_aspects_for_prompt(self, aspects: List[Dict[str, Any]]) -> str:
        """Format transit aspects for LLM prompt."""
        if not aspects:
            return "Нет значимых транзитных аспектов."

        lines = []
        for asp in aspects:
            # In synastry format: planet1 is natal, planet2 is transit
            natal_planet = asp.get("planet1", "")
            transit_planet = asp.get("planet2", "")
            aspect_type = asp.get("aspect_type", "")
            orb = asp.get("orb", 0)
            applying = asp.get("applying")

            applying_text = (
                " (сходящийся)"
                if applying
                else " (расходящийся)" if applying is False else ""
            )

            lines.append(
                f"- Транзитный {transit_planet} {aspect_type} натальный {natal_planet} (орб {orb:.1f}°){applying_text}"
            )

        return "\n".join(lines)

