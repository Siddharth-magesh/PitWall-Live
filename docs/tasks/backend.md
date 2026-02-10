# Backend Tasks

## Overview

Detailed task breakdown for the PitWall Live backend services built with FastAPI, Python, and various data processing tools.

---

## Project Setup

### BE-001: Set up FastAPI Project Structure
**Priority:** P0 | **Effort:** S | **Dependencies:** None

**Description:**
Initialize the FastAPI project with proper structure and configurations.

**Acceptance Criteria:**
- [ ] FastAPI app initialized
- [ ] Project structure created
- [ ] Poetry/pip dependencies configured
- [ ] Environment configuration
- [ ] Logging configured
- [ ] Docker development setup

**Project Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── timing.py
│   │   │   │   ├── telemetry.py
│   │   │   │   ├── predictions.py
│   │   │   │   └── users.py
│   │   │   └── dependencies.py
│   │   └── websocket/
│   ├── core/
│   │   ├── security.py
│   │   ├── database.py
│   │   └── cache.py
│   ├── models/
│   │   ├── database/
│   │   └── schemas/
│   ├── services/
│   │   ├── timing_service.py
│   │   ├── prediction_service.py
│   │   └── commentary_service.py
│   └── utils/
├── tests/
├── alembic/
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

### BE-002: Implement Database Models
**Priority:** P0 | **Effort:** M | **Dependencies:** BE-001, INF-003

**Description:**
Create SQLAlchemy models for all database entities.

**Models to Create:**
```python
# models/database/race.py
class Race(Base):
    __tablename__ = "races"

    id = Column(UUID, primary_key=True)
    season = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    circuit_id = Column(String, ForeignKey("circuits.id"))
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)

# models/database/driver.py
class Driver(Base):
    __tablename__ = "drivers"

    id = Column(String(3), primary_key=True)  # VER, HAM, etc.
    name = Column(String, nullable=False)
    nationality = Column(String)
    date_of_birth = Column(Date)
    number = Column(Integer)

# models/database/lap_time.py (TimescaleDB)
class LapTime(Base):
    __tablename__ = "lap_times"

    timestamp = Column(DateTime, primary_key=True)
    session_id = Column(UUID, primary_key=True)
    driver_id = Column(String(3), primary_key=True)
    lap_number = Column(Integer, nullable=False)
    sector_1 = Column(Numeric(6, 3))
    sector_2 = Column(Numeric(6, 3))
    sector_3 = Column(Numeric(6, 3))
    lap_time = Column(Numeric(7, 3))
    compound = Column(String(10))
    tire_age = Column(Integer)
```

**Acceptance Criteria:**
- [ ] All core models implemented
- [ ] Relationships defined
- [ ] Indexes created
- [ ] TimescaleDB hypertables set up
- [ ] Alembic migrations created

---

## API Routes

### BE-003: Create REST API for Race Data
**Priority:** P0 | **Effort:** M | **Dependencies:** BE-002

**Description:**
Implement REST endpoints for race data access.

**Endpoints:**
```
GET  /api/v1/seasons
GET  /api/v1/seasons/{year}/races
GET  /api/v1/races/{race_id}
GET  /api/v1/races/{race_id}/results
GET  /api/v1/races/{race_id}/laps
GET  /api/v1/races/{race_id}/telemetry
GET  /api/v1/drivers
GET  /api/v1/drivers/{driver_id}
GET  /api/v1/drivers/{driver_id}/stats
GET  /api/v1/circuits
GET  /api/v1/circuits/{circuit_id}
GET  /api/v1/standings/drivers
GET  /api/v1/standings/constructors
```

**Implementation Example:**
```python
# api/v1/routes/races.py
from fastapi import APIRouter, Depends, Query
from app.services import RaceService
from app.models.schemas import RaceResponse, RaceListResponse

router = APIRouter(prefix="/races", tags=["races"])

@router.get("", response_model=RaceListResponse)
async def list_races(
    season: int = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    race_service: RaceService = Depends()
):
    """List races with optional season filter"""
    races = await race_service.list_races(
        season=season,
        limit=limit,
        offset=offset
    )
    return races

@router.get("/{race_id}", response_model=RaceResponse)
async def get_race(
    race_id: str,
    race_service: RaceService = Depends()
):
    """Get race details by ID"""
    race = await race_service.get_race(race_id)
    if not race:
        raise HTTPException(404, "Race not found")
    return race
```

---

### BE-004: Implement WebSocket Server
**Priority:** P1 | **Effort:** M | **Dependencies:** BE-001

**Description:**
Create WebSocket endpoints for real-time data streaming.

**Channels:**
```
ws://api/ws/timing/{session_key}    # Live timing updates
ws://api/ws/positions/{session_key} # Position updates
ws://api/ws/commentary/{session_key} # Live commentary
ws://api/ws/telemetry/{session_key}/{driver_id} # Driver telemetry
```

**Implementation:**
```python
# api/websocket/timing.py
from fastapi import WebSocket
from app.services import TimingService, RealtimeService

class TimingWebSocket:
    def __init__(self, realtime: RealtimeService):
        self.realtime = realtime

    async def handle(self, websocket: WebSocket, session_key: str):
        await websocket.accept()

        try:
            async for update in self.realtime.subscribe(f"timing:{session_key}"):
                await websocket.send_json(update)
        except WebSocketDisconnect:
            pass
        finally:
            await self.realtime.unsubscribe(f"timing:{session_key}")
```

---

### BE-005: Add Authentication
**Priority:** P1 | **Effort:** M | **Dependencies:** BE-003

**Description:**
Implement user authentication using Auth0 or Clerk.

**Acceptance Criteria:**
- [ ] JWT validation middleware
- [ ] User registration/login endpoints
- [ ] Protected route decorator
- [ ] Role-based access control
- [ ] API key authentication for bots/services

**Implementation:**
```python
# core/security.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    auth_service: AuthService = Depends()
) -> User:
    try:
        user = await auth_service.verify_token(token.credentials)
        return user
    except AuthError:
        raise HTTPException(401, "Invalid token")

# Usage in routes
@router.get("/me")
async def get_profile(user: User = Depends(get_current_user)):
    return user
```

---

## Services

### SVC-001: Timing Service
**Priority:** P0 | **Effort:** M | **Dependencies:** BE-002

**Description:**
Implement the timing data service.

```python
# services/timing_service.py
class TimingService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache

    async def get_current_timing(self, session_key: str) -> List[DriverTiming]:
        """Get current timing for all drivers"""
        cached = await self.cache.get(f"timing:{session_key}")
        if cached:
            return cached

        timing = await self.db.fetch_timing(session_key)
        await self.cache.set(f"timing:{session_key}", timing, ttl=1)
        return timing

    async def get_lap_times(
        self,
        session_key: str,
        driver_id: str = None,
        lap_range: Tuple[int, int] = None
    ) -> List[LapTime]:
        """Get lap times with optional filters"""
        pass
```

---

### SVC-002: Prediction Service
**Priority:** P1 | **Effort:** L | **Dependencies:** ML-002

**Description:**
Implement prediction service for ML model inference.

```python
# services/prediction_service.py
class PredictionService:
    def __init__(self, model_registry: ModelRegistry, feature_store: FeatureStore):
        self.models = model_registry
        self.features = feature_store

    async def predict_race_winner(
        self,
        session_key: str,
        use_live_data: bool = True
    ) -> Dict[str, float]:
        """Get race winner probabilities"""
        model = self.models.get("race_winner", version="production")

        if use_live_data:
            features = await self.features.get_live_features(session_key)
        else:
            features = await self.features.get_pre_race_features(session_key)

        probabilities = model.predict_proba(features)
        return {
            driver: float(prob)
            for driver, prob in zip(features.drivers, probabilities)
        }
```

---

### SVC-003: Commentary Service
**Priority:** P1 | **Effort:** L | **Dependencies:** COM-001

**Description:**
Implement commentary generation service.

```python
# services/commentary_service.py
import anthropic

class CommentaryService:
    def __init__(self, client: anthropic.Anthropic):
        self.client = client
        self.model = "claude-3-5-sonnet-20241022"

    async def generate_commentary(
        self,
        event: RaceEvent,
        context: RaceContext,
        style: str = "casual"
    ) -> str:
        """Generate commentary for a race event"""
        prompt = self._build_prompt(event, context, style)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=200,
            system=self._get_system_prompt(style),
            messages=[{"role": "user", "content": prompt}]
        )

        commentary = response.content[0].text
        return self._validate_commentary(commentary, context)
```

---

## Data Pipeline

### DAT-001: Implement FastF1 Data Loader
**Priority:** P0 | **Effort:** M | **Dependencies:** INF-003

**Description:**
Create data loader for historical F1 data via FastF1.

```python
# data/loaders/fastf1_loader.py
import fastf1

class FastF1Loader:
    def __init__(self, cache_path: str):
        fastf1.Cache.enable_cache(cache_path)

    async def load_session(
        self,
        year: int,
        grand_prix: str,
        session_type: str
    ) -> SessionData:
        """Load a complete session with all data"""
        session = fastf1.get_session(year, grand_prix, session_type)
        session.load()

        return SessionData(
            laps=self._process_laps(session.laps),
            results=self._process_results(session.results),
            weather=self._process_weather(session.weather_data),
        )

    async def load_telemetry(
        self,
        session: Session,
        driver: str,
        lap: int = None
    ) -> TelemetryData:
        """Load driver telemetry for a lap"""
        driver_laps = session.laps.pick_driver(driver)

        if lap:
            lap_data = driver_laps[driver_laps['LapNumber'] == lap].iloc[0]
        else:
            lap_data = driver_laps.pick_fastest()

        telemetry = lap_data.get_telemetry()
        return self._process_telemetry(telemetry)
```

---

### DAT-002: Implement OpenF1 Client
**Priority:** P0 | **Effort:** M | **Dependencies:** INF-003

**Description:**
Create client for OpenF1 real-time API.

```python
# data/clients/openf1_client.py
import httpx

class OpenF1Client:
    BASE_URL = "https://api.openf1.org/v1"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_positions(
        self,
        session_key: str = "latest",
        driver_number: int = None
    ) -> List[Position]:
        """Get driver positions"""
        params = {"session_key": session_key}
        if driver_number:
            params["driver_number"] = driver_number

        response = await self.client.get(
            f"{self.BASE_URL}/position",
            params=params
        )
        return [Position(**p) for p in response.json()]

    async def get_car_data(
        self,
        session_key: str = "latest",
        driver_number: int = None
    ) -> List[CarData]:
        """Get car telemetry data"""
        params = {"session_key": session_key}
        if driver_number:
            params["driver_number"] = driver_number

        response = await self.client.get(
            f"{self.BASE_URL}/car_data",
            params=params
        )
        return [CarData(**c) for c in response.json()]
```

---

## Real-time Processing

### RT-001: Event Detection System
**Priority:** P1 | **Effort:** L | **Dependencies:** DAT-004

**Description:**
Implement real-time event detection for commentary.

```python
# services/event_detector.py
class EventDetector:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.previous_state = {}

    async def process_update(self, timing_update: TimingUpdate) -> List[Event]:
        """Detect events from timing update"""
        events = []

        # Detect position changes
        position_events = self._detect_position_changes(timing_update)
        events.extend(position_events)

        # Detect pit stops
        pit_events = self._detect_pit_stops(timing_update)
        events.extend(pit_events)

        # Detect fastest laps
        fl_events = self._detect_fastest_lap(timing_update)
        events.extend(fl_events)

        # Update state
        self._update_state(timing_update)

        return events

    def _detect_position_changes(self, update: TimingUpdate) -> List[Event]:
        events = []
        for driver, current_pos in update.positions.items():
            previous_pos = self.previous_state.get(driver, {}).get('position')
            if previous_pos and current_pos < previous_pos:
                events.append(OvertakeEvent(
                    driver=driver,
                    from_position=previous_pos,
                    to_position=current_pos,
                    priority=self._calculate_priority(previous_pos, current_pos)
                ))
        return events
```

---

## Testing

### BE-TEST-001: Unit Tests
**Priority:** P0 | **Effort:** L | **Dependencies:** All BE tasks

**Description:**
Write comprehensive unit tests for all services.

**Coverage Requirements:**
- Services: 85%
- API Routes: 80%
- Data Loaders: 75%
- Utils: 100%

**Example Test:**
```python
# tests/services/test_timing_service.py
import pytest
from unittest.mock import AsyncMock
from app.services import TimingService

@pytest.fixture
def timing_service(mock_db, mock_cache):
    return TimingService(db=mock_db, cache=mock_cache)

@pytest.mark.asyncio
async def test_get_current_timing_from_cache(timing_service, mock_cache):
    mock_cache.get.return_value = [{"driver": "VER", "position": 1}]

    result = await timing_service.get_current_timing("session_123")

    assert len(result) == 1
    assert result[0]["driver"] == "VER"
    mock_cache.get.assert_called_once_with("timing:session_123")
```

---

## Performance

### BE-PERF-001: API Caching
**Priority:** P0 | **Effort:** M | **Dependencies:** BE-003

**Description:**
Implement caching for API responses.

```python
# core/cache.py
from functools import wraps
from redis import asyncio as aioredis

def cached(ttl: int = 60, key_builder = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            key = key_builder(*args, **kwargs) if key_builder else f"{func.__name__}:{args}:{kwargs}"

            cached_result = await cache.get(key)
            if cached_result:
                return cached_result

            result = await func(*args, **kwargs)
            await cache.set(key, result, ex=ttl)
            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=300, key_builder=lambda race_id: f"race:{race_id}")
async def get_race(race_id: str):
    return await db.fetch_race(race_id)
```

---

## Monitoring

### BE-MON-001: Logging and Metrics
**Priority:** P1 | **Effort:** M | **Dependencies:** BE-001

**Description:**
Implement structured logging and metrics collection.

```python
# core/logging.py
import structlog
from prometheus_client import Counter, Histogram

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Structured logging
logger = structlog.get_logger()

async def log_request(request, response, duration):
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration * 1000
    )
```
