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
        "analytics_title": "📊 දත්ත වාර්තාව",
        "total_area": "මුළු ප්‍රමාණය",
        "perch_unit": "P",
        "chart_title": "මිල දර්ශක ප්‍රස්ථාරය",
        "price_per_perch": "පර්චසයක මිල (රු.):",
        "execute_split": "🚀 කට්ටි කර පෙන්වන්න",
        "reset_map": "🗑️ සියල්ල මකන්න",
        "plot_label_prefix": "කැබැල්ල",
        "remainder_label": "ඉතිරිය"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "International Standard Surveying & Subdivision System",
        "analytics_title": "📊 ANALYTICS",
        "total_area": "Total Area",
        "perch_unit": "P",
        "chart_title": "Price Trend Chart",
        "price_per_perch": "Price per Perch (LKR):",
        "execute_split": "🚀 EXECUTE SUBDIVISION",
        "reset_map": "🗑️ RESET MAP",
        "plot_label_prefix": "Plot",
        "remainder_label": "REM"
    }
}

# --- Utility Functions ---
def calculate_polygon_area_perch(coords):
    if not coords or len(coords) < 3: return 0.0
    polygon = Polygon(coords)
    area_sq_deg = polygon.area
    avg_lat_rad = math.radians(coords[0][0]) 
    area_m2 = area_sq_deg * (111319.9 ** 2) * abs(math.cos(avg_lat_rad))
    return area_m2 / 25.29

def render_green_grid_chart(T):
    # දත්ත සැකසීම
    x = np.arange(1, 11)
    y = [10, 12, 11, 14, 13, 16, 18, 17, 20, 22] # මිල උදාහරණ
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#1d2129') # Card color
    ax.set_facecolor('#ffffff')
    
    ax.plot(x, y, color='#1b5e20', marker='o', linewidth=2)
    
    # ඔබ ඉල්ලූ පැහැදිලි කොළ පාට කට්ටි (Grid Lines)
    ax.minorticks_on()
    ax.grid(which='major', color='#2ecc71', linestyle='-', linewidth=1.2, alpha=0.8)
    ax.grid(which='minor', color='#d5f5e3', linestyle=':', linewidth=0.7, alpha=0.6)
    
    ax.set_title(T['chart_title'], color='white', fontsize=10)
    ax.tick_params(colors='white', which='both', labelsize=8)
    return fig

# --- Main Logic ---
if st.session_state.lang is None:
    st.markdown("<div class='main-header'><h1>SELECT LANGUAGE / භාෂාව තෝරන්න</h1></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("ENGLISH"): st.session_state.lang = "en"; st.rerun()
    if c2.button("සිංහල"): st.session_state.lang = "si"; st.rerun()
else:
    T = texts[st.session_state.lang]
    
    # Sidebar
    st.sidebar.title(T['title'])
    if st.sidebar.button(T['reset_map']):
        st.session_state.update({"points": [], "final_plots": [], 'total_area_perch': 0.0})
        st.rerun()

    st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)
    
    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        # Draw Existing Points & Lines
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffeb3b", weight=4).add_to(m)
        
        # Draw Subdivided Plots (කට්ටි වෙන වෙනම පෙන්වන කොටස)
        for plot in st.session_state.final_plots:
            line_color = "#f44336" if plot['is_rem'] else "#00e676"
            folium.Polygon(
                locations=plot['coords'],
                color=line_color, # පැහැදිලි වෙන් කළ හැකි රේඛා
                weight=3,
                fill=True,
                fill_opacity=0.3,
                tooltip=plot['label']
            ).add_to(m)

        map_data = st_folium(m, height=600, width="100%", key="gis_map")

        if map_data['last_clicked']:
            clicked = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            st.session_state.points.append(clicked)
            st.rerun()

    with col_tools:
        # Analytics Card
        st.markdown(f"<div class='card'><h3>{T['analytics_title']}</h3>", unsafe_allow_html=True)
        area = calculate_polygon_area_perch(st.session_state.points)
        st.markdown(f"{T['total_area']}: <span class='metric-val'>{area:.2f} {T['perch_unit']}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ඔබ ඉල්ලූ පැහැදිලි Grid Lines සහිත ප්‍රස්ථාරය
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.pyplot(render_green_grid_chart(T))
        st.markdown("</div>", unsafe_allow_html=True)

        # Subdivision Execution
        if st.button(T['execute_split']):
            if len(st.session_state.points) >= 4:
                # සරල උදාහරණ බෙදුමක් (මෙහිදී Logic එක අනුව කට්ටි වෙන් කරයි)
                # මෙම කොටසට ඔබේ Subdivision Logic එක ඇතුළත් කළ හැක
                p = st.session_state.points
                st.session_state.final_plots = [
                    {'coords': [p[0], p[1], (p[1][0], p[2][1]), (p[0][0], p[2][1])], 'label': 'කැබැල්ල 1', 'is_rem': False},
                    {'coords': [(p[1][0], p[2][1]), p[2], p[3], (p[0][0], p[2][1])], 'label': 'ඉතිරිය', 'is_rem': True}
                ]
                st.rerun()

st.markdown("<p style='text-align:center; opacity:0.5;'>LankaLand Pro v26.0</p>", unsafe_allow_html=True)
