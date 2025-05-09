# 🚴‍♂️ Strava Activity Tracker

<p style="text-align: center;">

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Strava](https://img.shields.io/badge/Strava-orange?logo=strava&logoColor=white)

</p>

A **Streamlit** app for tracking and visualizing your **personal Strava activity statistics**, providing interactive charts and insights into your performance trends over time.
 
## 📊 Features

- 📅 Weekly, monthly, and yearly activity summaries
- 🏔️ Visualize elevation, pace, speed, and distance over time
- 📈 Dynamic charts powered by **Plotly** or **Altair**
- 🔍 Filter activities by type (run, ride, hike, etc.)
- 💾 Optional data caching for faster performance

## 🎨 Color Palette

The colors used in this application are defined as follows in the CSS code:
Main dark color: #1c1c1e
Very dark background: #101011
Vibrant orange accent: #FC4C02
Main white color: #ffffff

## 🖼️ Demo

To do

## ⚙️ Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/strava_streamlit_app
cd strava_streamlit_app
python -m venv strava-env
source strava-env/bin/activate
pip install -r requirements.txt
streamlit run app.py
