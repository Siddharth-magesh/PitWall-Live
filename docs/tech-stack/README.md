# Technology Stack

## Overview

PitWall Live is built on a modern, scalable technology stack designed for real-time data processing, machine learning workloads, and responsive user experiences. This document outlines our technology choices and rationale.

---

## Stack Summary

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  Next.js 14 | React 18 | TypeScript | TailwindCSS           │
│  Recharts | D3.js | Socket.io-client | TanStack Query       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY                             │
│              Kong / AWS API Gateway / Nginx                  │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    REST API     │ │   WebSocket     │ │    GraphQL      │
│    FastAPI      │ │   Service       │ │    Strawberry   │
│    (Python)     │ │   (Python)      │ │    (Python)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     ML & DATA LAYER                          │
│  PyTorch | scikit-learn | XGBoost | FastF1 | Pandas         │
│  MLflow | Ray | Celery | Redis                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASES                              │
│  PostgreSQL | TimescaleDB | Redis | ClickHouse              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                            │
│  Docker | Kubernetes | AWS/GCP | Terraform | GitHub Actions │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Stack

### Core Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.x | React framework with SSR/SSG |
| **React** | 18.x | UI component library |
| **TypeScript** | 5.x | Type-safe JavaScript |

**Rationale:**
- Next.js 14 App Router for improved performance and SEO
- Server Components for reduced client-side JavaScript
- Built-in API routes for BFF pattern
- Excellent developer experience

### Styling

| Technology | Purpose |
|------------|---------|
| **TailwindCSS** | Utility-first CSS framework |
| **shadcn/ui** | Component library |
| **Framer Motion** | Animations |
| **Lucide Icons** | Icon library |

### Data Visualization

| Technology | Purpose |
|------------|---------|
| **Recharts** | Standard charts (line, bar, pie) |
| **D3.js** | Custom visualizations |
| **Canvas API** | High-performance rendering |
| **Three.js** | 3D track visualization |

### State Management & Data Fetching

| Technology | Purpose |
|------------|---------|
| **TanStack Query** | Server state management |
| **Zustand** | Client state management |
| **Socket.io-client** | WebSocket connections |

### Code Example

```typescript
// Example: Live Timing Component
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useSocket } from '@/hooks/useSocket';

export function LiveTiming({ sessionKey }: { sessionKey: string }) {
  const queryClient = useQueryClient();

  // Initial data fetch
  const { data: timing } = useQuery({
    queryKey: ['timing', sessionKey],
    queryFn: () => fetchTiming(sessionKey),
  });

  // Real-time updates via WebSocket
  useSocket(`timing:${sessionKey}`, (update) => {
    queryClient.setQueryData(['timing', sessionKey], (old) => ({
      ...old,
      ...update,
    }));
  });

  return (
    <TimingTable data={timing} />
  );
}
```

---

## Backend Stack

### API Layer

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.100+ | REST API framework |
| **Strawberry** | 0.200+ | GraphQL API |
| **Pydantic** | 2.x | Data validation |
| **uvicorn** | 0.23+ | ASGI server |

**Rationale:**
- FastAPI for high performance and automatic OpenAPI docs
- Async-first design for real-time data handling
- Excellent Python type hint integration
- GraphQL for flexible data queries

### WebSocket Service

| Technology | Purpose |
|------------|---------|
| **python-socketio** | WebSocket server |
| **Redis Pub/Sub** | Message distribution |
| **asyncio** | Async I/O |

### Code Example

```python
# Example: FastAPI endpoint with real-time data
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

@app.get("/api/v1/timing/{session_key}")
async def get_timing(session_key: str):
    """Get current timing data for a session"""
    timing = await timing_service.get_current(session_key)
    return timing

@app.websocket("/ws/timing/{session_key}")
async def timing_websocket(websocket: WebSocket, session_key: str):
    await websocket.accept()
    async for update in timing_service.subscribe(session_key):
        await websocket.send_json(update)
```

---

## Machine Learning Stack

### Core Libraries

| Technology | Purpose |
|------------|---------|
| **PyTorch** | Deep learning framework |
| **scikit-learn** | Traditional ML algorithms |
| **XGBoost** | Gradient boosting |
| **LightGBM** | Fast gradient boosting |
| **CatBoost** | Categorical feature handling |

### Data Processing

| Technology | Purpose |
|------------|---------|
| **Pandas** | Data manipulation |
| **NumPy** | Numerical computing |
| **Polars** | High-performance DataFrames |
| **FastF1** | F1 data access |

### MLOps

| Technology | Purpose |
|------------|---------|
| **MLflow** | Experiment tracking |
| **Ray** | Distributed computing |
| **Optuna** | Hyperparameter optimization |
| **DVC** | Data versioning |

### LLM Integration

| Technology | Purpose |
|------------|---------|
| **Claude API** | Commentary generation |
| **LangChain** | LLM orchestration |
| **Anthropic SDK** | API client |

### Code Example

```python
# Example: Model training pipeline
import mlflow
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score

class RaceWinnerModel:
    def __init__(self):
        self.model = XGBClassifier(
            n_estimators=500,
            max_depth=8,
            learning_rate=0.05,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )

    def train(self, X, y):
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(self.model.get_params())

            # Train with cross-validation
            scores = cross_val_score(self.model, X, y, cv=5)
            self.model.fit(X, y)

            # Log metrics
            mlflow.log_metric("cv_accuracy", scores.mean())
            mlflow.log_metric("cv_std", scores.std())

            # Log model
            mlflow.sklearn.log_model(self.model, "model")

        return self.model
```

---

## Database Layer

### Primary Databases

| Database | Purpose | Use Case |
|----------|---------|----------|
| **PostgreSQL** | Relational data | Users, sessions, config |
| **TimescaleDB** | Time-series data | Telemetry, lap times |
| **Redis** | Caching & Pub/Sub | Real-time data, sessions |
| **ClickHouse** | Analytics | Historical queries |

### Schema Design

```sql
-- TimescaleDB: Lap times hypertable
CREATE TABLE lap_times (
    timestamp TIMESTAMPTZ NOT NULL,
    session_id UUID NOT NULL,
    driver_id VARCHAR(3) NOT NULL,
    lap_number INTEGER NOT NULL,
    sector_1 NUMERIC(6,3),
    sector_2 NUMERIC(6,3),
    sector_3 NUMERIC(6,3),
    lap_time NUMERIC(7,3),
    compound VARCHAR(10),
    tire_age INTEGER,
    PRIMARY KEY (timestamp, session_id, driver_id)
);

SELECT create_hypertable('lap_times', 'timestamp');

-- PostgreSQL: User preferences
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY,
    commentary_style VARCHAR(20) DEFAULT 'casual',
    favorite_drivers VARCHAR(3)[],
    notification_settings JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Caching Strategy

```python
# Redis caching example
from redis import asyncio as aioredis

class CacheService:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)

    async def get_or_compute(
        self,
        key: str,
        compute_fn: Callable,
        ttl: int = 300
    ):
        # Try cache first
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        # Compute and cache
        result = await compute_fn()
        await self.redis.setex(key, ttl, json.dumps(result))
        return result
```

---

## Infrastructure

### Containerization

| Technology | Purpose |
|------------|---------|
| **Docker** | Container runtime |
| **Docker Compose** | Local development |
| **Kubernetes** | Container orchestration |
| **Helm** | K8s package management |

### Cloud Providers

| Provider | Services Used |
|----------|---------------|
| **AWS** | EKS, RDS, ElastiCache, S3, CloudFront |
| **GCP** | GKE, Cloud SQL, Memorystore (alternative) |
| **Vercel** | Frontend hosting (optional) |

### CI/CD

| Technology | Purpose |
|------------|---------|
| **GitHub Actions** | CI/CD pipeline |
| **Terraform** | Infrastructure as code |
| **ArgoCD** | GitOps deployment |

### Monitoring

| Technology | Purpose |
|------------|---------|
| **Prometheus** | Metrics collection |
| **Grafana** | Dashboards |
| **Sentry** | Error tracking |
| **OpenTelemetry** | Distributed tracing |

---

## Development Tools

### Code Quality

| Tool | Purpose |
|------|---------|
| **ESLint** | JavaScript linting |
| **Prettier** | Code formatting |
| **Ruff** | Python linting |
| **Black** | Python formatting |
| **mypy** | Python type checking |
| **pytest** | Python testing |
| **Vitest** | JavaScript testing |

### Documentation

| Tool | Purpose |
|------|---------|
| **Swagger/OpenAPI** | API documentation |
| **Storybook** | Component documentation |
| **MkDocs** | Project documentation |

---

## Technology Decisions

### Why FastAPI over Django/Flask?

| Factor | FastAPI | Django | Flask |
|--------|---------|--------|-------|
| Performance | Excellent | Good | Good |
| Async Support | Native | Limited | Limited |
| Type Hints | Excellent | Limited | None |
| API Docs | Automatic | Manual | Manual |
| Learning Curve | Medium | Steep | Low |

**Decision:** FastAPI for async-first design and automatic API documentation.

### Why Next.js over Create React App?

| Factor | Next.js | CRA |
|--------|---------|-----|
| SSR/SSG | Yes | No |
| Performance | Excellent | Good |
| SEO | Excellent | Poor |
| API Routes | Yes | No |
| File Routing | Yes | No |

**Decision:** Next.js for SEO, performance, and full-stack capabilities.

### Why TimescaleDB over InfluxDB?

| Factor | TimescaleDB | InfluxDB |
|--------|-------------|----------|
| Query Language | SQL | InfluxQL/Flux |
| PostgreSQL Compatibility | Full | None |
| Complex Joins | Yes | Limited |
| Ecosystem | PostgreSQL | Specialized |

**Decision:** TimescaleDB for SQL familiarity and PostgreSQL ecosystem.

---

## Performance Considerations

### Real-time Data Flow

```
Data Source (OpenF1)
        │
        ▼ (~3s latency)
┌──────────────────┐
│  Ingestion       │
│  Service         │
└────────┬─────────┘
         │
         ▼ (< 100ms)
┌──────────────────┐
│  Redis           │
│  Pub/Sub         │
└────────┬─────────┘
         │
         ▼ (< 50ms)
┌──────────────────┐
│  WebSocket       │
│  Server          │
└────────┬─────────┘
         │
         ▼ (< 50ms)
┌──────────────────┐
│  Client          │
│  Browser         │
└──────────────────┘

Total: < 3.5s from event to display
```

### Scaling Strategy

| Component | Scaling Method | Trigger |
|-----------|----------------|---------|
| API Servers | Horizontal | CPU > 70% |
| WebSocket Servers | Horizontal | Connections > 10k |
| ML Workers | Vertical + Horizontal | Queue depth |
| Databases | Read replicas | Query latency |

---

## Security

### Authentication

| Technology | Purpose |
|------------|---------|
| **Auth0/Clerk** | User authentication |
| **JWT** | API authentication |
| **OAuth 2.0** | Third-party integrations |

### Data Protection

- HTTPS everywhere
- Encrypted data at rest
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

---

## Related Documentation

- [Architecture](../architecture/README.md)
- [Deployment](../deployment/README.md)
- [API Design](../api-design/README.md)
