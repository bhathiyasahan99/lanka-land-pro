import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import split
import math
import numpy as np

# --- Configuration & Styling (ඔබේ පැරණි CSS එලෙසම තබා ගන්න) ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(90deg, #1b5e20, #4caf50); 
        padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; color: white;
    }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; background: #2e7d32 !important; 
        font-weight: 800; color: white !important;
    }
    .card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
    .metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'lang' not in st.session_state: st.session_state.lang = None
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = -1
if 'final_plots' not in st.session_state: st.session_state.final_plots = []
if 'total_area_perch' not in st.session_state: st.session_state.total_area_perch = 0.0
if 'orientation' not in st.session_state: st.session_state.orientation = "vertical"

# --- Language Dictionary (ඔබේ පැරණි Dictionary එක) ---
texts = {
    "si": {
        "title": "🌍 ලංකාලෑන්ඩ් ප්‍රෝ GIS",
        "subtitle": "ඕනෑම හැඩයක ඉඩම් නිවැරදිව කට්ටි කිරීමේ පද්ධතිය",
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
        "fixed_area": "පර්චස් ප්‍රමාණය අනුව (සම දුර)",
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
        "vertical": "සිරස්",
        "horizontal": "තිරස්",
        "processing_split": "බෙදීම් සැකසෙමින් පවතී...",
        "plot_tooltip": "කැබැල්ල: {label} ({area:.2f}P)"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "Advanced Irregular Land Subdivision System",
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
        "fixed_area": "Fixed Width Split",
        "equal_shares": "Equal Shares (Total)",
        "target_value": "Target Value:",
        "execute_split": "🚀 EXECUTE SUBDIVISION",
        "clear_plots": "🔄 CLEAR PLOTS",
        "reset_map": "🗑️ RESET MAP",
        "remainder_label": "REM",
        "plot_label_prefix": "Plot",
        "sub_success": "Subdivision Success: {num_plots} plots created.",
        "not_enough_land": "⚠️ Not enough land marked.",
        "change_lang": "🌐 Change Language",
        "vertical": "Vertical",
        "horizontal": "Horizontal",
        "processing_split": "Processing subdivision...",
        "plot_tooltip": "Plot: {label} ({area:.2f}P)"
    }
}

# --- Utility Function: Calculate Area ---
def calculate_polygon_area_perch(coords):
    if not coords or len(coords) < 3: return 0.0
    poly = Polygon(coords)
    avg_lat = math.radians(coords[0][0])
    # එකම සූත්‍රය වඩාත් නිවැරදිව
    area_m2 = poly.area * (111319.9 ** 2) * abs(math.cos(avg_lat))
    return area_m2 / 25.29

# --- භාෂා තේරීම (Step 0) ---
if st.session_state.lang is None:
    st.markdown("<div class='main-header'><h1>SELECT LANGUAGE / භාෂාව තෝරන්න</h1></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("ENGLISH"): st.session_state.lang = "en"; st.rerun()
    if c2.button("සිංහල"): st.session_state.lang = "si"; st.rerun()

else:
    T = texts[st.session_state.lang]
    
    # --- Sidebar ---
    if st.sidebar.button(T['back_to_menu']):
        st.session_state.update({"method": None, "points": [], "edit_idx": -1, "final_plots": []})
        st.rerun()
    if st.sidebar.button(T['change_lang']):
        st.session_state.lang = None; st.rerun()

    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button(T['manual_marking']): st.session_state.method = "manual"; st.rerun()
        if col2.button(T['gps_survey']): st.session_state.method = "gps"; st.rerun()
    
    else:
        col_map, col_tools = st.columns([2.5, 1])

        with col_map:
            m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
            LocateControl().add_to(m); Fullscreen().add_to(m); MeasureControl().add_to(m)

            # Draw Subdivided Plots
            for item in st.session_state.final_plots:
                folium.Polygon(locations=item['coords'], color="#4CAF50", weight=2, fill=True, fill_opacity=0.5, tooltip=item['label']).add_to(m)

            # Main Boundary
            if len(st.session_state.points) >= 3:
                folium.Polygon(locations=st.session_state.points, color="yellow", weight=3, fill=False).add_to(m)

            for i, p in enumerate(st.session_state.points):
                folium.CircleMarker(location=p, radius=5, color='orange', fill=True).add_to(m)

            map_data = st_folium(m, height=600, width="100%", key="gis_map")

            if map_data['last_clicked']:
                clicked = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                st.session_state.points.append(clicked)
                st.rerun()

        with col_tools:
            # Analytics Card
            st.markdown(f"<div class='card'><h3>{T['analytics_title']}</h3>", unsafe_allow_html=True)
            if len(st.session_state.points) >= 3:
                st.session_state.total_area_perch = calculate_polygon_area_perch(st.session_state.points)
                st.markdown(f"{T['total_area']}: <span class='metric-val'>{st.session_state.total_area_perch:.2f} P</span>", unsafe_allow_html=True)
            else:
                st.info(T['not_enough_land'])
            st.markdown("</div>", unsafe_allow_html=True)

            # Subdivision Card
            st.markdown(f"<div class='card'><h3>{T['subdivision_engine']}</h3>", unsafe_allow_html=True)
            sub_method = st.selectbox(T['split_method'], [T['fixed_area'], T['equal_shares']])
            
            c1, c2 = st.columns(2)
            if c1.button(T['vertical']): st.session_state.orientation = "vertical"
            if c2.button(T['horizontal']): st.session_state.orientation = "horizontal"
            
            target_val = st.number_input(T['target_value'], min_value=1.0, value=5.0)

            # --- මෙන්න අලුත් Logic එක ---
            if st.button(T['execute_split']):
                if len(st.session_state.points) >= 3:
                    main_poly = Polygon(st.session_state.points)
                    min_lat, min_lon, max_lat, max_lon = main_poly.bounds
                    
                    num_plots = int(st.session_state.total_area_perch // target_val) if sub_method == T['fixed_area'] else int(target_val)
                    
                    st.session_state.final_plots = []
                    
                    if st.session_state.orientation == "vertical":
                        cuts = np.linspace(min_lon, max_lon, num_plots + 1)
                        for i in range(len(cuts)-1):
                            blade = box(min_lat-0.1, cuts[i], max_lat+0.1, cuts[i+1])
                            intersect = main_poly.intersection(blade)
                            if not intersect.is_empty:
                                if intersect.geom_type == 'Polygon':
                                    st.session_state.final_plots.append({'coords': list(intersect.exterior.coords), 'label': f"P{i+1}"})
                    else:
                        cuts = np.linspace(min_lat, max_lat, num_plots + 1)
                        for i in range(len(cuts)-1):
                            blade = box(cuts[i], min_lon-0.1, cuts[i+1], max_lon+0.1)
                            intersect = main_poly.intersection(blade)
                            if not intersect.is_empty:
                                if intersect.geom_type == 'Polygon':
                                    st.session_state.final_plots.append({'coords': list(intersect.exterior.coords), 'label': f"P{i+1}"})
                    st.rerun()

            if st.button(T['clear_plots']): st.session_state.final_plots = []; st.rerun()
            if st.button(T['reset_map']): st.session_state.points = []; st.session_state.final_plots = []; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; opacity:0.5;'>LankaLand Pro v26.0</p>", unsafe_allow_html=True)
