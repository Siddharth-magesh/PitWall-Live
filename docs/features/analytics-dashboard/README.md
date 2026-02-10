# Analytics Dashboard

## Overview

The Analytics Dashboard provides comprehensive visualization and analysis tools for F1 telemetry, timing data, and race statistics. It serves as the primary interface for exploring F1 data, comparing driver performances, and understanding race dynamics.

---

## Dashboard Modules

### 1. Live Timing View
Real-time race timing and position tracking

### 2. Telemetry Comparison
Head-to-head driver telemetry analysis

### 3. Strategy Tracker
Pit stop timing and tire strategy visualization

### 4. Historical Analysis
Multi-season trend analysis and comparisons

### 5. Championship Tracker
Points, standings, and projections

---

## Live Timing View

### Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LIVE TIMING - LAP 45/58                          │
├─────────────────────────────────────────────────────────────────────────┤
│ POS │ DRIVER      │ TEAM        │ GAP      │ INT    │ S1    │ S2    │ S3│
├─────┼─────────────┼─────────────┼──────────┼────────┼───────┼───────┼───┤
│  1  │ VER         │ Red Bull    │ LEADER   │  -     │ 28.4  │ 35.2  │ 17.8│
│  2  │ NOR         │ McLaren     │ +3.245   │ +3.245 │ 28.5  │ 35.4  │ 17.9│
│  3  │ HAM         │ Mercedes    │ +8.892   │ +5.647 │ 28.6  │ 35.3  │ 18.0│
│  4  │ LEC         │ Ferrari     │ +12.104  │ +3.212 │ 28.7  │ 35.5  │ 18.1│
│  5  │ SAI         │ Ferrari     │ +15.667  │ +3.563 │ 28.8  │ 35.6  │ 18.2│
└─────┴─────────────┴─────────────┴──────────┴────────┴───────┴───────┴───┘

Legend:  🟣 Personal Best  🟢 Session Best  🔴 Slower than previous
         [H] Hard  [M] Medium  [S] Soft
```

### Features
- Real-time position updates
- Gap and interval calculations
- Sector time colors (purple/green/yellow)
- Tire compound and age display
- Pit stop indicator
- DRS status

---

## Telemetry Comparison

### Comparison Types

#### Speed Trace
```
Speed (km/h)
350 ┤
300 ┤    ╱╲    ╱╲           VER ────
250 ┤   ╱  ╲  ╱  ╲          NOR - - -
200 ┤  ╱    ╲╱    ╲
150 ┤ ╱            ╲
100 ┤╱              ╲
 50 ┼────────────────────────────────
    0    1000   2000   3000   4000  Distance (m)
```

#### Throttle/Brake Analysis
```
Throttle %                              Brake %
100 ┤████████░░░░████████░░░░          100 ┤░░░░░░░░████░░░░░░░░████
 50 ┤                                   50 ┤
  0 ┼────────────────────────            0 ┼────────────────────────
```

#### Gear Map
```
Gear
  8 ┤    ████        ████
  7 ┤   █    █      █    █
  6 ┤  █      █    █      █
  5 ┤ █        ████        █
  4 ┤█                      █
  3 ┼────────────────────────
```

### Interactive Controls
- Driver selector (multi-select)
- Lap selector (overlay multiple laps)
- Zoom and pan
- Sync cursors across charts
- Data export (CSV, JSON)

---

## Strategy Tracker

### Race Strategy Timeline

```
LAP  0    10    20    30    40    50    60
     │     │     │     │     │     │     │
VER  ├─────[S]───────────[H]────────────────────┤
     │ Soft (15L)     Hard (43L)
     │
NOR  ├─────[M]─────────[H]──────────[M]────────┤
     │ Medium (12L)  Hard (25L)  Medium (21L)
     │
HAM  ├──────[M]────────────[H]────────[S]──────┤
     │ Medium (18L)      Hard (30L)   Soft (10L)
```

### Pit Stop Analysis

| Driver | Stop 1 | Stop 2 | Stop 3 | Total Time | Net Position |
|--------|--------|--------|--------|------------|--------------|
| VER | 2.3s (L15) | - | - | 2.3s | 0 |
| NOR | 2.5s (L12) | 2.4s (L37) | - | 4.9s | +1 |
| HAM | 2.8s (L18) | 2.6s (L48) | - | 5.4s | -1 |

### Strategy Predictions
- Predicted pit windows
- Undercut/overcut opportunities
- Tire cliff warnings
- Optimal compound suggestions

---

## Historical Analysis

### Multi-Season Comparison

```
Driver Points Progression (2020-2024)
Points
500 ┤                              ★ 2023
400 ┤                        ●━━━━━━━━━━━
300 ┤              ○━━━━━━━━━●    2024 (in progress)
200 ┤      △━━━━━━━○        2022
100 ┤△━━━━△       2021
  0 ┼────────────────────────────────────
    1  3  5  7  9  11 13 15 17 19 21 23  Race
```

### Track Record Evolution

```
Monza Lap Record History
Time
1:20 ┤●
1:21 ┤  ●
1:22 ┤    ●  ●
1:23 ┤          ●  ●
1:24 ┤                ●  ●  ●
     ┼────────────────────────
     2015 2016 2017 2018 2019 2020 2021 2022 2023 2024
```

### Statistical Insights
- Pole-to-win conversion rates
- Average positions gained/lost at start
- DNF patterns
- Teammate head-to-head records

---

## Championship Tracker

### Current Standings

```
┌─────────────────────────────────────────────────────────────┐
│               DRIVER CHAMPIONSHIP - 2024                     │
├─────────────────────────────────────────────────────────────┤
│  1. ████████████████████████████████████ VER  412 pts       │
│  2. ██████████████████████████ NOR  285 pts                 │
│  3. █████████████████████████ LEC  275 pts                  │
│  4. ████████████████████ SAI  240 pts                       │
│  5. ███████████████████ HAM  221 pts                        │
└─────────────────────────────────────────────────────────────┘
```

### Championship Projections
- Points needed to clinch
- Mathematical elimination scenarios
- Historical projection accuracy
- Monte Carlo simulations

---

## Custom Chart Builder

### Available Chart Types

| Chart Type | Use Case | Data Types |
|------------|----------|------------|
| Line | Time series, trends | Numeric |
| Bar | Comparisons | Categorical + Numeric |
| Scatter | Correlations | Numeric x Numeric |
| Heatmap | Multi-dimensional | Numeric matrix |
| Box Plot | Distributions | Numeric groups |
| Track Map | Position data | Coordinates |
| Radar | Multi-metric comparison | Numeric array |

### Builder Interface

```
┌─────────────────────────────────────────────────────────────┐
│                    Custom Chart Builder                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Data Source: [Session Data ▼]                              │
│  Chart Type:  [Scatter Plot ▼]                              │
│                                                              │
│  X-Axis: [Qualifying Position ▼]                            │
│  Y-Axis: [Race Position ▼]                                  │
│  Color:  [Team ▼]                                           │
│  Size:   [None ▼]                                           │
│                                                              │
│  Filters:                                                    │
│  Season: [2023, 2024]                                        │
│  Circuit: [All]                                              │
│                                                              │
│  [Generate Chart] [Save] [Export]                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Visualization Components

### Track Map Widget

```python
# Component configuration
track_map = TrackMapWidget(
    circuit="monza",
    show_sectors=True,
    show_drs_zones=True,
    show_corners=True,
    driver_positions=live_positions
)
```

### Tire Degradation Chart

```
Lap Time (s)
82.5 ┤
82.0 ┤    ●  ●
81.5 ┤  ●      ●  ●
81.0 ┤●              ●  ●
80.5 ┤                      ●  ●     ← Tire cliff
80.0 ┤                            ●●●●
     ┼────────────────────────────────
     0  2  4  6  8  10 12 14 16 18 20  Tire Age (laps)
```

### Gap Evolution

```
Gap to Leader (s)
 0 ┤━━━━━━━━━━━━━━━━━━━━━━━━━━━ VER (Leader)
 5 ┤╲  ╱╲
10 ┤ ╲╱  ╲    ╱╲ ╱╲           NOR
15 ┤       ╲╱    ╲  ╲╱╲
20 ┤                   ╲━━━━━━
   ┼────────────────────────────
   0    10    20    30    40    50  Lap
```

---

## Export & Embedding

### Export Formats
- PNG/SVG for static images
- Interactive HTML
- CSV/JSON for raw data
- Jupyter notebook

### Embed Options

```html
<!-- Embed live timing widget -->
<iframe
  src="https://pitwall.live/embed/timing?session=monaco_2024_race"
  width="800"
  height="600"
  frameborder="0">
</iframe>

<!-- Embed specific chart -->
<script src="https://pitwall.live/embed.js"></script>
<div
  data-pitwall="chart"
  data-type="gap-evolution"
  data-session="monaco_2024_race">
</div>
```

---

## Performance Optimization

### Data Loading
- Lazy loading for historical data
- WebSocket for real-time updates
- Service worker for offline caching
- Virtual scrolling for large tables

### Rendering
- Canvas for high-frequency updates
- SVG for interactive charts
- WebGL for track maps
- Debounced redraws

---

## Accessibility

### Features
- Keyboard navigation
- Screen reader support
- High contrast mode
- Customizable font sizes
- Color blind friendly palettes

---

## Related Documentation

- [Data Sources](../../data-sources/README.md)
- [API Design](../../api-design/README.md)
- [Tech Stack - Frontend](../../tech-stack/README.md)
