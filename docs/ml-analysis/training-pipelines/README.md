# Training Pipelines

## Overview

This document describes the machine learning training infrastructure for PitWall Live, including local development workflows, distributed training, and automated retraining pipelines.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING ORCHESTRATION                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌───────────┐    ┌───────────┐    ┌───────────┐          │
│   │   Data    │ -> │  Feature  │ -> │   Model   │          │
│   │   Loader  │    │  Pipeline │    │  Training │          │
│   └───────────┘    └───────────┘    └───────────┘          │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│   ┌───────────┐    ┌───────────┐    ┌───────────┐          │
│   │   Data    │    │  Feature  │    │   Model   │          │
│   │   Store   │    │   Store   │    │  Registry │          │
│   └───────────┘    └───────────┘    └───────────┘          │
│                                              │               │
│                          ┌───────────────────┘               │
│                          ▼                                   │
│                    ┌───────────┐                            │
│                    │Deployment │                            │
│                    │  Service  │                            │
│                    └───────────┘                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Local Training

### Quick Start

```bash
# Install dependencies
pip install -r requirements-ml.txt

# Run training
python -m pitwall.ml.train \
    --model race_winner \
    --seasons 2022,2023,2024 \
    --algorithm xgboost \
    --output models/race_winner_v1.pkl
```

### Training Script

```python
# train.py
import argparse
from pitwall.ml import ModelBuilder, FeatureStore
from pitwall.data import DataLoader
import mlflow

def main(args):
    # Initialize MLflow
    mlflow.set_experiment(args.experiment)

    with mlflow.start_run(run_name=args.run_name):
        # Load data
        loader = DataLoader()
        data = loader.load_training_data(
            seasons=args.seasons,
            target=args.target
        )

        # Split data
        X_train, X_test, y_train, y_test = data.split(
            test_size=0.2,
            random_state=42
        )

        # Log data info
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        mlflow.log_param("features", X_train.shape[1])

        # Build model
        builder = ModelBuilder(
            task=args.task,
            algorithm=args.algorithm
        )

        # Train
        model = builder.train(
            X_train, y_train,
            X_val=X_test, y_val=y_test,
            tune_hyperparams=args.tune
        )

        # Evaluate
        metrics = model.evaluate(X_test, y_test)
        mlflow.log_metrics(metrics)

        # Save model
        mlflow.sklearn.log_model(model, "model")

        print(f"Training complete. Accuracy: {metrics['accuracy']:.2%}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--seasons", nargs="+", type=int)
    parser.add_argument("--algorithm", default="xgboost")
    parser.add_argument("--tune", action="store_true")
    args = parser.parse_args()
    main(args)
```

---

## Distributed Training

### Ray Configuration

```python
# ray_training.py
import ray
from ray import tune
from ray.tune.schedulers import ASHAScheduler
from ray.tune.search.optuna import OptunaSearch

# Initialize Ray cluster
ray.init(address="auto")

# Define search space
search_space = {
    "n_estimators": tune.randint(100, 1000),
    "max_depth": tune.randint(3, 12),
    "learning_rate": tune.loguniform(0.001, 0.3),
    "subsample": tune.uniform(0.5, 1.0),
    "colsample_bytree": tune.uniform(0.5, 1.0),
    "min_child_weight": tune.randint(1, 10),
    "reg_alpha": tune.loguniform(0.001, 10),
    "reg_lambda": tune.loguniform(0.001, 10),
}

# Define training function
def train_model(config):
    from xgboost import XGBClassifier
    from sklearn.model_selection import cross_val_score

    model = XGBClassifier(**config)
    scores = cross_val_score(model, X_train, y_train, cv=5)

    tune.report(accuracy=scores.mean(), std=scores.std())

# Configure scheduler
scheduler = ASHAScheduler(
    max_t=100,
    grace_period=10,
    reduction_factor=3
)

# Configure search
search = OptunaSearch(metric="accuracy", mode="max")

# Run tuning
analysis = tune.run(
    train_model,
    config=search_space,
    num_samples=100,
    scheduler=scheduler,
    search_alg=search,
    resources_per_trial={"cpu": 4, "gpu": 0},
    local_dir="~/ray_results"
)

# Get best config
best_config = analysis.best_config
print(f"Best config: {best_config}")
print(f"Best accuracy: {analysis.best_result['accuracy']:.2%}")
```

### Kubernetes Job

```yaml
# training-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: race-winner-training
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: pitwall/ml-trainer:latest
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        env:
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow:5000"
        - name: MODEL_NAME
          value: "race_winner"
        - name: SEASONS
          value: "2022,2023,2024"
        volumeMounts:
        - name: data-volume
          mountPath: /data
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: training-data-pvc
      restartPolicy: Never
  backoffLimit: 3
```

---

## Automated Retraining

### Trigger Conditions

```python
class RetrainingTrigger:
    """
    Determines when to retrain models
    """

    def should_retrain(self, model_name: str) -> bool:
        triggers = [
            self._check_schedule(),
            self._check_performance_drift(),
            self._check_data_drift(),
            self._check_new_data(),
        ]
        return any(triggers)

    def _check_schedule(self) -> bool:
        """Retrain after each race weekend"""
        last_race = get_last_race_date()
        last_training = get_last_training_date(model_name)
        return last_race > last_training

    def _check_performance_drift(self) -> bool:
        """Retrain if prediction accuracy drops"""
        recent_accuracy = get_recent_accuracy(model_name, n=5)
        baseline_accuracy = get_baseline_accuracy(model_name)
        return recent_accuracy < baseline_accuracy * 0.9  # 10% drop

    def _check_data_drift(self) -> bool:
        """Retrain if input distribution changes"""
        current_stats = get_current_feature_stats()
        training_stats = get_training_feature_stats(model_name)
        drift_score = calculate_drift(current_stats, training_stats)
        return drift_score > 0.1  # 10% drift threshold

    def _check_new_data(self) -> bool:
        """Retrain when significant new data available"""
        new_samples = count_new_samples_since_training(model_name)
        return new_samples >= 20  # ~1 race worth
```

### Retraining Pipeline

```python
# retraining_pipeline.py
from prefect import flow, task
from prefect.schedules import CronSchedule

@task
def fetch_new_data():
    """Fetch latest race data"""
    from pitwall.data import DataFetcher
    fetcher = DataFetcher()
    return fetcher.fetch_latest()

@task
def validate_data(data):
    """Validate data quality"""
    from pitwall.data import DataValidator
    validator = DataValidator()
    return validator.validate(data)

@task
def compute_features(data):
    """Compute training features"""
    from pitwall.features import FeaturePipeline
    pipeline = FeaturePipeline()
    return pipeline.compute(data)

@task
def train_model(features, model_name):
    """Train model with new data"""
    from pitwall.ml import ModelBuilder
    builder = ModelBuilder(model_name)
    return builder.train(features)

@task
def evaluate_model(model, test_data):
    """Evaluate model performance"""
    return model.evaluate(test_data)

@task
def deploy_if_better(model, metrics, model_name):
    """Deploy if beats current production"""
    from pitwall.ml import ModelRegistry
    registry = ModelRegistry()

    current_metrics = registry.get_production_metrics(model_name)
    if metrics['accuracy'] > current_metrics['accuracy']:
        registry.promote_to_production(model, model_name)
        return True
    return False

@flow(schedule=CronSchedule("0 6 * * TUE"))  # Every Tuesday 6 AM
def retraining_pipeline():
    """Automated model retraining after race weekends"""

    # Fetch and validate data
    new_data = fetch_new_data()
    validated_data = validate_data(new_data)

    # Compute features
    features = compute_features(validated_data)

    # Train models
    models_to_retrain = ["race_winner", "quali_order", "pit_window"]

    for model_name in models_to_retrain:
        model = train_model(features, model_name)
        metrics = evaluate_model(model, features.test)
        deployed = deploy_if_better(model, metrics, model_name)

        if deployed:
            notify_team(f"{model_name} updated to production")
```

---

## Hyperparameter Tuning

### Optuna Integration

```python
import optuna
from optuna.integration import MLflowCallback

def objective(trial):
    """Optuna objective function"""

    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 0.001, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
    }

    model = XGBClassifier(**params)
    scores = cross_val_score(model, X_train, y_train, cv=5)

    return scores.mean()

# Create study
study = optuna.create_study(
    direction="maximize",
    study_name="race_winner_tuning",
    storage="postgresql://localhost/optuna"
)

# Add MLflow callback
mlflow_callback = MLflowCallback(
    tracking_uri="http://mlflow:5000",
    metric_name="accuracy"
)

# Run optimization
study.optimize(
    objective,
    n_trials=100,
    callbacks=[mlflow_callback],
    n_jobs=4
)

print(f"Best params: {study.best_params}")
print(f"Best accuracy: {study.best_value:.2%}")
```

---

## Training Monitoring

### Metrics Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                  TRAINING DASHBOARD                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Active Jobs: 3                                              │
│  Queued Jobs: 7                                              │
│  Completed Today: 12                                         │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Job: race_winner_v4                                 │   │
│  │  Status: Training (Epoch 45/100)                     │   │
│  │  Progress: ████████████████████░░░░░░░░░░ 45%       │   │
│  │  Current Accuracy: 0.462                             │   │
│  │  Best Accuracy: 0.468                                │   │
│  │  ETA: 12 minutes                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  Resource Usage:                                             │
│  CPU: ████████████████████░░░░ 78%                          │
│  Memory: ██████████████░░░░░░░░ 56%                         │
│  GPU: ████████████░░░░░░░░░░░░ 42%                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Alerting

```python
class TrainingAlerts:
    """Training failure and anomaly alerts"""

    def __init__(self, slack_webhook: str):
        self.slack = SlackClient(slack_webhook)

    def on_training_failure(self, job_id: str, error: Exception):
        self.slack.post({
            "text": f":x: Training job `{job_id}` failed",
            "attachments": [{
                "color": "danger",
                "text": str(error),
                "fields": [
                    {"title": "Job ID", "value": job_id},
                    {"title": "Error Type", "value": type(error).__name__},
                ]
            }]
        })

    def on_performance_regression(self, model: str, old: float, new: float):
        self.slack.post({
            "text": f":warning: Performance regression detected for `{model}`",
            "attachments": [{
                "color": "warning",
                "fields": [
                    {"title": "Previous Accuracy", "value": f"{old:.2%}"},
                    {"title": "New Accuracy", "value": f"{new:.2%}"},
                    {"title": "Delta", "value": f"{new - old:.2%}"},
                ]
            }]
        })
```

---

## Best Practices

### Training Checklist

- [ ] Data validation before training
- [ ] Feature scaling/normalization
- [ ] Cross-validation (time-series aware)
- [ ] Hyperparameter tuning
- [ ] Model evaluation on holdout set
- [ ] Comparison with baseline
- [ ] Model card documentation
- [ ] Artifact logging (MLflow)

### Time-Series Cross-Validation

```python
from sklearn.model_selection import TimeSeriesSplit

def time_series_cv(X, y, model, n_splits=5):
    """
    Walk-forward cross-validation for time series data
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = []

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        scores.append(score)

    return {
        "mean": np.mean(scores),
        "std": np.std(scores),
        "scores": scores
    }
```

---

## Related Documentation

- [Models](../models/README.md)
- [Datasets](../datasets/README.md)
- [Evaluation](../evaluation/README.md)
