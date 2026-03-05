"""
Core service logic – orchestrates weather + meteor shower checks.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, Optional

import requests

from . import config
from .meteor_showers import get_active_showers, get_upcoming_showers
from .notifier import build_report, notify
from .weather import evaluate_tonight, fetch_hourly_forecast

logger = logging.getLogger(__name__)


def run_check(check_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Perform a single stargazing check and print the result.

    Returns
    -------
    dict
        ``report``          – formatted report string
        ``is_good_night``   – True if weather is clear OR a shower is active
        ``weather``         – raw weather evaluation dict
        ``active_showers``  – list of active :class:`MeteorShower` objects
        ``upcoming_showers``– list of upcoming :class:`MeteorShower` objects
    """
    if check_date is None:
        check_date = date.today()

    logger.info("Running stargazing check for %s at %s",
                check_date, config.LOCATION_NAME)

    # --- Fetch weather ---
    try:
        forecast = fetch_hourly_forecast()
        weather_result = evaluate_tonight(forecast, check_date)
    except requests.RequestException as exc:
        logger.error("Weather API request failed: %s", exc)
        weather_result = {
            "is_clear": False,
            "cloud_cover": None,
            "precip_prob": None,
            "visibility": None,
            "reason": f"Weather data unavailable: {exc}",
        }
    except (ValueError, KeyError) as exc:
        logger.error("Failed to parse weather response: %s", exc)
        weather_result = {
            "is_clear": False,
            "cloud_cover": None,
            "precip_prob": None,
            "visibility": None,
            "reason": f"Weather data could not be parsed: {exc}",
        }
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Unexpected error fetching weather: %s", exc)
        weather_result = {
            "is_clear": False,
            "cloud_cover": None,
            "precip_prob": None,
            "visibility": None,
            "reason": f"Weather data unavailable (unexpected error): {exc}",
        }

    # --- Check meteor showers ---
    active_showers = get_active_showers(check_date)
    upcoming_showers = get_upcoming_showers(check_date, within_days=7)
    # Exclude from "upcoming" any that are already in "active"
    active_names = {s.name for s in active_showers}
    upcoming_showers = [s for s in upcoming_showers if s.name not in active_names]

    # --- Build & deliver report ---
    report = build_report(
        weather_result=weather_result,
        active_showers=active_showers,
        upcoming_showers=upcoming_showers,
        check_date=check_date,
        location_name=config.LOCATION_NAME,
    )
    notify(report)

    is_good_night = weather_result["is_clear"] or bool(active_showers)

    return {
        "report": report,
        "is_good_night": is_good_night,
        "weather": weather_result,
        "active_showers": active_showers,
        "upcoming_showers": upcoming_showers,
    }
