import streamlit as st

def local_css(file_name):
    """
    Injects local CSS styles into a Streamlit app.

    Parameters:
    file_name (str): The path to the local CSS file to be included.
    """
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
