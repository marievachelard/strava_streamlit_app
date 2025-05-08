import streamlit as st

def display_kpi_card(col, emoji, label, value):
    """
    Displays a styled KPI card with an emoji, label, and value.
    """
    col.markdown(f"""
        <div class="kpiCard">
            <div class="kpiLabel">{emoji} {label}</div>
            <div class="kpiValue">{value}</div>
        </div>
    """, unsafe_allow_html=True)
