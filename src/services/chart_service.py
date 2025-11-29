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
            logger.debug(f"Received houses from Nocturna API: {houses}")

            if not positions:
                raise ChartServiceError("No planetary positions received from API")

            if not houses or len(houses) < 12:
                raise ChartServiceError("Invalid houses data received from API")

            # Convert to chart service format
            planets_dict = self._convert_planets_to_chart_format(positions)
            houses_list = self._convert_houses_to_chart_format(houses)

            logger.debug(f"Converted planets for chart service: {planets_dict}")
            logger.debug(f"Converted houses for chart service: {houses_list}")
            logger.info(f"Houses data - First house longitude: {houses_list[0]['lon'] if houses_list else 'N/A'}")

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

    def generate_natal_chart(
        self,
        positions: List[Dict[str, Any]],
        houses: List[Dict[str, Any]],
        width: int = 800,
        height: int = 800,
    ) -> bytes:
        """
        Generate chart image for natal chart from cached data.

        Args:
            positions: List of planetary positions
            houses: List of house data
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            bytes: Image data (PNG format)

        Raises:
            ChartServiceError: If chart generation fails
        """
        try:
            logger.info("Generating natal chart from cached data")

            if not positions:
                raise ChartServiceError("No planetary positions provided")

            if not houses or len(houses) < 12:
                raise ChartServiceError("Invalid houses data provided")

            # Convert to chart service format
            planets_dict = self._convert_planets_to_chart_format(positions)
            houses_list = self._convert_houses_to_chart_format(houses)

            logger.debug(f"Converted planets for chart service: {planets_dict}")
            logger.debug(f"Converted houses for chart service: {houses_list}")

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

            logger.info(f"Natal chart generated successfully: {len(image_bytes)} bytes")
            return image_bytes

        except ChartServiceError:
            raise
        except Exception as e:
            logger.error(f"Error generating natal chart: {str(e)}", exc_info=True)
            raise ChartServiceError(f"Failed to generate natal chart: {str(e)}")

    def generate_personal_transit_chart(
        self,
        natal_positions: List[Dict[str, Any]],
        natal_houses: List[Dict[str, Any]],
        transit_positions: List[Dict[str, Any]],
        transit_date: str,
        transit_time: str,
        width: int = 1000,
        height: int = 1000,
    ) -> bytes:
        """
        Generate biwheel chart for personal transits (natal + transits).
        
        Uses Chart Service /transit endpoint to render:
        - Inner wheel: Natal chart
        - Outer wheel: Transit positions
        - Aspects between natal and transit planets

        Args:
            natal_positions: List of natal planetary positions
            natal_houses: List of natal house data
            transit_positions: List of transit planetary positions
            transit_date: Transit date in YYYY-MM-DD format
            transit_time: Transit time in HH:MM:SS format
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            bytes: Image data (PNG format)

        Raises:
            ChartServiceError: If chart generation fails
        """
        try:
            logger.info("Generating personal transit biwheel chart")

            if not natal_positions:
                raise ChartServiceError("No natal positions provided")

            if not natal_houses or len(natal_houses) < 12:
                raise ChartServiceError("Invalid natal houses data provided")

            if not transit_positions:
                raise ChartServiceError("No transit positions provided")

            # Convert to chart service format
            natal_planets_dict = self._convert_planets_to_chart_format(natal_positions)
            natal_houses_list = self._convert_houses_to_chart_format(natal_houses)
            transit_planets_dict = self._convert_planets_to_chart_format(transit_positions)

            # Create ISO datetime string
            transit_datetime = f"{transit_date}T{transit_time}Z"

            logger.debug(f"Natal planets: {natal_planets_dict}")
            logger.debug(f"Transit planets: {transit_planets_dict}")
            logger.debug(f"Transit datetime: {transit_datetime}")

            # Render biwheel chart using transit endpoint
            image_bytes = self.chart_service_client.render_transit_chart(
                natal_planets=natal_planets_dict,
                natal_houses=natal_houses_list,
                transit_planets=transit_planets_dict,
                transit_datetime=transit_datetime,
                format="png",
                width=width,
                height=height,
                theme="light",
            )

            logger.info(f"Personal transit biwheel chart generated successfully: {len(image_bytes)} bytes")
            return image_bytes

        except ChartServiceError:
            raise
        except Exception as e:
            logger.error(f"Error generating personal transit chart: {str(e)}", exc_info=True)
            raise ChartServiceError(f"Failed to generate personal transit chart: {str(e)}")

