"""
Configuration for the Algonquin Park Stargazing Service.

All values can be overridden via environment variables for easy deployment.
"""

import os

# ---------------------------------------------------------------------------
# Location – Algonquin Provincial Park Observatory (Mew Lake area)
# ---------------------------------------------------------------------------
LATITUDE: float = float(os.environ.get("AST_LATITUDE", "45.5363"))
LONGITUDE: float = float(os.environ.get("AST_LONGITUDE", "-78.3522"))
LOCATION_NAME: str = os.environ.get("AST_LOCATION_NAME", "Algonquin Provincial Park")
TIMEZONE: str = os.environ.get("AST_TIMEZONE", "America/Toronto")

# ---------------------------------------------------------------------------
# Scheduling – time of day (24-hour, local time) when the daily check runs
# ---------------------------------------------------------------------------
POLL_HOUR: int = int(os.environ.get("AST_POLL_HOUR", "21"))    # 9 PM default
POLL_MINUTE: int = int(os.environ.get("AST_POLL_MINUTE", "0"))

# ---------------------------------------------------------------------------
# Clear-sky thresholds
# ---------------------------------------------------------------------------
# Maximum cloud cover percentage considered "clear"
MAX_CLOUD_COVER_PCT: int = int(os.environ.get("AST_MAX_CLOUD_COVER", "30"))
# Maximum precipitation probability (%) considered "acceptable"
MAX_PRECIP_PROBABILITY: int = int(os.environ.get("AST_MAX_PRECIP_PROB", "20"))
# Minimum visibility in metres considered "good"
MIN_VISIBILITY_M: int = int(os.environ.get("AST_MIN_VISIBILITY_M", "15000"))

# ---------------------------------------------------------------------------
# Open-Meteo API endpoint (free, no key required)
# ---------------------------------------------------------------------------
OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"

# ---------------------------------------------------------------------------
# How many days ahead to fetch the forecast
# ---------------------------------------------------------------------------
FORECAST_DAYS: int = 1
