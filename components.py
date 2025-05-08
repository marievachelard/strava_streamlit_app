import streamlit as st

def display_profile_card(photo_url, name, location, description):
    """
    Displays a styled profile card with photo, name, location, and description.
    """
    st.sidebar.markdown(f"""
        <div class="profileCard">
            <img src="{photo_url}" class="profileImage" />
            <div class="profileName">{name}</div>
            <div class="profileLocation">📍 {location}</div>
            <div class="profileDescription">{description}</div>
        </div>
    """, unsafe_allow_html=True)

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
