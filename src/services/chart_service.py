"""Service for chart image generation."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from io import BytesIO

from src.api.nocturna_client import NocturnaClient
from src.api.chart_service_client import ChartServiceClient, ChartServiceError


logger = logging.getLogger(__name__)


class ChartService:
    """
    Service for generating chart images.

    Handles business logic for converting astrological data
    from Nocturna API into chart images via Chart Service.
    """

    # Mapping from Nocturna planet names to chart service planet names
    PLANET_MAPPING = {
        "SUN": "sun",
        "MOON": "moon",
        "MERCURY": "mercury",
        "VENUS": "venus",
        "MARS": "mars",
        "JUPITER": "jupiter",
        "SATURN": "saturn",
        "URANUS": "uranus",
        "NEPTUNE": "neptune",
        "PLUTO": "pluto",
    }

    def __init__(
        self,
        nocturna_client: NocturnaClient,
        chart_service_client: ChartServiceClient,
        timezone: str = "Europe/Moscow",
    ):
        """
        Initialize chart service.

        Args:
            nocturna_client: Client for Nocturna API
            chart_service_client: Client for Chart Rendering Service
            timezone: Default timezone for calculations
        """
        self.nocturna_client = nocturna_client
        self.chart_service_client = chart_service_client
        self.timezone = timezone

    def _convert_planets_to_chart_format(
        self, positions: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Convert Nocturna API planet positions to chart service format.

        Args:
            positions: List of planet positions from Nocturna API

        Returns:
            Dictionary in chart service format
        """
        planets_dict = {}
        for pos in positions:
            planet_name = pos.get("planet", "").upper()
            chart_planet_name = self.PLANET_MAPPING.get(planet_name)
            if chart_planet_name:
                longitude = pos.get("longitude", 0.0)
                latitude = pos.get("latitude", 0.0)
                retrograde = pos.get("is_retrograde", False) # Get retrograde status from Nocturna API
                planets_dict[chart_planet_name] = {
                    "lon": longitude,
                    "lat": latitude,
                    "retrograde": retrograde, # Add retrograde to dictionary
                }
        return planets_dict

    def _convert_houses_to_chart_format(
        self, houses: List[Dict[str, Any]]
    ) -> List[Dict[str, float]]:
        """
        Convert Nocturna API house data to chart service format.

        Args:
            houses: List of house data from Nocturna API

        Returns:
            List of house cusps in chart service format
        """
        # Sort houses by number to ensure correct order
        sorted_houses = sorted(houses, key=lambda h: h.get("number", 0))
        return [{"lon": house.get("longitude", 0.0)} for house in sorted_houses]

    def generate_current_transit_chart(
        self,
        latitude: float = 55.7558,
        longitude: float = 37.6173,
        width: int = 800,
        height: int = 800,
    ) -> bytes:
        """
        Generate chart image for current transit.

        Args:
            latitude: Geographic latitude (default: Moscow)
            longitude: Geographic longitude (default: Moscow)
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            bytes: Image data (PNG format)

        Raises:
            ChartServiceError: If chart generation fails
        """
        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            logger.info(f"Generating transit chart for {date_str} {time_str}")

            # Get planetary positions
            positions_data = self.nocturna_client.calculate_planetary_positions(
                date=date_str,
                time=time_str,
                latitude=latitude,
                longitude=longitude,
                timezone=self.timezone,
            )

            # Get houses
            houses_data = self.nocturna_client.calculate_houses(
                date=date_str,
                time=time_str,
                latitude=latitude,
                longitude=longitude,
                timezone=self.timezone,
            )

            positions = positions_data.get("positions", [])
            houses = houses_data.get("houses", [])

            logger.debug(f"Received positions from Nocturna API: {positions}")

            if not positions:
                raise ChartServiceError("No planetary positions received from API")

            if not houses or len(houses) < 12:
                raise ChartServiceError("Invalid houses data received from API")

            # Convert to chart service format
            planets_dict = self._convert_planets_to_chart_format(positions)
            houses_list = self._convert_houses_to_chart_format(houses)

            logger.debug(f"Converted planets for chart service: {planets_dict}")

            # Render chart
            image_bytes = self.chart_service_client.render_chart(
                planets=planets_dict,
                houses=houses_list,
                format="png",
                width=width,
                height=height,
                theme="light",
                aspect_orb=6,
            )

            logger.info(f"Chart generated successfully: {len(image_bytes)} bytes")
            return image_bytes

        except ChartServiceError:
            raise
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}", exc_info=True)
            raise ChartServiceError(f"Failed to generate chart: {str(e)}")

