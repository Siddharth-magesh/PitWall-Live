# Machine Learning Analysis

## Overview

This section documents the machine learning capabilities of PitWall Live, including model architectures, training pipelines, datasets, and evaluation methodologies. Our ML infrastructure supports both pre-built models and custom experimentation.

---

## ML Capabilities Matrix

| Capability | Models | Accuracy | Latency |
|------------|--------|----------|---------|
| Race Winner Prediction | XGBoost, CatBoost, Neural | 45-50% | < 100ms |
| Lap Time Prediction | LightGBM, LSTM | MAE 0.3s | < 50ms |
| Tire Degradation | Time Series | MAE 0.02s/lap | < 100ms |
| Pit Stop Timing | Reinforcement Learning | 75% optimal | < 200ms |
| Commentary Generation | LLM (Claude/GPT) | 95% factual | < 3s |
| Driver Clustering | K-Means, DBSCAN | Silhouette 0.7 | < 500ms |

---

## Directory Structure

```
ml-analysis/
├── models/              # Model architectures and implementations
│   ├── README.md
│   ├── race-prediction.md
│   ├── lap-time-prediction.md
│   ├── tire-degradation.md
│   ├── strategy-optimization.md
│   └── commentary-generation.md
├── datasets/            # Dataset documentation and sources
│   ├── README.md
│   ├── historical-data.md
│   ├── telemetry-data.md
│   └── feature-engineering.md
├── training-pipelines/  # Training infrastructure
│   ├── README.md
│   ├── local-training.md
│   ├── distributed-training.md
│   └── automl.md
├── evaluation/          # Evaluation methodologies
│   ├── README.md
│   ├── metrics.md
│   ├── backtesting.md
│   └── a-b-testing.md
└── experiments/         # Experiment logs and notebooks
    ├── README.md
    └── templates/
```

---

## Model Categories

### 1. Prediction Models

Supervised learning models for forecasting race outcomes.

| Model | Type | Target | Features |
|-------|------|--------|----------|
| Race Winner | Multi-class Classification | Winner (1 of 20) | Grid, form, track history |
| Podium Finish | Multi-label Classification | Top 3 | Grid, pace, reliability |
| Points Finish | Binary Classification | Top 10 | Grid, avg finish, DNF rate |
| Qualifying Order | Learning to Rank | Quali positions | FP times, sector splits |

### 2. Regression Models

Continuous value predictions.

| Model | Target | Unit | MAE |
|-------|--------|------|-----|
| Lap Time | Predicted lap time | Seconds | 0.3s |
| Pit Stop Duration | Stop time | Seconds | 0.5s |
| Gap Evolution | Time delta | Seconds | 2.1s |
| Tire Degradation | Pace loss per lap | Seconds/lap | 0.02s |

### 3. Time Series Models

Sequential prediction and forecasting.

| Model | Application | Architecture |
|-------|-------------|--------------|
| Tire Energy | Deg prediction | LSTM + Attention |
| Gap Forecast | Race simulation | Transformer |
| Weather Impact | Condition prediction | GRU |

### 4. Reinforcement Learning

Strategy optimization through simulation.

| Model | Environment | Action Space |
|-------|-------------|--------------|
| Pit Strategy | Race Simulator | Pit/Stay, Compound |
| Undercut/Overcut | Battle Simulator | Pit timing |
| Safety Car Response | SC Simulator | Strategy adjustment |

### 5. Natural Language Generation

Commentary and insight generation.

| Model | Task | Technology |
|-------|------|------------|
| Live Commentary | Real-time narration | Claude 3.5 |
| Race Summary | Post-race reports | GPT-4 |
| Statistical Insights | Data narratives | Fine-tuned LLM |

---

## Feature Engineering

### Feature Categories

```python
FEATURE_GROUPS = {
    "driver": [
        "avg_quali_position_last_5",
        "avg_race_position_last_5",
        "wins_at_circuit",
        "podiums_at_circuit",
        "avg_positions_gained_at_start",
        "dnf_rate_season",
        "championship_position",
    ],

    "team": [
        "constructor_championship_position",
        "avg_pit_stop_time",
        "reliability_rate",
        "development_trajectory",
    ],

    "circuit": [
        "circuit_type",  # street, permanent, hybrid
        "power_sensitivity",
        "downforce_sensitivity",
        "overtaking_difficulty",
        "historical_safety_car_rate",
    ],

    "session": [
        "grid_position",
        "quali_gap_to_pole",
        "fp_pace_ranking",
        "tire_compound_start",
        "weather_condition",
    ],

    "telemetry": [
        "avg_corner_speed",
        "straight_line_speed",
        "braking_performance",
        "tire_deg_rate_practice",
    ]
}
```

### Feature Store Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RAW DATA SOURCES                          │
│  FastF1 | OpenF1 | Jolpica-F1 | Weather APIs                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  FEATURE PIPELINES                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Batch      │  │   Streaming  │  │   On-demand  │      │
│  │   (Daily)    │  │   (Real-time)│  │   (Request)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FEATURE STORE                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Offline Store (Historical)     │ Online Store (Live) │   │
│  │  - Training data                │ - Real-time features│   │
│  │  - Batch inference              │ - Low latency       │   │
│  │  - Backfilling                  │ - Caching           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Training Infrastructure

### Local Training

```bash
# Train a model locally
pitwall ml train \
    --model race_winner \
    --data seasons=2022,2023,2024 \
    --algorithm xgboost \
    --tune-hyperparams
```

### Distributed Training

```python
# Ray-based distributed training
import ray
from ray import tune

ray.init()

config = {
    "n_estimators": tune.randint(100, 1000),
    "max_depth": tune.randint(3, 12),
    "learning_rate": tune.loguniform(0.001, 0.1),
}

analysis = tune.run(
    train_model,
    config=config,
    num_samples=100,
    resources_per_trial={"cpu": 4, "gpu": 0.5}
)
```

### AutoML Pipeline

```python
from pitwall.ml import AutoMLTrainer

trainer = AutoMLTrainer(
    task="classification",
    target="race_winner",
    time_budget=3600,
    metric="accuracy"
)

best_model = trainer.fit(X_train, y_train)
```

---

## Evaluation Framework

### Metrics by Task

| Task | Primary Metric | Secondary Metrics |
|------|---------------|-------------------|
| Classification | Accuracy | Precision, Recall, F1, ROC-AUC |
| Regression | MAE | RMSE, R², MAPE |
| Ranking | NDCG | MAP, MRR |
| Time Series | MAE | RMSE, MASE |

### Backtesting Protocol

```python
class Backtester:
    def backtest(
        self,
        model,
        start_season: int,
        end_season: int,
        walk_forward: bool = True
    ) -> BacktestResults:
        """
        Backtest a model on historical data

        Walk-forward validation:
        - Train on seasons[0:i]
        - Test on season[i]
        - Repeat for each season
        """
        results = []

        for test_season in range(start_season, end_season + 1):
            # Train on all prior seasons
            train_data = self.get_data(end=test_season - 1)
            test_data = self.get_data(season=test_season)

            model.fit(train_data)
            predictions = model.predict(test_data)

            results.append({
                "season": test_season,
                "accuracy": accuracy_score(test_data.y, predictions),
                "predictions": predictions
            })

        return BacktestResults(results)
```

---

## Model Versioning

### MLflow Tracking

```python
import mlflow

mlflow.set_tracking_uri("http://mlflow.pitwall.live")
mlflow.set_experiment("race_winner_prediction")

with mlflow.start_run(run_name="xgb_v3"):
    # Log parameters
    mlflow.log_params({
        "algorithm": "xgboost",
        "n_estimators": 500,
        "max_depth": 8
    })

    # Train model
    model = train_model(params)

    # Log metrics
    mlflow.log_metrics({
        "train_accuracy": 0.52,
        "test_accuracy": 0.47,
        "cv_mean": 0.48
    })

    # Log model
    mlflow.sklearn.log_model(model, "model")

    # Log artifacts
    mlflow.log_artifact("feature_importance.png")
```

### Model Registry

```
Model Registry
├── race_winner_prediction
│   ├── v1.0.0 (Production)
│   ├── v1.1.0 (Staging)
│   └── v2.0.0-beta (Development)
├── lap_time_prediction
│   ├── v1.0.0 (Production)
│   └── v1.1.0 (Staging)
└── tire_degradation
    └── v1.0.0 (Production)
```

---

## Research Directions

### Current Focus Areas

1. **Explainable AI**: SHAP values for prediction explanations
2. **Uncertainty Quantification**: Confidence intervals for predictions
3. **Transfer Learning**: Cross-season model adaptation
4. **Real-time Inference**: Edge deployment for low latency
5. **Multi-modal Learning**: Combining telemetry with video

### Planned Experiments

| Experiment | Hypothesis | Status |
|------------|------------|--------|
| Transformer for Lap Times | Attention improves sequence modeling | Planned |
| Graph Neural Networks | Driver interactions as graph | Research |
| Meta-learning | Quick adaptation to new regulations | Planned |
| Ensemble Calibration | Improved probability estimates | In Progress |

---

## Detailed Documentation

- [Models](models/README.md) - Model architectures and implementations
- [Datasets](datasets/README.md) - Data sources and preprocessing
- [Training Pipelines](training-pipelines/README.md) - Training infrastructure
- [Evaluation](evaluation/README.md) - Metrics and validation
- [Experiments](experiments/README.md) - Experiment tracking

---

## Quick Start

### Train a Model

```python
from pitwall.ml import ModelBuilder, FeatureStore

# Load features
fs = FeatureStore()
data = fs.get_training_data(
    seasons=[2022, 2023, 2024],
    target="race_winner"
)

# Build and train model
builder = ModelBuilder(task="classification")
model = builder.train(
    data,
    algorithm="xgboost",
    auto_tune=True
)

# Evaluate
results = model.evaluate(test_data)
print(f"Accuracy: {results.accuracy:.2%}")

# Deploy
model.deploy(name="race_winner_v1")
```

### Make Predictions

```python
from pitwall.ml import ModelRegistry

# Load production model
model = ModelRegistry.load("race_winner_prediction", version="production")

# Get features for upcoming race
features = FeatureStore().get_live_features(session="monaco_2024_race")

# Predict
predictions = model.predict_proba(features)
for driver, prob in predictions.items():
    print(f"{driver}: {prob:.1%}")
```

---

## Related Documentation

- [ML Playground](../features/ml-playground/README.md)
- [Data Sources](../data-sources/README.md)
- [Architecture](../architecture/README.md)
