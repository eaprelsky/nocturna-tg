"""Service for natal chart calculations and management."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.api.nocturna_client import NocturnaClient
from src.formatters.russian_formatter import RussianFormatter

logger = logging.getLogger(__name__)


class NatalChartService:
    """
    Service for natal chart calculations.
    
    Handles calculations of natal charts using Nocturna API
    and caching results in database.
    """

    def __init__(
        self,
        nocturna_client: NocturnaClient,
        timezone: str = "Europe/Moscow",
        interpretation_service: Optional[Any] = None,
    ):
        """
        Initialize natal chart service.
        
        Args:
            nocturna_client: Client for Nocturna API
            timezone: Default timezone for calculations
            interpretation_service: Optional service for LLM interpretation
        """
        self.nocturna_client = nocturna_client
        self.timezone = timezone
        self.formatter = RussianFormatter()
        self.interpretation_service = interpretation_service

    async def create_natal_chart(
        self,
        birth_date: str,
        birth_time: str,
        latitude: float,
        longitude: float,
        timezone: str,
    ) -> Dict[str, Any]:
        """
        Create natal chart in Nocturna API.
        
        Args:
            birth_date: Birth date in YYYY-MM-DD format
            birth_time: Birth time in HH:MM:SS format
            latitude: Geographic latitude
            longitude: Geographic longitude
            timezone: Timezone name
            
        Returns:
            Dictionary with chart_id and chart data
        """
        logger.info(f"Creating natal chart for {birth_date} {birth_time}")

        try:
            # Create chart in Nocturna API
            chart_response = self.nocturna_client.create_chart(
                date=birth_date,
                time=birth_time,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
            )

            chart_id = chart_response.get("id")
            if not chart_id:
                raise ValueError("No chart_id returned from API")

            logger.info(f"Created chart {chart_id} in Nocturna API")

            return {
                "chart_id": chart_id,
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error creating natal chart: {str(e)}")
            raise

    async def get_chart_positions(self, chart_id: str) -> List[Dict[str, Any]]:
        """
        Get planetary positions for a chart.
        
        Args:
            chart_id: Chart ID from Nocturna API
            
        Returns:
            List of planetary positions
        """
        try:
            positions_data = self.nocturna_client.get_chart_positions(chart_id)
            return positions_data.get("positions", [])
        except Exception as e:
            logger.error(f"Error getting chart positions for {chart_id}: {str(e)}")
            raise

    async def get_chart_houses(self, chart_id: str) -> List[Dict[str, Any]]:
        """
        Get houses for a chart.
        
        Args:
            chart_id: Chart ID from Nocturna API
            
        Returns:
            List of house data
        """
        try:
            houses_data = self.nocturna_client.get_chart_houses(chart_id)
            return houses_data.get("houses", [])
        except Exception as e:
            logger.error(f"Error getting chart houses for {chart_id}: {str(e)}")
            raise

    def format_natal_chart_report(
        self,
        positions: List[Dict[str, Any]],
        houses: Optional[List[Dict[str, Any]]] = None,
        birth_date: Optional[str] = None,
        birth_time: Optional[str] = None,
    ) -> str:
        """
        Format natal chart data as readable text report.
        
        Args:
            positions: List of planetary positions
            houses: List of house data (optional)
            birth_date: Birth date string (optional)
            birth_time: Birth time string (optional)
            
        Returns:
            Formatted text report in Russian
        """
        # Format birth information
        report = "🌟 <b>Натальная карта</b>\n\n"
        if birth_date:
            report += f"📅 <b>Дата рождения:</b> {birth_date}\n"
        if birth_time:
            report += f"🕐 <b>Время рождения:</b> {birth_time}\n"
        
        # Format positions
        report += "\n" + self.formatter.format_positions_list(positions)
        
        # Format houses
        if houses:
            report += "\n\n🏠 <b>Дома</b>\n\n"
            # Show main angles (1, 4, 7, 10)
            main_houses = [h for h in houses if h.get("number") in [1, 4, 7, 10]]
            for house in main_houses:
                house_num = house.get("number", 0)
                sign = house.get("sign", "").capitalize()
                degree = house.get("degree", 0)
                minute = house.get("minute", 0)
                
                if house_num == 1:
                    house_name = "Асцендент (1 дом)"
                elif house_num == 4:
                    house_name = "IC (4 дом)"
                elif house_num == 7:
                    house_name = "Десцендент (7 дом)"
                elif house_num == 10:
                    house_name = "MC (10 дом)"
                else:
                    house_name = f"{house_num} дом"
                
                report += f"  • {house_name}: {sign} {int(degree)}°{int(minute):02d}'\n"

        return report
