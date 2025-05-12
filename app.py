import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from api.authentication import get_strava_access_token
from api.athlete import get_athlete_profile
from api.activities import get_strava_activities

from components.profile_card import display_profile_card
from components.distance_chart import display_distance_trend_chart

from config import kpi_config

from services.data_processing import (
    load_current_year_data,
    load_last_year_data,
    compute_all_comparisons,
    process_period,
    add_average_line
)

from utils.style import local_css
from utils.kpi_display import display_kpi_with_comparison

st.set_page_config(page_title="Strava Monitor", layout="wide")
st.title("Strava Activity Tracker")

local_css("assets/styles.css")

try:
    token = get_strava_access_token()

    # --------------- #
    # --  SIDEBAR  -- #
    # --------------- #

    # Load athlete data
    athlete = get_athlete_profile(token)

    # Profile card
    photo_url = athlete.get("profile", "")
    name = f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}"
    location = f"{athlete.get('city', '')}, {athlete.get('country', '')}"
    description = athlete.get("bio", "Sportif Strava")

    display_profile_card(
        photo_url=photo_url,
        name=name,
        location=location,
        description=description
    )

    # --------------- #
    # -- MAIN AREA -- #
    # --------------- #

    # Date filter
    default_start_date = datetime.now() - timedelta(days=30)
    
    cols = st.columns(4)
    with cols[0]:
        start_date = st.date_input("Start Date", default_start_date)
    
    df, kpis = load_current_year_data(token, start_date)

    if df.empty:
        st.warning("No activities found for this period.")
    else:
        df_last_year, kpis_last_year = load_last_year_data(token, start_date)
        
        comparisons = compute_all_comparisons(kpis, kpis_last_year)

        # KPI card
        cols = st.columns(4)
        for idx, config in enumerate(kpi_config):
            key = config["key"]
            col = cols[idx % 4]
            icon = config["icon"]
            label = config["label"]
            unit = config.get("unit", "")
            is_duration = config.get("is_duration", False)

            display_kpi_with_comparison(
                col,
                icon,
                label,
                kpis[key],
                comparisons[key],
                unit=unit,
                is_duration=is_duration
            )

        # Segmented control
        period = st.segmented_control(
            "Period",
            options = ["Week", "Month"],
            selection_mode="single",
            default = "Week",
            label_visibility="hidden"
        )

        # Line chart with markers
        with st.container():
            grouped_df, period_label = process_period(df, start_date, period_type=period)
            average_distance = add_average_line(grouped_df)

            fig = display_distance_trend_chart(grouped_df, average_distance, period_type=period)

            st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
