import pandas as pd
from datetime import datetime, timedelta

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
    df["start_date"] = pd.to_datetime(df["start_date"])
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

def get_last_year_range(start_date):
    """
    Get the date range corresponding to the previous year for the selected period.

    Args:
        start_date (datetime.date): The selected start date for comparison.

    Returns:
        tuple: A tuple containing the start and end dates for the previous year.
    """
    period_days = (datetime.now().date() - start_date).days
    start_last_year = start_date - timedelta(days=365)
    end_last_year = start_last_year + timedelta(days=period_days)
    return start_last_year, end_last_year

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
