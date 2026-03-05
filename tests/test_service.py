"""
Tests for stargazing_service.service (run_check integration)

HTTP calls are mocked so tests remain offline.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import patch, MagicMock

import pytest

from stargazing_service.service import run_check


def _good_weather_result() -> dict:
    return {
        "is_clear": True,
        "cloud_cover": 10.0,
        "precip_prob": 5.0,
        "visibility": 20000.0,
        "reason": "Skies look clear – great night for stargazing!",
    }


def _bad_weather_result() -> dict:
    return {
        "is_clear": False,
        "cloud_cover": 90.0,
        "precip_prob": 80.0,
        "visibility": 1000.0,
        "reason": "Not ideal: cloud cover 90% > threshold 30%.",
    }


class TestRunCheck:
    @patch("stargazing_service.service.fetch_hourly_forecast")
    @patch("stargazing_service.service.evaluate_tonight")
    def test_good_night_clear_skies(self, mock_eval, mock_fetch):
        mock_fetch.return_value = {}
        mock_eval.return_value = _good_weather_result()

        result = run_check(check_date=date(2024, 8, 12))

        assert result["is_good_night"] is True
        assert result["weather"]["is_clear"] is True
        assert "report" in result

    @patch("stargazing_service.service.fetch_hourly_forecast")
    @patch("stargazing_service.service.evaluate_tonight")
    def test_poor_night_bad_weather_no_shower(self, mock_eval, mock_fetch):
        mock_fetch.return_value = {}
        mock_eval.return_value = _bad_weather_result()

        # Use mid-March: no active showers
        result = run_check(check_date=date(2024, 3, 15))

        assert result["is_good_night"] is False
        assert result["active_showers"] == []

    @patch("stargazing_service.service.fetch_hourly_forecast")
    @patch("stargazing_service.service.evaluate_tonight")
    def test_good_night_due_to_shower(self, mock_eval, mock_fetch):
        """Even with bad weather, is_good_night should be True if a shower is active."""
        mock_fetch.return_value = {}
        mock_eval.return_value = _bad_weather_result()

        # August 12 = Perseids peak
        result = run_check(check_date=date(2024, 8, 12))

        assert result["is_good_night"] is True
        assert any(s.name == "Perseids" for s in result["active_showers"])

    @patch("stargazing_service.service.fetch_hourly_forecast",
           side_effect=Exception("network error"))
    def test_weather_api_failure_graceful(self, mock_fetch):
        """Service should degrade gracefully if the weather API fails."""
        result = run_check(check_date=date(2024, 3, 15))
        assert "report" in result
        assert result["weather"]["is_clear"] is False

    @patch("stargazing_service.service.fetch_hourly_forecast")
    @patch("stargazing_service.service.evaluate_tonight")
    def test_upcoming_showers_excluded_from_active(self, mock_eval, mock_fetch):
        """Upcoming showers that are also active should not appear in upcoming list."""
        mock_fetch.return_value = {}
        mock_eval.return_value = _good_weather_result()

        # August 12: Perseids is active AND has its peak on this day → days_to_peak=0
        result = run_check(check_date=date(2024, 8, 12))

        active_names = {s.name for s in result["active_showers"]}
        upcoming_names = {s.name for s in result["upcoming_showers"]}
        # No name should appear in both lists
        assert active_names.isdisjoint(upcoming_names)
