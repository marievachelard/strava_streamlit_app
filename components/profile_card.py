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
