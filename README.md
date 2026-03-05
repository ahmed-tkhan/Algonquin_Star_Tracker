# Algonquin Star Tracker

A background service that checks whether tonight is a good night for stargazing at **Algonquin Provincial Park** (Ontario, Canada).

Every evening at the configured time (default **9:00 PM Eastern**) the service automatically:

1. Queries the [Open-Meteo](https://open-meteo.com/) API for tonight's cloud cover, precipitation probability, and visibility at the park.
2. Checks a built-in calendar of major annual meteor showers (Perseids, Geminids, Lyrids, Leonids, …).
3. Prints a human-readable **go / no-go report** with a clear verdict.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run as a background service (daemon mode)

The service blocks until you press **Ctrl-C** or send SIGTERM.

```bash
python main.py
```

The nightly check will fire automatically each evening at **21:00 America/Toronto** (9 PM ET).

### 3. Run a check immediately and exit

```bash
python main.py --once
```

### 4. Start the background service AND run a check right now

```bash
python main.py --now
```

---

## Configuration

All settings can be overridden via environment variables:

| Variable              | Default                      | Description                                |
|-----------------------|------------------------------|--------------------------------------------|
| `AST_LATITUDE`        | `45.5363`                    | Latitude of the observation site           |
| `AST_LONGITUDE`       | `-78.3522`                   | Longitude of the observation site          |
| `AST_LOCATION_NAME`   | `Algonquin Provincial Park`  | Display name used in reports               |
| `AST_TIMEZONE`        | `America/Toronto`            | Timezone for the scheduler and forecasts   |
| `AST_POLL_HOUR`       | `21`                         | Hour (24 h) the nightly check fires        |
| `AST_POLL_MINUTE`     | `0`                          | Minute the nightly check fires             |
| `AST_MAX_CLOUD_COVER` | `30`                         | Max cloud cover % considered "clear"       |
| `AST_MAX_PRECIP_PROB` | `20`                         | Max precipitation probability % accepted  |
| `AST_MIN_VISIBILITY_M`| `15000`                      | Min visibility (metres) considered "good"  |

### Example – change the poll time to 8:30 PM

```bash
AST_POLL_HOUR=20 AST_POLL_MINUTE=30 python main.py
```

---

## Project Structure

```
Algonquin_Star_Tracker/
├── main.py                        # CLI entry point
├── requirements.txt
├── stargazing_service/
│   ├── config.py                  # Configuration (env-var overrideable)
│   ├── weather.py                 # Open-Meteo API client & sky-quality evaluator
│   ├── meteor_showers.py          # Annual meteor shower calendar & helpers
│   ├── notifier.py                # Report formatter & printer
│   ├── service.py                 # Orchestrates weather + meteor checks
│   └── scheduler.py               # APScheduler background daemon
└── tests/
    ├── test_meteor_showers.py
    ├── test_weather.py
    ├── test_notifier.py
    └── test_service.py
```

---

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Sample Output

```
============================================================
  Algonquin Stargazing Report – Friday, August 12 2026
  Location : Algonquin Provincial Park
============================================================

  WEATHER
  -------
  🌟  Skies look clear – great night for stargazing!
       Cloud cover   : 8%
       Precip. prob. : 3%
       Visibility    : 24.0 km

  METEOR SHOWERS
  --------------
  Currently active showers:
    • Perseids           ZHR~100  [★★★★★···]  ← PEAK TONIGHT

  VERDICT
  -------
  🌟 EXCELLENT – Clear skies AND an active meteor shower. Go out!
============================================================
```

---

## Data Sources

- **Weather**: [Open-Meteo](https://open-meteo.com/) – free, no API key required.
- **Meteor showers**: Built-in IMO annual shower calendar (Quadrantids, Lyrids, Eta Aquariids, Delta Aquariids, Perseids, Draconids, Orionids, Leonids, Geminids, Ursids).

