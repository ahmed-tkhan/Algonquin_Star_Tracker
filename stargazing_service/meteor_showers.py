"""
Meteor shower calendar for the Northern Hemisphere.

Data sourced from the International Meteor Organization (IMO) annual shower list.
Each entry covers the *active window* of the shower and its peak date.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class MeteorShower:
    """Represents a single annual meteor shower."""

    name: str
    peak_month: int   # 1-12
    peak_day: int
    active_start_month: int
    active_start_day: int
    active_end_month: int
    active_end_day: int
    # Zenithal Hourly Rate (ZHR) at peak – larger = more meteors
    zhr: int
    radiant_constellation: str

    def is_active(self, check_date: date) -> bool:
        """Return True if *check_date* falls within the shower's active window."""
        year = check_date.year
        start = date(year, self.active_start_month, self.active_start_day)
        end = date(year, self.active_end_month, self.active_end_day)
        # Handle showers that wrap across the new year (e.g. Quadrantids don't,
        # but Geminids/Ursids are close to year-end; keep simple for now)
        return start <= check_date <= end

    def days_to_peak(self, check_date: date) -> int:
        """Return the number of days between *check_date* and this year's peak."""
        year = check_date.year
        peak = date(year, self.peak_month, self.peak_day)
        return (peak - check_date).days


# ---------------------------------------------------------------------------
# Major annual meteor showers (Northern Hemisphere, IMO data)
# ---------------------------------------------------------------------------
METEOR_SHOWERS: List[MeteorShower] = [
    MeteorShower("Quadrantids",     peak_month=1,  peak_day=3,
                 active_start_month=1,  active_start_day=1,
                 active_end_month=1,    active_end_day=5,
                 zhr=120, radiant_constellation="Boötes"),
    MeteorShower("Lyrids",          peak_month=4,  peak_day=22,
                 active_start_month=4,  active_start_day=16,
                 active_end_month=4,    active_end_day=25,
                 zhr=18,  radiant_constellation="Lyra"),
    MeteorShower("Eta Aquariids",   peak_month=5,  peak_day=6,
                 active_start_month=4,  active_start_day=19,
                 active_end_month=5,    active_end_day=28,
                 zhr=50,  radiant_constellation="Aquarius"),
    MeteorShower("Delta Aquariids", peak_month=7,  peak_day=30,
                 active_start_month=7,  active_start_day=12,
                 active_end_month=8,    active_end_day=23,
                 zhr=20,  radiant_constellation="Aquarius"),
    MeteorShower("Perseids",        peak_month=8,  peak_day=12,
                 active_start_month=7,  active_start_day=17,
                 active_end_month=8,    active_end_day=24,
                 zhr=100, radiant_constellation="Perseus"),
    MeteorShower("Draconids",       peak_month=10, peak_day=8,
                 active_start_month=10, active_start_day=6,
                 active_end_month=10,   active_end_day=10,
                 zhr=10,  radiant_constellation="Draco"),
    MeteorShower("Orionids",        peak_month=10, peak_day=21,
                 active_start_month=10, active_start_day=2,
                 active_end_month=11,   active_end_day=7,
                 zhr=20,  radiant_constellation="Orion"),
    MeteorShower("Leonids",         peak_month=11, peak_day=17,
                 active_start_month=11, active_start_day=6,
                 active_end_month=11,   active_end_day=30,
                 zhr=15,  radiant_constellation="Leo"),
    MeteorShower("Geminids",        peak_month=12, peak_day=14,
                 active_start_month=12, active_start_day=4,
                 active_end_month=12,   active_end_day=17,
                 zhr=150, radiant_constellation="Gemini"),
    MeteorShower("Ursids",          peak_month=12, peak_day=22,
                 active_start_month=12, active_start_day=17,
                 active_end_month=12,   active_end_day=26,
                 zhr=10,  radiant_constellation="Ursa Minor"),
]


def get_active_showers(check_date: Optional[date] = None) -> List[MeteorShower]:
    """Return all showers active on *check_date* (defaults to today)."""
    if check_date is None:
        check_date = date.today()
    return [s for s in METEOR_SHOWERS if s.is_active(check_date)]


def get_upcoming_showers(check_date: Optional[date] = None,
                         within_days: int = 7) -> List[MeteorShower]:
    """Return showers whose peak is within *within_days* days of *check_date*."""
    if check_date is None:
        check_date = date.today()
    result = []
    for shower in METEOR_SHOWERS:
        days = shower.days_to_peak(check_date)
        if 0 <= days <= within_days:
            result.append(shower)
    return result
