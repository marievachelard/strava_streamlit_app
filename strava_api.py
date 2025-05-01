import os
import base64
import json
import requests

def get_strava_credentials():
    base64_content = os.environ.get("STRAVA_CREDENTIALS")
    if base64_content and base64_content.startswith("STRAVA_CREDENTIALS="):
        base64_content = base64_content.replace("STRAVA_CREDENTIALS=", "")
    return json.loads(base64.b64decode(base64_content))

def get_strava_access_token():
    creds = get_strava_credentials()
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            'client_id': creds['client_id'],
            'client_secret': creds['client_secret'],
            'refresh_token': creds['refresh_token'],
            'grant_type': 'refresh_token'
        }
    )
    if response.status_code != 200:
        raise Exception("❌ Token refresh failed")
    return response.json()["access_token"]

def get_strava_activities(access_token, per_page=10):
    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"per_page": per_page}
    )
    return response.json()

def get_all_activities(access_token, after=None):
    all_activities = []
    page = 1
    while True:
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "per_page": 100,
                "page": page,
                "after": after
            }
        )
        data = response.json()
        if not data or response.status_code != 200:
            break
        all_activities.extend(data)
        page += 1
    return all_activities

