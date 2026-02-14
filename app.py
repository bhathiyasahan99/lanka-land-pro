import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import split
import math

# --- Configuration & Styling ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(90deg, #1b5e20, #4caf50); 
        padding: 25px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 25px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
        color: white;
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background: #2e7d32 !important; 
        border: none; 
        font-weight: 800; 
        color: white !important; 
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background: #43a047 !important;
        transform: translateY(-2px);
    }
    .card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
    .metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
    .plot-result { background-color: #1d2129; border: 1px solid #4caf50; border-radius: 8px; padding: 10px; margin-top: 10px; }
    .lang-button { margin: 5px; padding: 10px 20px; border-radius: 8px; border: 1px solid #4caf50; background-color: #1d2129; color: #4caf50; font-weight: bold; cursor: pointer; }
    .lang-button:hover { background-color: #4caf50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'lang' not in st.session_state: st.session_state.lang = None
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = -1
if 'final_plots' not in st.session_state: st.session_state.final_plots = []
if 'total_area_perch' not in st.session_state: st.session_state.total_area_perch = 0.0

# --- Language Dictionary ---
texts = {
    "si": {
        "title": "🌍 ලංකාලෑන්ඩ් ප්‍රෝ GIS",
        "subtitle": "ජාත්‍යන්තර මට්ටමේ ඉඩම් මැනුම් සහ කට්ටි කිරීමේ පද්ධතිය",
        "select_lang": "භාෂාව තෝරන්න",
        "manual_marking": "🗺️ සිතියම මත ලකුණු කිරීම",
        "gps_survey": "🛰️ GPS මගින් මැනීම",
        "back_to_menu": "🔙 මුල් මෙනුවට",
        "analytics_title": "📊 දත්ත වාර්තාව",
        "total_area": "මුළු ප්‍රමාණය",
        "perch_unit": "P",
        "value_per_perch": "පර්චසයක මිල (රු.):",
        "total_value": "මුළු වටිනාකම",
        "subdivision_engine": "🏗️ ඉඩම් කට්ටි කිරීමේ එන්ජිම",
        "split_method": "බෙදුම් ක්‍රමය:",
        "fixed_area": "පර්චස් ප්‍රමාණය අනුව",
        "equal_shares": "සමාන කොටස් ගණන අනුව",
        "target_value": "අගය:",
        "execute_split": "🚀 කට්ටි කර පෙන්වන්න",
        "clear_plots": "🔄 බෙදීම් මකන්න",
        "reset_map": "🗑️ සියල්ල මකන්න",
        "remainder_label": "ඉතිරිය",
        "plot_label_prefix": "කැබැල්ල",
        "sub_success": "කට්ටි කිරීම සාර්ථකයි: {num_plots} සම්පූර්ණ කැබලි.",
        "not_enough_land": "⚠️ ප්‍රමාණවත් ඉඩමක් සලකුණු කර නැත.",
        "change_lang": "🌐 භාෂාව මාරු කරන්න",
        "orientation": "දිශාව:",
        "vertical": "සිර
