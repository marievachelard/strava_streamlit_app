import plotly.express as px

from config import ORANGE_PRIMARY_COLOR

def display_distance_trend_chart(grouped_df, average_distance, period_type):
    """
    Display a Plotly line chart displaying distance trends.

    Args:
        grouped_df (pd.DataFrame): The DataFrame containing the activity data.
        average_distance (float): The average distance for the period.
        period_type (str): The type of period ('Week' or 'Month').

    Returns:
        plotly.graph_objects.Figure: The generated Plotly figure.
    """
    fig = px.line(
        grouped_df,
        x="period",
        y="distance_km",
        title=f"{period_type}ly Distance Trend",
        labels={"period": period_type, "distance_km": "Distance (km)"},
        markers=True,
        color_discrete_sequence=[ORANGE_PRIMARY_COLOR]
    )

    fig.update_traces(marker=dict(size=8, symbol="circle"))

    fig.add_hline(
        y=average_distance,
        line=dict(color="gray", dash="dash", width=1),
        annotation_text=f"Average: {average_distance:.0f} km",
        annotation_position="bottom right",
        annotation_font_size=12,
        annotation_font_color="white"
    )

    fig.update_layout(
        xaxis_title=period_type,
        yaxis_title="Distance (km)",
        template="plotly_dark",
        title_font_color="#FFFFFF",
        font_color="white",
        showlegend=False
    )

    fig.update_xaxes(
        tickformat="%b %Y" if period_type == "Month" else "W%W %Y"
    )

    return fig
