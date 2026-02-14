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
.card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
.metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'lang' not in st.session_state: st.session_state.lang = None
if 'points' not in st.session_state: st.session_state.points = []
if 'final_plots' not in st.session_state: st.session_state.final_plots = []

# --- Language Dictionary (Error Free) ---
texts = {
    "si": {
        "title": "🌍 ලංකාලෑන්ඩ් ප්‍රෝ GIS",
        "subtitle": "ජාත්‍යන්තර මට්ටමේ ඉඩම් මැනුම් සහ කට්ටි කිරීමේ පද්ධතිය",
        "analytics_title": "📊 දත්ත වාර්තාව",
        "total_area": "මුළු ප්‍රමාණය",
        "perch_unit": "P",
        "chart_title": "මිල දර්ශක ප්‍රස්ථාරය (Grid Lines සහිත)",
        "execute_split": "🚀 කට්ටි කර පෙන්වන්න",
        "reset_map": "🗑️ සියල්ල මකන්න"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "International Standard Surveying & Subdivision System",
        "analytics_title": "📊 ANALYTICS",
        "total_area": "Total Area",
        "perch_unit": "P",
        "chart_title": "Price Trend Chart (With Grid)",
        "execute_split": "🚀 EXECUTE SUBDIVISION",
        "reset_map": "🗑️ RESET MAP"
    }
}

# --- Functions ---
def calculate_area(coords):
    if len(coords) < 3: return 0.0
    poly = Polygon(coords)
    avg_lat = math.radians(coords[0][0])
    return (poly.area * (111319.9**2) * abs(math.cos(avg_lat))) / 25.29

def plot_price_graph(T):
    x = np.linspace(0, 10, 10)
    y = [10, 15, 13, 18, 20, 25, 22, 28, 30, 35]
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#1d2129')
    ax.set_facecolor('#ffffff')
    ax.plot(x, y, color='#1b5e20', marker='o', linewidth=2)
    
    # ඔබ ඉල්ලූ පැහැදිලි කොළ පාට Grid Lines
    ax.minorticks_on()
    ax.grid(which='major', color='#2ecc71', linestyle='-', linewidth=1.2)
    ax.grid(which='minor', color='#d5f5e3', linestyle=':', linewidth=0.8)
    
    ax.set_title(T['chart_title'], color='white')
    ax.tick_params(colors='white', which='both')
    return fig

# --- App Interface ---
if st.session_state.lang is None:
    st.title("SELECT LANGUAGE")
    if st.button("සිංහල"): st.session_state.lang = "si"; st.rerun()
    if st.button("ENGLISH"): st.session_state.lang = "en"; st.rerun()
else:
    T = texts[st.session_state.lang]
    st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    
    with col1:
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        # ඉඩම් කට්ටි (Lines) පෙන්වීම
        for plot in st.session_state.final_plots:
            folium.Polygon(locations=plot['coords'], color="#00e676", weight=3, fill=True, fill_opacity=0.4).add_to(m)
            
        map_out = st_folium(m, height=500, width="100%")
        if map_out['last_clicked']:
            st.session_state.points.append((map_out['last_clicked']['lat'], map_out['last_clicked']['lng']))
            st.rerun()

    with col2:
        st.markdown(f"<div class='card'><h3>{T['analytics_title']}</h3>", unsafe_allow_html=True)
        area = calculate_area(st.session_state.points)
        st.markdown(f"{T['total_area']}: <span class='metric-val'>{area:.2f} P</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Grid chart
        st.pyplot(plot_price_graph(T))
        
        if st.button(T['execute_split']):
            # සරල බෙදුම් logic එකක් (Placeholder)
            if len(st.session_state.points) >= 3:
                st.session_state.final_plots.append({'coords': st.session_state.points})
                st.rerun()

        if st.button(T['reset_map']):
            st.session_state.points = []; st.session_state.final_plots = []; st.rerun()
