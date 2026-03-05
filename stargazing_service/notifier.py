"""
Notification / reporting module.

Formats the combined weather + meteor-shower assessment and prints it to
stdout (and optionally a log file).
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, List

from .meteor_showers import MeteorShower

logger = logging.getLogger(__name__)

_STAR = "★"
_CLEAR = "🌟"
_CLOUD = "☁"
_RAIN = "🌧"


def _stars_bar(zhr: int) -> str:
    """Return a simple visual bar proportional to ZHR."""
    filled = min(max(1, zhr // 20), 8)
    return _STAR * filled + "·" * (8 - filled)


def build_report(
    weather_result: Dict[str, Any],
    active_showers: List[MeteorShower],
    upcoming_showers: List[MeteorShower],
    check_date: date,
    location_name: str,
) -> str:
    """
    Build a human-readable stargazing report string.

    Parameters
    ----------
    weather_result:
        Output from :func:`stargazing_service.weather.evaluate_tonight`.
    active_showers:
        Showers currently active (from :func:`meteor_showers.get_active_showers`).
    upcoming_showers:
        Showers peaking within the next week.
    check_date:
        The date the report covers.
    location_name:
        Friendly location name used in the header.
    """
    lines: List[str] = []
    sep = "=" * 60

    lines.append(sep)
    lines.append(f"  Algonquin Stargazing Report – {check_date.strftime('%A, %B %d %Y')}")
    lines.append(f"  Location : {location_name}")
    lines.append(sep)

    # --- Weather summary ---
    lines.append("")
    lines.append("  WEATHER")
    lines.append("  -------")
    icon = _CLEAR if weather_result["is_clear"] else _CLOUD

    cloud = weather_result.get("cloud_cover")
    precip = weather_result.get("precip_prob")
    vis = weather_result.get("visibility")

    lines.append(f"  {icon}  {weather_result['reason']}")
    if cloud is not None:
        lines.append(f"       Cloud cover   : {cloud:.0f}%")
    if precip is not None:
        lines.append(f"       Precip. prob. : {precip:.0f}%")
    if vis is not None:
        lines.append(f"       Visibility    : {vis / 1000:.1f} km")

    # --- Meteor showers ---
    lines.append("")
    lines.append("  METEOR SHOWERS")
    lines.append("  --------------")
    if active_showers:
        lines.append("  Currently active showers:")
        for s in active_showers:
            bar = _stars_bar(s.zhr)
            days = s.days_to_peak(check_date)
            if days == 0:
                peak_note = "  ← PEAK TONIGHT"
            elif days > 0:
                peak_note = f"  (peak in {days} day{'s' if days != 1 else ''})"
            else:
                peak_note = f"  (peak was {-days} day{'s' if days != -1 else ''} ago)"
            lines.append(f"    • {s.name:<18} ZHR~{s.zhr:>3}  [{bar}]{peak_note}")
    else:
        lines.append("  No major meteor showers active tonight.")

    if upcoming_showers:
        lines.append("")
        lines.append("  Upcoming peaks (within 7 days):")
        for s in upcoming_showers:
            days = s.days_to_peak(check_date)
            lines.append(
                f"    • {s.name:<18} peaks in {days} day{'s' if days != 1 else ''}"
                f"  (ZHR~{s.zhr})"
            )

    # --- Final verdict ---
    lines.append("")
    lines.append("  VERDICT")
    lines.append("  -------")
    has_shower = bool(active_showers)
    if weather_result["is_clear"] and has_shower:
        verdict = "🌟 EXCELLENT – Clear skies AND an active meteor shower. Go out!"
    elif weather_result["is_clear"]:
        verdict = "✅ GOOD – Clear skies. Great night for general stargazing."
    elif has_shower:
        verdict = "⚠️  MIXED – Meteor shower active but skies are not ideal."
    else:
        verdict = "❌ POOR – Not a good night for stargazing."

    lines.append(f"  {verdict}")
    lines.append(sep)

    return "\n".join(lines)


def notify(report: str) -> None:
    """Print *report* to stdout and log it at INFO level."""
    print(report)
    logger.info(report)
