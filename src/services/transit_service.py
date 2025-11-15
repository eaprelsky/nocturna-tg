"""Service for transit analysis."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from src.api.nocturna_client import NocturnaClient
from src.formatters.russian_formatter import RussianFormatter
from src.services.interpretation_service import InterpretationService


logger = logging.getLogger(__name__)


class TransitService:
    """
    Service for analyzing planetary transits.

    Handles business logic for calculating and formatting
    current planetary positions and aspects.
    """

    def __init__(
        self,
        nocturna_client: NocturnaClient,
        timezone: str = "Europe/Moscow",
        interpretation_service: Optional[InterpretationService] = None,
    ):
        """
        Initialize transit service.

        Args:
            nocturna_client: Client for Nocturna API
            timezone: Default timezone for calculations
            interpretation_service: Optional service for LLM interpretation
        """
        self.nocturna_client = nocturna_client
        self.timezone = timezone
        self.formatter = RussianFormatter()
        self.interpretation_service = interpretation_service

    def get_current_positions(
        self, latitude: float = 55.7558, longitude: float = 37.6173
    ) -> List[Dict[str, Any]]:
        """
        Get current planetary positions.

        Args:
            latitude: Geographic latitude (default: Moscow)
            longitude: Geographic longitude (default: Moscow)

        Returns:
            List of planetary positions
        """
        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            logger.info(f"Calculating positions for {date_str} {time_str}")

            positions_data = self.nocturna_client.calculate_planetary_positions(
                date=date_str,
                time=time_str,
                latitude=latitude,
                longitude=longitude,
                timezone=self.timezone,
            )

            return positions_data.get("positions", [])

        except Exception as e:
            logger.error(f"Error calculating positions: {str(e)}")
            raise

    def get_current_aspects(
        self, latitude: float = 55.7558, longitude: float = 37.6173
    ) -> List[Dict[str, Any]]:
        """
        Get current planetary aspects.

        Args:
            latitude: Geographic latitude (default: Moscow)
            longitude: Geographic longitude (default: Moscow)

        Returns:
            List of planetary aspects
        """
        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            logger.info(f"Calculating aspects for {date_str} {time_str}")

            aspects_data = self.nocturna_client.calculate_aspects(
                date=date_str,
                time=time_str,
                latitude=latitude,
                longitude=longitude,
                timezone=self.timezone,
            )

            return aspects_data.get("aspects", [])

        except Exception as e:
            logger.error(f"Error calculating aspects: {str(e)}")
            raise

    def get_current_transit(
        self, latitude: float = 55.7558, longitude: float = 37.6173
    ) -> str:
        """
        Get current planetary transit analysis (full report).

        Args:
            latitude: Geographic latitude (default: Moscow)
            longitude: Geographic longitude (default: Moscow)

        Returns:
            Formatted transit report in Russian
        """
        try:
            positions = self.get_current_positions(latitude, longitude)
            aspects = self.get_current_aspects(latitude, longitude)

            # Format basic report
            basic_report = self.formatter.format_transit_report(positions, aspects)

            # Add LLM interpretation if available
            if self.interpretation_service:
                try:
                    logger.info("Generating LLM interpretation...")
                    interpretation = self.interpretation_service.interpret_transit(
                        positions, aspects
                    )
                    report = f"{basic_report}\n\n📖 *Интерпретация:*\n\n{interpretation}"
                except Exception as e:
                    logger.error(f"Error in interpretation: {str(e)}")
                    report = basic_report
            else:
                report = basic_report

            return report

        except Exception as e:
            logger.error(f"Error calculating transit: {str(e)}")
            return f"❌ Ошибка при расчете транзита: {str(e)}"

    def get_interpretation(
        self, latitude: float = 55.7558, longitude: float = 37.6173
    ) -> Optional[str]:
        """
        Get LLM interpretation for current transit.

        Args:
            latitude: Geographic latitude (default: Moscow)
            longitude: Geographic longitude (default: Moscow)

        Returns:
            Interpretation text or None if service unavailable
        """
        if not self.interpretation_service:
            return None

        try:
            positions = self.get_current_positions(latitude, longitude)
            aspects = self.get_current_aspects(latitude, longitude)

            logger.info("Generating LLM interpretation...")
            interpretation = self.interpretation_service.interpret_transit(
                positions, aspects
            )
            return interpretation

        except Exception as e:
            logger.error(f"Error generating interpretation: {str(e)}")
            return None

