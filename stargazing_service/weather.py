"""
Weather checker using the Open-Meteo API (free, no API key required).

Fetches hourly cloud cover, precipitation probability, and visibility for
the configured location and evaluates whether tonight is suitable for
stargazing.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests

from . import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _tonight_hours() -> List[int]:
    """Return the evening/night hours we care about (20:00 – 02:00 next day)."""
    return list(range(20, 24))   # 8 PM – midnight  (index into today's hours)


# ---------------------------------------------------------------------------
# API fetch
# ---------------------------------------------------------------------------

def fetch_hourly_forecast(
    latitude: float = config.LATITUDE,
    longitude: float = config.LONGITUDE,
    forecast_days: int = config.FORECAST_DAYS,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    """
    Fetch hourly forecast from Open-Meteo.

    Returns the raw JSON response as a dict.

    Raises
    ------
    requests.RequestException
        If the HTTP request fails for any reason.
    ValueError
        If the response cannot be parsed as JSON.
    """
    params: Dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "cloud_cover,precipitation_probability,visibility",
        "forecast_days": forecast_days,
        "timezone": config.TIMEZONE,
    }
    requester = session or requests
    response = requester.get(config.OPEN_METEO_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def _average(values: List[Optional[float]]) -> Optional[float]:
    """Return the mean of non-None values, or None if the list is empty."""
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


def evaluate_tonight(
    forecast: Dict[str, Any],
    check_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Evaluate whether *tonight* is good for stargazing.

    Parameters
    ----------
    forecast:
        Raw JSON from :func:`fetch_hourly_forecast`.
    check_date:
        The night to evaluate (defaults to *today*).

    Returns
    -------
    dict with keys:
        ``is_clear``       – bool
        ``cloud_cover``    – average cloud cover (%) for the evening hours
        ``precip_prob``    – average precipitation probability (%)
        ``visibility``     – average visibility (m)
        ``reason``         – human-readable explanation
    """
    if check_date is None:
        check_date = date.today()

    hourly = forecast.get("hourly", {})
    times: List[str] = hourly.get("time", [])
    cloud_covers: List[Optional[float]] = hourly.get("cloud_cover", [])
    precip_probs: List[Optional[float]] = hourly.get("precipitation_probability", [])
    visibilities: List[Optional[float]] = hourly.get("visibility", [])

    date_str = check_date.strftime("%Y-%m-%d")
    tonight_indices: List[int] = []
    for idx, t in enumerate(times):
        if t.startswith(date_str):
            try:
                hour = datetime.fromisoformat(t).hour
            except ValueError:
                continue
            if hour in _tonight_hours():
                tonight_indices.append(idx)

    if not tonight_indices:
        return {
            "is_clear": False,
            "cloud_cover": None,
            "precip_prob": None,
            "visibility": None,
            "reason": "No forecast data available for tonight's hours.",
        }

    avg_cloud = _average([cloud_covers[i] for i in tonight_indices
                          if i < len(cloud_covers)])
    avg_precip = _average([precip_probs[i] for i in tonight_indices
                           if i < len(precip_probs)])
    avg_vis = _average([visibilities[i] for i in tonight_indices
                        if i < len(visibilities)])

    reasons: List[str] = []
    is_clear = True

    if avg_cloud is not None and avg_cloud > config.MAX_CLOUD_COVER_PCT:
        is_clear = False
        reasons.append(
            f"cloud cover {avg_cloud:.0f}% > threshold {config.MAX_CLOUD_COVER_PCT}%"
        )
    if avg_precip is not None and avg_precip > config.MAX_PRECIP_PROBABILITY:
        is_clear = False
        reasons.append(
            f"precipitation probability {avg_precip:.0f}% > threshold "
            f"{config.MAX_PRECIP_PROBABILITY}%"
        )
    if avg_vis is not None and avg_vis < config.MIN_VISIBILITY_M:
        is_clear = False
        reasons.append(
            f"visibility {avg_vis:.0f} m < threshold {config.MIN_VISIBILITY_M} m"
        )

    if is_clear:
        reason = "Skies look clear – great night for stargazing!"
    else:
        reason = "Not ideal: " + "; ".join(reasons) + "."

    return {
        "is_clear": is_clear,
        "cloud_cover": avg_cloud,
        "precip_prob": avg_precip,
        "visibility": avg_vis,
        "reason": reason,
    }
