# Datasets

## Overview

This document catalogs the datasets available for machine learning in PitWall Live, including data sources, schemas, preprocessing pipelines, and access methods.

---

## Dataset Inventory

### Core Datasets

| Dataset | Records | Features | Time Range | Update Frequency |
|---------|---------|----------|------------|------------------|
| Race Results | 15,000+ | 25 | 1950-2024 | Post-race |
| Qualifying Results | 8,000+ | 20 | 1994-2024 | Post-session |
| Lap Times | 500,000+ | 15 | 2018-2024 | Post-session |
| Telemetry | 50M+ | 12 | 2018-2024 | Post-session |
| Pit Stops | 25,000+ | 10 | 2012-2024 | Post-race |
| Weather | 2,000+ | 15 | 2018-2024 | Per-session |

---

## Race Results Dataset

### Schema

```python
RaceResultSchema = {
    # Identifiers
    "race_id": str,           # Unique race identifier
    "season": int,            # Year
    "round": int,             # Race number in season
    "circuit_id": str,        # Circuit identifier

    # Driver info
    "driver_id": str,         # 3-letter code
    "driver_name": str,       # Full name
    "constructor_id": str,    # Team identifier
    "constructor_name": str,  # Team name

    # Grid & Results
    "grid_position": int,     # Starting position
    "finish_position": int,   # Final position (null if DNF)
    "status": str,            # "Finished", "Retired", etc.
    "points": float,          # Points scored

    # Performance
    "laps_completed": int,    # Laps finished
    "race_time": float,       # Total time in seconds (winner)
    "gap_to_leader": float,   # Time gap in seconds
    "fastest_lap": bool,      # Had fastest lap
    "fastest_lap_time": float,# Fastest lap time

    # Metadata
    "date": date,             # Race date
    "created_at": datetime,   # Record creation
}
```

### Sample Data

| season | round | driver_id | grid | finish | points | status |
|--------|-------|-----------|------|--------|--------|--------|
| 2024 | 1 | VER | 1 | 1 | 25 | Finished |
| 2024 | 1 | PER | 5 | 2 | 18 | Finished |
| 2024 | 1 | SAI | 3 | 3 | 15 | Finished |
| 2024 | 1 | LEC | 2 | 4 | 12 | Finished |
| 2024 | 1 | RUS | 4 | 5 | 10 | Finished |

### Access Methods

```python
from pitwall.data import RaceResults

# Load all results
results = RaceResults.load()

# Filter by season
results_2024 = RaceResults.load(seasons=[2024])

# Filter by driver
ver_results = RaceResults.load(drivers=['VER'])

# Get as DataFrame
df = results.to_dataframe()
```

---

## Telemetry Dataset

### Schema

```python
TelemetrySchema = {
    # Identifiers
    "session_key": str,       # Unique session ID
    "driver_id": str,         # Driver code
    "lap_number": int,        # Lap number

    # Position
    "timestamp": float,       # Session timestamp (ms)
    "distance": float,        # Distance from start (m)
    "x": float,               # X coordinate
    "y": float,               # Y coordinate
    "z": float,               # Z coordinate

    # Car data
    "speed": int,             # Speed in km/h
    "throttle": int,          # Throttle % (0-100)
    "brake": int,             # Brake % (0-100)
    "gear": int,              # Current gear (0-8)
    "rpm": int,               # Engine RPM
    "drs": int,               # DRS status (0/1)
}
```

### Data Characteristics

```
Telemetry Data Properties:

Sampling Rate:     3.7 Hz (varies by source)
Points per Lap:    ~300-500 (circuit dependent)
Storage per Race:  ~500 MB (compressed)

Example Distribution:
- Speed: 0-350 km/h
- Throttle: 0-100%
- Brake: 0-100%
- Gear: 0-8
```

### Telemetry Visualization

```
Sample Telemetry Trace - Turn 1

Speed     350│
(km/h)    300│──────╮
          250│      │
          200│      ╰───╮
          150│          │
          100│          ╰──────
           50├──────────────────
              0    200   400   600  Distance (m)

Throttle  100│──────╮     ╭─────
(%)        50│      ╰─────╯
            0├──────────────────

Brake     100│      ╭────╮
(%)        50│     ╱      ╲
            0│────╯        ╰────
```

---

## Lap Times Dataset

### Schema

```python
LapTimeSchema = {
    # Identifiers
    "session_key": str,
    "driver_id": str,
    "lap_number": int,

    # Timing
    "lap_time": float,        # Total lap time (seconds)
    "sector_1": float,        # Sector 1 time
    "sector_2": float,        # Sector 2 time
    "sector_3": float,        # Sector 3 time

    # Tire info
    "compound": str,          # SOFT, MEDIUM, HARD, INTER, WET
    "tire_life": int,         # Laps on current tire
    "fresh_tire": bool,       # New tire this lap

    # Status
    "is_personal_best": bool,
    "is_overall_best": bool,
    "track_status": str,      # Green, Yellow, SC, VSC, Red

    # Pit info
    "pit_in_time": float,     # Time entering pit (null if no pit)
    "pit_out_time": float,    # Time exiting pit
}
```

### Lap Time Distribution

```
LAP TIME DISTRIBUTION - MONACO 2024 RACE

Time (s)    Frequency
75-76  │██ 2%
76-77  │████████ 8%
77-78  │████████████████████████████ 28%
78-79  │██████████████████████████████████████ 38%
79-80  │████████████████████ 20%
80-81  │████ 4%
>81    │░░ Out-laps/In-laps

Median: 78.2s
Mean: 78.5s
Std Dev: 1.2s
```

---

## Weather Dataset

### Schema

```python
WeatherSchema = {
    "session_key": str,
    "timestamp": datetime,

    # Temperature
    "air_temperature": float,     # Celsius
    "track_temperature": float,   # Celsius

    # Conditions
    "humidity": float,            # Percentage
    "pressure": float,            # mBar
    "wind_speed": float,          # km/h
    "wind_direction": int,        # Degrees

    # Precipitation
    "rainfall": bool,             # Is it raining
    "rainfall_intensity": float,  # mm/h if raining

    # Track Status
    "track_status": str,          # Dry, Damp, Wet
}
```

---

## Feature Engineering Datasets

### Pre-computed Feature Store

```python
FeatureStoreSchema = {
    # Driver Features
    "driver_avg_finish_last_5": float,
    "driver_avg_quali_last_5": float,
    "driver_wins_at_circuit": int,
    "driver_podiums_at_circuit": int,
    "driver_dnf_rate": float,
    "driver_positions_gained_avg": float,

    # Team Features
    "team_constructor_position": int,
    "team_avg_pit_time": float,
    "team_reliability_rate": float,

    # Circuit Features
    "circuit_overtaking_score": float,
    "circuit_power_sensitivity": float,
    "circuit_downforce_sensitivity": float,
    "circuit_safety_car_probability": float,

    # Session Features
    "quali_gap_to_pole": float,
    "grid_position": int,
    "fp_pace_ranking": int,
}
```

### Feature Computation Pipeline

```python
from pitwall.features import FeaturePipeline

pipeline = FeaturePipeline()

# Register feature computations
@pipeline.register("driver_form")
def compute_driver_form(driver_id, cutoff_date):
    """Compute rolling driver form metrics"""
    results = RaceResults.load(
        drivers=[driver_id],
        before=cutoff_date,
        limit=5
    )
    return {
        "avg_finish": results.finish_position.mean(),
        "avg_quali": results.grid_position.mean(),
        "wins": (results.finish_position == 1).sum(),
        "podiums": (results.finish_position <= 3).sum(),
    }

@pipeline.register("circuit_stats")
def compute_circuit_stats(circuit_id):
    """Compute circuit-specific statistics"""
    races = RaceResults.load(circuits=[circuit_id])
    return {
        "overtakes_avg": races.position_changes.mean(),
        "sc_probability": races.safety_car.mean(),
        "pole_win_rate": (races.grid_position == 1 & races.finish_position == 1).mean(),
    }

# Run pipeline
features = pipeline.compute_all(session_key="monaco_2024_race")
```

---

## Data Quality

### Quality Metrics

| Dataset | Completeness | Accuracy | Consistency |
|---------|--------------|----------|-------------|
| Race Results | 99.8% | 99.9% | 100% |
| Qualifying | 99.5% | 99.8% | 99.9% |
| Lap Times | 98.2% | 99.5% | 99.7% |
| Telemetry | 95.0% | 98.0% | 97.5% |
| Weather | 97.0% | 98.5% | 99.0% |

### Known Issues

```
DATA QUALITY ISSUES LOG

1. Telemetry Gaps
   - Issue: Missing data during certain laps
   - Affected: ~5% of telemetry records
   - Mitigation: Interpolation for small gaps

2. Historical Lap Times
   - Issue: Pre-2018 lap times less granular
   - Affected: 2014-2017 seasons
   - Mitigation: Use aggregate metrics only

3. Weather Data
   - Issue: Some sessions missing weather
   - Affected: ~3% of sessions
   - Mitigation: Impute from location/date

4. Position Data
   - Issue: Recent restrictions on car position data
   - Affected: 2024+ sessions
   - Mitigation: Alternative sources (OpenF1)
```

---

## Data Loading Examples

### Load Race Data for Training

```python
from pitwall.data import DataLoader

loader = DataLoader()

# Load training data
train_data = loader.load_training_data(
    seasons=[2020, 2021, 2022, 2023],
    target="race_winner",
    features=["driver", "team", "circuit", "session"]
)

# Split data
X_train, X_test, y_train, y_test = train_data.split(
    test_size=0.2,
    stratify_by="season"  # Ensure each season represented
)

print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")
print(f"Features: {X_train.shape[1]}")
```

### Load Real-time Data

```python
from pitwall.data import LiveDataLoader

live = LiveDataLoader()

# Get current session data
timing = await live.get_timing(session_key="current")
positions = await live.get_positions(session_key="current")
telemetry = await live.get_telemetry(
    session_key="current",
    drivers=["VER", "NOR", "HAM"]
)
```

---

## Data Versioning

### DVC Configuration

```yaml
# dvc.yaml
stages:
  fetch_data:
    cmd: python scripts/fetch_data.py
    deps:
      - scripts/fetch_data.py
    outs:
      - data/raw/

  preprocess:
    cmd: python scripts/preprocess.py
    deps:
      - scripts/preprocess.py
      - data/raw/
    outs:
      - data/processed/

  compute_features:
    cmd: python scripts/compute_features.py
    deps:
      - scripts/compute_features.py
      - data/processed/
    outs:
      - data/features/
```

### Version History

| Version | Date | Changes | Size |
|---------|------|---------|------|
| v1.0 | 2024-01 | Initial dataset | 2.1 GB |
| v1.1 | 2024-02 | Added 2024 pre-season | 2.3 GB |
| v1.2 | 2024-03 | Added Bahrain 2024 | 2.4 GB |
| v1.3 | 2024-04 | Added Saudi, Australia | 2.6 GB |

---

## Related Documentation

- [Models](../models/README.md)
- [Feature Engineering](feature-engineering.md)
- [Data Sources](../../data-sources/README.md)
