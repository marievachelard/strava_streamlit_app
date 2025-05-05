import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from strava_api import get_strava_access_token, get_all_activities

st.set_page_config(page_title="Strava Monitor", layout="wide")
st.title("Strava Activity Tracker")

# Choose a start date
st.sidebar.header("📅 Filter Activities")
default_start_date = datetime.now() - timedelta(days=7)
start_date = st.sidebar.date_input("Start Date", default_start_date)
start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp())

try:
    token = get_strava_access_token()
    activities = get_all_activities(token, after=start_ts)

    if not activities:
        st.warning("No activities found for this period.")
    else:
        df = pd.DataFrame(activities)

        # Ensure required columns are present
        required_columns = ["name", "distance", "moving_time", "type", "start_date"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            # Format the start_date column
            df["start_date"] = pd.to_datetime(df["start_date"])
            df["distance_km"] = df["distance"] / 1000  # Convert distance to kilometers
            df["date_only"] = df["start_date"].dt.date  # Extract the date part only (remove time)
            df = df.sort_values("start_date")

            # Group by date and sum the distances for each day
            daily_distances = df.groupby("date_only")["distance_km"].sum().reset_index()

            # Generate all dates in the range (even if there were no activities)
            all_dates = pd.date_range(start=start_date, end=datetime.now()).date
            all_dates_df = pd.DataFrame(all_dates, columns=["date_only"])

            # Merge the activity data with all possible dates
            daily_distances = pd.merge(all_dates_df, daily_distances, on="date_only", how="left")
            daily_distances["distance_km"].fillna(0, inplace=True)  # Fill NaN with 0 for no activity days

            # KPIs - Total activities, total distance, total time
            total_activities = len(df)
            total_distance = df["distance_km"].sum()  # Total distance in km
            total_time = df["moving_time"].sum() / 3600  # Total time in hours

            # Display KPIs in a row
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            with kpi_col1:
                st.metric("Total Activities", total_activities)
            with kpi_col2:
                st.metric("Total Distance", f"{total_distance:.2f} km")
            with kpi_col3:
                st.metric("Total Time", f"{total_time:.2f} h")

            # Display raw data with an expander
            with st.expander("📄 View raw data"):
                st.dataframe(df[required_columns])

            # 🎯 Distance over time chart with Plotly
            fig = px.line(
                daily_distances,
                x="date_only",
                y="distance_km",
                title="Daily Distance Trend",
                labels={"date_only": "Date", "distance_km": "Distance (km)"},
            )

            # Update the x-axis format to show just the date and make it readable
            fig.update_xaxes(
                tickformat="%d %b",  # Format the date as day and month (e.g., 01 Jan)
                title="Date"
            )

            # Update the layout for better visualization
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Distance (km)",
                template="plotly_dark",  # Optional: to use a dark theme
            )

            # Show the plot
            st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
