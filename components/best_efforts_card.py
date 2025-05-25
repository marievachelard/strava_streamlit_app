import streamlit as st
from utils.duration import format_duration

def display_best_efforts(best_efforts: dict):
    st.sidebar.markdown("## 🏅 All-Time Best Efforts")

    for label, result in best_efforts.items():
        if result:
            formatted_time = format_duration(result["time_sec"])

            st.sidebar.markdown(f"""
            <div class="bestTimeCard">
                <div class="bestTimeLabel">{label}</div>
                <div class="bestTimeValue">⏱️ {formatted_time}</div>
                <div class="bestTimeMeta">📅 {result['date']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"""
            <div class="bestTimeCard">
                <div class="bestTimeLabel">{label}</div>
                <div class="bestTimeValue">–</div>
                <div class="bestTimeMeta">No matching activity</div>
            </div>
            """, unsafe_allow_html=True)
