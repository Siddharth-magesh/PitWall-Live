"""
F1 Data Loader
==============

Unified data loading from FastF1, OpenF1, and other sources.
"""

import os
import logging
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import fastf1
from fastf1 import get_session, get_event_schedule
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


class F1DataLoader:
    """
    Unified F1 data loader supporting multiple data sources.

    Provides access to:
    - Historical race results
    - Session data (Practice, Qualifying, Race)
    - Lap times and telemetry
    - Driver and constructor standings

    Example:
        >>> loader = F1DataLoader(cache_dir="./data/cache")
        >>> races = loader.load_race_results(seasons=[2023, 2024])
        >>> session = loader.load_session(2024, "Monaco", "R")
    """

    def __init__(self, cache_dir: str = "./data/cache"):
        """
        Initialize the data loader.

        Args:
            cache_dir: Directory for caching FastF1 data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Enable FastF1 caching
        fastf1.Cache.enable_cache(str(self.cache_dir))

        # OpenF1 API base URL
        self.openf1_base = "https://api.openf1.org/v1"

        logger.info(f"F1DataLoader initialized with cache at {self.cache_dir}")

    # =========================================================================
    # Schedule and Event Data
    # =========================================================================

    def get_schedule(self, year: int) -> pd.DataFrame:
        """
        Get the race schedule for a given year.

        Args:
            year: Season year

        Returns:
            DataFrame with race schedule
        """
        schedule = get_event_schedule(year)
        return schedule

    def get_all_races(self, seasons: List[int]) -> pd.DataFrame:
        """
        Get list of all races across multiple seasons.

        Args:
            seasons: List of season years

        Returns:
            DataFrame with all races
        """
        all_races = []

        for year in tqdm(seasons, desc="Loading schedules"):
            try:
                schedule = self.get_schedule(year)
                schedule["Season"] = year
                all_races.append(schedule)
            except Exception as e:
                logger.warning(f"Could not load {year} schedule: {e}")

        return pd.concat(all_races, ignore_index=True)

    # =========================================================================
    # Session Data
    # =========================================================================

    def load_session(
        self,
        year: int,
        grand_prix: str,
        session_type: str,
        load_telemetry: bool = False,
        load_weather: bool = True,
    ) -> fastf1.core.Session:
        """
        Load a complete F1 session.

        Args:
            year: Season year
            grand_prix: Race name (e.g., "Monaco", "Silverstone")
            session_type: Session type ("FP1", "FP2", "FP3", "Q", "S", "R")
            load_telemetry: Whether to load telemetry data (slower)
            load_weather: Whether to load weather data

        Returns:
            FastF1 Session object
        """
        logger.info(f"Loading {year} {grand_prix} {session_type}")

        session = get_session(year, grand_prix, session_type)
        session.load(
            telemetry=load_telemetry,
            weather=load_weather,
            messages=False,
        )

        return session

    def load_session_laps(
        self,
        year: int,
        grand_prix: str,
        session_type: str,
    ) -> pd.DataFrame:
        """
        Load lap data for a session.

        Args:
            year: Season year
            grand_prix: Race name
            session_type: Session type

        Returns:
            DataFrame with lap data
        """
        session = self.load_session(year, grand_prix, session_type)
        laps = session.laps.copy()

        # Add metadata
        laps["Season"] = year
        laps["GrandPrix"] = grand_prix
        laps["SessionType"] = session_type

        return laps

    # =========================================================================
    # Race Results
    # =========================================================================

    def load_race_results(
        self,
        seasons: List[int],
        include_dnf: bool = True,
    ) -> pd.DataFrame:
        """
        Load race results for multiple seasons.

        Args:
            seasons: List of season years
            include_dnf: Whether to include DNF results

        Returns:
            DataFrame with race results
        """
        all_results = []

        for year in tqdm(seasons, desc="Loading race results"):
            try:
                schedule = self.get_schedule(year)

                for _, event in schedule.iterrows():
                    if event["EventFormat"] == "testing":
                        continue

                    try:
                        session = self.load_session(
                            year, event["EventName"], "R"
                        )
                        results = session.results.copy()

                        # Add metadata
                        results["Season"] = year
                        results["Round"] = event["RoundNumber"]
                        results["GrandPrix"] = event["EventName"]
                        results["CircuitKey"] = event.get("Location", "")
                        results["Date"] = event["EventDate"]

                        all_results.append(results)

                    except Exception as e:
                        logger.warning(
                            f"Could not load {year} {event['EventName']}: {e}"
                        )

            except Exception as e:
                logger.warning(f"Could not process {year}: {e}")

        if not all_results:
            return pd.DataFrame()

        df = pd.concat(all_results, ignore_index=True)

        if not include_dnf:
            df = df[df["Status"] == "Finished"]

        return df

    def load_qualifying_results(self, seasons: List[int]) -> pd.DataFrame:
        """
        Load qualifying results for multiple seasons.

        Args:
            seasons: List of season years

        Returns:
            DataFrame with qualifying results
        """
        all_results = []

        for year in tqdm(seasons, desc="Loading qualifying results"):
            try:
                schedule = self.get_schedule(year)

                for _, event in schedule.iterrows():
                    if event["EventFormat"] == "testing":
                        continue

                    try:
                        session = self.load_session(
                            year, event["EventName"], "Q"
                        )
                        results = session.results.copy()

                        results["Season"] = year
                        results["Round"] = event["RoundNumber"]
                        results["GrandPrix"] = event["EventName"]

                        all_results.append(results)

                    except Exception as e:
                        logger.debug(
                            f"Could not load {year} {event['EventName']} Q: {e}"
                        )

            except Exception as e:
                logger.warning(f"Could not process {year}: {e}")

        if not all_results:
            return pd.DataFrame()

        return pd.concat(all_results, ignore_index=True)

    # =========================================================================
    # Lap Times
    # =========================================================================

    def load_all_lap_times(
        self,
        seasons: List[int],
        session_type: str = "R",
    ) -> pd.DataFrame:
        """
        Load all lap times for multiple seasons.

        Args:
            seasons: List of season years
            session_type: Session type to load

        Returns:
            DataFrame with all lap times
        """
        all_laps = []

        for year in tqdm(seasons, desc="Loading lap times"):
            try:
                schedule = self.get_schedule(year)

                for _, event in schedule.iterrows():
                    if event["EventFormat"] == "testing":
                        continue

                    try:
                        laps = self.load_session_laps(
                            year, event["EventName"], session_type
                        )
                        laps["Round"] = event["RoundNumber"]
                        all_laps.append(laps)

                    except Exception as e:
                        logger.debug(
                            f"Could not load laps for {year} {event['EventName']}: {e}"
                        )

            except Exception as e:
                logger.warning(f"Could not process {year}: {e}")

        if not all_laps:
            return pd.DataFrame()

        return pd.concat(all_laps, ignore_index=True)

    # =========================================================================
    # Driver/Team Information
    # =========================================================================

    def get_driver_info(self, session: fastf1.core.Session) -> pd.DataFrame:
        """
        Extract driver information from a session.

        Args:
            session: FastF1 session object

        Returns:
            DataFrame with driver info
        """
        drivers = []

        for drv in session.drivers:
            driver_info = session.get_driver(drv)
            drivers.append({
                "DriverNumber": drv,
                "Abbreviation": driver_info["Abbreviation"],
                "FullName": driver_info["FullName"],
                "TeamName": driver_info["TeamName"],
                "TeamColor": driver_info["TeamColor"],
            })

        return pd.DataFrame(drivers)

    # =========================================================================
    # Telemetry Data
    # =========================================================================

    def load_telemetry(
        self,
        year: int,
        grand_prix: str,
        session_type: str,
        driver: str,
        lap: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Load telemetry data for a specific driver.

        Args:
            year: Season year
            grand_prix: Race name
            session_type: Session type
            driver: Driver abbreviation (e.g., "VER")
            lap: Specific lap number (None for fastest lap)

        Returns:
            DataFrame with telemetry data
        """
        session = self.load_session(
            year, grand_prix, session_type, load_telemetry=True
        )

        driver_laps = session.laps.pick_driver(driver)

        if lap is not None:
            lap_data = driver_laps[driver_laps["LapNumber"] == lap].iloc[0]
        else:
            lap_data = driver_laps.pick_fastest()

        telemetry = lap_data.get_telemetry()

        # Add metadata
        telemetry["Driver"] = driver
        telemetry["Season"] = year
        telemetry["GrandPrix"] = grand_prix
        telemetry["LapNumber"] = lap_data["LapNumber"]

        return telemetry

    # =========================================================================
    # OpenF1 API (Real-time data)
    # =========================================================================

    def get_openf1_data(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict]:
        """
        Fetch data from OpenF1 API.

        Args:
            endpoint: API endpoint (e.g., "position", "car_data")
            params: Query parameters

        Returns:
            List of data dictionaries
        """
        url = f"{self.openf1_base}/{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenF1 API error: {e}")
            return []

    def get_live_timing(self, session_key: str = "latest") -> pd.DataFrame:
        """
        Get live timing data from OpenF1.

        Args:
            session_key: Session identifier

        Returns:
            DataFrame with timing data
        """
        data = self.get_openf1_data(
            "position",
            params={"session_key": session_key}
        )

        if not data:
            return pd.DataFrame()

        return pd.DataFrame(data)

    # =========================================================================
    # Standings
    # =========================================================================

    def load_standings(
        self,
        year: int,
        round_num: Optional[int] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load driver and constructor standings.

        Args:
            year: Season year
            round_num: Specific round (None for latest)

        Returns:
            Tuple of (driver_standings, constructor_standings)
        """
        # This would typically use Ergast/Jolpica API
        # For now, we'll compute from race results

        race_results = self.load_race_results([year])

        if round_num:
            race_results = race_results[race_results["Round"] <= round_num]

        # Driver standings
        driver_standings = (
            race_results.groupby(["Abbreviation", "FullName", "TeamName"])
            .agg({
                "Points": "sum",
                "Position": lambda x: (x == 1).sum(),  # Wins
            })
            .rename(columns={"Position": "Wins"})
            .sort_values("Points", ascending=False)
            .reset_index()
        )
        driver_standings["Position"] = range(1, len(driver_standings) + 1)

        # Constructor standings
        constructor_standings = (
            race_results.groupby("TeamName")
            .agg({
                "Points": "sum",
            })
            .sort_values("Points", ascending=False)
            .reset_index()
        )
        constructor_standings["Position"] = range(1, len(constructor_standings) + 1)

        return driver_standings, constructor_standings


# =============================================================================
# Convenience Functions
# =============================================================================

def load_seasons_data(
    seasons: List[int],
    cache_dir: str = "./data/cache",
) -> Dict[str, pd.DataFrame]:
    """
    Load comprehensive data for multiple seasons.

    Args:
        seasons: List of season years
        cache_dir: Cache directory

    Returns:
        Dictionary with race_results, qualifying, lap_times
    """
    loader = F1DataLoader(cache_dir)

    return {
        "race_results": loader.load_race_results(seasons),
        "qualifying": loader.load_qualifying_results(seasons),
        "lap_times": loader.load_all_lap_times(seasons),
    }
