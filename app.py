import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from strava_api import get_strava_access_token, get_athlete_profile, get_strava_activities

st.set_page_config(page_title="Strava Monitor", layout="wide")
st.title("Strava Activity Tracker")

# Fonction pour afficher le profil dans la sidebar
def sidebar_profile(photo_url, name, location, description):
    st.sidebar.markdown(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #1c1c1e;
            padding: 20px 10px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 0 6px rgba(0,0,0,0.15);
        ">
            <img src="{photo_url}" style="width:80px; height:80px; border-radius:50%; margin-bottom:10px; border:2px solid #FC4C02;" />
            <div style="color: white; font-size: 16px; font-weight: bold;">{name}</div>
            <div style="color: #aaa; font-size: 13px;">📍 {location}</div>
            <div style="color: white; font-size: 12px; margin-top: 8px; text-align: center;">{description}</div>
        </div>
    """, unsafe_allow_html=True)

# Fonction pour afficher les KPIs globaux 
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

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/style.css")

# Récupère ton token Strava
try:
    token = get_strava_access_token()

    # Utiliser le token pour récupérer les informations de profil
    athlete = get_athlete_profile(token)

    # Extraire les informations du profil
    photo_url = athlete.get("profile", "")
    name = f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}"
    location = f"{athlete.get('city', '')}, {athlete.get('country', '')}"
    description = athlete.get("bio", "Sportif Strava")

    # Afficher le profil dans la sidebar
    sidebar_profile(
        photo_url=photo_url,
        name=name,
        location=location,
        description=description
    )

    # Récupérer les activités comme avant
    default_start_date = datetime.now() - timedelta(days=30)
    start_date = st.sidebar.date_input("Start Date", default_start_date)
    start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp())

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

            # Graph + toggle buttons
            st.markdown("<div style='margin-bottom: -10px'></div>", unsafe_allow_html=True)
            
            # Radio buttons for period selection with horizontal layout
            period = st.radio(
                "Period", 
                options=["Week", "Month"], 
                horizontal=True,
                label_visibility="collapsed"
            )

            with st.container():  # Conteneur pour le graphique
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
                    labels={"label": period, "distance_km": "Distance (km)"},
                    color_discrete_sequence=["#FC4C02"]
                )

                fig.update_layout(
                    xaxis_title=period,
                    yaxis_title="Distance (km)",
                    template="plotly_dark",
                    title_font_color="#FFFFFF",
                    font_color="white"
                )

                st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
