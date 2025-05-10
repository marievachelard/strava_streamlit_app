import streamlit as st

def display_kpi_card(col, emoji, label, value, subtitle=""):
    with col:
        st.markdown(
            f"""
            <div class="kpiCard">
                <div class="kpiLabel">{emoji} {label}</div>
                <div class="kpiValue">{value}</div>
                <div style="font-size:14px; color:gray;">{subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
