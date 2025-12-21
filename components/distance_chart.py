def display_distance_trend_chart(grouped_df, average_distance, period_type, grouped_last_df=None):
    import plotly.express as px
    import plotly.graph_objects as go
    from config import ORANGE_PRIMARY_COLOR

    # Ligne principale année en cours
    fig = px.line(
        grouped_df,
        x="period_index",
        y="distance_km",
        title=f"{period_type}ly Distance Trend",
        markers=True,
        color_discrete_sequence=[ORANGE_PRIMARY_COLOR],
        hover_data={"period_index": False, "distance_km": False, "label": False}  # On masque les colonnes par défaut
    )

    # Ajouter hover template pour l’année en cours
    fig.update_traces(
        hovertemplate="%{customdata[0]}<br>Distance: %{y:.1f} km",
        customdata=grouped_df[["label"]].values,
        marker=dict(size=8, symbol="circle")
    )

    # Ligne moyenne
    fig.add_hline(
        y=average_distance,
        line=dict(color="gray", dash="dash", width=1),
        annotation_text=f"Average: {average_distance:.1f} km",
        annotation_position="bottom right",
        annotation_font_size=12,
        annotation_font_color="white"
    )

    # Ligne année précédente
    if grouped_last_df is not None:
        fig.add_trace(
            go.Scatter(
                x=grouped_last_df["period_index"],
                y=grouped_last_df["distance_km"],
                mode="lines+markers",
                name="Last Year",
                line=dict(color="lightblue", dash="dot"),
                marker=dict(size=6, symbol="circle"),
                hovertemplate="%{customdata[0]} (Last Year)<br>Distance: %{y:.1f} km",
                customdata=grouped_last_df[["label"]].values
            )
        )

    # Axe X
    fig.update_xaxes(
        tickvals=grouped_df["period_index"],
        ticktext=grouped_df["label"]
    )

    fig.update_layout(
        xaxis_title=period_type,
        yaxis_title="Distance (km)",
        template="plotly_dark",
        title_font_color="#FFFFFF",
        font_color="white",
        showlegend=True
    )

    return fig
