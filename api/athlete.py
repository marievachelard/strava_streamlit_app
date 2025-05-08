import requests

def get_athlete_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)
    response.raise_for_status()
    return response.json()
