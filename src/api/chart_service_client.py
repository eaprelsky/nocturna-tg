"""Client for Chart Rendering Service."""

import logging
import base64
import time
from typing import Dict, List, Optional, Literal
from io import BytesIO

import requests


logger = logging.getLogger(__name__)


class ChartServiceError(Exception):
    """Base exception for Chart Service errors."""

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[dict] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class ChartServiceClient:
    """Client for Chart Rendering Service."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize Chart Service Client.

        Args:
            base_url: Base URL for chart rendering service
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def render_chart(
        self,
        planets: Dict[str, Dict[str, float]],
        houses: List[Dict[str, float]],
        format: Literal["png", "svg", "jpeg"] = "png",
        width: int = 800,
        height: int = 800,
        theme: Literal["light", "dark"] = "light",
        aspect_orb: int = 6,
    ) -> bytes:
        """
        Render natal chart and return image data.

        Args:
            planets: Dictionary with planet data (e.g., {"sun": {"lon": 85.83, "lat": 0.0}})
            houses: List of 12 house cusps (e.g., [{"lon": 300.32}, ...])
            format: Output format (png, svg, jpeg)
            width: Image width in pixels
            height: Image height in pixels
            theme: Color theme
            aspect_orb: Orb for aspect calculation

        Returns:
            bytes: Image data in specified format

        Raises:
            ChartServiceError: If rendering fails
        """
        url = f"{self.base_url}/api/v1/chart/render"

        payload = {
            "planets": planets,
            "houses": houses,
            "aspectSettings": {
                "enabled": True,
                "orb": aspect_orb,
                "types": {
                    "conjunction": {"enabled": True},
                    "opposition": {"enabled": True},
                    "trine": {"enabled": True},
                    "square": {"enabled": True},
                    "sextile": {"enabled": True},
                },
            },
            "renderOptions": {
                "format": format,
                "width": width,
                "height": height,
                "quality": 90,
                "theme": theme,
            },
        }

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Requesting chart render (attempt {attempt + 1}/{self.max_retries})")
                logger.debug(f"Chart render request payload: {payload}") # Log the payload

                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    image_base64 = data["data"]["image"]
                    image_bytes = base64.b64decode(image_base64)

                    logger.info(
                        f"Chart rendered successfully: "
                        f"{data['data']['size']} bytes, "
                        f"{data['meta']['renderTime']}ms"
                    )

                    return image_bytes

                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", 60)
                    logger.warning(f"Rate limit exceeded, retry after {retry_after}s")
                    raise ChartServiceError(
                        "Rate limit exceeded",
                        code="RATE_LIMIT_EXCEEDED",
                        details={"retry_after": retry_after},
                    )

                elif response.status_code >= 400:
                    try:
                        error_data = response.json()
                        error_info = error_data.get("error", {})
                        raise ChartServiceError(
                            error_info.get("message", "Unknown error"),
                            code=error_info.get("code"),
                            details=error_info.get("details"),
                        )
                    except ValueError:
                        # Response is not JSON
                        raise ChartServiceError(
                            f"Service error: {response.status_code}",
                            code="HTTP_ERROR",
                            details={"status_code": response.status_code},
                        )

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise ChartServiceError("Service timeout", code="TIMEOUT")
                time.sleep(2**attempt)

            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error: {e}")
                if attempt == self.max_retries - 1:
                    raise ChartServiceError("Service unavailable", code="CONNECTION_ERROR")
                time.sleep(2**attempt)

        raise ChartServiceError("Max retries exceeded", code="MAX_RETRIES")

    def render_transit_chart(
        self,
        natal_planets: Dict[str, Dict[str, float]],
        natal_houses: List[Dict[str, float]],
        transit_planets: Dict[str, Dict[str, float]],
        transit_datetime: str,
        format: Literal["png", "svg", "jpeg"] = "png",
        width: int = 1000,
        height: int = 1000,
        theme: Literal["light", "dark"] = "light",
    ) -> bytes:
        """
        Render transit chart (biwheel with natal inner and transit outer).

        Args:
            natal_planets: Natal planet positions
            natal_houses: Natal house cusps
            transit_planets: Transit planet positions
            transit_datetime: Transit datetime in ISO format
            format: Output format (png, svg, jpeg)
            width: Image width in pixels
            height: Image height in pixels
            theme: Color theme

        Returns:
            bytes: Image data in specified format

        Raises:
            ChartServiceError: If rendering fails
        """
        url = f"{self.base_url}/api/v1/chart/render/transit"

        payload = {
            "natal": {
                "planets": natal_planets,
                "houses": natal_houses,
            },
            "transit": {
                "planets": transit_planets,
                "datetime": transit_datetime,
            },
            "aspectSettings": {
                "natal": {
                    "enabled": False,  # Don't show natal-to-natal aspects
                    "orb": 6,
                },
                "transit": {
                    "enabled": False,  # Don't show transit-to-transit aspects
                    "orb": 6,
                },
                "natalToTransit": {
                    "enabled": True,  # Show transit-to-natal aspects (main focus)
                    "orb": 3,
                    "types": {
                        "conjunction": {"enabled": True},
                        "opposition": {"enabled": True},
                        "trine": {"enabled": True},
                        "square": {"enabled": True},
                        "sextile": {"enabled": True},
                    },
                },
            },
            "renderOptions": {
                "format": format,
                "width": width,
                "height": height,
                "quality": 90,
                "theme": theme,
            },
        }

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Requesting transit chart render (attempt {attempt + 1}/{self.max_retries})")
                logger.debug(f"Transit chart render payload: {payload}")

                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    image_base64 = data["data"]["image"]
                    image_bytes = base64.b64decode(image_base64)

                    logger.info(
                        f"Transit chart rendered successfully: "
                        f"{data['data']['size']} bytes, "
                        f"{data['meta']['renderTime']}ms"
                    )

                    return image_bytes

                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", 60)
                    logger.warning(f"Rate limit exceeded, retry after {retry_after}s")
                    raise ChartServiceError(
                        "Rate limit exceeded",
                        code="RATE_LIMIT_EXCEEDED",
                        details={"retry_after": retry_after},
                    )

                elif response.status_code >= 400:
                    try:
                        error_data = response.json()
                        error_info = error_data.get("error", {})
                        raise ChartServiceError(
                            error_info.get("message", "Unknown error"),
                            code=error_info.get("code"),
                            details=error_info.get("details"),
                        )
                    except ValueError:
                        raise ChartServiceError(
                            f"Service error: {response.status_code}",
                            code="HTTP_ERROR",
                            details={"status_code": response.status_code},
                        )

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise ChartServiceError("Service timeout", code="TIMEOUT")
                time.sleep(2**attempt)

            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error: {e}")
                if attempt == self.max_retries - 1:
                    raise ChartServiceError("Service unavailable", code="CONNECTION_ERROR")
                time.sleep(2**attempt)

        raise ChartServiceError("Max retries exceeded", code="MAX_RETRIES")

    def health_check(self) -> bool:
        """
        Check if service is healthy.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

