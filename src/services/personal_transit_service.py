"""Service for personal transit calculations."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.api.nocturna_client import NocturnaClient
from src.services.interpretation_service import InterpretationService
from src.formatters.russian_formatter import RussianFormatter

logger = logging.getLogger(__name__)


class PersonalTransitService:
    """
    Service for calculating personal transits.
    
    Calculates transits of current planets to natal chart positions,
    providing personalized astrological analysis.
    """

    def __init__(
        self,
        nocturna_client: NocturnaClient,
        timezone: str = "Europe/Moscow",
        interpretation_service: Optional[InterpretationService] = None,
    ):
        """
        Initialize personal transit service.
        
        Args:
            nocturna_client: Client for Nocturna API
            timezone: Default timezone for calculations
            interpretation_service: Service for AI interpretations (optional)
        """
        self.nocturna_client = nocturna_client
        self.timezone = timezone
        self.interpretation_service = interpretation_service
        self.formatter = RussianFormatter()

    async def calculate_personal_transits(
        self,
        natal_chart_id: str,
        latitude: float,
        longitude: float,
        timezone: str,
        transit_date: Optional[str] = None,
        transit_time: Optional[str] = None,
        natal_birth_date: Optional[str] = None,
        natal_birth_time: Optional[str] = None,
        natal_latitude: Optional[float] = None,
        natal_longitude: Optional[float] = None,
        natal_timezone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate personal transits (transits to natal chart).
        
        Calculates aspects between current planetary positions and natal chart
        using the nocturna-calculations API synastry endpoint.
        
        Args:
            natal_chart_id: ID of natal chart (for reference only, chart will be recreated)
            latitude: Geographic latitude for transit location
            longitude: Geographic longitude for transit location
            timezone: Timezone for transit calculation
            transit_date: Transit date in YYYY-MM-DD format (default: now)
            transit_time: Transit time in HH:MM:SS format (default: now)
            natal_birth_date: Natal birth date in YYYY-MM-DD format (required)
            natal_birth_time: Natal birth time in HH:MM:SS format (required)
            natal_latitude: Natal birth latitude (required)
            natal_longitude: Natal birth longitude (required)
            natal_timezone: Natal birth timezone (required)
            
        Returns:
            Dictionary with transit data including:
            - transit_date: Date of transit calculation
            - transit_time: Time of transit calculation
            - transit_positions: Current planetary positions
            - transit_aspects: Aspects between transit and natal positions
            
        Raises:
            ValueError: If required natal data is missing
            NocturnaAPIError: If API request fails
        """
        # Validate natal data
        if not all([natal_birth_date, natal_birth_time, natal_latitude is not None, 
                    natal_longitude is not None, natal_timezone]):
            raise ValueError("Natal birth data is required for transit calculations")
        
        # Use current time if not specified
        if not transit_date or not transit_time:
            now = datetime.now()
            transit_date = now.strftime("%Y-%m-%d")
            transit_time = now.strftime("%H:%M:%S")

        logger.info(f"Calculating personal transits for chart {natal_chart_id} at {transit_date} {transit_time}")

        try:
            # Recreate natal chart in API (since it doesn't persist long-term)
            natal_chart_response = self.nocturna_client.create_chart(
                date=natal_birth_date,
                time=natal_birth_time,
                latitude=natal_latitude,
                longitude=natal_longitude,
                timezone=natal_timezone,
            )
            
            fresh_natal_chart_id = natal_chart_response.get("id")
            if not fresh_natal_chart_id:
                raise ValueError("Failed to recreate natal chart")
            
            logger.info(f"Recreated natal chart {fresh_natal_chart_id} for transit calculation")
            
            # Calculate natal positions and houses directly (API doesn't store them in charts)
            natal_positions_data = self.nocturna_client.calculate_planetary_positions(
                date=natal_birth_date,
                time=natal_birth_time,
                latitude=natal_latitude,
                longitude=natal_longitude,
                timezone=natal_timezone
            )
            natal_positions = natal_positions_data.get("positions", [])
            
            natal_houses_data = self.nocturna_client.calculate_houses(
                date=natal_birth_date,
                time=natal_birth_time,
                latitude=natal_latitude,
                longitude=natal_longitude,
                timezone=natal_timezone
            )
            natal_houses = natal_houses_data.get("houses", [])
            
            logger.info(f"Calculated natal positions: {len(natal_positions)}, natal houses: {len(natal_houses)}")
            
            # Create transit chart in API
            transit_chart_response = self.nocturna_client.create_chart(
                date=transit_date,
                time=transit_time,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
            )

            transit_chart_id = transit_chart_response.get("id")
            if not transit_chart_id:
                raise ValueError("Failed to create transit chart")

            logger.info(f"Created transit chart {transit_chart_id}")

            # Calculate transit positions and houses directly (API doesn't store them in charts)
            transit_positions_data = self.nocturna_client.calculate_planetary_positions(
                date=transit_date,
                time=transit_time,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone
            )
            transit_positions = transit_positions_data.get("positions", [])
            
            transit_houses_data = self.nocturna_client.calculate_houses(
                date=transit_date,
                time=transit_time,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone
            )
            transit_houses = transit_houses_data.get("houses", [])
            
            logger.info(f"Calculated transit positions: {len(transit_positions)}, transit houses: {len(transit_houses)}")

            # Calculate synastry (transits to natal)
            synastry_data = self.nocturna_client.calculate_synastry(
                chart_id=fresh_natal_chart_id,
                target_chart_id=transit_chart_id,
                aspects=["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
                orb_multiplier=1.0,
            )

            transit_aspects = synastry_data.get("aspects", [])

            # Clean up transit chart (we don't need to store it)
            try:
                self.nocturna_client.delete_chart(transit_chart_id)
                self.nocturna_client.delete_chart(fresh_natal_chart_id)
            except:
                pass

            result = {
                "transit_date": transit_date,
                "transit_time": transit_time,
                "transit_positions": transit_positions,
                "transit_houses": transit_houses,
                "natal_positions": natal_positions,
                "natal_houses": natal_houses,
                "natal_chart_id": natal_chart_id,
                "transit_aspects": transit_aspects,
                "calculated_at": datetime.utcnow().isoformat(),
            }

            return result

        except Exception as e:
            logger.error(f"Error calculating personal transits: {str(e)}")
            raise

    def format_personal_transit_report(
        self, transit_data: Dict[str, Any], max_aspects: int = 10
    ) -> str:
        """
        Format personal transit data as readable text report.
        
        Args:
            transit_data: Personal transit data dictionary
            max_aspects: Maximum number of aspects to display
            
        Returns:
            Formatted text report in Russian
        """
        transit_date = transit_data.get("transit_date", "N/A")
        transit_time = transit_data.get("transit_time", "N/A")
        transit_aspects = transit_data.get("transit_aspects", [])

        report = "🌟 <b>Персональные транзиты</b>\n\n"
        report += f"📅 <b>Дата:</b> {transit_date}\n"
        report += f"🕐 <b>Время:</b> {transit_time}\n\n"

        if not transit_aspects:
            report += "ℹ️ Сейчас нет значимых транзитных аспектов к вашей натальной карте.\n"
            return report

        report += "🔮 <b>Транзитные аспекты к натальной карте:</b>\n\n"

        # Show only major transits (limited by max_aspects)
        for aspect in transit_aspects[:max_aspects]:
            # Synastry API returns planet1 (natal) and planet2 (transit)
            planet1 = self.formatter.format_planet_name(aspect.get("planet1", ""))
            planet2 = self.formatter.format_planet_name(aspect.get("planet2", ""))
            aspect_type = aspect.get("aspect_type", "")
            orb = aspect.get("orb", 0)
            applying = aspect.get("applying", None)
            
            # Translate aspect type to Russian
            aspect_names = {
                "CONJUNCTION": "Соединение",
                "OPPOSITION": "Оппозиция",
                "TRINE": "Трин",
                "SQUARE": "Квадрат",
                "SEXTILE": "Секстиль",
            }
            aspect_name_ru = aspect_names.get(aspect_type, aspect_type)
            
            status = ""
            if applying is not None:
                status = "▶️ " if applying else "◀️ "
            
            report += f"  {status}<b>{planet2}</b> (транзит) {aspect_name_ru} натальный <b>{planet1}</b>\n"
            report += f"      Орб: {orb:.1f}°\n\n"

        if len(transit_aspects) > max_aspects:
            report += f"\n<i>... и еще {len(transit_aspects) - max_aspects} аспектов</i>\n"

        if any(aspect.get("applying") is not None for aspect in transit_aspects):
            report += "\n💡 <i>▶️ - аспект формируется, ◀️ - аспект расходится</i>"

        return report
