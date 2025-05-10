import requests

def get_strava_activities(access_token, after=None, activity_types=None):
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
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        all_activities.extend(data)
        page += 1

    if activity_types:
        all_activities = [
            activity for activity in all_activities
            if activity.get("type") in activity_types
        ]

    return all_activities
