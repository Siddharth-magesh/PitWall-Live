"""
Data Processor
==============

Data cleaning, validation, and preprocessing utilities.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Data processing and cleaning utilities for F1 data.

    Handles:
    - Missing value imputation
    - Outlier detection and handling
    - Data type conversions
    - Feature scaling
    """

    def __init__(self):
        self.scalers = {}
        self.encoders = {}

    # =========================================================================
    # Lap Time Processing
    # =========================================================================

    def clean_lap_times(
        self,
        laps: pd.DataFrame,
        remove_outliers: bool = True,
        min_lap_time: float = 60.0,
        max_lap_time: float = 180.0,
    ) -> pd.DataFrame:
        """
        Clean lap time data.

        Args:
            laps: DataFrame with lap times
            remove_outliers: Whether to remove outlier laps
            min_lap_time: Minimum valid lap time (seconds)
            max_lap_time: Maximum valid lap time (seconds)

        Returns:
            Cleaned DataFrame
        """
        df = laps.copy()

        # Convert LapTime to seconds if it's a timedelta
        if "LapTime" in df.columns:
            if pd.api.types.is_timedelta64_any_dtype(df["LapTime"]):
                df["LapTimeSeconds"] = df["LapTime"].dt.total_seconds()
            else:
                df["LapTimeSeconds"] = pd.to_numeric(
                    df["LapTime"], errors="coerce"
                )

        # Remove invalid lap times
        if remove_outliers and "LapTimeSeconds" in df.columns:
            initial_count = len(df)

            df = df[
                (df["LapTimeSeconds"] >= min_lap_time) &
                (df["LapTimeSeconds"] <= max_lap_time)
            ]

            removed = initial_count - len(df)
            if removed > 0:
                logger.info(f"Removed {removed} outlier laps")

        # Remove pit in/out laps if marked
        if "PitInTime" in df.columns:
            df = df[df["PitInTime"].isna()]

        if "PitOutTime" in df.columns:
            df = df[df["PitOutTime"].isna()]

        # Handle missing sector times
        sector_cols = ["Sector1Time", "Sector2Time", "Sector3Time"]
        for col in sector_cols:
            if col in df.columns:
                if pd.api.types.is_timedelta64_any_dtype(df[col]):
                    df[f"{col}Seconds"] = df[col].dt.total_seconds()

        return df

    def process_race_results(
        self,
        results: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Process race results data.

        Args:
            results: Raw race results DataFrame

        Returns:
            Processed DataFrame
        """
        df = results.copy()

        # Clean position data
        if "Position" in df.columns:
            df["Position"] = pd.to_numeric(df["Position"], errors="coerce")

        if "GridPosition" in df.columns:
            df["GridPosition"] = pd.to_numeric(
                df["GridPosition"], errors="coerce"
            )

        # Calculate positions gained/lost
        if "Position" in df.columns and "GridPosition" in df.columns:
            df["PositionsGained"] = df["GridPosition"] - df["Position"]

        # Encode status
        if "Status" in df.columns:
            df["IsFinished"] = df["Status"] == "Finished"
            df["IsDNF"] = ~df["IsFinished"]

        # Points to numeric
        if "Points" in df.columns:
            df["Points"] = pd.to_numeric(df["Points"], errors="coerce").fillna(0)

        return df

    # =========================================================================
    # Feature Scaling
    # =========================================================================

    def fit_scaler(
        self,
        df: pd.DataFrame,
        columns: List[str],
        scaler_name: str = "default",
    ) -> pd.DataFrame:
        """
        Fit and transform numeric columns with StandardScaler.

        Args:
            df: Input DataFrame
            columns: Columns to scale
            scaler_name: Name for storing the scaler

        Returns:
            DataFrame with scaled columns
        """
        df = df.copy()
        valid_cols = [c for c in columns if c in df.columns]

        if not valid_cols:
            return df

        scaler = StandardScaler()
        df[valid_cols] = scaler.fit_transform(df[valid_cols].fillna(0))

        self.scalers[scaler_name] = {
            "scaler": scaler,
            "columns": valid_cols,
        }

        return df

    def transform_scaler(
        self,
        df: pd.DataFrame,
        scaler_name: str = "default",
    ) -> pd.DataFrame:
        """
        Transform data using a fitted scaler.

        Args:
            df: Input DataFrame
            scaler_name: Name of the fitted scaler

        Returns:
            Transformed DataFrame
        """
        if scaler_name not in self.scalers:
            raise ValueError(f"Scaler '{scaler_name}' not found")

        df = df.copy()
        scaler_info = self.scalers[scaler_name]
        scaler = scaler_info["scaler"]
        columns = scaler_info["columns"]

        valid_cols = [c for c in columns if c in df.columns]
        df[valid_cols] = scaler.transform(df[valid_cols].fillna(0))

        return df

    # =========================================================================
    # Categorical Encoding
    # =========================================================================

    def encode_categorical(
        self,
        df: pd.DataFrame,
        columns: List[str],
        method: str = "label",
    ) -> pd.DataFrame:
        """
        Encode categorical columns.

        Args:
            df: Input DataFrame
            columns: Columns to encode
            method: Encoding method ("label" or "onehot")

        Returns:
            DataFrame with encoded columns
        """
        df = df.copy()

        for col in columns:
            if col not in df.columns:
                continue

            if method == "label":
                encoder = LabelEncoder()
                # Handle missing values
                df[col] = df[col].fillna("Unknown")
                df[f"{col}_encoded"] = encoder.fit_transform(df[col])
                self.encoders[col] = encoder

            elif method == "onehot":
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df, dummies], axis=1)

        return df

    # =========================================================================
    # Train/Test Split
    # =========================================================================

    def time_series_split(
        self,
        df: pd.DataFrame,
        date_column: str = "Date",
        test_size: float = 0.2,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data chronologically for time series validation.

        Args:
            df: Input DataFrame
            date_column: Column containing dates
            test_size: Proportion of data for testing

        Returns:
            Tuple of (train_df, test_df)
        """
        df = df.sort_values(date_column)
        split_idx = int(len(df) * (1 - test_size))

        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]

        logger.info(
            f"Split data: {len(train_df)} train, {len(test_df)} test"
        )

        return train_df, test_df

    def season_split(
        self,
        df: pd.DataFrame,
        train_seasons: List[int],
        test_seasons: List[int],
        season_column: str = "Season",
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data by season.

        Args:
            df: Input DataFrame
            train_seasons: Seasons for training
            test_seasons: Seasons for testing
            season_column: Column containing season year

        Returns:
            Tuple of (train_df, test_df)
        """
        train_df = df[df[season_column].isin(train_seasons)]
        test_df = df[df[season_column].isin(test_seasons)]

        logger.info(
            f"Split by season: {len(train_df)} train ({train_seasons}), "
            f"{len(test_df)} test ({test_seasons})"
        )

        return train_df, test_df

    # =========================================================================
    # Data Validation
    # =========================================================================

    def validate_data(
        self,
        df: pd.DataFrame,
        required_columns: List[str],
        min_rows: int = 100,
    ) -> Dict[str, Any]:
        """
        Validate data quality.

        Args:
            df: DataFrame to validate
            required_columns: Columns that must be present
            min_rows: Minimum number of rows required

        Returns:
            Validation report dictionary
        """
        report = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "stats": {},
        }

        # Check row count
        if len(df) < min_rows:
            report["errors"].append(
                f"Insufficient data: {len(df)} rows (need {min_rows})"
            )
            report["is_valid"] = False

        # Check required columns
        missing_cols = [c for c in required_columns if c not in df.columns]
        if missing_cols:
            report["errors"].append(
                f"Missing columns: {missing_cols}"
            )
            report["is_valid"] = False

        # Check for missing values
        null_counts = df.isnull().sum()
        high_null_cols = null_counts[null_counts > len(df) * 0.1].index.tolist()
        if high_null_cols:
            report["warnings"].append(
                f"High null percentage in: {high_null_cols}"
            )

        # Statistics
        report["stats"] = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "null_counts": null_counts.to_dict(),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }

        return report

    # =========================================================================
    # Aggregations
    # =========================================================================

    def compute_driver_stats(
        self,
        results: pd.DataFrame,
        window: int = 5,
    ) -> pd.DataFrame:
        """
        Compute rolling statistics for drivers.

        Args:
            results: Race results DataFrame
            window: Rolling window size

        Returns:
            DataFrame with driver statistics
        """
        df = results.sort_values(["Abbreviation", "Date"])

        # Group by driver and compute rolling stats
        stats = df.groupby("Abbreviation").apply(
            lambda x: pd.DataFrame({
                "AvgFinishLast5": x["Position"].rolling(window, min_periods=1).mean(),
                "AvgGridLast5": x["GridPosition"].rolling(window, min_periods=1).mean(),
                "WinsLast5": (x["Position"] == 1).rolling(window, min_periods=1).sum(),
                "PodiumsLast5": (x["Position"] <= 3).rolling(window, min_periods=1).sum(),
                "PointsLast5": x["Points"].rolling(window, min_periods=1).sum(),
                "DNFsLast5": x["IsDNF"].rolling(window, min_periods=1).sum() if "IsDNF" in x.columns else 0,
            })
        ).reset_index(level=0, drop=True)

        return pd.concat([df, stats], axis=1)

    def compute_team_stats(
        self,
        results: pd.DataFrame,
        window: int = 5,
    ) -> pd.DataFrame:
        """
        Compute rolling statistics for teams.

        Args:
            results: Race results DataFrame
            window: Rolling window size

        Returns:
            DataFrame with team statistics
        """
        df = results.sort_values(["TeamName", "Date"])

        # Aggregate by team per race first
        team_race = df.groupby(["TeamName", "Season", "Round"]).agg({
            "Points": "sum",
            "Position": "mean",
        }).reset_index()

        team_race = team_race.sort_values(["TeamName", "Season", "Round"])

        # Compute rolling stats
        stats = team_race.groupby("TeamName").apply(
            lambda x: pd.DataFrame({
                "TeamAvgPointsLast5": x["Points"].rolling(window, min_periods=1).mean(),
                "TeamAvgFinishLast5": x["Position"].rolling(window, min_periods=1).mean(),
            })
        ).reset_index(level=0, drop=True)

        return pd.concat([team_race, stats], axis=1)
