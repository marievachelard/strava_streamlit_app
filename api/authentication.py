import os
import json
import requests
import streamlit as st

def get_strava_access_token():
    # Environnement cloud : secrets
    if st.secrets.get("strava"):
        client_id = st.secrets["strava"]["client_id"]
        client_secret = st.secrets["strava"]["client_secret"]
        refresh_token = st.secrets["strava"]["refresh_token"]
    else:
        # Environnement local : fichier JSON
        with open("strava_token/strava_credentials.json", "r") as file:
            creds = json.load(file)
            client_id = creds["client_id"]
            client_secret = creds["client_secret"]
            refresh_token = creds["refresh_token"]

    response = requests.post(
        url="https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )

    if response.status_code != 200:
        raise Exception(f"Failed to refresh Strava token: {response.text}")

    return response.json()["access_token"]
