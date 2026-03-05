"""
Tests for stargazing_service.meteor_showers
"""

from datetime import date

import pytest

from stargazing_service.meteor_showers import (
    MeteorShower,
    get_active_showers,
    get_upcoming_showers,
)


# ---------------------------------------------------------------------------
# MeteorShower.is_active
# ---------------------------------------------------------------------------

class TestIsActive:
    """Tests for MeteorShower.is_active."""

    def _make_shower(self) -> MeteorShower:
        return MeteorShower(
            name="Test Shower",
            peak_month=8, peak_day=12,
            active_start_month=8, active_start_day=1,
            active_end_month=8, active_end_day=20,
            zhr=100,
            radiant_constellation="Perseus",
        )

    def test_active_on_start_day(self):
        shower = self._make_shower()
        assert shower.is_active(date(2024, 8, 1)) is True

    def test_active_on_peak_day(self):
        shower = self._make_shower()
        assert shower.is_active(date(2024, 8, 12)) is True

    def test_active_on_end_day(self):
        shower = self._make_shower()
        assert shower.is_active(date(2024, 8, 20)) is True

    def test_not_active_before_start(self):
        shower = self._make_shower()
        assert shower.is_active(date(2024, 7, 31)) is False

    def test_not_active_after_end(self):
        shower = self._make_shower()
        assert shower.is_active(date(2024, 8, 21)) is False


# ---------------------------------------------------------------------------
# MeteorShower.days_to_peak
# ---------------------------------------------------------------------------

class TestDaysToPeak:
    def _make_shower(self) -> MeteorShower:
        return MeteorShower(
            name="Test Shower",
            peak_month=8, peak_day=12,
            active_start_month=8, active_start_day=1,
            active_end_month=8, active_end_day=20,
            zhr=100,
            radiant_constellation="Perseus",
        )

    def test_days_to_peak_on_peak(self):
        assert self._make_shower().days_to_peak(date(2024, 8, 12)) == 0

    def test_days_to_peak_before_peak(self):
        assert self._make_shower().days_to_peak(date(2024, 8, 10)) == 2

    def test_days_to_peak_after_peak(self):
        assert self._make_shower().days_to_peak(date(2024, 8, 15)) == -3


# ---------------------------------------------------------------------------
# get_active_showers
# ---------------------------------------------------------------------------

class TestGetActiveShowers:
    def test_perseids_active_in_august(self):
        showers = get_active_showers(date(2024, 8, 12))
        names = [s.name for s in showers]
        assert "Perseids" in names

    def test_no_major_shower_mid_march(self):
        # Mid-March has no major IMO showers in our calendar
        showers = get_active_showers(date(2024, 3, 15))
        assert showers == []

    def test_geminids_active_in_december(self):
        showers = get_active_showers(date(2024, 12, 14))
        names = [s.name for s in showers]
        assert "Geminids" in names


# ---------------------------------------------------------------------------
# get_upcoming_showers
# ---------------------------------------------------------------------------

class TestGetUpcomingShowers:
    def test_perseids_upcoming_before_peak(self):
        # 5 days before Perseid peak
        showers = get_upcoming_showers(date(2024, 8, 7), within_days=7)
        names = [s.name for s in showers]
        assert "Perseids" in names

    def test_perseids_not_upcoming_8_days_before(self):
        showers = get_upcoming_showers(date(2024, 8, 4), within_days=7)
        names = [s.name for s in showers]
        assert "Perseids" not in names

    def test_no_upcoming_far_from_any_peak(self):
        # Pick a date with no showers peaking within 7 days
        # March 15 – nearest shower peak would be April 22 (Lyrids, 38 days away)
        showers = get_upcoming_showers(date(2024, 3, 15), within_days=7)
        assert showers == []
