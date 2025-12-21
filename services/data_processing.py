import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from api.activities import get_strava_activities

def preprocess_activities(raw_activities):
    """
    Prepare the raw activity data for analysis.
    Converts timestamps to datetime and calculates additional metrics like distance in km and speed in km/h.

    Args:
        raw_activities (list): A list of activities as returned from the Strava API.

    Returns:
        pd.DataFrame: A cleaned DataFrame with preprocessed activity data.
    """
    df = pd.DataFrame(raw_activities)
    df["start_date"] = pd.to_datetime(df["start_date"], utc=True).dt.tz_localize(None)
    df["distance_km"] = df["distance"] / 1000
    df["avg_speed_kmh"] = df["distance_km"] / (df["moving_time"] / 3600)
    df = df.sort_values("start_date")
    return df

def compute_kpis(df):
    """
    Compute key performance indicators (KPIs) based on activity data.

    Args:
        df (pd.DataFrame): The preprocessed activity data.

    Returns:
        dict: A dictionary of KPIs such as total activities, total distance, total time, and others.
    """
    total_activities = len(df)
    total_distance = df["distance_km"].sum()
    total_seconds = df["moving_time"].sum()
    total_elevation = df["total_elevation_gain"].sum()
    longest_distance = df["distance_km"].max()
    avg_duration_sec = df["moving_time"].mean()
    avg_speed = df["avg_speed_kmh"].mean()
    avg_elevation = df["total_elevation_gain"].mean()
    
    return {
        "total_activities": total_activities,
        "total_distance": total_distance,
        "total_seconds": total_seconds,
        "total_elevation": total_elevation,
        "longest_distance": longest_distance,
        "avg_duration_sec": avg_duration_sec,
        "avg_speed": avg_speed,
        "avg_elevation": avg_elevation
    }

def get_df_and_kpis(activities):
    """
    Processes raw activity data into a cleaned DataFrame and computes KPIs.

    Parameters:
    activities (list[dict]): A list of activity records, typically from the Strava API.

    Returns:
    tuple: 
        - df (pd.DataFrame): A cleaned and preprocessed DataFrame of activities.
        - kpis (dict): A dictionary containing computed key performance indicators (KPIs).
    """
    df = preprocess_activities(activities)
    kpis = compute_kpis(df)

    return df, kpis

@st.cache_data(show_spinner="📥 Loading current year activities from Strava...")
def load_current_year_data(token, start_date, end_date, activity_type="Run"):
    """
    Fetches and preprocesses activities from Strava and calculates KPIs.

    Args:
        token (str): The authentication token for the Strava athlete.
        start_date (datetime): The start date for fetching activities.
        activity_type (str): The type of activity to fetch (default is "Run").

    Returns:
        tuple: A tuple containing:
            - df (pd.DataFrame): Processed activities in a DataFrame.
            - kpis (dict): Calculated KPIs for the activities.
    """
    start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp())
    end_ts = int(datetime.combine(end_date, datetime.max.time()).timestamp())

    activities = get_strava_activities(
        token,
        after=start_ts,
        activity_types=[activity_type]
    )

    activities = [
        act for act in activities
        if pd.to_datetime(act["start_date"]).timestamp() <= end_ts
    ]
    return get_df_and_kpis(activities)

def get_last_year_range(start_date, end_date):
    """
    Get the date range corresponding to the previous year for the selected period.

    Args:
        start_date (datetime.date): The selected start date for comparison.

    Returns:
        tuple: A tuple containing the start and end dates for the previous year.
    """
    period_days = (end_date - start_date).days
    start_last_year = start_date - timedelta(days=365)
    end_last_year = start_last_year + timedelta(days=period_days)
    return start_last_year, end_last_year

@st.cache_data(show_spinner="📥 Loading last year activities from Strava...")
def load_last_year_data(token, start_date, end_date, activity_type="Run"):
    """
    Fetches activities from the previous year within a date range for comparison.

    Args:
        token (str): The authentication token for the Strava athlete.
        start_date (datetime): The start date for fetching activities.
        activity_type (str): The type of activity to fetch (default is "Run").

    Returns:
        tuple: A tuple containing:
            - df_last_year (pd.DataFrame): Processed activities from last year in a DataFrame.
            - kpis_last_year (dict): Calculated KPIs for the activities from last year.
    """
    start_last_year, end_last_year = get_last_year_range(start_date, end_date)
    start_ts = int(datetime.combine(start_last_year, datetime.min.time()).timestamp())
    end_ts = int(datetime.combine(end_last_year, datetime.max.time()).timestamp())

    activities = get_strava_activities(token, after=start_ts, activity_types=[activity_type])
    activities = [
        act for act in activities
        if pd.to_datetime(act["start_date"]).timestamp() <= end_ts
    ]

    return get_df_and_kpis(activities)

def compute_all_comparisons(kpis_current, kpis_last_year):
    """
    Compare all KPIs between current and last year.

    Args:
        kpis_current (dict): KPIs for the current year.
        kpis_last_year (dict): KPIs for the previous year.

    Returns:
        dict: A dictionary where each KPI has a sub-dictionary with 'diff' and 'percent_diff'.
    """
    comparisons = {}

    for key in kpis_current:
        if key in kpis_last_year:
            current_value = kpis_current[key]
            last_value = kpis_last_year[key]
            diff = current_value - last_value
            percent_diff = (diff / last_value * 100) if last_value else 0.0
            comparisons[key] = {
                "diff": diff,
                "percent_diff": percent_diff,
                "total_last_year": last_value
            }

    return comparisons

def process_period(df, start_date, end_date, period_type="Week"):
    df = df.copy()
    df["start_date"] = pd.to_datetime(df["start_date"]).dt.tz_localize(None)

    # 1️⃣ Filtrage STRICT
    df = df[
        (df["start_date"].dt.date >= start_date) &
        (df["start_date"].dt.date <= end_date)
    ]

    if df.empty:
        return pd.DataFrame(columns=["period_index", "label", "distance_km"]), period_type

    if period_type == "Week":
        iso = df["start_date"].dt.isocalendar()

        df["iso_year"] = iso["year"]
        df["iso_week"] = iso["week"]

        df["label"] = df.apply(
            lambda r: f"W{int(r.iso_week)} {int(r.iso_year)}",
            axis=1
        )

        grouped = (
            df.groupby(["iso_year", "iso_week", "label"], as_index=False)
              .agg(distance_km=("distance_km", "sum"))
              .sort_values(["iso_year", "iso_week"])
        )

        grouped["period_index"] = range(len(grouped))

    else:
        grouped = (
            df.groupby(df["start_date"].dt.to_period("M"), as_index=False)
              .agg(distance_km=("distance_km", "sum"))
        )
        grouped["label"] = grouped["start_date"].dt.strftime("%b %Y")
        grouped["period_index"] = range(len(grouped))

    return grouped[["period_index", "label", "distance_km"]], period_type

def add_average_line(grouped_df):
    """
    Calculate and add the average distance line to the grouped DataFrame.

    Args:
        grouped_df (pd.DataFrame): The DataFrame containing aggregated activity data.

    Returns:
        float: The average distance across all periods.
    """
    average_distance = grouped_df["distance_km"].mean()
    return average_distance

@st.cache_data(show_spinner="📥 Loading all-time activities from Strava...")
def load_all_time_data(token, activity_type="Run"):
    """
    Loads and preprocesses all-time activity data from Strava.

    Args:
        token (str): Strava access token.
        activity_type (str): Type of activity to filter for (default: "Run").

    Returns:
        tuple:
            - df (pd.DataFrame): Preprocessed DataFrame of all activities.
            - kpis (dict): KPIs for the full dataset.
    """
    activities = get_strava_activities(token, after=0, activity_types=[activity_type])
    return get_df_and_kpis(activities)

def get_best_efforts(df, thresholds=[(10, "10K"), (21.1, "Half"), (42.2, "Marathon")]):
    """
    Find the best all-time times for standard race distances.

    Args:
        df (pd.DataFrame): Preprocessed Strava activity data.
        thresholds (list): List of tuples with (target distance in km, label).

    Returns:
        dict: Best times per distance with time, date, and exact distance.
    """
    best_efforts = {}

    for target_distance, label in thresholds:
        lower = target_distance * 0.99
        upper = target_distance * 1.01

        mask = df["distance_km"].between(lower, upper)
        filtered = df[mask]

        if not filtered.empty:
            best_activity = filtered.loc[filtered["moving_time"].idxmin()]
            best_efforts[label] = {
                "time_sec": best_activity["moving_time"],
                "date": best_activity["start_date"].date()
            }
        else:
            best_efforts[label] = None

    return best_efforts
