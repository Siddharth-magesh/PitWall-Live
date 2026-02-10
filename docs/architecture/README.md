# System Architecture

## Overview

PitWall Live is built on a modern, event-driven microservices architecture designed for real-time data processing, scalable machine learning inference, and responsive user experiences.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                     │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│   │   Web    │   │  Mobile  │   │   API    │   │ Widgets  │           │
│   │   App    │   │   App    │   │ Clients  │   │ (Embed)  │           │
│   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘           │
└────────┼──────────────┼──────────────┼──────────────┼───────────────────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          CDN / LOAD BALANCER                             │
│                     (CloudFront / Cloudflare / Nginx)                    │
└─────────────────────────────────────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   API Gateway   │  │   WebSocket     │  │   Static        │
│   (FastAPI)     │  │   Gateway       │  │   Assets        │
│                 │  │                 │  │   (Next.js)     │
└────────┬────────┘  └────────┬────────┘  └─────────────────┘
         │                    │
         └────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           SERVICE MESH                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │    Timing    │  │  Commentary  │  │  Prediction  │                  │
│  │   Service    │  │   Service    │  │   Service    │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Telemetry  │  │     User     │  │   Feature    │                  │
│  │   Service    │  │   Service    │  │    Store     │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  PostgreSQL  │  │ TimescaleDB  │  │    Redis     │                  │
│  │   (Users,    │  │  (Time-      │  │  (Cache,     │                  │
│  │   Config)    │  │   Series)    │  │   Pub/Sub)   │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐                                    │
│  │  ClickHouse  │  │     S3       │                                    │
│  │  (Analytics) │  │  (Objects)   │                                    │
│  └──────────────┘  └──────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL DATA SOURCES                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │    OpenF1    │  │    FastF1    │  │  Jolpica-F1  │                  │
│  │  (Real-time) │  │ (Historical) │  │  (Archive)   │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Service Architecture

### Microservices Overview

| Service | Responsibility | Technology | Scaling |
|---------|---------------|------------|---------|
| API Gateway | Request routing, auth | FastAPI | Horizontal |
| WebSocket Gateway | Real-time connections | Socket.io | Horizontal |
| Timing Service | Live timing data | Python | Horizontal |
| Telemetry Service | Car telemetry | Python | Horizontal |
| Commentary Service | AI commentary | Python + Claude | Vertical |
| Prediction Service | ML inference | Python + PyTorch | Horizontal |
| Feature Store | ML features | Feast | Horizontal |
| User Service | Auth, preferences | Python | Horizontal |

### Service Communication

```
┌─────────────────────────────────────────────────────────────┐
│                 SERVICE COMMUNICATION                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Synchronous (REST/gRPC):                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  API Gateway ──► User Service (auth validation)    │    │
│  │  Prediction ──► Feature Store (get features)       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Asynchronous (Redis Pub/Sub):                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Data Ingestion ──► timing:* ──► Timing Service    │    │
│  │  Timing Service ──► events:* ──► Commentary Svc    │    │
│  │  Commentary ──► commentary:* ──► WebSocket GW      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow Architecture

### Real-time Data Flow

```
External Sources                    Processing                      Delivery
     │                                  │                              │
     ▼                                  ▼                              ▼
┌─────────┐    ┌─────────┐    ┌─────────────────┐    ┌─────────┐    ┌─────────┐
│ OpenF1  │───►│ Ingest  │───►│ Event Detection │───►│ Redis   │───►│ WS      │
│ LiveF1  │    │ Service │    │ & Processing    │    │ Pub/Sub │    │ Gateway │
└─────────┘    └─────────┘    └─────────────────┘    └─────────┘    └─────────┘
                                      │
                                      ▼
                              ┌─────────────────┐
                              │ TimescaleDB     │
                              │ (Persistence)   │
                              └─────────────────┘
```

### Latency Budget

| Stage | Target | Measurement |
|-------|--------|-------------|
| External Source → Ingestion | 3000ms | OpenF1 delay |
| Ingestion → Processing | 50ms | Internal |
| Processing → Redis | 10ms | Internal |
| Redis → WebSocket | 30ms | Network |
| WebSocket → Client | 50ms | Network |
| **Total** | **< 3500ms** | End-to-end |

---

## ML Architecture

### Training Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ML TRAINING PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│   │  Data    │───►│ Feature  │───►│  Model   │───►│  Model   │        │
│   │  Loader  │    │  Engine  │    │ Training │    │ Registry │        │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘        │
│        │                                                │               │
│        │                                                ▼               │
│        │          ┌──────────────────────────────────────────┐        │
│        │          │              MLflow                       │        │
│        │          │  - Experiment Tracking                    │        │
│        │          │  - Model Versioning                       │        │
│        │          │  - Model Registry                         │        │
│        │          └──────────────────────────────────────────┘        │
│        │                                                               │
│        ▼                                                               │
│   ┌──────────────────────────────────────────────────────────┐        │
│   │              Feature Store (Feast)                        │        │
│   │  - Offline Store (Historical features)                   │        │
│   │  - Online Store (Real-time features)                     │        │
│   └──────────────────────────────────────────────────────────┘        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Inference Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ML INFERENCE PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Request                                                                │
│      │                                                                   │
│      ▼                                                                   │
│   ┌──────────────┐                                                      │
│   │   Feature    │  Get online features from Feature Store             │
│   │   Retrieval  │                                                      │
│   └──────┬───────┘                                                      │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐                                                      │
│   │    Model     │  Load model from registry (cached)                   │
│   │    Loading   │                                                      │
│   └──────┬───────┘                                                      │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐                                                      │
│   │  Inference   │  Run prediction                                      │
│   │   Engine     │                                                      │
│   └──────┬───────┘                                                      │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐                                                      │
│   │    Post-     │  Calibration, formatting                            │
│   │  Processing  │                                                      │
│   └──────────────┘                                                      │
│                                                                          │
│   Latency Target: < 100ms                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Database Architecture

### Schema Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABASE SCHEMA                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PostgreSQL (Relational Data)                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │
│  │   users     │  │   drivers   │  │   circuits  │                     │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤                     │
│  │ id          │  │ id (code)   │  │ id          │                     │
│  │ email       │  │ name        │  │ name        │                     │
│  │ preferences │  │ nationality │  │ country     │                     │
│  │ created_at  │  │ number      │  │ length      │                     │
│  └─────────────┘  └─────────────┘  └─────────────┘                     │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │
│  │   races     │  │   sessions  │  │constructors │                     │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤                     │
│  │ id          │  │ id          │  │ id          │                     │
│  │ season      │  │ race_id     │  │ name        │                     │
│  │ round       │  │ type        │  │ nationality │                     │
│  │ circuit_id  │  │ date        │  │ color       │                     │
│  └─────────────┘  └─────────────┘  └─────────────┘                     │
│                                                                          │
│  TimescaleDB (Time-Series)                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │   lap_times (hypertable)                                         │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ time | session_id | driver_id | lap | s1 | s2 | s3 | compound   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │   telemetry (hypertable)                                         │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ time | session_id | driver_id | speed | throttle | brake | gear │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Caching Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CACHING LAYERS                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  L1: Application Cache (In-memory)                                      │
│  ├─ Scope: Per-instance                                                 │
│  ├─ TTL: 1-5 seconds                                                    │
│  └─ Use: Hot data (current session state)                               │
│                                                                          │
│  L2: Redis Cache (Distributed)                                          │
│  ├─ Scope: Cluster-wide                                                 │
│  ├─ TTL: 30 seconds - 5 minutes                                        │
│  └─ Use: Session data, computed features, predictions                   │
│                                                                          │
│  L3: CDN Cache (Edge)                                                   │
│  ├─ Scope: Global                                                       │
│  ├─ TTL: 5 minutes - 1 hour                                            │
│  └─ Use: Static assets, historical data, embeddings                     │
│                                                                          │
│  Cache Key Pattern:                                                      │
│  └─ {service}:{entity}:{id}:{version}                                   │
│     Example: timing:session:monaco_2024_race:v2                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Kubernetes Cluster

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     KUBERNETES CLUSTER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Namespace: pitwall-production                                          │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Ingress Controller (nginx)                                      │   │
│  │  └─ TLS termination, routing, rate limiting                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Deployments                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │ api-gateway │  │ ws-gateway  │  │ timing-svc  │             │   │
│  │  │ replicas: 3 │  │ replicas: 2 │  │ replicas: 2 │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │commentary-sv│  │prediction-sv│  │ user-svc    │             │   │
│  │  │ replicas: 2 │  │ replicas: 2 │  │ replicas: 2 │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  StatefulSets                                                    │   │
│  │  ┌─────────────┐  ┌─────────────┐                               │   │
│  │  │ redis       │  │ postgresql  │                               │   │
│  │  │ replicas: 3 │  │ replicas: 3 │                               │   │
│  │  └─────────────┘  └─────────────┘                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Jobs/CronJobs                                                   │   │
│  │  - data-sync (every race weekend)                               │   │
│  │  - model-retrain (weekly)                                       │   │
│  │  - feature-compute (daily)                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Scaling Configuration

```yaml
# HorizontalPodAutoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Security Architecture

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AUTHENTICATION FLOW                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   1. User Login                                                         │
│   ┌────────┐    ┌────────┐    ┌────────┐                               │
│   │ Client │───►│  Auth  │───►│ Auth0/ │                               │
│   │        │◄───│  API   │◄───│ Clerk  │                               │
│   └────────┘    └────────┘    └────────┘                               │
│       │              │                                                   │
│       │         JWT Token                                               │
│       │              │                                                   │
│   2. API Request     ▼                                                  │
│   ┌────────┐    ┌────────┐    ┌────────┐                               │
│   │ Client │───►│  API   │───►│ Token  │                               │
│   │ + JWT  │    │Gateway │    │Validate│                               │
│   └────────┘    └────────┘    └────────┘                               │
│                      │                                                   │
│   3. Authorized      ▼                                                  │
│   ┌────────────────────────────────────────────────────┐               │
│   │              Protected Services                     │               │
│   └────────────────────────────────────────────────────┘               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Security Controls

| Layer | Control | Implementation |
|-------|---------|----------------|
| Network | TLS 1.3 | All external traffic |
| Network | WAF | Rate limiting, bot protection |
| Application | JWT | Bearer token auth |
| Application | RBAC | Role-based permissions |
| Data | Encryption | At-rest and in-transit |
| API | Rate Limiting | Per-user, per-endpoint |

---

## Monitoring & Observability

### Observability Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     OBSERVABILITY STACK                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Metrics (Prometheus + Grafana)                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ - Request latency (p50, p95, p99)                               │   │
│   │ - Error rates                                                    │   │
│   │ - Resource utilization                                          │   │
│   │ - Business metrics (predictions/min, users online)              │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   Logging (Loki + Grafana)                                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ - Structured JSON logs                                          │   │
│   │ - Correlation IDs                                               │   │
│   │ - Log levels (DEBUG, INFO, WARN, ERROR)                        │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   Tracing (OpenTelemetry + Jaeger)                                      │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ - Distributed traces across services                            │   │
│   │ - Span visualization                                            │   │
│   │ - Latency breakdown                                             │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   Alerting (Alertmanager + PagerDuty)                                   │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ - P1: Service down, >5% error rate                              │   │
│   │ - P2: High latency, resource exhaustion                         │   │
│   │ - P3: Anomaly detection, drift alerts                           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Disaster Recovery

### Backup Strategy

| Data Type | Frequency | Retention | Location |
|-----------|-----------|-----------|----------|
| PostgreSQL | Daily | 30 days | S3 Cross-region |
| TimescaleDB | Hourly | 7 days | S3 Cross-region |
| Redis | Real-time | N/A | Replication |
| ML Models | Per-version | Indefinite | S3 + MLflow |

### Recovery Objectives

| Metric | Target | Current |
|--------|--------|---------|
| RTO (Recovery Time) | < 1 hour | TBD |
| RPO (Recovery Point) | < 5 minutes | TBD |
| Availability | 99.9% | TBD |

---

## Related Documentation

- [Tech Stack](../tech-stack/README.md)
- [Deployment](../deployment/README.md)
- [API Design](../api-design/README.md)
