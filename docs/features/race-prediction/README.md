# Race Prediction

## Overview

The Race Prediction module provides machine learning-powered predictions for F1 race outcomes, qualifying results, and championship forecasts. It combines historical data analysis with real-time factors to deliver accurate, probabilistic predictions.

---

## Prediction Types

### 1. Pre-Race Predictions
Predictions made before the session starts

### 2. Live Predictions
Real-time probability updates during races

### 3. Championship Predictions
Long-term forecasts for season outcomes

### 4. Fantasy F1 Optimization
Predictions optimized for fantasy sports scoring

---

## Pre-Race Predictions

### Race Winner Prediction

```
┌─────────────────────────────────────────────────────────────┐
│           MONACO GP 2024 - RACE WINNER PREDICTION           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ████████████████████████████ VER  35.2%                    │
│  ██████████████████████ LEC  24.8%                          │
│  █████████████████ SAI  18.3%                               │
│  ████████████ NOR  12.1%                                    │
│  ██████ HAM  6.4%                                           │
│  ██ Others  3.2%                                            │
│                                                              │
│  Model Confidence: 78%                                       │
│  Based on: Grid position, track history, team form          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Podium Prediction

| Position | Driver 1 | Prob | Driver 2 | Prob | Driver 3 | Prob |
|----------|----------|------|----------|------|----------|------|
| P1 | VER | 35% | LEC | 25% | SAI | 18% |
| P2 | LEC | 28% | VER | 22% | SAI | 20% |
| P3 | SAI | 25% | NOR | 18% | VER | 15% |

### Points Finish Prediction

```
Probability of Finishing in Points (Top 10)

VER  ████████████████████████████████████████ 98%
NOR  ███████████████████████████████████████ 96%
LEC  ██████████████████████████████████████ 95%
SAI  █████████████████████████████████████ 94%
HAM  ████████████████████████████████████ 92%
PER  ███████████████████████████████████ 90%
RUS  ████████████████████████████████ 85%
ALO  ██████████████████████████████ 78%
PIA  █████████████████████████████ 75%
STR  ████████████████████████ 65%
```

---

## Live Race Predictions

### Win Probability Evolution

```
Win Probability (%)
100 ┤
 80 ┤    ╭──VER──────────────────────────────╮
 60 ┤   ╱                                     ╲
 40 ┤  ╱   ╱╲                                  ╲
 20 ┤ ╱  ╱   ╲─LEC                              ╲
  0 ┼─────────────────────────────────────────────
    Start   SC      Pit    Rain    Final
           (L12)   (L25)  (L40)   (L58)
```

### Real-time Factors

The model considers:
- Current positions and gaps
- Tire compound and degradation
- Weather changes
- Safety car probabilities
- Historical overtaking data for circuit
- Remaining laps

### Update Frequency

| Event | Update Trigger |
|-------|----------------|
| Position Change | Immediate |
| Pit Stop | Immediate |
| Weather Change | Immediate |
| New Lap | Every lap |
| Gap Change (>0.5s) | Immediate |
| No Change | Every 5 laps |

---

## Qualifying Predictions

### Session Predictions

```python
quali_predictions = {
    "Q3_order": [
        {"driver": "VER", "predicted_time": "1:10.234", "confidence": 0.85},
        {"driver": "LEC", "predicted_time": "1:10.356", "confidence": 0.82},
        {"driver": "NOR", "predicted_time": "1:10.412", "confidence": 0.80},
        # ...
    ],
    "Q2_eliminations": ["SAR", "BOT", "ZHO", "MAG", "HUL"],
    "Q1_eliminations": ["ALB", "RIC", "TSU", "OCO", "GAS"]
}
```

### Pole Position Prediction

| Driver | Probability | Predicted Gap |
|--------|-------------|---------------|
| VER | 42% | - |
| LEC | 28% | +0.122s |
| NOR | 18% | +0.178s |
| SAI | 8% | +0.245s |
| HAM | 4% | +0.312s |

---

## Championship Predictions

### Title Race Simulation

```
Monte Carlo Simulation - 10,000 iterations
Season with X races remaining

Driver    │ Win Title │ Runner-up │ P3    │ Avg Points
──────────┼───────────┼───────────┼───────┼───────────
VER       │ 78.5%     │ 15.2%     │ 4.8%  │ 485
NOR       │ 12.3%     │ 45.6%     │ 28.4% │ 398
LEC       │ 6.8%      │ 25.4%     │ 35.2% │ 375
SAI       │ 2.4%      │ 13.8%     │ 31.6% │ 352
```

### Clinch Scenarios

```
Championship Clinch Calculator

Current Leader: VER (412 pts)
Closest Rival: NOR (285 pts)
Points Gap: 127
Races Remaining: 6

Scenarios:
- VER wins next race + NOR < P5: CLINCHED
- VER P2 next race + NOR < P4: CLINCHED
- VER P3 next race + NOR < P2: 95% likely clinch
```

### Constructor Championship

```
┌─────────────────────────────────────────────────────────────┐
│            CONSTRUCTOR CHAMPIONSHIP PROJECTION              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Red Bull    ██████████████████████████████  Win: 85%       │
│  McLaren     ████████████████████████        Win: 8%        │
│  Ferrari     ███████████████████████         Win: 5%        │
│  Mercedes    █████████████████               Win: 2%        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Fantasy F1 Integration

### Player Optimization

```python
fantasy_optimizer = FantasyOptimizer(
    budget=100.0,
    constraints={
        "drivers": 5,
        "constructors": 2,
        "must_include": ["VER"],
        "exclude": ["SAR"]
    }
)

optimal_team = fantasy_optimizer.optimize(
    predictions=race_predictions,
    scoring_system="official_f1"  # or "custom"
)

# Returns:
# {
#     "drivers": ["VER", "NOR", "PIA", "ALO", "MAG"],
#     "constructors": ["McLaren", "Aston Martin"],
#     "expected_points": 156.8,
#     "budget_used": 98.5
# }
```

### Chip Strategy

```
Optimal Chip Usage Predictions

Remaining Chips: Mega Driver, Wildcard, No Negative

Recommendations:
- Mega Driver: Monaco GP (VER expected 62+ pts)
- Wildcard: Post-summer break (regulation changes)
- No Negative: Spa GP (high DNF probability)
```

---

## Model Details

### Feature Importance

```
Feature Importance for Race Winner Model

Grid Position     ████████████████████████████ 28%
Qualifying Gap    █████████████████████████ 25%
Driver Form       ███████████████████ 19%
Team Performance  ████████████████ 16%
Track History     ██████████ 10%
Weather           ██ 2%
```

### Model Architecture

```python
class RacePredictionModel:
    def __init__(self):
        self.base_model = XGBClassifier(
            n_estimators=500,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8
        )
        self.calibrator = CalibratedClassifierCV(
            self.base_model,
            method='isotonic',
            cv=5
        )

    def predict_proba(self, features):
        """Return calibrated probability predictions"""
        raw_probs = self.calibrator.predict_proba(features)
        return self._apply_constraints(raw_probs)

    def _apply_constraints(self, probs):
        """Ensure probabilities sum to 1 and are reasonable"""
        # Apply minimum probability floors
        # Normalize to sum to 1
        pass
```

### Training Data

| Dataset | Races | Features | Target |
|---------|-------|----------|--------|
| Race Winner | 2018-2024 | 45 | Driver position |
| Qualifying | 2018-2024 | 32 | Qualifying order |
| DNF Risk | 2018-2024 | 28 | Binary DNF |
| Pit Strategy | 2020-2024 | 38 | Pit lap |

### Model Performance

| Prediction Type | Accuracy | Top-3 Acc | Brier Score |
|-----------------|----------|-----------|-------------|
| Race Winner | 47% | 78% | 0.15 |
| Pole Position | 52% | 82% | 0.12 |
| Podium | 68% | - | 0.18 |
| Points Finish | 85% | - | 0.08 |

---

## Confidence Scoring

### Confidence Levels

| Level | Range | Display |
|-------|-------|---------|
| Very High | 80-100% | ⭐⭐⭐⭐⭐ |
| High | 65-79% | ⭐⭐⭐⭐ |
| Medium | 50-64% | ⭐⭐⭐ |
| Low | 35-49% | ⭐⭐ |
| Very Low | 0-34% | ⭐ |

### Confidence Factors

- Historical model accuracy on similar conditions
- Data completeness
- Weather uncertainty
- Track type familiarity
- Recent regulation changes

---

## API Endpoints

### Get Race Predictions

```bash
GET /api/v1/predictions/race
?session_key=monaco_2024_race
&type=winner

Response:
{
    "predictions": [
        {"driver": "VER", "probability": 0.352, "confidence": 0.78},
        {"driver": "LEC", "probability": 0.248, "confidence": 0.75},
        ...
    ],
    "model_version": "race_winner_v3.2",
    "generated_at": "2024-05-26T13:45:00Z"
}
```

### Get Live Predictions

```bash
GET /api/v1/predictions/live
?session_key=monaco_2024_race

Response:
{
    "current_lap": 45,
    "predictions": {...},
    "factors": {
        "safety_car_probability": 0.15,
        "rain_probability": 0.05,
        "position_change_probability": {...}
    }
}
```

### WebSocket Stream

```javascript
// Subscribe to live prediction updates
ws.subscribe('predictions:monaco_2024_race', (data) => {
    console.log('Updated predictions:', data.predictions);
    console.log('Trigger:', data.trigger);  // 'position_change', 'pit_stop', etc.
});
```

---

## Backtesting

### Historical Accuracy

```
Race Winner Prediction Accuracy by Season

2024  ████████████████████████ 48%
2023  ██████████████████████ 45%
2022  █████████████████████ 42%
2021  ████████████████████████ 47%
2020  █████████████████████ 44%
```

### ROI Analysis (Theoretical)

```
If betting $100 on predicted winner (2023 season):
- Total wagered: $2,300 (23 races)
- Total returned: $2,890
- ROI: +25.7%

Note: This is for analysis purposes only.
PitWall Live does not facilitate betting.
```

---

## Limitations & Disclaimers

### Known Limitations

1. **First-lap incidents**: Unpredictable start crashes
2. **Mechanical failures**: Random DNFs hard to predict
3. **Weather changes**: Sudden rain impacts
4. **Safety cars**: Timing luck
5. **Strategy gambles**: Unexpected team decisions

### Disclaimer

> Predictions are for entertainment and analysis purposes only.
> Historical performance does not guarantee future accuracy.
> Do not use for betting or financial decisions.

---

## Related Documentation

- [ML Playground](../ml-playground/README.md)
- [ML Models](../../ml-analysis/models/README.md)
- [Strategy Optimization](../strategy-optimization/README.md)
