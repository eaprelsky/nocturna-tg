"""Russian language formatter for astrological data."""

from typing import Dict, List, Any


class RussianFormatter:
    """Format astrological data in Russian language."""

    # Planet names translation
    PLANETS = {
        "SUN": "Солнце",
        "MOON": "Луна",
        "MERCURY": "Меркурий",
        "VENUS": "Венера",
        "MARS": "Марс",
        "JUPITER": "Юпитер",
        "SATURN": "Сатурн",
        "URANUS": "Уран",
        "NEPTUNE": "Нептун",
        "PLUTO": "Плутон",
    }

    # Zodiac signs translation
    SIGNS = {
        "ARIES": "Овен",
        "TAURUS": "Телец",
        "GEMINI": "Близнецы",
        "CANCER": "Рак",
        "LEO": "Лев",
        "VIRGO": "Дева",
        "LIBRA": "Весы",
        "SCORPIO": "Скорпион",
        "SAGITTARIUS": "Стрелец",
        "CAPRICORN": "Козерог",
        "AQUARIUS": "Водолей",
        "PISCES": "Рыбы",
    }

    # Aspect names translation
    ASPECTS = {
        "CONJUNCTION": "Соединение",
        "OPPOSITION": "Оппозиция",
        "TRINE": "Трин",
        "SQUARE": "Квадрат",
        "SEXTILE": "Секстиль",
        "QUINCUNX": "Квинконс",
        "QUINTILE": "Квинтиль",
    }

    # Aspect symbols
    ASPECT_SYMBOLS = {
        "CONJUNCTION": "☌",
        "OPPOSITION": "☍",
        "TRINE": "△",
        "SQUARE": "□",
        "SEXTILE": "⚹",
        "QUINCUNX": "⚻",
        "QUINTILE": "Q",
    }

    @classmethod
    def format_planet_name(cls, planet: str) -> str:
        """Format planet name in Russian."""
        return cls.PLANETS.get(planet.upper(), planet)

    @classmethod
    def format_sign_name(cls, sign: str) -> str:
        """Format zodiac sign name in Russian."""
        return cls.SIGNS.get(sign.upper(), sign)

    @classmethod
    def format_aspect_name(cls, aspect: str) -> str:
        """Format aspect name in Russian."""
        return cls.ASPECTS.get(aspect.upper(), aspect)

    @classmethod
    def format_aspect_symbol(cls, aspect: str) -> str:
        """Get aspect symbol."""
        return cls.ASPECT_SYMBOLS.get(aspect.upper(), "")

    @classmethod
    def format_position(cls, position: Dict[str, Any]) -> str:
        """
        Format planetary position.

        Args:
            position: Position data from API

        Returns:
            Formatted position string
        """
        planet = cls.format_planet_name(position.get("planet", ""))
        sign = cls.format_sign_name(position.get("sign", ""))
        degree = int(position.get("degree", 0))
        minute = int(position.get("minute", 0))
        is_retrograde = position.get("is_retrograde", False)

        retrograde_mark = " ℞" if is_retrograde else ""

        return f"{planet} в {sign} {degree}°{minute:02d}'{retrograde_mark}"

    @classmethod
    def format_positions_list(cls, positions: List[Dict[str, Any]]) -> str:
        """
        Format list of planetary positions.

        Args:
            positions: List of position data from API

        Returns:
            Formatted positions as multi-line string
        """
        if not positions:
            return "Нет данных о позициях планет."

        lines = ["🌟 *Позиции планет:*\n"]
        for pos in positions:
            lines.append(cls.format_position(pos))

        return "\n".join(lines)

    @classmethod
    def format_aspect(cls, aspect: Dict[str, Any]) -> str:
        """
        Format aspect between planets.

        Args:
            aspect: Aspect data from API

        Returns:
            Formatted aspect string
        """
        planet1 = cls.format_planet_name(aspect.get("planet1", ""))
        planet2 = cls.format_planet_name(aspect.get("planet2", ""))
        aspect_type = aspect.get("aspect_type", "")
        aspect_name = cls.format_aspect_name(aspect_type)
        aspect_symbol = cls.format_aspect_symbol(aspect_type)
        orb = aspect.get("orb", 0)
        applying = aspect.get("applying")

        applying_text = " (сходящийся)" if applying else " (расходящийся)" if applying is False else ""

        return f"{planet1} {aspect_symbol} {planet2} ({aspect_name}, орб {orb:.1f}°){applying_text}"

    @classmethod
    def format_aspects_list(cls, aspects: List[Dict[str, Any]]) -> str:
        """
        Format list of aspects.

        Args:
            aspects: List of aspect data from API

        Returns:
            Formatted aspects as multi-line string
        """
        if not aspects:
            return "\n🔮 *Аспекты:*\nНет значимых аспектов."

        lines = ["\n🔮 *Аспекты:*\n"]
        for asp in aspects:
            lines.append(cls.format_aspect(asp))

        return "\n".join(lines)

    @classmethod
    def format_transit_report(
        cls, positions: List[Dict[str, Any]], aspects: List[Dict[str, Any]]
    ) -> str:
        """
        Format complete transit report.

        Args:
            positions: Planetary positions
            aspects: Planetary aspects

        Returns:
            Complete formatted report
        """
        positions_text = cls.format_positions_list(positions)
        aspects_text = cls.format_aspects_list(aspects)

        return f"{positions_text}\n{aspects_text}"

