# Live Commentary Engine

## Overview

The Live Commentary Engine is the flagship feature of PitWall Live, generating broadcast-quality AI narration in real-time during F1 sessions. It transforms raw telemetry and timing data into engaging, contextual commentary that rivals professional race broadcasting.

---

## Feature Goals

1. **Real-time Generation**: < 3 second latency from event to commentary
2. **Contextual Awareness**: Understanding race situations, history, and significance
3. **Multiple Styles**: Technical, casual, and dramatic commentary modes
4. **Multi-language**: Support for major languages
5. **Accuracy**: 95%+ factual accuracy on data-driven statements

---

## Commentary Types

### 1. Event-Triggered Commentary
Immediate reactions to race events:

| Event Type | Trigger | Example Output |
|------------|---------|----------------|
| Overtake | Position change detected | "Hamilton sweeps past Leclerc into Turn 3! That's P4 for the Mercedes driver." |
| Pit Stop | Pit entry/exit detected | "Verstappen boxes for hard tires. A 2.3 second stop - excellent work by Red Bull." |
| Fastest Lap | New session fastest | "Purple sectors across the board! Norris sets a 1:21.456 - the fastest lap of the race." |
| Incident | Yellow/Red flag | "Yellow flags in sector 2. Replays show Sainz has gone into the gravel at Turn 9." |
| DRS | DRS activation | "Perez into DRS range. He's within a second of Russell now." |

### 2. Analytical Commentary
Periodic insights based on data analysis:

- Gap trends and projections
- Tire degradation observations
- Strategy predictions
- Historical comparisons
- Championship implications

### 3. Ambient Commentary
Filling gaps with contextual information:

- Driver backgrounds
- Circuit history
- Technical explanations
- Team dynamics
- Weather updates

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Ingestion                            │
│  OpenF1 / LiveF1 → Event Detection → Event Queue            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Context Builder                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Race     │  │  Driver    │  │  History   │            │
│  │   State    │  │  Context   │  │  Context   │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Commentary Generator                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │              LLM (Claude/GPT-4)                     │    │
│  │  - Prompt engineering for F1 domain                 │    │
│  │  - Style-specific system prompts                    │    │
│  │  - Fact verification layer                          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Output Processing                          │
│  - Deduplication                                             │
│  - Rate limiting (avoid commentary spam)                     │
│  - Priority queue (important events first)                   │
│  - Text-to-speech (optional)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Event Detection System

### Priority Levels

| Priority | Events | Max Latency |
|----------|--------|-------------|
| P0 (Critical) | Crashes, red flags, race lead changes | < 1s |
| P1 (High) | Overtakes, pit stops, fastest laps | < 2s |
| P2 (Medium) | DRS, tire changes, gap changes | < 3s |
| P3 (Low) | Sector improvements, minor position changes | < 5s |

### Event Detection Logic

```python
class EventDetector:
    def detect_overtake(self, prev_positions, curr_positions):
        """Detect position changes between drivers"""
        overtakes = []
        for driver, curr_pos in curr_positions.items():
            prev_pos = prev_positions.get(driver)
            if prev_pos and curr_pos < prev_pos:
                # Driver gained positions
                overtakes.append({
                    "type": "overtake",
                    "driver": driver,
                    "from_pos": prev_pos,
                    "to_pos": curr_pos,
                    "priority": self._calculate_priority(prev_pos, curr_pos)
                })
        return overtakes

    def detect_pit_stop(self, timing_data):
        """Detect pit entry and exit"""
        # Check for pit lane entry/exit markers
        pass

    def detect_fastest_lap(self, lap_times, session_fastest):
        """Detect new fastest lap"""
        pass
```

---

## Context Building

### Race State Context

```python
race_context = {
    "session_type": "Race",
    "lap": 45,
    "total_laps": 58,
    "leader": "VER",
    "safety_car": False,
    "weather": "dry",
    "track_temp": 42,
    "championship_leader": "VER",
    "points_gap": 78,

    "positions": {
        "VER": {"position": 1, "gap": 0, "tire": "hard", "tire_age": 15},
        "NOR": {"position": 2, "gap": 3.2, "tire": "medium", "tire_age": 8},
        # ...
    },

    "recent_events": [
        {"type": "pit_stop", "driver": "HAM", "lap": 42},
        {"type": "overtake", "driver": "NOR", "passed": "PER", "lap": 44}
    ]
}
```

### Historical Context

```python
historical_context = {
    "driver_stats": {
        "VER": {
            "wins_this_season": 8,
            "poles_this_season": 6,
            "wins_at_circuit": 2,
            "best_finish_at_circuit": 1
        }
    },
    "circuit_records": {
        "lap_record": {"driver": "HAM", "time": "1:21.046", "year": 2020},
        "most_wins": {"driver": "HAM", "count": 6}
    },
    "head_to_head": {
        "VER_vs_NOR": {"wins": 15, "losses": 3}
    }
}
```

---

## Commentary Styles

### Technical Style
For data-focused viewers:
```
"Verstappen's tire degradation curve suggests optimal pit window at lap 32-35.
Current deg rate of 0.08s per lap puts him at 23.4s gap by potential undercut window."
```

### Casual Style
For general audience:
```
"Verstappen's looking comfortable out front, but those tires are starting to go off.
Expect a pit stop soon - Red Bull won't want to risk losing this lead."
```

### Dramatic Style
For entertainment focus:
```
"The gap is shrinking! Norris smells blood in the water! Can McLaren finally break
Red Bull's stranglehold? The tension in the pit lane is palpable!"
```

---

## LLM Integration

### Model Selection

| Model | Pros | Cons | Use Case |
|-------|------|------|----------|
| Claude 3.5 | Fast, accurate, good context | Cost | Primary |
| GPT-4 Turbo | Good quality | Latency | Backup |
| Claude 3 Haiku | Very fast, cheap | Less nuanced | High-volume events |
| Fine-tuned Llama | Low cost, controllable | Training required | Future |

### Prompt Engineering

```python
SYSTEM_PROMPT = """
You are an expert Formula 1 commentator providing live race commentary.

Style: {style}  # technical/casual/dramatic
Language: {language}

Guidelines:
- Be accurate with data - never invent statistics
- Match the excitement level to the event importance
- Reference relevant history when appropriate
- Keep responses concise (1-3 sentences for events)
- Use driver surnames after first mention
- Include technical details for technical style

Current Race State:
{race_context}

Recent Events:
{recent_events}

Generate commentary for the following event:
{event}
"""
```

### Response Validation

```python
class CommentaryValidator:
    def validate(self, commentary, event, context):
        """Validate commentary accuracy"""
        checks = [
            self._check_driver_names(commentary, context),
            self._check_positions(commentary, context),
            self._check_lap_times(commentary, context),
            self._check_no_hallucination(commentary, event)
        ]
        return all(checks)
```

---

## Rate Limiting & Queue Management

### Commentary Cadence

```python
COMMENTARY_RULES = {
    "min_gap_between_commentary": 5,  # seconds
    "max_queue_size": 10,
    "priority_timeout": {
        "P0": 30,  # Must generate within 30s or drop
        "P1": 60,
        "P2": 120,
        "P3": 300
    },
    "batch_similar_events": True,  # Combine multiple minor position changes
}
```

### Queue Priority

```
┌─────────────────────────────────────────┐
│            Commentary Queue              │
├─────────────────────────────────────────┤
│ P0: [CRASH_T3]                          │ ← Process immediately
│ P1: [OVERTAKE_VER, PIT_HAM]            │ ← Process next
│ P2: [GAP_CHANGE, DRS_ENABLED]          │ ← Queue
│ P3: [SECTOR_IMPROVEMENT]               │ ← Low priority
└─────────────────────────────────────────┘
```

---

## Multi-language Support

### Supported Languages (v1.0)

| Language | Code | Status |
|----------|------|--------|
| English | en | Primary |
| Spanish | es | Planned |
| German | de | Planned |
| French | fr | Planned |
| Italian | it | Planned |
| Dutch | nl | Planned |

### Translation Strategy

1. **Direct Generation**: Generate commentary in target language
2. **Translation Layer**: Translate English commentary (faster, less accurate)

---

## Performance Metrics

### Key Performance Indicators

| Metric | Target | Measurement |
|--------|--------|-------------|
| Event-to-Commentary Latency | < 3s | P95 |
| Factual Accuracy | > 95% | Manual review |
| User Engagement | > 80% session retention | Analytics |
| Commentary Quality | > 4.0/5.0 | User ratings |

### Monitoring

```python
metrics = {
    "latency_histogram": Histogram("commentary_latency_seconds"),
    "events_processed": Counter("events_processed_total"),
    "commentary_generated": Counter("commentary_generated_total"),
    "errors": Counter("commentary_errors_total"),
    "queue_size": Gauge("commentary_queue_size")
}
```

---

## User Customization

### Settings

```typescript
interface CommentarySettings {
  style: 'technical' | 'casual' | 'dramatic';
  language: string;
  volume: number;  // For TTS
  enabled_events: EventType[];
  commentary_frequency: 'low' | 'medium' | 'high';
  favorite_drivers: string[];  // Prioritize these drivers
  mute_during_ads: boolean;
}
```

---

## Future Enhancements

### Planned Features

1. **Text-to-Speech**: AI voice generation for audio commentary
2. **Voice Cloning**: Famous commentator voice styles
3. **Interactive Mode**: Users can ask questions
4. **Crowd Commentary**: Aggregate fan reactions
5. **Podcast Generation**: Automatic race summary podcasts

### Research Areas

- Emotion detection in race situations
- Predictive commentary (anticipating events)
- Personalized commentary based on user knowledge level
- Multi-modal commentary (video clip integration)

---

## Related Documentation

- [Data Sources](../../data-sources/README.md)
- [Architecture](../../architecture/README.md)
- [ML Analysis](../../ml-analysis/README.md)
