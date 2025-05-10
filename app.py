import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from api.authentication import get_strava_access_token
from api.athlete import get_athlete_profile
from api.activities import get_strava_activities

from components.profile_card import display_profile_card

from config import ORANGE_PRIMARY_COLOR, kpi_config

from services.data_processing import (
    preprocess_activities,
    compute_kpis,
    get_last_year_range,
    compute_all_comparisons
)

from utils import display_kpi_with_comparison

st.set_page_config(page_title="Strava Monitor", layout="wide")
st.title("Strava Activity Tracker")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
    
    start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp())

    # Load activities data
    activities = get_strava_activities(token, after=start_ts, activity_types=['Run'])

    if not activities:
        st.warning("No activities found for this period.")
    else:
        df = preprocess_activities(activities)
        kpis = compute_kpis(df)

        start_last_year, end_last_year = get_last_year_range(start_date)
        start_ts_last_year = int(datetime.combine(start_last_year, datetime.min.time()).timestamp())
        end_ts_last_year = int(datetime.combine(end_last_year, datetime.max.time()).timestamp())

        activities_last_year = get_strava_activities(token, after=start_ts_last_year, activity_types=['Run'])
        activities_last_year = [act for act in activities_last_year if pd.to_datetime(act["start_date"]).timestamp() <= end_ts_last_year]
        
        df_last_year = preprocess_activities(activities_last_year)
        kpis_last_year = compute_kpis(df_last_year)

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
            if period == "Week":
                df["period"] = df["start_date"].dt.tz_localize(None).dt.to_period("W").dt.start_time
                all_periods = pd.date_range(start=start_date, end=datetime.now(), freq="W-MON")
                period_label = [f"Week of {d.strftime('%b %d')}" for d in all_periods]
            else:
                df["period"] = df["start_date"].dt.tz_localize(None).dt.to_period("M").dt.start_time
                all_periods = pd.date_range(start=start_date, end=datetime.now(), freq="MS")
                period_label = [d.strftime('%B') for d in all_periods]  # 'April', 'May', etc.

            all_periods_df = pd.DataFrame({
                "period": pd.to_datetime(all_periods),
                "label": period_label
            })

            grouped_df = df.groupby("period")["distance_km"].sum().reset_index()
            grouped_df = pd.merge(all_periods_df, grouped_df, on="period", how="left")
            grouped_df["distance_km"] = grouped_df["distance_km"].fillna(0)

            # Calculating the average distance
            average_distance = grouped_df["distance_km"].mean()

            # Plotting the line chart with markers
            fig = px.line(
                grouped_df,
                x="label",
                y="distance_km",
                title=f"{period}ly Distance Trend",
                labels={"label": period, "distance_km": "Distance (km)"},
                markers=True,  # Adding markers
                color_discrete_sequence=[ORANGE_PRIMARY_COLOR]
            )

            fig.update_traces(marker=dict(size=8, symbol="circle"))

            # Adding a horizontal line for the average
            fig.add_hline(
                y=average_distance,
                line=dict(color="gray", dash="dash", width=1),
                annotation_text=f"Average: {average_distance:.0f} km",
                annotation_position="bottom right",
                annotation_font_size=12,
                annotation_font_color="white"
            )

            fig.update_layout(
                xaxis_title=period,
                yaxis_title="Distance (km)",
                template="plotly_dark",
                title_font_color="#FFFFFF",
                font_color="white",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
