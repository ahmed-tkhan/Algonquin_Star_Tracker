"""
Tests for stargazing_service.weather

All HTTP calls are mocked so tests run offline.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
import requests

from stargazing_service import config
from stargazing_service.weather import (
    _average,
    evaluate_tonight,
    fetch_hourly_forecast,
)


# ---------------------------------------------------------------------------
# _average helper
# ---------------------------------------------------------------------------

class TestAverage:
    def test_basic(self):
        assert _average([10.0, 20.0, 30.0]) == pytest.approx(20.0)

    def test_empty(self):
        assert _average([]) is None

    def test_all_none(self):
        assert _average([None, None]) is None

    def test_mixed_none(self):
        assert _average([None, 10.0, None, 20.0]) == pytest.approx(15.0)


# ---------------------------------------------------------------------------
# fetch_hourly_forecast – mocked HTTP
# ---------------------------------------------------------------------------

class TestFetchHourlyForecast:
    def _mock_response(self, json_data: dict, status_code: int = 200) -> MagicMock:
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data
        resp.raise_for_status.return_value = None
        return resp

    def test_returns_json(self):
        mock_session = MagicMock()
        mock_session.get.return_value = self._mock_response({"hourly": {}})
        result = fetch_hourly_forecast(session=mock_session)
        assert result == {"hourly": {}}

    def test_passes_correct_params(self):
        mock_session = MagicMock()
        mock_session.get.return_value = self._mock_response({})
        fetch_hourly_forecast(latitude=45.5, longitude=-78.3, session=mock_session)
        _, kwargs = mock_session.get.call_args
        params = kwargs["params"]
        assert params["latitude"] == 45.5
        assert params["longitude"] == -78.3
        assert "cloud_cover" in params["hourly"]

    def test_raises_on_http_error(self):
        mock_session = MagicMock()
        mock_session.get.return_value.raise_for_status.side_effect = (
            requests.HTTPError("500")
        )
        with pytest.raises(requests.HTTPError):
            fetch_hourly_forecast(session=mock_session)


# ---------------------------------------------------------------------------
# evaluate_tonight
# ---------------------------------------------------------------------------

def _make_forecast(
    date_str: str = "2024-08-12",
    hours: list[int] | None = None,
    cloud: float = 10.0,
    precip: float = 5.0,
    vis: float = 20000.0,
) -> dict:
    """Build a minimal forecast dict for a single date."""
    if hours is None:
        hours = [20, 21, 22, 23]
    times = [f"{date_str}T{h:02d}:00" for h in hours]
    clouds = [cloud] * len(times)
    precips = [precip] * len(times)
    viss = [vis] * len(times)
    return {
        "hourly": {
            "time": times,
            "cloud_cover": clouds,
            "precipitation_probability": precips,
            "visibility": viss,
        }
    }


class TestEvaluateTonight:
    def test_clear_sky(self):
        forecast = _make_forecast(cloud=10.0, precip=5.0, vis=25000.0)
        result = evaluate_tonight(forecast, check_date=date(2024, 8, 12))
        assert result["is_clear"] is True
        assert "clear" in result["reason"].lower()

    def test_cloudy_night(self):
        forecast = _make_forecast(cloud=80.0, precip=5.0, vis=25000.0)
        result = evaluate_tonight(forecast, check_date=date(2024, 8, 12))
        assert result["is_clear"] is False
        assert "cloud" in result["reason"].lower()

    def test_high_precipitation(self):
        forecast = _make_forecast(cloud=10.0, precip=70.0, vis=25000.0)
        result = evaluate_tonight(forecast, check_date=date(2024, 8, 12))
        assert result["is_clear"] is False
        assert "precipitation" in result["reason"].lower()

    def test_low_visibility(self):
        forecast = _make_forecast(cloud=10.0, precip=5.0, vis=500.0)
        result = evaluate_tonight(forecast, check_date=date(2024, 8, 12))
        assert result["is_clear"] is False
        assert "visibility" in result["reason"].lower()

    def test_no_data_for_date(self):
        # Forecast is for a different date
        forecast = _make_forecast(date_str="2024-09-01")
        result = evaluate_tonight(forecast, check_date=date(2024, 8, 12))
        assert result["is_clear"] is False
        assert "No forecast data" in result["reason"]

    def test_returns_averages(self):
        forecast = _make_forecast(cloud=20.0, precip=10.0, vis=18000.0)
        result = evaluate_tonight(forecast, check_date=date(2024, 8, 12))
        assert result["cloud_cover"] == pytest.approx(20.0)
        assert result["precip_prob"] == pytest.approx(10.0)
        assert result["visibility"] == pytest.approx(18000.0)
