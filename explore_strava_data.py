from strava_api import get_strava_access_token, get_strava_activities
import pandas as pd
import json

def explore_data():
    token = get_strava_access_token()
    activities = get_strava_activities(token, per_page=30)  # on en prend un peu plus

    # On affiche toutes les clés de la première activité
    print("\n📌 Clés disponibles dans une activité :")
    print(list(activities[0].keys()))

    # On convertit en DataFrame pour visualiser
    df = pd.DataFrame(activities)
    print("\n📊 Aperçu du DataFrame :")
    print(df.head(3).T)  # Transposé pour voir plus facilement

    # Optionnel : enregistrer en local pour inspection complète
    with open("strava_sample.json", "w") as f:
        json.dump(activities, f, indent=2)

if __name__ == "__main__":
    explore_data()
