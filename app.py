import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from api.authentication import get_strava_access_token
from api.athlete import get_athlete_profile
from api.activities import get_strava_activities

from components.profile_card import display_profile_card
from components.kpi_card import display_kpi_card, display_kpi_card_test

from config import ORANGE_PRIMARY_COLOR

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

    # Date filter
    default_start_date = datetime.now() - timedelta(days=30)
    start_date = st.sidebar.date_input("Start Date", default_start_date)
    start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp())

    # --------------- #
    # -- MAIN AREA -- #
    # --------------- #

    activities = get_strava_activities(token, after=start_ts)

    if not activities:
        st.warning("No activities found for this period.")
    else:
        df = pd.DataFrame(activities)

        required_columns = ["name", "distance", "moving_time", "type", "start_date"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            df["start_date"] = pd.to_datetime(df["start_date"])
            df["distance_km"] = df["distance"] / 1000
            df = df.sort_values("start_date")

            # KPI card
            total_activities = len(df)

            total_distance = df["distance_km"].sum()

            # test -----------
            period_days = (datetime.now().date() - start_date).days
            start_date_last_year = start_date - timedelta(days=365)
            end_date_last_year = start_date_last_year + timedelta(days=period_days)

            start_ts_last_year = int(datetime.combine(start_date_last_year, datetime.min.time()).timestamp())
            end_ts_last_year = int(datetime.combine(end_date_last_year, datetime.max.time()).timestamp())

            activities_last_year = get_strava_activities(token, after=start_ts_last_year)
            activities_last_year = [act for act in activities_last_year if pd.to_datetime(act["start_date"]).timestamp() <= end_ts_last_year]

            df_last_year = pd.DataFrame(activities_last_year)
            df_last_year["distance_km"] = df_last_year["distance"] / 1000

            total_distance_last_year = df_last_year["distance_km"].sum()

            diff_distance = total_distance - total_distance_last_year
            percent_diff_distance = (diff_distance / total_distance_last_year) * 100 if total_distance_last_year > 0 else 0
            # end test -----------

            total_seconds = df["moving_time"].sum()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)

            total_elevation = df["total_elevation_gain"].sum()

            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            display_kpi_card(kpi_col1, "🏃‍♂️", "Total Activities", total_activities)
            diff_str = f"{diff_distance:+.1f} km ({percent_diff_distance:+.1f}%)"
            display_kpi_card_test(kpi_col2, "📏", "Total Distance", f"{total_distance:.2f} km", subtitle=diff_str)
            display_kpi_card(kpi_col3, "⏱️", "Total Time", f"{hours}h {minutes}min")
            display_kpi_card(kpi_col4, "🏔️", "Elevation Gain", f"{total_elevation:.0f} m")

            longest_distance = df["distance_km"].max()
            
            avg_duration_sec = df["moving_time"].mean()
            avg_duration_min = avg_duration_sec / 60
            avg_hours = int(avg_duration_min // 60)
            avg_minutes = int(avg_duration_min % 60)
            
            df["avg_speed_kmh"] = df["distance_km"] / (df["moving_time"] / 3600)
            avg_speed = df["avg_speed_kmh"].mean()

            avg_elevation = df["total_elevation_gain"].mean()
            
            kpi_col5, kpi_col6, kpi_col7, kpi_col8 = st.columns(4)
            display_kpi_card(kpi_col5, "🏁", "Longest Activity", f"{longest_distance:.0f} km")
            display_kpi_card(kpi_col6, "⏳", "Average Duration", f"{avg_hours}h {avg_minutes}min")
            display_kpi_card(kpi_col7, "🐇", "Average Speed", f"{avg_speed:.2f} km/h")
            display_kpi_card(kpi_col8, "🏔️", "Average Elevation Gain", f"{avg_elevation:.0f} m")

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

                fig.update_traces(marker=dict(size=8, symbol="circle"))  # Customize marker size and shape

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
                    showlegend=False  # Hides legend as we only have one line
                )

                st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
