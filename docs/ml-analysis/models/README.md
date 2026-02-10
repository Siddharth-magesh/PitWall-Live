# ML Models

## Overview

This document details the machine learning models used in PitWall Live, including architectures, training approaches, and performance benchmarks.

---

## Model Inventory

### Production Models

| Model ID | Name | Type | Version | Accuracy |
|----------|------|------|---------|----------|
| `race_winner` | Race Winner Predictor | Classification | v3.2 | 47% |
| `lap_time` | Lap Time Predictor | Regression | v2.1 | MAE 0.31s |
| `tire_deg` | Tire Degradation | Time Series | v1.5 | MAE 0.02s |
| `pit_window` | Pit Window Classifier | Classification | v2.0 | 75% |
| `dnf_risk` | DNF Risk Predictor | Binary Classification | v1.3 | 71% |
| `quali_order` | Qualifying Order | Learning to Rank | v2.4 | NDCG 0.89 |

---

## Race Winner Prediction

### Model Architecture

```python
class RaceWinnerModel:
    """
    Multi-class classification model for predicting race winner

    Architecture: Ensemble of XGBoost + CatBoost + Neural Network
    """

    def __init__(self):
        self.xgb = XGBClassifier(
            n_estimators=500,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            reg_alpha=0.1,
            reg_lambda=1.0
        )

        self.catboost = CatBoostClassifier(
            iterations=500,
            depth=8,
            learning_rate=0.05,
            cat_features=['circuit_type', 'weather'],
            verbose=False
        )

        self.neural = MLPClassifier(
            hidden_layer_sizes=(256, 128, 64),
            activation='relu',
            alpha=0.001,
            max_iter=500
        )

        self.meta_learner = LogisticRegression()

    def fit(self, X, y):
        # Train base models
        self.xgb.fit(X, y)
        self.catboost.fit(X, y)
        self.neural.fit(X, y)

        # Create meta-features
        meta_X = np.column_stack([
            self.xgb.predict_proba(X),
            self.catboost.predict_proba(X),
            self.neural.predict_proba(X)
        ])

        # Train meta-learner
        self.meta_learner.fit(meta_X, y)

    def predict_proba(self, X):
        meta_X = np.column_stack([
            self.xgb.predict_proba(X),
            self.catboost.predict_proba(X),
            self.neural.predict_proba(X)
        ])
        return self.meta_learner.predict_proba(meta_X)
```

### Feature Importance

```
Top Features for Race Winner Prediction

Grid Position          ████████████████████████████ 28%
Qualifying Gap         █████████████████████████ 25%
Driver Form (Last 5)   ███████████████████ 19%
Team Performance       ████████████████ 16%
Track History          ██████████ 10%
Weather Condition      ██ 2%
```

### Performance by Track Type

| Track Type | Accuracy | Top-3 Accuracy | Notes |
|------------|----------|----------------|-------|
| Street Circuits | 52% | 82% | Pole advantage high |
| Power Circuits | 44% | 75% | More unpredictable |
| High Downforce | 48% | 80% | Aero advantage matters |
| Mixed | 46% | 78% | Average performance |

---

## Lap Time Prediction

### Model Architecture

```python
class LapTimeModel:
    """
    Regression model for predicting lap times

    Architecture: LightGBM with feature engineering
    """

    def __init__(self):
        self.model = LGBMRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            num_leaves=31,
            min_child_samples=20,
            subsample=0.8,
            colsample_bytree=0.8
        )

        self.scaler = StandardScaler()

    def preprocess(self, X):
        # Engineer lap-specific features
        X['tire_performance'] = X['tire_age'] * X['deg_rate']
        X['fuel_effect'] = X['fuel_load'] * 0.03  # 0.03s per kg
        X['track_evolution'] = X['session_time'] * X['rubber_rate']

        return self.scaler.fit_transform(X)

    def fit(self, X, y):
        X_processed = self.preprocess(X)
        self.model.fit(X_processed, y)

    def predict(self, X):
        X_processed = self.preprocess(X)
        return self.model.predict(X_processed)
```

### Error Analysis

```
Lap Time Prediction Error Distribution

Error (s) │ Frequency
──────────┼──────────────────────────────────────
  < 0.1   │ ████████████████████████ 24%
0.1 - 0.2 │ ██████████████████████████████████ 34%
0.2 - 0.3 │ ████████████████████████ 24%
0.3 - 0.5 │ ██████████████ 14%
  > 0.5   │ ████ 4%

Mean Absolute Error: 0.31s
Median Absolute Error: 0.22s
95th Percentile Error: 0.58s
```

---

## Tire Degradation Model

### Architecture: LSTM with Attention

```python
class TireDegradationModel(nn.Module):
    """
    Time series model for predicting tire degradation curve

    Architecture: LSTM with self-attention
    """

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
            num_heads=4,
            dropout=0.1
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # x shape: (batch, seq_len, features)
        lstm_out, _ = self.lstm(x)

        # Self-attention
        attn_out, _ = self.attention(
            lstm_out.transpose(0, 1),
            lstm_out.transpose(0, 1),
            lstm_out.transpose(0, 1)
        )
        attn_out = attn_out.transpose(0, 1)

        # Predict degradation for each lap
        out = self.fc(attn_out)
        return out.squeeze(-1)
```

### Input Features

| Feature | Description | Type |
|---------|-------------|------|
| lap_time | Current lap time | Numeric |
| tire_age | Laps on current tire | Integer |
| compound | Tire compound | Categorical |
| fuel_load | Estimated fuel | Numeric |
| track_temp | Track temperature | Numeric |
| air_temp | Air temperature | Numeric |
| corner_count | Corners on circuit | Integer |
| avg_corner_speed | Average corner speed | Numeric |
| braking_intensity | Braking performance | Numeric |
| driver_style | Aggressive/conservative | Categorical |
| track_evolution | Rubber buildup | Numeric |
| weather | Current conditions | Categorical |

---

## Pit Stop Strategy Model

### Reinforcement Learning Approach

```python
class PitStrategyAgent:
    """
    Deep Q-Network for pit stop timing optimization

    State: Race position, gaps, tire age, laps remaining, etc.
    Action: Pit now with compound X, or stay out
    Reward: Final position relative to optimal
    """

    def __init__(self, state_size=20, action_size=4):
        # Actions: [Stay, Pit-Soft, Pit-Medium, Pit-Hard]
        self.model = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_size)
        )

        self.target_model = copy.deepcopy(self.model)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.memory = deque(maxlen=10000)
        self.gamma = 0.99
        self.epsilon = 1.0

    def get_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.action_size)

        with torch.no_grad():
            q_values = self.model(torch.FloatTensor(state))
            return q_values.argmax().item()

    def train(self, batch_size=32):
        if len(self.memory) < batch_size:
            return

        batch = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        # Double DQN update
        current_q = self.model(states).gather(1, actions)
        next_actions = self.model(next_states).argmax(1)
        next_q = self.target_model(next_states).gather(1, next_actions)

        target_q = rewards + self.gamma * next_q * (1 - dones)

        loss = F.mse_loss(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
```

### Training Environment

```python
class RaceSimulator:
    """
    Simulation environment for training RL agent
    """

    def __init__(self, circuit, weather='dry'):
        self.circuit = circuit
        self.weather = weather
        self.reset()

    def reset(self):
        self.lap = 0
        self.position = np.random.randint(1, 21)
        self.tire_age = 0
        self.compound = 'medium'
        self.fuel_load = 110  # kg
        return self._get_state()

    def step(self, action):
        # Execute action
        if action > 0:  # Pit stop
            self._execute_pit(action)

        # Simulate lap
        self._simulate_lap()

        # Calculate reward
        reward = self._calculate_reward()

        # Check if race finished
        done = self.lap >= self.total_laps

        return self._get_state(), reward, done
```

---

## Commentary Generation Model

### LLM Configuration

```python
class CommentaryGenerator:
    """
    Generate live commentary using Claude API
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-3-5-sonnet-20241022"

    async def generate(
        self,
        event: RaceEvent,
        context: RaceContext,
        style: str = "casual"
    ) -> str:
        system_prompt = self._build_system_prompt(style)
        user_prompt = self._build_event_prompt(event, context)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=200,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        return self._validate_response(response.content[0].text)

    def _build_system_prompt(self, style):
        styles = {
            "technical": """You are a technical F1 analyst providing
                data-driven commentary with precise statistics.""",
            "casual": """You are an enthusiastic F1 commentator
                making racing accessible and exciting for all fans.""",
            "dramatic": """You are a passionate motorsport commentator
                capturing the emotion and tension of every moment."""
        }
        return styles.get(style, styles["casual"])
```

---

## Model Comparison

### Race Winner Models

| Model | Accuracy | Top-3 Acc | Training Time | Inference |
|-------|----------|-----------|---------------|-----------|
| XGBoost | 45% | 76% | 5 min | 10ms |
| CatBoost | 46% | 77% | 8 min | 12ms |
| LightGBM | 44% | 75% | 3 min | 8ms |
| Neural Net | 43% | 74% | 15 min | 5ms |
| Ensemble | **47%** | **78%** | 30 min | 35ms |

### Ensemble Weights

```
Ensemble Combination (Stacking)

XGBoost     ████████████████████ 35%
CatBoost    ██████████████████ 30%
Neural Net  ████████████████ 25%
LightGBM    ██████ 10%
```

---

## Model Cards

### Race Winner Prediction Model Card

```yaml
model_name: race_winner_prediction
version: 3.2.0
type: Multi-class Classification
task: Predict Formula 1 race winner

training_data:
  seasons: 2018-2024
  races: 142
  samples: 2840 (driver-race pairs)

features:
  count: 45
  categories:
    - driver_performance (15)
    - team_performance (10)
    - circuit_specific (8)
    - session_specific (12)

performance:
  accuracy: 0.47
  top_3_accuracy: 0.78
  log_loss: 1.82
  brier_score: 0.15

limitations:
  - First-lap incidents unpredictable
  - New regulations require retraining
  - Weather changes impact accuracy
  - Limited sample size for rare events

ethical_considerations:
  - Not for betting purposes
  - Predictions are probabilistic
  - Historical bias may exist

last_updated: 2024-03-15
maintainer: PitWall ML Team
```

---

## Related Documentation

- [Datasets](../datasets/README.md)
- [Training Pipelines](../training-pipelines/README.md)
- [Evaluation](../evaluation/README.md)
