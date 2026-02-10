"""
Feature Engineering
===================

Comprehensive feature engineering for F1 machine learning models.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, Callable
from functools import wraps

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Feature engineering pipeline for F1 data.

    Creates features for:
    - Driver performance
    - Team performance
    - Circuit characteristics
    - Session-specific metrics
    - Telemetry-derived features
    """

    def __init__(self):
        self._feature_registry = {}
        self._register_default_features()

    def _register_default_features(self):
        """Register default feature computation functions."""
        # These will be populated by the decorator
        pass

    def register(self, name: str):
        """
        Decorator to register a feature computation function.

        Args:
            name: Feature name

        Example:
            @engineer.register("momentum_score")
            def compute_momentum(df):
                return df["Points"].rolling(3).mean()
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            self._feature_registry[name] = wrapper
            return wrapper

        return decorator

    # =========================================================================
    # Driver Features
    # =========================================================================

    def compute_driver_features(
        self,
        results: pd.DataFrame,
        driver_id: str,
        as_of_date: Optional[pd.Timestamp] = None,
        window: int = 5,
    ) -> Dict[str, float]:
        """
        Compute features for a specific driver.

        Args:
            results: Historical race results
            driver_id: Driver abbreviation
            as_of_date: Point-in-time for feature computation
            window: Rolling window size

        Returns:
            Dictionary of feature values
        """
        df = results[results["Abbreviation"] == driver_id].copy()

        if as_of_date:
            df = df[df["Date"] < as_of_date]

        if len(df) == 0:
            return self._default_driver_features()

        df = df.sort_values("Date")

        # Recent performance (last N races)
        recent = df.tail(window)

        features = {
            # Recent form
            "avg_finish_last_n": recent["Position"].mean() if "Position" in recent else np.nan,
            "avg_grid_last_n": recent["GridPosition"].mean() if "GridPosition" in recent else np.nan,
            "avg_points_last_n": recent["Points"].mean() if "Points" in recent else 0,

            # Win/podium rates
            "wins_last_n": (recent["Position"] == 1).sum() if "Position" in recent else 0,
            "podiums_last_n": (recent["Position"] <= 3).sum() if "Position" in recent else 0,
            "points_finishes_last_n": (recent["Position"] <= 10).sum() if "Position" in recent else 0,

            # Positions gained/lost
            "avg_positions_gained": recent["PositionsGained"].mean() if "PositionsGained" in recent else 0,

            # Reliability
            "dnf_rate": df["IsDNF"].mean() if "IsDNF" in df else 0,

            # Career stats
            "career_races": len(df),
            "career_wins": (df["Position"] == 1).sum() if "Position" in df else 0,
            "career_podiums": (df["Position"] <= 3).sum() if "Position" in df else 0,
            "career_points": df["Points"].sum() if "Points" in df else 0,

            # Current season
            "season_points": 0,  # Will be computed separately
            "season_position": 0,
        }

        return features

    def _default_driver_features(self) -> Dict[str, float]:
        """Return default feature values for unknown drivers."""
        return {
            "avg_finish_last_n": 15.0,
            "avg_grid_last_n": 15.0,
            "avg_points_last_n": 0.0,
            "wins_last_n": 0,
            "podiums_last_n": 0,
            "points_finishes_last_n": 0,
            "avg_positions_gained": 0.0,
            "dnf_rate": 0.1,
            "career_races": 0,
            "career_wins": 0,
            "career_podiums": 0,
            "career_points": 0.0,
            "season_points": 0.0,
            "season_position": 20,
        }

    # =========================================================================
    # Circuit Features
    # =========================================================================

    def compute_circuit_features(
        self,
        results: pd.DataFrame,
        circuit_name: str,
        driver_id: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Compute circuit-specific features.

        Args:
            results: Historical race results
            circuit_name: Circuit/Grand Prix name
            driver_id: Optional driver for driver-circuit features

        Returns:
            Dictionary of feature values
        """
        circuit_df = results[results["GrandPrix"] == circuit_name].copy()

        if len(circuit_df) == 0:
            return self._default_circuit_features()

        features = {
            # Circuit characteristics
            "circuit_races_in_data": len(circuit_df["Season"].unique()),

            # Safety car probability (from historical data)
            "circuit_sc_rate": 0.5,  # Would need SC data

            # Overtaking difficulty (based on position changes)
            "avg_position_changes": circuit_df["PositionsGained"].abs().mean() if "PositionsGained" in circuit_df else 3.0,

            # DNF rate at circuit
            "circuit_dnf_rate": circuit_df["IsDNF"].mean() if "IsDNF" in circuit_df else 0.1,
        }

        # Driver-specific circuit features
        if driver_id:
            driver_circuit = circuit_df[circuit_df["Abbreviation"] == driver_id]

            if len(driver_circuit) > 0:
                features.update({
                    "driver_circuit_races": len(driver_circuit),
                    "driver_circuit_avg_finish": driver_circuit["Position"].mean(),
                    "driver_circuit_best_finish": driver_circuit["Position"].min(),
                    "driver_circuit_wins": (driver_circuit["Position"] == 1).sum(),
                    "driver_circuit_podiums": (driver_circuit["Position"] <= 3).sum(),
                })
            else:
                features.update({
                    "driver_circuit_races": 0,
                    "driver_circuit_avg_finish": 10.0,
                    "driver_circuit_best_finish": 10,
                    "driver_circuit_wins": 0,
                    "driver_circuit_podiums": 0,
                })

        return features

    def _default_circuit_features(self) -> Dict[str, float]:
        """Return default circuit feature values."""
        return {
            "circuit_races_in_data": 0,
            "circuit_sc_rate": 0.5,
            "avg_position_changes": 3.0,
            "circuit_dnf_rate": 0.1,
        }

    # =========================================================================
    # Team Features
    # =========================================================================

    def compute_team_features(
        self,
        results: pd.DataFrame,
        team_name: str,
        as_of_date: Optional[pd.Timestamp] = None,
        window: int = 5,
    ) -> Dict[str, float]:
        """
        Compute team performance features.

        Args:
            results: Historical race results
            team_name: Team/constructor name
            as_of_date: Point-in-time for features
            window: Rolling window size

        Returns:
            Dictionary of feature values
        """
        df = results[results["TeamName"] == team_name].copy()

        if as_of_date:
            df = df[df["Date"] < as_of_date]

        if len(df) == 0:
            return self._default_team_features()

        df = df.sort_values("Date")

        # Aggregate by race (sum both drivers)
        team_races = df.groupby(["Season", "Round"]).agg({
            "Points": "sum",
            "Position": "mean",  # Average of both drivers
        }).reset_index()

        recent = team_races.tail(window)

        features = {
            "team_avg_points_last_n": recent["Points"].mean(),
            "team_avg_finish_last_n": recent["Position"].mean(),

            "team_season_points": 0,  # Will be computed separately
            "team_constructor_position": 5,  # Will be computed separately

            "team_reliability_rate": 1 - df["IsDNF"].mean() if "IsDNF" in df else 0.9,
        }

        return features

    def _default_team_features(self) -> Dict[str, float]:
        """Return default team feature values."""
        return {
            "team_avg_points_last_n": 5.0,
            "team_avg_finish_last_n": 10.0,
            "team_season_points": 0.0,
            "team_constructor_position": 5,
            "team_reliability_rate": 0.9,
        }

    # =========================================================================
    # Session Features
    # =========================================================================

    def compute_session_features(
        self,
        quali_results: pd.DataFrame,
        practice_laps: Optional[pd.DataFrame] = None,
        driver_id: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Compute session-specific features (qualifying, practice).

        Args:
            quali_results: Qualifying results
            practice_laps: Practice lap times
            driver_id: Driver abbreviation

        Returns:
            Dictionary of feature values
        """
        features = {}

        # Qualifying features
        if driver_id and len(quali_results) > 0:
            driver_quali = quali_results[
                quali_results["Abbreviation"] == driver_id
            ]

            if len(driver_quali) > 0:
                row = driver_quali.iloc[0]

                features["grid_position"] = row.get("Position", 10)

                # Gap to pole
                pole_time = quali_results[
                    quali_results["Position"] == 1
                ]["Q3"].iloc[0] if "Q3" in quali_results else None

                if pole_time and "Q3" in row and pd.notna(row["Q3"]):
                    # Convert to seconds and compute gap
                    driver_time = row["Q3"]
                    if hasattr(driver_time, "total_seconds"):
                        driver_time = driver_time.total_seconds()
                    if hasattr(pole_time, "total_seconds"):
                        pole_time = pole_time.total_seconds()

                    features["quali_gap_to_pole"] = driver_time - pole_time
                else:
                    features["quali_gap_to_pole"] = 1.0  # Default gap

        # Practice features (if available)
        if practice_laps is not None and driver_id and len(practice_laps) > 0:
            driver_practice = practice_laps[
                practice_laps["Driver"] == driver_id
            ]

            if len(driver_practice) > 0:
                features["fp_best_lap_time"] = driver_practice["LapTimeSeconds"].min()
                features["fp_avg_lap_time"] = driver_practice["LapTimeSeconds"].mean()
                features["fp_lap_count"] = len(driver_practice)

        return features

    # =========================================================================
    # Full Feature Pipeline
    # =========================================================================

    def build_race_features(
        self,
        race_results: pd.DataFrame,
        quali_results: pd.DataFrame,
        target_season: int,
        target_round: int,
    ) -> pd.DataFrame:
        """
        Build complete feature set for a race prediction.

        Args:
            race_results: Historical race results
            quali_results: Qualifying results for target race
            target_season: Season year
            target_round: Round number

        Returns:
            DataFrame with features for each driver
        """
        # Filter historical data (before target race)
        historical = race_results[
            (race_results["Season"] < target_season) |
            ((race_results["Season"] == target_season) &
             (race_results["Round"] < target_round))
        ]

        # Get target race info
        target_race = race_results[
            (race_results["Season"] == target_season) &
            (race_results["Round"] == target_round)
        ]

        if len(target_race) == 0:
            logger.warning(f"No data for {target_season} Round {target_round}")
            return pd.DataFrame()

        circuit_name = target_race["GrandPrix"].iloc[0]
        drivers = target_race["Abbreviation"].unique()

        # Build features for each driver
        feature_rows = []

        for driver in drivers:
            driver_row = target_race[target_race["Abbreviation"] == driver].iloc[0]

            # Compute all features
            driver_features = self.compute_driver_features(
                historical, driver, window=5
            )
            circuit_features = self.compute_circuit_features(
                historical, circuit_name, driver
            )
            team_features = self.compute_team_features(
                historical, driver_row["TeamName"], window=5
            )
            session_features = self.compute_session_features(
                quali_results, driver_id=driver
            )

            # Combine all features
            features = {
                "Season": target_season,
                "Round": target_round,
                "GrandPrix": circuit_name,
                "Driver": driver,
                "Team": driver_row["TeamName"],
                **driver_features,
                **circuit_features,
                **team_features,
                **session_features,
                # Target variable
                "Position": driver_row["Position"],
                "Points": driver_row["Points"],
                "IsWinner": driver_row["Position"] == 1,
                "IsPodium": driver_row["Position"] <= 3,
                "IsPoints": driver_row["Position"] <= 10,
            }

            feature_rows.append(features)

        return pd.DataFrame(feature_rows)

    def build_training_dataset(
        self,
        race_results: pd.DataFrame,
        quali_results: pd.DataFrame,
        seasons: List[int],
    ) -> pd.DataFrame:
        """
        Build complete training dataset for multiple seasons.

        Args:
            race_results: All race results
            quali_results: All qualifying results
            seasons: Seasons to include

        Returns:
            DataFrame with features and targets
        """
        all_features = []

        for season in seasons:
            season_races = race_results[race_results["Season"] == season]
            rounds = sorted(season_races["Round"].unique())

            for round_num in rounds:
                try:
                    # Get qualifying for this race
                    race_quali = quali_results[
                        (quali_results["Season"] == season) &
                        (quali_results["Round"] == round_num)
                    ]

                    race_features = self.build_race_features(
                        race_results, race_quali, season, round_num
                    )

                    if len(race_features) > 0:
                        all_features.append(race_features)

                except Exception as e:
                    logger.warning(
                        f"Could not build features for {season} R{round_num}: {e}"
                    )

        if not all_features:
            return pd.DataFrame()

        return pd.concat(all_features, ignore_index=True)

    # =========================================================================
    # Telemetry Features
    # =========================================================================

    def compute_telemetry_features(
        self,
        telemetry: pd.DataFrame,
    ) -> Dict[str, float]:
        """
        Compute features from telemetry data.

        Args:
            telemetry: Telemetry DataFrame

        Returns:
            Dictionary of telemetry features
        """
        features = {}

        if "Speed" in telemetry.columns:
            features["max_speed"] = telemetry["Speed"].max()
            features["avg_speed"] = telemetry["Speed"].mean()
            features["min_speed"] = telemetry["Speed"].min()

        if "Throttle" in telemetry.columns:
            features["avg_throttle"] = telemetry["Throttle"].mean()
            features["full_throttle_pct"] = (telemetry["Throttle"] >= 95).mean()

        if "Brake" in telemetry.columns:
            features["brake_usage_pct"] = (telemetry["Brake"] > 0).mean()
            features["heavy_brake_pct"] = (telemetry["Brake"] >= 50).mean()

        if "nGear" in telemetry.columns:
            features["avg_gear"] = telemetry["nGear"].mean()

        if "DRS" in telemetry.columns:
            features["drs_usage_pct"] = telemetry["DRS"].mean()

        return features

    # =========================================================================
    # Tire Degradation Features
    # =========================================================================

    def compute_tire_features(
        self,
        laps: pd.DataFrame,
        driver_id: str,
    ) -> pd.DataFrame:
        """
        Compute tire-related features from lap data.

        Args:
            laps: Lap times DataFrame
            driver_id: Driver abbreviation

        Returns:
            DataFrame with tire features per stint
        """
        driver_laps = laps[laps["Driver"] == driver_id].copy()

        if len(driver_laps) == 0:
            return pd.DataFrame()

        driver_laps = driver_laps.sort_values("LapNumber")

        # Identify stints (tire compound changes)
        if "Compound" in driver_laps.columns:
            driver_laps["StintNumber"] = (
                driver_laps["Compound"] != driver_laps["Compound"].shift()
            ).cumsum()
        else:
            driver_laps["StintNumber"] = 1

        # Compute tire age within stint
        driver_laps["TireAge"] = driver_laps.groupby("StintNumber").cumcount() + 1

        # Compute degradation rate per stint
        stint_features = []

        for stint, stint_df in driver_laps.groupby("StintNumber"):
            if len(stint_df) < 3:
                continue

            # Linear regression to get degradation rate
            if "LapTimeSeconds" in stint_df.columns:
                x = stint_df["TireAge"].values
                y = stint_df["LapTimeSeconds"].values

                # Remove outliers (pit laps, etc.)
                mask = ~np.isnan(y)
                if mask.sum() >= 3:
                    slope = np.polyfit(x[mask], y[mask], 1)[0]

                    stint_features.append({
                        "StintNumber": stint,
                        "Compound": stint_df["Compound"].iloc[0] if "Compound" in stint_df else "Unknown",
                        "StintLength": len(stint_df),
                        "DegradationRate": slope,  # seconds per lap
                        "AvgLapTime": y[mask].mean(),
                        "BestLapTime": y[mask].min(),
                    })

        return pd.DataFrame(stint_features)
