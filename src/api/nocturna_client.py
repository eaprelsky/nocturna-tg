"""Client for Nocturna Calculations API."""

import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

import requests


logger = logging.getLogger(__name__)


class NocturnaAPIError(Exception):
    """Base exception for Nocturna API errors."""

    pass


class NocturnaClient:
    """
    Client for interacting with Nocturna Calculations API.

    Provides methods for calculating planetary positions and aspects
    using the direct calculations endpoint (stateless).
    """

    def __init__(
        self,
        api_url: str,
        service_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize Nocturna API client.

        Args:
            api_url: Base URL for Nocturna API
            service_token: Service token for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_url = api_url.rstrip("/")
        self.service_token = service_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "NocturnaTelegramBot/0.1.0",
        }
        
        # Add authorization header if service token is provided
        if service_token:
            headers["Authorization"] = f"Bearer {service_token}"
        
        self.session.headers.update(headers)

    def _handle_error_response(self, error: Any) -> str:
        """
        Handle error response that can be dict or string.
        
        Args:
            error: Error data (dict or string)
            
        Returns:
            Error message string
        """
        if isinstance(error, dict):
            return error.get('message', 'Unknown error')
        else:
            return str(error) if error else 'Unknown error'
    
    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Response data as dictionary

        Raises:
            NocturnaAPIError: If request fails after retries
        """
        url = f"{self.api_url}{endpoint}"

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )

                if response.status_code >= 500 and attempt < self.max_retries:
                    wait_time = 2**attempt
                    logger.warning(
                        f"Server error, retrying in {wait_time}s (attempt {attempt + 1})"
                    )
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    logger.warning(f"Timeout, retrying (attempt {attempt + 1})")
                    time.sleep(2**attempt)
                    continue
                raise NocturnaAPIError("Request timeout after retries")

            except requests.exceptions.HTTPError as e:
                # For client errors (4xx), don't retry - log the response body
                if 400 <= e.response.status_code < 500:
                    error_body = ""
                    try:
                        error_data = e.response.json()
                        error_body = f"\nAPI Response: {error_data}"
                    except Exception:
                        error_body = f"\nResponse Text: {e.response.text}"
                    
                    logger.error(f"Client error {e.response.status_code}: {str(e)}{error_body}")
                    raise NocturnaAPIError(f"Request failed: {str(e)}{error_body}")
                
                # For server errors (5xx), retry
                if attempt < self.max_retries:
                    logger.warning(f"Server error, retrying (attempt {attempt + 1})")
                    time.sleep(2**attempt)
                    continue
                raise NocturnaAPIError(f"Request failed: {str(e)}")
            
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    logger.warning(f"Request error, retrying (attempt {attempt + 1})")
                    time.sleep(2**attempt)
                    continue
                raise NocturnaAPIError(f"Request failed: {str(e)}")

        raise NocturnaAPIError("Max retries exceeded")

    def calculate_planetary_positions(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        planets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate current planetary positions.

        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            timezone: Timezone string (e.g., "Europe/Moscow")
            planets: List of planet names (default: all major planets)

        Returns:
            Dictionary with planetary positions
        """
        if planets is None:
            planets = [
                "SUN",
                "MOON",
                "MERCURY",
                "VENUS",
                "MARS",
                "JUPITER",
                "SATURN",
                "URANUS",
                "NEPTUNE",
                "PLUTO",
            ]

        payload = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "planets": planets,
            "include_retrograde": True,
            "include_speed": True,
        }

        response = self._make_request(
            "POST", "/calculations/planetary-positions", json=payload
        )

        # Direct calculations endpoint returns data directly without wrapper
        # Check if response has 'success' field (wrapped format) or direct data
        if "success" in response:
            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", {})
                raise NocturnaAPIError(f"API error: {self._handle_error_response(error)}")
        else:
            # Direct format - return as is
            return response

    def calculate_aspects(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        planets: Optional[List[str]] = None,
        aspects: Optional[List[str]] = None,
        orb_multiplier: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Calculate aspects between planets.

        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            timezone: Timezone string
            planets: List of planet names
            aspects: List of aspect types
            orb_multiplier: Orb multiplier (default: 1.0)

        Returns:
            Dictionary with aspects data
        """
        if planets is None:
            planets = [
                "SUN",
                "MOON",
                "MERCURY",
                "VENUS",
                "MARS",
                "JUPITER",
                "SATURN",
                "URANUS",
                "NEPTUNE",
                "PLUTO",
            ]

        if aspects is None:
            aspects = ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"]

        payload = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "planets": planets,
            "aspects": aspects,
            "orb_multiplier": orb_multiplier,
        }

        response = self._make_request("POST", "/calculations/aspects", json=payload)

        # Direct calculations endpoint returns data directly without wrapper
        # Check if response has 'success' field (wrapped format) or direct data
        if "success" in response:
            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", {})
                raise NocturnaAPIError(f"API error: {self._handle_error_response(error)}")
        else:
            # Direct format - return as is
            return response

    def calculate_houses(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        house_system: str = "PLACIDUS",
        include_angles: bool = True,
    ) -> Dict[str, Any]:
        """
        Calculate house cusps.

        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            timezone: Timezone string
            house_system: House system (default: PLACIDUS)
            include_angles: Include angles (ASC, MC, etc.)

        Returns:
            Dictionary with houses data
        """
        payload = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "house_system": house_system,
            "include_angles": include_angles,
        }

        response = self._make_request("POST", "/calculations/houses", json=payload)

        # Direct calculations endpoint returns data directly without wrapper
        # Check if response has 'success' field (wrapped format) or direct data
        if "success" in response:
            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", {})
                raise NocturnaAPIError(f"API error: {self._handle_error_response(error)}")
        else:
            # Direct format - return as is
            return response

    def create_chart(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a chart in Nocturna API.
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            timezone: Timezone string (e.g., "Europe/Moscow")
            config: Optional chart configuration (house system, aspects, orbs)
            
        Returns:
            Dictionary with chart data including chart_id
        """
        # Combine date and time into ISO datetime format
        # API expects: "1990-01-01T12:00:00" format
        datetime_str = f"{date}T{time}"
        
        # Provide default config if not specified (required by API)
        if config is None:
            config = {
                "house_system": "placidus",
                "aspects": ["conjunction", "opposition", "trine", "square", "sextile"],
                "orbs": {
                    "conjunction": 8,
                    "opposition": 8,
                    "trine": 6,
                    "square": 6,
                    "sextile": 4
                }
            }
        
        payload = {
            "date": datetime_str,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "config": config,
        }
        
        logger.debug(f"Creating chart with payload: {payload}")
        response = self._make_request("POST", "/charts", json=payload)
        
        # Handle wrapped or direct response
        if "success" in response:
            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", {})
                raise NocturnaAPIError(f"API error: {self._handle_error_response(error)}")
        else:
            # Direct format - return as is
            return response
    
    def get_chart(self, chart_id: str) -> Dict[str, Any]:
        """
        Get chart by ID.
        
        Args:
            chart_id: Chart ID
            
        Returns:
            Dictionary with chart data
        """
        response = self._make_request("GET", f"/charts/{chart_id}")
        
        if "success" in response:
            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", {})
                raise NocturnaAPIError(f"API error: {self._handle_error_response(error)}")
        else:
            return response
    
    def calculate_synastry(
        self,
        chart_id: str,
        target_chart_id: str,
        aspects: Optional[List[str]] = None,
        orb_multiplier: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Calculate synastry between two charts.
        
        Args:
            chart_id: First chart ID (e.g., natal chart)
            target_chart_id: Second chart ID (e.g., transit/comparison chart)
            aspects: Optional list of aspect types
            orb_multiplier: Orb multiplier for aspects
            
        Returns:
            Dictionary with synastry aspects
        """
        payload = {
            "target_chart_id": target_chart_id,  # API actually uses 'target_chart_id' (not 'second_chart_id' as in docs)
            "orb_multiplier": orb_multiplier,
        }
        
        if aspects:
            payload["aspects"] = aspects
        
        response = self._make_request(
            "POST", f"/charts/{chart_id}/synastry", json=payload
        )
        
        if "success" in response:
            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", {})
                raise NocturnaAPIError(f"API error: {self._handle_error_response(error)}")
        else:
            return response
    
    def delete_chart(self, chart_id: str) -> bool:
        """
        Delete chart by ID.
        
        Args:
            chart_id: Chart ID
            
        Returns:
            True if successful
        """
        try:
            self._make_request("DELETE", f"/charts/{chart_id}")
            return True
        except NocturnaAPIError:
            return False
    
    def calculate_planetary_positions(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        planets: Optional[List[str]] = None,
        house_system: str = "placidus",
    ) -> Dict[str, Any]:
        """
        Calculate planetary positions directly without creating a chart.
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Geographic latitude
            longitude: Geographic longitude
            timezone: Timezone string
            planets: Optional list of planets to calculate
            house_system: House system to use
            
        Returns:
            Dictionary with planetary positions
        """
        payload = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "house_system": house_system,
        }
        
        if planets:
            payload["planets"] = planets
        
        response = self._make_request("POST", "/calculations/planetary-positions", json=payload)
        
        if "success" in response:
            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", {})
                raise NocturnaAPIError(f"API error: {self._handle_error_response(error)}")
        else:
            return response
    
    def calculate_houses_direct(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        house_system: str = "placidus",
    ) -> Dict[str, Any]:
        """
        Calculate houses directly without creating a chart.
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Geographic latitude
            longitude: Geographic longitude
            timezone: Timezone string
            house_system: House system to use
            
        Returns:
            Dictionary with houses data
        """
        payload = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "house_system": house_system,
        }
        
        response = self._make_request("POST", "/calculations/houses", json=payload)
        
        if "success" in response:
            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", {})
                raise NocturnaAPIError(f"API error: {self._handle_error_response(error)}")
        else:
            return response
    
    def calculate_aspects_direct(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        house_system: str = "placidus",
    ) -> Dict[str, Any]:
        """
        Calculate aspects directly without creating a chart.
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Geographic latitude
            longitude: Geographic longitude
            timezone: Timezone string
            house_system: House system to use
            
        Returns:
            Dictionary with aspects data
        """
        payload = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "house_system": house_system,
        }
        
        response = self._make_request("POST", "/calculations/aspects", json=payload)
        
        if "success" in response:
            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", {})
                raise NocturnaAPIError(f"API error: {self._handle_error_response(error)}")
        else:
            return response

