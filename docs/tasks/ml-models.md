# ML/AI Tasks

## Overview

Detailed task breakdown for machine learning model development, training infrastructure, and AI-powered features.

---

## Model Development

### ML-001: Set Up Feature Store
**Priority:** P0 | **Effort:** L | **Dependencies:** DAT-005

**Description:**
Implement a feature store for managing ML features.

**Acceptance Criteria:**
- [ ] Feature definitions and schemas
- [ ] Offline feature computation
- [ ] Online feature serving
- [ ] Feature versioning
- [ ] Point-in-time correctness

**Implementation:**
```python
# ml/feature_store.py
from feast import FeatureStore

class PitWallFeatureStore:
    def __init__(self, config_path: str):
        self.store = FeatureStore(repo_path=config_path)

    def get_training_data(
        self,
        entity_df: pd.DataFrame,
        feature_refs: List[str]
    ) -> pd.DataFrame:
        """Get historical features for training"""
        return self.store.get_historical_features(
            entity_df=entity_df,
            features=feature_refs
        ).to_df()

    def get_online_features(
        self,
        entity_rows: List[Dict]
    ) -> Dict:
        """Get features for real-time inference"""
        return self.store.get_online_features(
            features=[
                "driver_features:avg_quali_last_5",
                "driver_features:avg_finish_last_5",
                "team_features:constructor_position",
            ],
            entity_rows=entity_rows
        ).to_dict()
```

---

### ML-002: Implement Race Winner Model
**Priority:** P0 | **Effort:** L | **Dependencies:** ML-001

**Description:**
Build and train the race winner prediction model.

**Model Architecture:**
```python
# ml/models/race_winner.py
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

class RaceWinnerModel:
    def __init__(self):
        self.pipeline = Pipeline([
            ('preprocessor', self._build_preprocessor()),
            ('classifier', XGBClassifier(
                n_estimators=500,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                use_label_encoder=False,
                eval_metric='mlogloss'
            ))
        ])

    def _build_preprocessor(self):
        numeric_features = [
            'grid_position', 'quali_gap', 'avg_finish_last_5',
            'driver_wins_at_circuit', 'team_points'
        ]
        categorical_features = ['circuit_type', 'weather']

        return ColumnTransformer([
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(), categorical_features)
        ])

    def train(self, X: pd.DataFrame, y: pd.Series):
        self.pipeline.fit(X, y)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict_proba(X)
```

**Training Script:**
```python
# scripts/train_race_winner.py
import mlflow
from ml.models import RaceWinnerModel
from ml.feature_store import PitWallFeatureStore

def train():
    mlflow.set_experiment("race_winner")

    with mlflow.start_run():
        # Load data
        fs = PitWallFeatureStore("feature_store/")
        X, y = load_training_data(fs, seasons=[2020, 2021, 2022, 2023])

        # Train
        model = RaceWinnerModel()
        model.train(X, y)

        # Evaluate
        cv_scores = cross_val_score(model.pipeline, X, y, cv=5)

        # Log
        mlflow.log_metric("cv_accuracy_mean", cv_scores.mean())
        mlflow.log_metric("cv_accuracy_std", cv_scores.std())
        mlflow.sklearn.log_model(model.pipeline, "model")

if __name__ == "__main__":
    train()
```

**Acceptance Criteria:**
- [ ] Model achieves >45% accuracy on test set
- [ ] Cross-validation implemented
- [ ] Feature importance analysis
- [ ] Model card documented
- [ ] MLflow tracking integrated

---

### ML-003: Create Model Training Pipeline
**Priority:** P0 | **Effort:** L | **Dependencies:** ML-002, INF-005

**Description:**
Build automated training pipeline with MLflow.

**Pipeline Steps:**
1. Data validation
2. Feature computation
3. Model training
4. Evaluation
5. Model registration
6. Promotion (if better)

**Implementation:**
```python
# ml/pipelines/training_pipeline.py
from prefect import flow, task

@task
def validate_data(data: pd.DataFrame) -> bool:
    """Validate training data quality"""
    checks = [
        len(data) > 1000,
        data.isnull().sum().max() < len(data) * 0.05,
        data['target'].nunique() >= 10
    ]
    return all(checks)

@task
def compute_features(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Compute ML features"""
    feature_pipeline = FeaturePipeline()
    return feature_pipeline.transform(raw_data)

@task
def train_model(features: pd.DataFrame, model_class: type) -> Model:
    """Train model with hyperparameter tuning"""
    X = features.drop('target', axis=1)
    y = features['target']

    model = model_class()
    model.train(X, y)
    return model

@task
def evaluate_model(model: Model, test_data: pd.DataFrame) -> Dict:
    """Evaluate model performance"""
    X_test = test_data.drop('target', axis=1)
    y_test = test_data['target']

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)

    return {
        'accuracy': accuracy_score(y_test, predictions),
        'log_loss': log_loss(y_test, probabilities),
        'top_3_accuracy': top_k_accuracy(y_test, probabilities, k=3)
    }

@task
def register_model(model: Model, metrics: Dict, model_name: str):
    """Register model in MLflow"""
    with mlflow.start_run():
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, model_name)

        if should_promote(model_name, metrics):
            mlflow.register_model(
                f"runs:/{mlflow.active_run().info.run_id}/{model_name}",
                model_name
            )

@flow
def training_pipeline(model_name: str, seasons: List[int]):
    """Full training pipeline"""
    # Load and validate
    raw_data = load_raw_data(seasons)
    is_valid = validate_data(raw_data)

    if not is_valid:
        raise ValueError("Data validation failed")

    # Split data
    train_data, test_data = split_data(raw_data)

    # Compute features
    train_features = compute_features(train_data)
    test_features = compute_features(test_data)

    # Train
    model = train_model(train_features, get_model_class(model_name))

    # Evaluate
    metrics = evaluate_model(model, test_features)

    # Register
    register_model(model, metrics, model_name)

    return metrics
```

---

### ML-005: Implement Lap Time Prediction Model
**Priority:** P1 | **Effort:** L | **Dependencies:** ML-001

**Description:**
Build model for predicting lap times.

**Architecture:**
```python
# ml/models/lap_time.py
from lightgbm import LGBMRegressor

class LapTimeModel:
    def __init__(self):
        self.model = LGBMRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            num_leaves=31,
            feature_fraction=0.8,
            bagging_fraction=0.8,
            bagging_freq=5
        )

    def train(self, X: pd.DataFrame, y: pd.Series):
        # Feature engineering
        X_transformed = self._engineer_features(X)
        self.model.fit(X_transformed, y)

    def _engineer_features(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        # Tire degradation estimate
        X['tire_performance'] = X['tire_age'] * X['deg_rate']
        # Fuel effect (0.03s per kg)
        X['fuel_effect'] = X['fuel_load'] * 0.03
        # Track evolution
        X['track_evolution'] = X['session_time'] * X['rubber_rate']
        return X
```

**Acceptance Criteria:**
- [ ] MAE < 0.35 seconds
- [ ] Handles tire compounds correctly
- [ ] Accounts for fuel load
- [ ] Works across different circuits

---

### ML-006: Create Tire Degradation Model
**Priority:** P1 | **Effort:** L | **Dependencies:** ML-001

**Description:**
Implement time-series model for tire degradation prediction.

**Architecture (LSTM):**
```python
# ml/models/tire_degradation.py
import torch
import torch.nn as nn

class TireDegradationLSTM(nn.Module):
    def __init__(self, input_size=12, hidden_size=64, num_layers=2):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )

        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=4
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # LSTM encoding
        lstm_out, _ = self.lstm(x)

        # Self-attention
        attn_out, _ = self.attention(
            lstm_out.transpose(0, 1),
            lstm_out.transpose(0, 1),
            lstm_out.transpose(0, 1)
        )
        attn_out = attn_out.transpose(0, 1)

        # Predict degradation
        out = self.fc(attn_out)
        return out.squeeze(-1)
```

**Training:**
```python
# scripts/train_tire_deg.py
def train_tire_model():
    model = TireDegradationLSTM()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    for epoch in range(100):
        for batch in dataloader:
            X, y = batch
            optimizer.zero_grad()

            predictions = model(X)
            loss = criterion(predictions, y)

            loss.backward()
            optimizer.step()

        # Validation
        val_loss = validate(model, val_loader)
        print(f"Epoch {epoch}: Val Loss = {val_loss:.4f}")
```

---

## Commentary Engine

### COM-001: Design Commentary System Architecture
**Priority:** P1 | **Effort:** M | **Dependencies:** None

**Description:**
Design the end-to-end commentary generation system.

**Architecture:**
```
┌─────────────────┐
│   Event Queue   │ ← Events from Event Detector
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context Builder │ ← Race state, history, driver info
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Prompt Engine  │ ← Style-specific prompts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM (Claude)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validator     │ ← Fact checking, rate limiting
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Broadcaster   │ → WebSocket, API
└─────────────────┘
```

---

### COM-002: Implement Event Detection System
**Priority:** P1 | **Effort:** L | **Dependencies:** DAT-004

**Description:**
Build system to detect commentary-worthy events.

**Event Types:**
```python
# ml/commentary/events.py
from enum import Enum
from pydantic import BaseModel

class EventPriority(Enum):
    CRITICAL = 0  # Crashes, red flags, lead changes
    HIGH = 1      # Overtakes, pit stops, fastest laps
    MEDIUM = 2    # DRS, gap changes
    LOW = 3       # Sector improvements

class RaceEvent(BaseModel):
    type: str
    priority: EventPriority
    timestamp: datetime
    driver: str
    details: Dict

class OvertakeEvent(RaceEvent):
    type: str = "overtake"
    passed_driver: str
    corner: int
    method: str  # "drs", "braking", "switchback"

class PitStopEvent(RaceEvent):
    type: str = "pit_stop"
    duration: float
    new_compound: str
    tire_age_old: int
```

---

### COM-004: Integrate Claude API
**Priority:** P1 | **Effort:** M | **Dependencies:** COM-003

**Description:**
Implement Claude API integration for commentary generation.

```python
# ml/commentary/generator.py
import anthropic

class CommentaryGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-3-5-sonnet-20241022"

    async def generate(
        self,
        event: RaceEvent,
        context: RaceContext,
        style: str = "casual"
    ) -> Commentary:
        system_prompt = self._get_system_prompt(style)
        user_prompt = self._build_prompt(event, context)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=200,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        text = response.content[0].text
        return Commentary(
            text=text,
            event=event,
            style=style,
            generated_at=datetime.now()
        )

    def _get_system_prompt(self, style: str) -> str:
        prompts = {
            "technical": """You are a technical F1 analyst. Provide
                data-driven commentary with precise statistics.
                Focus on lap times, gaps, tire degradation, and
                strategy implications.""",

            "casual": """You are an enthusiastic F1 commentator.
                Make racing exciting and accessible for all fans.
                Use clear language and explain technical concepts
                simply when needed.""",

            "dramatic": """You are a passionate motorsport commentator.
                Capture the emotion and tension of every moment.
                Build excitement and convey the stakes of each event."""
        }
        return prompts.get(style, prompts["casual"])

    def _build_prompt(self, event: RaceEvent, context: RaceContext) -> str:
        return f"""
        Current Race State:
        - Lap: {context.current_lap}/{context.total_laps}
        - Leader: {context.leader} with gap of {context.leader_gap}s
        - Weather: {context.weather}

        Recent Event:
        {event.type}: {event.details}

        Generate a single commentary line (1-2 sentences) for this event.
        """
```

---

## Reinforcement Learning

### RL-001: Pit Strategy RL Agent
**Priority:** P2 | **Effort:** XL | **Dependencies:** ML-006

**Description:**
Implement RL agent for pit stop optimization.

```python
# ml/rl/pit_strategy.py
import gymnasium as gym
from stable_baselines3 import PPO

class RaceEnvironment(gym.Env):
    """Custom environment for race simulation"""

    def __init__(self, circuit: str, weather: str = 'dry'):
        super().__init__()

        # Action: [Stay, Pit-Soft, Pit-Medium, Pit-Hard]
        self.action_space = gym.spaces.Discrete(4)

        # State: position, gaps, tire_age, compound, fuel, laps_remaining
        self.observation_space = gym.spaces.Box(
            low=0, high=1, shape=(20,), dtype=np.float32
        )

        self.circuit = circuit
        self.weather = weather

    def step(self, action):
        if action > 0:  # Pit stop
            self._execute_pit(action)

        self._simulate_lap()

        obs = self._get_observation()
        reward = self._calculate_reward()
        done = self.lap >= self.total_laps

        return obs, reward, done, False, {}

    def _calculate_reward(self):
        # Reward based on position improvement
        position_reward = (20 - self.position) / 20

        # Penalty for bad tire management
        tire_penalty = max(0, self.tire_age - 30) * 0.01

        return position_reward - tire_penalty
```

---

## Evaluation & Monitoring

### ML-EVAL-001: Model Monitoring
**Priority:** P1 | **Effort:** M | **Dependencies:** ML-002

**Description:**
Implement monitoring for production models.

```python
# ml/monitoring/model_monitor.py
class ModelMonitor:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.prometheus = PrometheusMetrics()

    def log_prediction(
        self,
        features: Dict,
        prediction: Any,
        actual: Any = None
    ):
        # Log to Prometheus
        self.prometheus.prediction_counter.inc()

        # Check for drift
        if self._detect_feature_drift(features):
            self.prometheus.drift_counter.inc()
            self._alert_drift()

        # Log accuracy if actual provided
        if actual is not None:
            is_correct = prediction == actual
            self.prometheus.accuracy_gauge.set(
                self._rolling_accuracy(is_correct)
            )

    def _detect_feature_drift(self, features: Dict) -> bool:
        """Detect if features have drifted from training distribution"""
        # Calculate PSI or KS statistic
        pass
```
