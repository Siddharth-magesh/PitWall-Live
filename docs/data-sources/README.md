# Data Sources

## Overview

PitWall Live aggregates data from multiple F1 sources to provide comprehensive coverage of both real-time and historical Formula 1 data. This document catalogs available data sources, their capabilities, limitations, and integration strategies.

---

## Data Source Landscape

### Quick Comparison

| Source | Type | Coverage | Latency | Cost | API Key |
|--------|------|----------|---------|------|---------|
| OpenF1 | Real-time + Historical | 2023+ | ~3s | Free | No |
| FastF1 | Historical + Telemetry | 2018+ | N/A | Free | No |
| LiveF1 | Real-time Streaming | Current | <1s | Free | No |
| Jolpica-F1 | Historical | 1950+ | N/A | Free | No |
| F1 Official | Real-time | Current | Real-time | Subscription | Yes |

---

## Primary Data Sources

### 1. OpenF1 API

**Website**: https://openf1.org
**GitHub**: https://github.com/br-g/openf1

#### Overview
OpenF1 is an open-source Formula 1 API providing real-time access to live telemetry, lap times, weather, and race control data. It's the most accessible real-time data source available.

#### Data Available
- **Car Data**: Speed, throttle, brake, RPM, gear (3.7 Hz sampling)
- **Lap Times**: Sector times, mini-sectors, speed traps
- **Position Data**: Driver positions on track
- **Weather**: Temperature, humidity, wind, rain
- **Race Control**: Flags, messages, incidents
- **Session Info**: Status, remaining time, track status

#### API Examples
```bash
# Get current driver positions
GET https://api.openf1.org/v1/position?session_key=latest

# Get car telemetry for driver 1 (Verstappen)
GET https://api.openf1.org/v1/car_data?driver_number=1&session_key=latest

# Get lap times
GET https://api.openf1.org/v1/laps?session_key=latest&driver_number=44
```

#### Rate Limits
- Free tier: 3 requests/second, 30 requests/minute
- Sufficient for most applications

#### Integration Notes
- Data typically available ~3 seconds after live events
- Faster than most TV broadcasts
- No authentication required
- Historical data from 2023 onwards

---

### 2. FastF1 (Python Library)

**Website**: https://docs.fastf1.dev
**GitHub**: https://github.com/theOehrly/Fast-F1
**PyPI**: https://pypi.org/project/fastf1/

#### Overview
FastF1 is the de-facto Python library for F1 data analysis, providing access to timing data, telemetry, tire information, and weather data. Essential for historical analysis and ML training.

#### Data Available
- **Session Results**: Final classifications, points
- **Lap Data**: Lap times, sectors, compounds, stint info
- **Telemetry**: Speed, throttle, brake, gear, RPM, DRS
- **Car Position**: X, Y, Z coordinates on track
- **Tire Data**: Compound, age, stint information
- **Weather**: Track/air temperature, humidity, pressure

#### Code Example
```python
import fastf1

# Enable caching for faster subsequent loads
fastf1.Cache.enable_cache('/path/to/cache')

# Load a session
session = fastf1.get_session(2024, 'Monza', 'R')
session.load()

# Get lap data
laps = session.laps
driver_laps = laps.pick_driver('VER')

# Get telemetry for fastest lap
fastest = driver_laps.pick_fastest()
telemetry = fastest.get_telemetry()
```

#### Key Features
- Built-in caching system
- Pandas DataFrame integration
- Matplotlib plotting helpers
- Ergast API integration (now Jolpica-F1)
- Session event data

#### Limitations
- Not suitable for real-time use
- Data available after session completion
- Some telemetry gaps during certain events

---

### 3. LiveF1 (Python Library)

**Website**: https://pypi.org/project/livef1/
**GitHub**: https://github.com/GoktugOcal/LiveF1

#### Overview
LiveF1 is a Python toolkit for accessing real-time and historical F1 data, designed for building live applications.

#### Data Available
- **Real-time Streaming**: Car data, positions, timing
- **Historical Archives**: Past sessions data
- **Processed Tables**: Laps, car telemetry, refined data

#### Architecture
Uses a medallion architecture:
- **Bronze**: Raw data ingestion
- **Silver**: Cleaned and validated data
- **Gold**: Analysis-ready aggregated data

#### Code Example
```python
from livef1 import RealF1Client

# Create real-time client
client = RealF1Client()

# Subscribe to topics
client.subscribe("CarData.z")
client.subscribe("Position.z")

# Define callback
def on_data(topic, data):
    print(f"Received {topic}: {data}")

client.on_message = on_data
client.start()
```

#### Use Cases
- Real-time dashboards
- Live commentary generation
- Strategy monitoring
- Position tracking

---

### 4. Jolpica-F1 (Ergast Replacement)

**GitHub**: https://github.com/jolpica/jolpica-f1

#### Overview
Jolpica-F1 is the community-maintained replacement for the Ergast API, which shut down at the end of 2024. It provides comprehensive historical F1 data from 1950 to present.

#### Data Available
- **Drivers**: Career stats, results, standings
- **Constructors**: Team history, results
- **Circuits**: Track information, records
- **Races**: Results, qualifying, sprint
- **Championships**: Standings, points
- **Lap Times**: Individual lap data
- **Pit Stops**: Stop times, durations

#### API Compatibility
Backwards compatible with Ergast endpoints:
```bash
# Get 2024 driver standings
GET https://api.jolpica.com/ergast/f1/2024/driverStandings

# Get race results
GET https://api.jolpica.com/ergast/f1/2024/1/results

# Get qualifying results
GET https://api.jolpica.com/ergast/f1/2024/5/qualifying
```

#### Migration from Ergast
FastF1 and other libraries are transitioning to Jolpica-F1 as the historical data source.

---

## Secondary Data Sources

### 5. F1 Official Live Timing

**Note**: Requires subscription; data access recently restricted.

#### Data Available
- Real-time timing and scoring
- Sector times
- Gap calculations
- Tire compound information
- Track status

#### Limitations
- Paid subscription required
- API access restricted
- Terms of service considerations

---

### 6. Weather APIs

For enhanced weather predictions beyond F1 data:

#### OpenWeatherMap
- Historical weather data
- Forecasts for race weekends
- Precipitation probability

#### Weather API Integration
```python
# Example: Enrich F1 data with detailed weather
weather_data = {
    "temperature": 28.5,
    "humidity": 65,
    "wind_speed": 12,
    "wind_direction": "NE",
    "rain_probability": 15,
    "pressure": 1013
}
```

---

## Data Integration Strategy

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Ingestion Layer                     │
├─────────────┬──────────────┬──────────────┬────────────────┤
│   OpenF1    │    LiveF1    │   FastF1     │   Jolpica-F1   │
│  (Real-time)│  (Streaming) │ (Historical) │   (Archive)    │
└──────┬──────┴──────┬───────┴──────┬───────┴───────┬────────┘
       │             │              │               │
       ▼             ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Unified Data Layer                        │
│  - Schema normalization                                      │
│  - Deduplication                                             │
│  - Quality validation                                        │
│  - Feature computation                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Storage                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  TimeSeries  │  │   Feature    │  │   Cache      │      │
│  │   Database   │  │    Store     │  │   Layer      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

#### Real-time Flow (During Sessions)
1. LiveF1/OpenF1 streams data
2. Ingest service normalizes and validates
3. Real-time processing for commentary
4. Storage for later analysis
5. WebSocket push to clients

#### Historical Flow (Analysis/Training)
1. FastF1 loads session data
2. Enrichment with Jolpica-F1 metadata
3. Feature extraction pipeline
4. Storage in feature store
5. Available for ML training

---

## Data Quality Considerations

### Known Issues

| Source | Issue | Mitigation |
|--------|-------|------------|
| OpenF1 | Occasional gaps in telemetry | Interpolation, gap detection |
| FastF1 | Delayed availability | Queue-based loading |
| LiveF1 | Connection drops | Automatic reconnection |
| Jolpica | Limited 2025 data initially | Fallback to FastF1 |

### Data Validation Rules

```python
validation_rules = {
    "lap_time": {
        "min": 60.0,  # Minimum realistic lap time
        "max": 180.0,  # Maximum reasonable lap time
        "required": True
    },
    "speed": {
        "min": 0,
        "max": 380,  # Max F1 speed km/h
        "required": False
    },
    "throttle": {
        "min": 0,
        "max": 100,
        "required": False
    }
}
```

---

## Caching Strategy

### Multi-tier Cache

1. **L1 - In-Memory**: Hot data (current session)
2. **L2 - Redis**: Recent sessions, computed features
3. **L3 - Disk**: FastF1 cache, historical data
4. **L4 - Object Storage**: Raw data archives

### Cache Invalidation

- Session-based invalidation
- TTL-based for real-time data
- Manual invalidation for corrections

---

## Future Data Sources

### Under Evaluation

1. **F1 TV Telemetry**: If API access becomes available
2. **Social Media APIs**: Driver/team social feeds
3. **News APIs**: F1 news aggregation
4. **Betting APIs**: Odds data for predictions

### Community Data

- User-contributed annotations
- Lap time corrections
- Incident classifications

---

## Legal Considerations

### Fair Use Guidelines

- Data used for analysis, education, and fan engagement
- No redistribution of raw official data
- Attribution where required
- Non-commercial core features

### API Terms of Service

| Source | Commercial Use | Attribution | Rate Limits |
|--------|---------------|-------------|-------------|
| OpenF1 | Allowed | Appreciated | 3/s, 30/min |
| FastF1 | Library is MIT | Required | N/A |
| LiveF1 | Check license | Required | Varies |
| Jolpica | Allowed | Required | Fair use |

---

## Related Documentation

- [Tech Stack](../tech-stack/README.md)
- [Architecture](../architecture/README.md)
- [ML Analysis - Datasets](../ml-analysis/datasets/README.md)
