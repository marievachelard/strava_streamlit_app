import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from strava_api import get_strava_access_token, get_all_activities


def styled_kpi(col, emoji, label, value, color="#FC4C02"):
    col.markdown(f"""
        <div style="
            background-color:#1c1c1e;
            padding:20px;
            border-radius:10px;
            text-align:center;
            box-shadow: 0 0 6px rgba(0,0,0,0.15);
            margin-bottom:10px;
        ">
            <div style="font-size:18px; color:white; margin-bottom:5px;">
                {emoji} {label}
            </div>
            <div style="color:{color}; font-size:22px; font-weight:bold;">
                {value}
            </div>
        </div>
    """, unsafe_allow_html=True)


st.set_page_config(page_title="Strava Monitor", layout="wide")
st.title("Strava Activity Tracker")

# Sidebar filter
st.sidebar.header("📅 Filter Activities")
default_start_date = datetime.now() - timedelta(days=30)
start_date = st.sidebar.date_input("Start Date", default_start_date)
start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp())

try:
    token = get_strava_access_token()
    activities = get_all_activities(token, after=start_ts)

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

            # KPIs
            total_activities = len(df)
            total_distance = df["distance_km"].sum()
            total_seconds = df["moving_time"].sum()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            total_elevation = df["total_elevation_gain"].sum()

            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            styled_kpi(kpi_col1, "🏃‍♂️", "Total Activities", total_activities)
            styled_kpi(kpi_col2, "📏", "Total Distance", f"{total_distance:.2f} km")
            styled_kpi(kpi_col3, "⏱️", "Total Time", f"{hours}h {minutes}min")
            styled_kpi(kpi_col4, "🏔️", "Elevation Gain", f"{total_elevation:.0f} m")

            st.markdown("<br>", unsafe_allow_html=True)

            with st.expander("📄 View raw data"):
                st.dataframe(df[required_columns])

            # Graph + toggle side by side
            chart_col, toggle_col = st.columns([5, 1])
            with toggle_col:
                period = st.radio(
                    "Period", 
                    options=["Week", "Month"], 
                    horizontal=True,
                    label_visibility="collapsed"
                )

            with chart_col:
                if period == "Week":
                    df["period"] = df["start_date"].dt.tz_localize(None).dt.to_period("W").dt.start_time
                    all_periods = pd.date_range(start=start_date, end=datetime.now(), freq="W-MON")
                    period_label = [f"Week of {d.strftime('%b %d')}" for d in all_periods]
                else:
                    df["period"] = df["start_date"].dt.tz_localize(None).dt.to_period("M").dt.start_time
                    all_periods = pd.date_range(start=start_date, end=datetime.now(), freq="MS")
                    period_label = [d.strftime('%B') for d in all_periods]  # 'April', 'May', etc.

                # Create full range of periods
                all_periods_df = pd.DataFrame({
                    "period": pd.to_datetime(all_periods),
                    "label": period_label
                })

                # Group data
                grouped_df = df.groupby("period")["distance_km"].sum().reset_index()
                grouped_df = pd.merge(all_periods_df, grouped_df, on="period", how="left")
                grouped_df["distance_km"] = grouped_df["distance_km"].fillna(0)

                # Bar chart
                fig = px.bar(
                    grouped_df,
                    x="label",
                    y="distance_km",
                    title=f"{period}ly Distance Trend",
                    labels={"label": period, "distance_km": "Distance (km)"}
                )

                fig.update_layout(
                    xaxis_title=period,
                    yaxis_title="Distance (km)",
                    template="plotly_dark"
                )

                st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
