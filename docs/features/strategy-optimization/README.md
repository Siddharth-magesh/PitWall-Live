# Strategy Optimization

## Overview

The Strategy Optimization module provides AI-powered race strategy recommendations, pit stop timing predictions, and real-time tactical insights. It combines machine learning models with simulation to optimize race outcomes.

---

## Core Capabilities

### 1. Pit Stop Optimization
Optimal timing and compound selection

### 2. Tire Strategy Planning
Multi-stop strategy comparison

### 3. Undercut/Overcut Detection
Real-time tactical opportunities

### 4. Weather Strategy
Rain response and intermediate timing

### 5. Safety Car Modeling
SC probability and response strategies

---

## Pit Stop Optimization

### Optimal Window Prediction

```
PIT WINDOW ANALYSIS - VER

Current: Lap 25 | Tire: Medium | Age: 18 laps

Recommended Window: Laps 28-32

Window Analysis:
Lap 26 ┤░░░░░░░░░░░░░░░░░░░░░░░░░░  Early  │ Net: -2.4s
Lap 27 ┤░░░░░░░░░░░░░░░░░░░░░░░░░░░ Marginal │ Net: -0.8s
Lap 28 ┤████████████████████████████ Optimal │ Net: +0.0s
Lap 29 ┤████████████████████████████ Optimal │ Net: +0.2s
Lap 30 ┤████████████████████████████ Optimal │ Net: +0.1s
Lap 31 ┤████████████████████████████ Optimal │ Net: -0.1s
Lap 32 ┤█████████████████████████░░░ Good    │ Net: -0.5s
Lap 33 ┤░░░░░░░░░░░░░░░░░░░░░░░░░░  Late    │ Net: -1.2s

Factors:
• Tire deg: 0.08s/lap (cliff at ~35 laps)
• Track position: P1 (+2.8s to P2)
• Traffic: Clear air expected post-pit
• Competitor threats: NOR pitting L27-29
```

### Compound Selection

```
TIRE COMPOUND DECISION

Remaining Laps: 33
Current Compound: Medium (Age: 18)

Option Analysis:

HARD (Prime):
├─ Predicted pace: 1:21.8 → 1:22.6 (+0.8s deg)
├─ Stop requirement: 0 additional
├─ Risk: Low (5% cliff risk)
└─ Recommendation: ████████████████████ 85%

MEDIUM (Option):
├─ Predicted pace: 1:21.2 → 1:22.8 (+1.6s deg)
├─ Stop requirement: 1 additional possible
├─ Risk: Medium (25% cliff risk)
└─ Recommendation: ██████████░░░░░░░░░░ 50%

SOFT (Qualifying):
├─ Predicted pace: 1:20.8 → 1:24.5 (+3.7s deg)
├─ Stop requirement: 1 additional required
├─ Risk: High (85% cliff before flag)
└─ Recommendation: ████░░░░░░░░░░░░░░░░ 15%
```

---

## Tire Strategy Planning

### Multi-Stop Strategy Comparison

```
STRATEGY COMPARISON - 52 LAP RACE

Strategy 1: ONE STOP (Recommended)
├─ Stint 1: Medium (L1-L26) ██████████████████████████
├─ Stint 2: Hard (L27-L52)  ██████████████████████████
├─ Predicted time: 1:32:45.234
├─ Risk Level: Low
└─ Win probability: 45%

Strategy 2: TWO STOP (Aggressive)
├─ Stint 1: Soft (L1-L15)   ███████████████
├─ Stint 2: Medium (L16-L35)████████████████████
├─ Stint 3: Soft (L36-L52)  █████████████████
├─ Predicted time: 1:32:52.678
├─ Risk Level: Medium
└─ Win probability: 38%

Strategy 3: TWO STOP (Conservative)
├─ Stint 1: Medium (L1-L18) ██████████████████
├─ Stint 2: Hard (L19-L38)  ████████████████████
├─ Stint 3: Medium (L39-L52)██████████████
├─ Predicted time: 1:32:58.123
├─ Risk Level: Very Low
└─ Win probability: 32%
```

### Strategy Visualization

```
LAP  0    10    20    30    40    50
     │     │     │     │     │     │
     │     │     │     │     │     │
S1   ├─────[M]─────────────[H]─────────────┤  ONE STOP
     │ Medium (26L)     Hard (26L)         Total: 2.4s pit
     │
S2   ├────[S]────────[M]─────────[S]──────┤  TWO STOP
     │ Soft (15L)  Med (20L)  Soft (17L)  Total: 4.8s pit
     │
S3   ├─────[M]────────[H]─────────[M]─────┤  CONSERVATIVE
     │ Med (18L)   Hard (20L)   Med (14L) Total: 4.8s pit

Pit Time Loss: 22s per stop
```

---

## Undercut/Overcut Detection

### Real-time Opportunity Alerts

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️  UNDERCUT OPPORTUNITY DETECTED                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Target: NOR (P2, +3.2s behind VER)                         │
│                                                              │
│  Current Situation:                                          │
│  • VER tire age: 22 laps (Medium)                           │
│  • NOR tire age: 18 laps (Medium)                           │
│  • Gap: 3.2 seconds                                          │
│                                                              │
│  Undercut Analysis:                                          │
│  • If NOR pits NOW → Expected out-lap: 1:23.5               │
│  • VER in-lap (if stays): 1:22.8                            │
│  • Fresh tire advantage: 1.8s/lap for 3 laps               │
│                                                              │
│  Prediction: NOR gains 2.1s | Jump probability: 72%         │
│                                                              │
│  Recommendation: VER should COVER - pit within 1 lap        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Undercut/Overcut Model

```python
class UndercutModel:
    def calculate_undercut_potential(
        self,
        attacker: Driver,
        defender: Driver,
        current_gap: float,
        pit_delta: float = 22.0
    ) -> UndercutAnalysis:
        """
        Calculate undercut potential

        Parameters:
        - attacker: Driver attempting undercut
        - defender: Driver being undercut
        - current_gap: Current time gap
        - pit_delta: Pit stop time loss

        Returns:
        - success_probability: Chance of gaining position
        - expected_gain: Expected time gained
        - optimal_lap: Best lap to execute
        """
        # Calculate tire delta
        fresh_tire_advantage = self._tire_advantage(
            attacker.tire_age,
            defender.tire_age
        )

        # Calculate in-lap/out-lap delta
        in_out_delta = self._in_out_delta(
            attacker.current_pace,
            defender.current_pace
        )

        # Factor in traffic
        traffic_impact = self._traffic_model(
            attacker.position,
            defender.position
        )

        return UndercutAnalysis(
            success_probability=...,
            expected_gain=...,
            optimal_lap=...
        )
```

---

## Weather Strategy

### Rain Response System

```
⛈️  WEATHER ALERT - Rain Expected

Current Conditions:
• Track Status: DRY
• Air Temp: 24°C
• Track Temp: 42°C
• Humidity: 78%
• Rain Probability: 85% in next 10 laps

Radar Analysis:
Lap 30    35    40    45    50
│░░░░░│░░░░░│█████│█████│█████│
       Light Rain  Heavy Rain

STRATEGY RECOMMENDATIONS:

Scenario A: Light Rain (40% prob)
├─ Stay out on slicks until lap 38
├─ Pit for intermediates
└─ Expected advantage: +5-10s vs early pit

Scenario B: Heavy Rain (45% prob)
├─ Pit for intermediates at lap 35
├─ May need full wets by lap 42
└─ Key: Be in pit window when rain hits

Scenario C: Rain Misses (15% prob)
├─ Continue normal strategy
└─ One-stop remains optimal

Current Recommendation: PREPARE FOR PIT LAP 35-38
```

### Intermediate Timing

```
INTERMEDIATE CROSSOVER POINT

Track Evolution After Rain Start:

Lap  │ Slicks  │ Inters  │ Wets    │ Optimal
─────┼─────────┼─────────┼─────────┼─────────
+0   │ 1:35.0  │ 1:28.0  │ 1:26.0  │ Wets
+2   │ 1:34.0  │ 1:25.5  │ 1:26.5  │ Inters
+4   │ 1:32.0  │ 1:24.0  │ 1:27.0  │ Inters
+6   │ 1:28.0  │ 1:23.5  │ 1:28.0  │ Inters
+8   │ 1:24.0  │ 1:24.0  │ 1:30.0  │ CROSSOVER
+10  │ 1:22.0  │ 1:24.5  │ 1:32.0  │ Slicks
+12  │ 1:21.5  │ 1:25.0  │ 1:34.0  │ Slicks

Crossover detected at: Lap +8 after rain stops
Recommendation: Switch to slicks at lap +8
```

---

## Safety Car Modeling

### SC Probability Prediction

```
SAFETY CAR PROBABILITY - Monaco GP

Current Race Status: Lap 35/78

Base SC Probability: 65% (historical Monaco rate)

Current Factors:
├─ Close racing in midfield: +8%
├─ Tire degradation high: +5%
├─ No incidents yet: -3%
├─ Weather stable: -2%
└─ Track position battles: +4%

Current SC Probability: 77%

Expected SC Laps: 42, 55, 68 (peak probability)

┌─────────────────────────────────────────────────────────────┐
│            SC PROBABILITY BY LAP                             │
├─────────────────────────────────────────────────────────────┤
│  100%│                                                       │
│   75%│          ╭──╮    ╭──╮         ╭──╮                   │
│   50%│      ╭───╯  ╰────╯  ╰─────────╯  ╰───╮               │
│   25%│  ────╯                                ╰───           │
│    0%┼───────────────────────────────────────────           │
│      35   40   45   50   55   60   65   70   75   78        │
└─────────────────────────────────────────────────────────────┘
```

### SC Response Strategy

```
SAFETY CAR RESPONSE OPTIONS

If SC deploys NOW (Lap 35):

Option 1: PIT IMMEDIATELY
├─ Tire: Change to Hard
├─ Position loss: ~3 positions
├─ Fresh tires for restart
├─ Recommendation: ████████████████████ OPTIMAL if > L50 SC

Option 2: STAY OUT
├─ Gain track position
├─ Older tires at restart
├─ Risk if SC extends
├─ Recommendation: ████████░░░░░░░░░░░░ Only if < L45 SC

Option 3: OPPOSITE TO RIVAL
├─ Pit if rival stays out
├─ Stay if rival pits
├─ Maintains relative position
├─ Recommendation: ████████████████░░░░ Safe play
```

---

## Strategy Simulation

### Monte Carlo Simulator

```python
class StrategySimulator:
    def simulate_race(
        self,
        strategy: Strategy,
        iterations: int = 10000
    ) -> SimulationResults:
        """
        Run Monte Carlo simulation of race outcome

        Simulates:
        - Tire degradation variance
        - Safety car probability
        - Weather changes
        - Pit stop variance
        - First lap incidents
        """
        results = []
        for _ in range(iterations):
            race = self._simulate_single_race(strategy)
            results.append(race.final_position)

        return SimulationResults(
            mean_position=np.mean(results),
            win_probability=results.count(1) / len(results),
            podium_probability=sum(1 for r in results if r <= 3) / len(results),
            position_distribution=Counter(results)
        )
```

### Simulation Output

```
STRATEGY SIMULATION RESULTS

Strategy: One-Stop (M-H)
Simulations: 10,000

Position Distribution:
P1  ████████████████████████████████████████ 42%
P2  ██████████████████████████████ 28%
P3  █████████████████ 15%
P4  ████████ 8%
P5+ ███████ 7%

Statistics:
• Mean Position: 1.85
• Win Probability: 42%
• Podium Probability: 85%
• Points Probability: 98%
• DNF Risk: 2%
```

---

## Real-time Strategy Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    STRATEGY CENTER - LAP 35/58                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CURRENT SITUATION                    │  RECOMMENDATIONS                 │
│  ────────────────                     │  ────────────────                │
│  Position: P1 (VER)                   │  ✓ Pit window: Laps 38-42       │
│  Gap to P2: +3.2s (NOR)              │  ✓ Compound: HARD                │
│  Tire: Medium (22 laps)               │  ⚠ Cover NOR if he pits         │
│                                        │  ⚠ SC probability: 35%          │
│  TIRE STATUS                          │                                  │
│  ──────────                           │  THREATS                         │
│  Deg Rate: 0.08s/lap                  │  ──────                          │
│  Est. Cliff: Lap 45                   │  • NOR undercut: 25% risk        │
│  Current Loss: 1.8s total             │  • HAM overcut: 15% risk         │
│                                        │  • SC losing position: 20%       │
│  PIT STATUS                           │                                  │
│  ──────────                           │                                  │
│  Stops Made: 1                        │                                  │
│  Strategy: Two-stop planned           │                                  │
│                                        │                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  📊 Gap Trend: Stable (+0.1s last 5 laps)                               │
│  🏁 Projected Finish: P1 (78% confidence)                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Get Strategy Recommendation

```bash
POST /api/v1/strategy/recommend
{
    "driver": "VER",
    "session_key": "monaco_2024_race",
    "current_lap": 35,
    "constraints": {
        "min_stops": 1,
        "available_compounds": ["hard", "medium", "soft"]
    }
}

Response:
{
    "recommended_strategy": {
        "type": "two_stop",
        "stops": [
            {"lap": 38, "compound": "hard"},
            {"lap": 52, "compound": "medium"}
        ],
        "predicted_time": "1:32:45.234",
        "win_probability": 0.45
    },
    "alternatives": [...],
    "alerts": [...]
}
```

### Get Pit Window

```bash
GET /api/v1/strategy/pit-window
?driver=VER
&session_key=monaco_2024_race

Response:
{
    "optimal_window": {"start": 38, "end": 42},
    "factors": {...},
    "competitor_windows": {...}
}
```

---

## Related Documentation

- [Race Prediction](../race-prediction/README.md)
- [ML Models](../../ml-analysis/models/README.md)
- [Data Sources](../../data-sources/README.md)
