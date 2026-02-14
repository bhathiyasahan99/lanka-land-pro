import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl, Draw
from shapely.geometry import Polygon, MultiPolygon, box
import math
import numpy as np

# --- 1. Configuration & Original Professional Styling ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(90deg, #1b5e20, #2e7d32); 
        padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); color: white;
    }
    .card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
    .metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; background: #2e7d32 !important; 
        font-weight: 800; color: white !important; transition: 0.3s;
    }
    .stButton>button:hover { background: #1b5e20 !important; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Advanced Mathematical Core (International Standard) ---
def get_actual_area_perch(poly):
    if poly is None or poly.is_empty: return 0.0
    if not hasattr(poly, 'exterior'): return 0.0
    coords = list(poly.exterior.coords)
    avg_lat = math.radians(coords[0][1])
    # WGS84 projection approximation for high accuracy
    area_m2 = poly.area * (111319.9 ** 2) * abs(math.cos(avg_lat))
    return area_m2 / 25.29

def split_equal_area_pro(polygon, target_perch, orientation="vertical"):
    """ හැඩය කුමක් වුවත් වර්ගඵලය සමාන වන සේ බෙදන ජාත්‍යන්තර ප්‍රමිතියේ Algorithm එක """
    plots = []
    remaining_poly = polygon
    total_area = get_actual_area_perch(polygon)
    num_plots = int(total_area // target_perch)
    
    for _ in range(num_plots):
        if remaining_poly.is_empty: break
        minx, miny, maxx, maxy = remaining_poly.bounds
        low, high = (minx, maxx) if orientation == "vertical" else (miny, maxy)
        
        # Binary Search for 99.9% Area Accuracy
        for _ in range(25):
            mid = (low + high) / 2
            blade = box(minx, miny, mid, maxy) if orientation == "vertical" else box(minx, miny, maxx, mid)
            if get_actual_area_perch(remaining_poly.intersection(blade)) < target_perch:
                low = mid
            else:
                high = mid
        
        cutter = box(minx, miny, high, maxy) if orientation == "vertical" else box(minx, miny, maxx, high)
        plot = remaining_poly.intersection(cutter)
        if not plot.is_empty:
            if plot.geom_type == 'Polygon': plots.append(plot)
            elif plot.geom_type in ['MultiPolygon', 'GeometryCollection']:
                for g in plot.geoms: 
                    if g.geom_type == 'Polygon': plots.append(g)
        remaining_poly = remaining_poly.difference(cutter)
    
    if not remaining_poly.is_empty and get_actual_area_perch(remaining_poly) > 0.1:
        plots.append(remaining_poly)
    return plots

# --- 3. Session State ---
if 'lang' not in st.session_state: st.session_state.lang = None
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'final_plots' not in st.session_state: st.session_state.final_plots = []
if 'orientation' not in st.session_state: st.session_state.orientation = "vertical"

# --- 4. Language Logic ---
texts = {
    "si": {
        "title": "🌍 ලංකාලෑන්ඩ් ප්‍රෝ GIS",
        "manual": "🗺️ සිතියම මත ලකුණු කිරීම",
        "gps": "🛰️ GPS මගින් මැනීම",
        "analytics": "📊 දත්ත වාර්තාව",
        "area": "මුළු ප්‍රමාණය",
        "execute": "🚀 නිරවද්‍යව කට්ටි කරන්න",
        "reset": "🗑️ සියල්ල මකන්න",
        "target": "කැබැල්ලක ප්‍රමාණය (P)",
        "undo": "↩️ අවසන් ලක්ෂ්‍යය මකන්න"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS",
        "manual": "🗺️ MANUAL MARKING",
        "gps": "🛰️ GPS LIVE SURVEY",
        "analytics": "📊 ANALYTICS",
        "area": "Total Area",
        "execute": "🚀 ACCURATE SPLIT",
        "reset": "🗑️ RESET ALL",
        "target": "Target Area (P)",
        "undo": "↩️ UNDO LAST"
    }
}

# --- 5. Main UI Flow ---
if st.session_state.lang is None:
    st.markdown("<div class='main-header'><h1>LANKALAND PRO GIS</h1></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("සිංහල"): st.session_state.lang = "si"; st.rerun()
    if c2.button("ENGLISH"): st.session_state.lang = "en"; st.rerun()
else:
    T = texts[st.session_state.lang]
    
    if st.sidebar.button("🔙 Main Menu"):
        st.session_state.update({"method": None, "points": [], "final_plots": []})
        st.rerun()

    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button(T['manual']): st.session_state.method = "manual"; st.rerun()
        if col2.button(T['gps']): st.session_state.method = "gps"; st.rerun()
    
    else:
        col_map, col_tools = st.columns([2.5, 1])

        with col_map:
            m = folium.Map(location=[7.8731, 80.7718], zoom_start=19, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
            LocateControl(auto_start=(st.session_state.method == "gps")).add_to(m)
            Fullscreen().add_to(m); MeasureControl().add_to(m)
            
            # 
            # Draw Subdivided Plots
            for item in st.session_state.final_plots:
                if hasattr(item, 'exterior'):
                    area_p = get_actual_area_perch(item)
                    folium.Polygon(locations=[(p[1], p[0]) for p in item.exterior.coords], 
                                  color="#4CAF50", weight=2, fill=True, fill_opacity=0.5,
                                  tooltip=f"{area_p:.2f} Perch").add_to(m)

            # Draw Main Boundary
            if len(st.session_state.points) >= 2:
                folium.Polygon(locations=st.session_state.points, color="yellow", weight=3, fill=False).add_to(m)

            # Markers
            for p in st.session_state.points:
                folium.Marker(location=p, icon=folium.Icon(color="green")).add_to(m)

            map_data = st_folium(m, height=650, width="100%", key="main_map")

            if map_data['last_clicked'] and st.session_state.method == "manual":
                st.session_state.points.append((map_data['last_clicked']['lat'], map_data['last_clicked']['lng']))
                st.rerun()

        with col_tools:
            st.markdown(f"<div class='card'><h3>{T['analytics']}</h3>", unsafe_allow_html=True)
            if len(st.session_state.points) >= 3:
                # Create Shapely Polygon for Calculations
                shp_poly = Polygon([(p[1], p[0]) for p in st.session_state.points])
                total_area = get_actual_area_perch(shp_poly)
                st.markdown(f"{T['area']}: <span class='metric-val'>{total_area:.2f} P</span>", unsafe_allow_html=True)
                
                st.markdown("---")
                target = st.number_input(T['target'], value=10.0, min_value=1.0)
                
                c1, c2 = st.columns(2)
                if c1.button("V - Split"): st.session_state.orientation = "vertical"
                if c2.button("H - Split"): st.session_state.orientation = "horizontal"
                
                if st.button(T['execute']):
                    st.session_state.final_plots = split_equal_area_pro(shp_poly, target, st.session_state.orientation)
                    st.rerun()
            else:
                st.info("සිතියම මත ලක්ෂ්‍ය 3ක් හෝ වැඩි ගණනක් ලකුණු කරන්න.")
            
            if st.button(T['undo']):
                if st.session_state.points: st.session_state.points.pop(); st.rerun()
            if st.button(T['reset']):
                st.session_state.points = []; st.session_state.final_plots = []; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; opacity:0.5;'>LankaLand Pro | International Level GIS Core</p>", unsafe_allow_html=True)
