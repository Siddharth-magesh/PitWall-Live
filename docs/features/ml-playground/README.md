# ML Playground

## Overview

The ML Playground is an interactive environment for training, evaluating, and deploying machine learning models on Formula 1 data. It provides both pre-built model templates for quick experimentation and full customization capabilities for advanced users.

---

## Core Capabilities

### 1. Pre-built Model Templates
Ready-to-use models for common F1 prediction tasks

### 2. Custom Model Training
Full flexibility for data scientists to build their own models

### 3. Experiment Tracking
MLflow-based versioning and comparison

### 4. One-click Deployment
Deploy models for real-time inference

### 5. Model Sharing
Community marketplace for sharing models

---

## Model Template Library

### Prediction Models

| Model | Description | Input Features | Output | Accuracy* |
|-------|-------------|----------------|--------|-----------|
| Race Winner | Predict race winner | Grid, quali times, form | Driver | ~45% |
| Podium Finish | Predict top 3 | Grid, track history | 3 drivers | ~65% |
| Points Finish | Predict top 10 | Grid, pace, reliability | 10 drivers | ~80% |
| Qualifying | Predict quali order | FP times, track type | Order | ~60% |
| Fastest Lap | Predict FL winner | Race pace, tire strategy | Driver | ~40% |

*Baseline accuracies on test data

### Regression Models

| Model | Description | Target | MAE* |
|-------|-------------|--------|------|
| Lap Time | Predict lap times | Seconds | 0.3s |
| Pit Stop Duration | Predict stop time | Seconds | 0.5s |
| Gap Prediction | Predict race gaps | Seconds | 2.1s |
| Tire Degradation | Predict deg curve | Seconds/lap | 0.02s |

### Classification Models

| Model | Description | Classes | F1 Score* |
|-------|-------------|---------|-----------|
| Pit Window | Optimal pit timing | Early/Mid/Late | 0.72 |
| Safety Car | SC probability | Yes/No | 0.68 |
| DNF Risk | Retirement risk | Yes/No | 0.71 |
| Rain Impact | Weather effect | Low/Med/High | 0.75 |

---

## Training Pipeline

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Selection                           │
│  - Season range                                              │
│  - Circuit filter                                            │
│  - Driver/team filter                                        │
│  - Weather conditions                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Feature Engineering                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Pre-built │  │   Custom    │  │  Auto-      │         │
│  │   Features  │  │   Features  │  │  Features   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Model Training                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Algorithm Selection                                 │   │
│  │  - XGBoost, LightGBM, CatBoost                      │   │
│  │  - Random Forest, Gradient Boosting                  │   │
│  │  - Neural Networks (PyTorch/TensorFlow)              │   │
│  │  - AutoML (auto-sklearn, FLAML)                      │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Hyperparameter Tuning                               │   │
│  │  - Grid Search                                       │   │
│  │  - Random Search                                     │   │
│  │  - Bayesian Optimization (Optuna)                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Evaluation                               │
│  - Cross-validation                                          │
│  - Holdout test set                                          │
│  - Time-series validation                                    │
│  - Backtesting on historical races                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Deployment                               │
│  - Model serialization                                       │
│  - API endpoint creation                                     │
│  - Real-time inference setup                                 │
│  - Monitoring configuration                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Feature Store

### Pre-computed Features

#### Driver Features
```python
driver_features = {
    # Performance
    "avg_quali_position_last_5": float,
    "avg_race_position_last_5": float,
    "avg_positions_gained": float,
    "dnf_rate_season": float,

    # Track-specific
    "avg_position_at_track": float,
    "best_finish_at_track": int,
    "track_experience_races": int,

    # Form
    "points_last_3_races": int,
    "quali_trend": float,  # Improving/declining
    "race_pace_vs_teammate": float,

    # Career
    "career_wins": int,
    "career_poles": int,
    "career_points": float
}
```

#### Team Features
```python
team_features = {
    # Performance
    "constructor_position": int,
    "avg_pit_stop_time": float,
    "reliability_rate": float,

    # Development
    "points_trajectory": float,
    "upgrade_effectiveness": float,

    # Track-specific
    "team_track_performance": float,
    "power_track_advantage": float,  # For power circuits
    "downforce_track_advantage": float  # For high-DF circuits
}
```

#### Session Features
```python
session_features = {
    # Timing
    "quali_gap_to_pole": float,
    "fp_pace_ranking": int,
    "sector_times": List[float],

    # Telemetry-derived
    "avg_corner_speed": float,
    "straight_line_speed": float,
    "tire_deg_rate": float,

    # Race-specific
    "start_position": int,
    "predicted_strategy": str,
    "weather_condition": str
}
```

---

## User Interface

### Training Wizard

```
┌─────────────────────────────────────────────────────────────┐
│                 ML Playground - New Model                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Select Model Type                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Race Winner │ │  Lap Time   │ │ Pit Window  │           │
│  │ Prediction  │ │ Prediction  │ │ Classifier  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │    DNF      │ │   Custom    │ │   Import    │           │
│  │    Risk     │ │   Model     │ │   Notebook  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                              │
│  Step 2: Configure Data                                      │
│  Seasons: [2020] [2021] [2022] [2023] [2024]               │
│  Circuits: [All] or [Select specific...]                    │
│  Conditions: [Dry] [Wet] [Mixed]                            │
│                                                              │
│  Step 3: Select Features                                     │
│  ☑ Driver form features                                     │
│  ☑ Team performance features                                │
│  ☑ Track-specific features                                  │
│  ☐ Telemetry features (requires more data)                  │
│  ☐ Weather features                                         │
│                                                              │
│  Step 4: Training Configuration                              │
│  Algorithm: [XGBoost ▼]                                     │
│  Auto-tune hyperparameters: [Yes]                           │
│  Cross-validation folds: [5]                                │
│                                                              │
│  [Start Training]                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Experiment Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                    Experiment: race_winner_v3                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Status: ✅ Completed                                        │
│  Duration: 12m 34s                                           │
│  Created: 2024-03-15 14:30                                   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Metrics                            │   │
│  │  Accuracy: 47.2%                                    │   │
│  │  Precision: 0.45                                    │   │
│  │  Recall: 0.48                                       │   │
│  │  F1 Score: 0.46                                     │   │
│  │  ROC AUC: 0.72                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Feature Importance                      │   │
│  │  ████████████████████ quali_position (0.25)         │   │
│  │  ████████████████ driver_form (0.20)                │   │
│  │  ██████████████ team_performance (0.18)             │   │
│  │  ██████████ track_history (0.12)                    │   │
│  │  ████████ weather_condition (0.10)                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  [Deploy Model] [Compare] [Download] [Share]                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Jupyter Integration

### Notebook Templates

```python
# Template: Race Prediction Model

import pitwall as pw
from pitwall.ml import ModelBuilder, FeatureStore

# Load data
fs = FeatureStore()
data = fs.get_features(
    seasons=[2022, 2023, 2024],
    feature_groups=['driver', 'team', 'session']
)

# Build model
builder = ModelBuilder(
    task='classification',
    target='race_winner'
)

# Train
model = builder.train(
    data,
    algorithm='xgboost',
    auto_tune=True
)

# Evaluate
results = model.evaluate(test_data)
results.plot_confusion_matrix()
results.plot_feature_importance()

# Deploy
model.deploy(name='race_winner_v1')
```

### Custom Feature Engineering

```python
from pitwall.features import FeatureEngineer

fe = FeatureEngineer()

# Create custom feature
@fe.register('momentum_score')
def momentum_score(driver_data):
    """Calculate driver momentum based on recent results"""
    recent_positions = driver_data['positions_last_5']
    weights = [0.35, 0.25, 0.20, 0.12, 0.08]

    score = sum(
        (21 - pos) * weight
        for pos, weight in zip(recent_positions, weights)
    )
    return score / 20  # Normalize to 0-1

# Use in training
data = fs.get_features(
    custom_features=['momentum_score']
)
```

---

## Model Deployment

### Deployment Options

#### 1. REST API
```bash
POST /api/v1/predict/race_winner
{
    "race": "monaco_2024",
    "grid_positions": {...}
}
```

#### 2. Real-time Inference
```python
# Connect model to live data stream
model.connect_to_stream(
    source='openf1',
    update_frequency='per_lap'
)
```

#### 3. Batch Prediction
```python
# Predict entire championship
predictions = model.predict_championship(
    season=2025,
    remaining_races=True
)
```

---

## AutoML Mode

### Supported Frameworks

| Framework | Use Case | Performance |
|-----------|----------|-------------|
| FLAML | Fast, general purpose | Good |
| Auto-sklearn | High accuracy | Best |
| H2O AutoML | Scalable | Good |
| PyCaret | Easy to use | Moderate |

### AutoML Configuration

```python
from pitwall.ml import AutoMLTrainer

trainer = AutoMLTrainer(
    task='classification',
    time_budget=3600,  # 1 hour
    metric='accuracy',
    ensemble=True
)

best_model = trainer.train(data)
print(f"Best model: {best_model.algorithm}")
print(f"Accuracy: {best_model.score}")
```

---

## Experiment Tracking

### MLflow Integration

```python
import mlflow

with mlflow.start_run(run_name="race_winner_xgb_v3"):
    # Log parameters
    mlflow.log_params({
        "algorithm": "xgboost",
        "max_depth": 6,
        "learning_rate": 0.1
    })

    # Train model
    model = train_model(params)

    # Log metrics
    mlflow.log_metrics({
        "accuracy": 0.47,
        "f1_score": 0.46
    })

    # Log model
    mlflow.sklearn.log_model(model, "model")
```

### Experiment Comparison

```
┌──────────────────────────────────────────────────────────────────┐
│                    Compare Experiments                            │
├──────────────────────────────────────────────────────────────────┤
│  Experiment    │ Algorithm │ Accuracy │ F1    │ Training Time   │
├────────────────┼───────────┼──────────┼───────┼─────────────────┤
│  race_v1       │ XGBoost   │ 42.1%    │ 0.41  │ 5m 12s          │
│  race_v2       │ LightGBM  │ 44.8%    │ 0.43  │ 3m 45s          │
│  race_v3 ★     │ CatBoost  │ 47.2%    │ 0.46  │ 8m 21s          │
│  race_v4       │ Ensemble  │ 46.5%    │ 0.45  │ 15m 33s         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Model Sharing

### Community Marketplace

```
┌─────────────────────────────────────────────────────────────┐
│                    Model Marketplace                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🏆 Top Models This Week                                     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🥇 Pit Stop Optimizer Pro                            │   │
│  │    by @f1_ml_guru | ⭐ 4.8 | Downloads: 1.2k        │   │
│  │    Predicts optimal pit windows with 78% accuracy   │   │
│  │    [Preview] [Download] [Fork]                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🥈 Rain Race Predictor                               │   │
│  │    by @weather_racing | ⭐ 4.6 | Downloads: 890     │   │
│  │    Specialized model for wet weather predictions    │   │
│  │    [Preview] [Download] [Fork]                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Resource Limits

### Free Tier
- 5 training jobs per day
- 1 hour max training time
- 100MB dataset limit
- 3 deployed models

### Pro Tier
- Unlimited training jobs
- 8 hours max training time
- 5GB dataset limit
- Unlimited deployed models
- GPU access

---

## Related Documentation

- [ML Analysis](../../ml-analysis/README.md)
- [Models](../../ml-analysis/models/README.md)
- [Datasets](../../ml-analysis/datasets/README.md)
- [Training Pipelines](../../ml-analysis/training-pipelines/README.md)
