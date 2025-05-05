import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from strava_api import get_strava_access_token, get_all_activities

st.set_page_config(page_title="Strava Monitor", layout="wide")
st.title("🚴‍♀️ Strava Activity Tracker")

# Choisir une date de départ
st.sidebar.header("📅 Filtrer les activités")
default_start_date = datetime.now() - timedelta(days=7)
start_date = st.sidebar.date_input("Date de début", default_start_date)
start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp())

try:
    token = get_strava_access_token()
    activities = get_all_activities(token, after=start_ts)

    if not activities:
        st.warning("Aucune activité trouvée sur cette période.")
    else:
        df = pd.DataFrame(activities)

        # Assurer la présence des colonnes nécessaires
        required_columns = ["name", "distance", "moving_time", "type", "start_date"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"Colonnes manquantes : {missing}")
        else:
            df["start_date"] = pd.to_datetime(df["start_date"])
            df = df.sort_values("start_date")

            st.success(f"✅ {len(df)} activités depuis le {start_date.strftime('%d %b %Y')}")

            with st.expander("📄 Voir les données brutes"):
                st.dataframe(df[required_columns])

            # 🎯 Graphique de la distance dans le temps
            line_chart = alt.Chart(df).mark_line(point=True).encode(
                x="start_date:T",
                y=alt.Y("distance", title="Distance (m)"),
                tooltip=["name", "type", "distance", "moving_time"]
            ).properties(title="Évolution des distances par activité")

            st.altair_chart(line_chart, use_container_width=True)

except Exception as e:
    st.error(f"❌ Erreur : {e}")
