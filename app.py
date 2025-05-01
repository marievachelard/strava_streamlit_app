import streamlit as st
import pandas as pd
from strava_api import get_strava_access_token, get_strava_activities

st.set_page_config(page_title="Strava Monitor", layout="wide")
st.title("🚴‍♀️ Strava Activity Tracker")

try:
    token = get_strava_access_token()
    activities = get_strava_activities(token)

    # Convertir les données en DataFrame
    df = pd.DataFrame(activities)
    st.success(f"✅ {len(df)} activités récupérées")

    # Afficher un tableau
    st.dataframe(df[["name", "distance", "moving_time", "type", "start_date"]])

    # Exemple de graphique (distance dans le temps)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df = df.sort_values("start_date")
    st.line_chart(df.set_index("start_date")["distance"])

except Exception as e:
    st.error(f"Erreur : {e}")
