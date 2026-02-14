import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl
from shapely.geometry import Polygon
import math
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration & Styling ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide", page_icon="🗺️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0e1117; color: white; }
.main-header { 
    background: linear-gradient(90deg, #1b5e20, #4caf50); 
    padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.5); color: white;
}
.stButton>button { 
    width: 100%; border-radius: 12px; height: 3.5em; background: #2e7d32 !important; 
    border: none; font-weight: 800; color: white !important; transition: 0.3s ease;
}
.stButton>button:hover { background: #43a047 !important; transform: translateY(-2px); }
.card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
.metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
.plot-result { background-color: #1d2129; border: 1px solid #4caf50; border-radius: 8px; padding: 10px; margin-top: 10px; }
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
        "vertical": "සිරස්",
        "horizontal": "තිරස්",
        "chart_title": "මිල දර්ශක ප්‍රස්ථාරය",
        "price_label": "මිල (LKR)",
        "time_label": "කාලය (දින)"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "International Standard Surveying & Subdivision System",
        "select_lang": "SELECT LANGUAGE",
        "manual_marking": "🗺️ MANUAL SATELLITE MARKING",
        "gps_survey": "🛰️ LIVE GPS FIELD SURVEY",
        "back_to_menu": "🔙 BACK TO MAIN MENU",
        "analytics_title": "📊 ANALYTICS",
        "total_area": "Total Area",
        "perch_unit": "P",
        "value_per_perch": "Value per Perch (LKR):",
        "total_value": "Total Value",
        "subdivision_engine": "🏗️ SUBDIVISION ENGINE",
        "split_method": "Split Method:",
        "fixed_area": "Fixed Area (e.g. 25P)",
        "equal_shares": "Equal Shares (e.g. 5 Lots)",
        "target_value": "Target Value:",
        "execute_split": "🚀 EXECUTE SUBDIVISION",
        "clear_plots": "🔄 CLEAR PLOTS",
        "reset_map": "🗑️ RESET MAP",
        "remainder_label": "REM",
        "plot_label_prefix": "Plot",
        "sub_success": "Subdivision Success: {num_plots} full plots created.",
        "not_enough_land": "⚠️ Not enough land marked.",
        "change_lang": "🌐 Change Language",
        "orientation": "Orientation:",
        "vertical": "Vertical",
        "horizontal": "Horizontal",
        "chart_title": "Price Trend Chart",
        "price_label": "Price (LKR)",
        "time_label": "Time (Days)"
    }
}

# --- Utility Functions ---
def calculate_polygon_area_perch(coords):
    if not coords or len(coords) < 3: return 0.0
    poly = Polygon(coords)
    avg_lat = math.radians(coords[0][0])
    area_m2 = poly.area * (111319.9 ** 2) * abs(math.cos(avg_lat))
    return area_m2 / 25.29

def render_price_chart(T):
    x = np.linspace(0, 10, 20)
    y = [105, 108, 107, 110, 115, 112, 118, 122, 125, 124, 130, 135, 138, 136, 142, 148, 150, 149, 155, 160]
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#1d2129')
    ax.set_facecolor('#ffffff')
    ax.plot(x, y, color='#1b5e20', marker='o', linewidth=2)
    ax.minorticks_on()
    ax.grid(which='major', color='#2ecc71', linestyle='-', linewidth=1.2, alpha=0.8)
    ax.grid(which='minor', color='#d5f5e3', linestyle=':', linewidth=0.7, alpha=0.6)
    ax.set_title(T['chart_title'], color='white', fontsize=12)
    ax.tick_params(colors='white', which='both')
    return fig

# --- Main Logic ---
if st.session_state.lang is None:
    st.markdown("<div class='main-header'><h1>SELECT LANGUAGE / භාෂාව තෝරන්න</h1></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("ENGLISH"): st.session_state.lang = "en"; st.rerun()
    if c2.button("සිංහල"): st.session_state.lang = "si"; st.rerun()
else:
    T = texts[st.session_state.lang]
    st.sidebar.markdown(f"### {T['title']}")
    if st.sidebar.button(T['back_to_menu']):
        st.session_state.update({"method": None, "points": [], "final_plots": [], 'total_area_perch': 0.0})
        st.rerun()

    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button(T['manual_marking']): st.session_state.method = "manual"; st.rerun()
        if col2.button(T['gps_survey']): st.session_state.method = "gps"; st.rerun()
    else:
        col_map, col_tools = st.columns([2.5, 1])
        with col_map:
            m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
            LocateControl().add_to(m)
            Fullscreen().add_to(m)
            MeasureControl().add_to(m)

            if len(st.session_state.points) >= 3:
                folium.Polygon(locations=st.session_state.points, color="#ffeb3b", weight=5).add_to(m)

            for plot in st.session_state.final_plots:
                color = "#FF3D00" if plot['is_rem'] else "#4CAF50"
                folium.Polygon(locations=plot['coords'], color=color, weight=3, fill=True, fill_opacity=0.5, tooltip=plot['label']).add_to(m)

            map_data = st_folium(m, height=650, width="100%", key="gis_map")
            if map_data['last_clicked']:
                st.session_state.points.append((map_data['last_clicked']['lat'], map_data['last_clicked']['lng']))
                st.rerun()

        with col_tools:
            st.markdown(f"<div class='card'><h3>{T['analytics_title']}</h3>", unsafe_allow_html=True)
            area = calculate_polygon_area_perch(st.session_state.points)
            st.markdown(f"{T['total_area']}: <span class='metric-val'>{area:.2f} {T['perch_unit']}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.pyplot(render_price_chart(T))
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button(T['reset_map']):
                st.session_state.update({"points": [], "final_plots": [], 'total_area_perch': 0.0})
                st.rerun()

st.markdown("<p style='text-align:center; opacity:0.5;'>LankaLand Pro v26.0</p>", unsafe_allow_html=True)
