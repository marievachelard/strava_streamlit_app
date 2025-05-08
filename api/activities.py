import requests

def get_strava_activities(access_token, after=None):
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
