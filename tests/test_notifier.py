"""
Tests for stargazing_service.notifier
"""

from datetime import date

from stargazing_service.meteor_showers import MeteorShower
from stargazing_service.notifier import build_report


def _make_weather(is_clear: bool = True,
                  cloud: float = 10.0,
                  precip: float = 5.0,
                  vis: float = 20000.0,
                  reason: str = "Skies look clear – great night for stargazing!") -> dict:
    return {
        "is_clear": is_clear,
        "cloud_cover": cloud,
        "precip_prob": precip,
        "visibility": vis,
        "reason": reason,
    }


def _make_shower(name: str = "Perseids") -> MeteorShower:
    return MeteorShower(
        name=name,
        peak_month=8, peak_day=12,
        active_start_month=8, active_start_day=1,
        active_end_month=8, active_end_day=24,
        zhr=100,
        radiant_constellation="Perseus",
    )


CHECK_DATE = date(2024, 8, 12)


class TestBuildReport:
    def test_contains_location(self):
        report = build_report(
            weather_result=_make_weather(),
            active_showers=[],
            upcoming_showers=[],
            check_date=CHECK_DATE,
            location_name="Algonquin Provincial Park",
        )
        assert "Algonquin Provincial Park" in report

    def test_contains_date(self):
        report = build_report(
            weather_result=_make_weather(),
            active_showers=[],
            upcoming_showers=[],
            check_date=CHECK_DATE,
            location_name="Algonquin Provincial Park",
        )
        assert "August 12 2024" in report

    def test_excellent_verdict_clear_with_shower(self):
        report = build_report(
            weather_result=_make_weather(is_clear=True),
            active_showers=[_make_shower()],
            upcoming_showers=[],
            check_date=CHECK_DATE,
            location_name="Park",
        )
        assert "EXCELLENT" in report

    def test_good_verdict_clear_no_shower(self):
        report = build_report(
            weather_result=_make_weather(is_clear=True),
            active_showers=[],
            upcoming_showers=[],
            check_date=CHECK_DATE,
            location_name="Park",
        )
        assert "GOOD" in report

    def test_poor_verdict_cloudy_no_shower(self):
        report = build_report(
            weather_result=_make_weather(
                is_clear=False,
                reason="Not ideal: cloud cover 80% > threshold 30%."
            ),
            active_showers=[],
            upcoming_showers=[],
            check_date=CHECK_DATE,
            location_name="Park",
        )
        assert "POOR" in report

    def test_mixed_verdict_cloudy_with_shower(self):
        report = build_report(
            weather_result=_make_weather(
                is_clear=False,
                reason="Not ideal: cloud cover 80% > threshold 30%."
            ),
            active_showers=[_make_shower()],
            upcoming_showers=[],
            check_date=CHECK_DATE,
            location_name="Park",
        )
        assert "MIXED" in report

    def test_shower_name_in_report(self):
        report = build_report(
            weather_result=_make_weather(),
            active_showers=[_make_shower("Geminids")],
            upcoming_showers=[],
            check_date=CHECK_DATE,
            location_name="Park",
        )
        assert "Geminids" in report

    def test_upcoming_shower_in_report(self):
        upcoming = MeteorShower(
            name="Orionids",
            peak_month=10, peak_day=21,
            active_start_month=10, active_start_day=2,
            active_end_month=11, active_end_day=7,
            zhr=20,
            radiant_constellation="Orion",
        )
        report = build_report(
            weather_result=_make_weather(),
            active_showers=[],
            upcoming_showers=[upcoming],
            check_date=CHECK_DATE,
            location_name="Park",
        )
        assert "Orionids" in report

    def test_no_shower_message(self):
        report = build_report(
            weather_result=_make_weather(),
            active_showers=[],
            upcoming_showers=[],
            check_date=CHECK_DATE,
            location_name="Park",
        )
        assert "No major meteor showers active tonight" in report
