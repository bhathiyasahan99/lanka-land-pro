import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl, Draw
from shapely.geometry import Polygon, MultiPolygon, box
import math
import numpy as np

# --- Configuration & Styling ---
st.set_page_config(page_title="LankaLand Pro GIS | Enterprise", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%); 
        padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; color: white;
    }
    .card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
    .metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; background: #2e7d32 !important; 
        font-weight: 800; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'lang' not in st.session_state: st.session_state.lang = None
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'final_plots' not in st.session_state: st.session_state.final_plots = []
if 'orientation' not in st.session_state: st.session_state.orientation = "vertical"

# --- Math Functions ---
def get_distance_meters(p1, p2):
    R = 6371000
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    return 2 * R * math.asin(math.sqrt(math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2))

def get_actual_area_perch(poly):
    if poly is None or poly.is_empty: return 0.0
    if not hasattr(poly, 'exterior'): return 0.0
    coords = list(poly.exterior.coords)
    avg_lat = math.radians(coords[0][1])
    area_m2 = poly.area * (111319.9 ** 2) * abs(math.cos(avg_lat))
    return area_m2 / 25.29

# --- Equal Area Splitting Logic ---
def split_equal_area(polygon, target_perch, orientation="vertical"):
    total_area = get_actual_area_perch(polygon)
    if total_area <= target_perch:
        return [polygon]
    
    plots = []
    remaining_poly = polygon
    num_plots = int(total_area // target_perch)
    
    for _ in range(num_plots):
        if remaining_poly.is_empty: break
        minx, miny, maxx, maxy = remaining_poly.bounds
        low, high = (minx, maxx) if orientation == "vertical" else (miny, maxy)
        
        # Binary Search for high precision area cutting
        for _ in range(25):
            mid = (low + high) / 2
            blade = box(mid, miny, maxx, maxy) if orientation == "vertical" else box(minx, mid, maxx, maxy)
            # We want to cut 'target_perch' from the other side
            test_part = remaining_poly.difference(blade)
            if get_actual_area_perch(test_part) < target_perch:
                low = mid if orientation == "vertical" else low # Logic depends on direction
                high = mid
            else:
                high = mid if orientation == "vertical" else high
                low = mid
        
        # This part handles the split effectively
        split_line = high
        cutter = box(minx, miny, split_line, maxy) if orientation == "vertical" else box(minx, miny, maxx, split_line)
        plot = remaining_poly.intersection(cutter)
        
        if not plot.is_empty:
            if plot.geom_type == 'Polygon': plots.append(plot)
            elif plot.geom_type in ['MultiPolygon', 'GeometryCollection']:
                for g in plot.geoms:
                    if g.geom_type == 'Polygon': plots.append(g)
                    
        remaining_poly = remaining_poly.difference(cutter)
        
    if not remaining_poly.is_empty and get_actual_area_perch(remaining_poly) > 0.05:
        plots.append(remaining_poly)
    return plots

# --- UI Dictionary ---
T_DICT = {
    "si": {"title": "LANKALAND PRO GIS", "analytics": "මැනුම් වාර්තාව", "subdivision": "කට්ටි කිරීම", "execute": "කට්ටි කරන්න", "reset": "සියල්ල මකන්න", "area": "වර්ගඵලය", "mark_gps": "ස්ථානය සලකුණු කරන්න", "undo": "පොයින්ට් එකක් මකන්න"},
    "en": {"title": "LANKALAND PRO GIS", "analytics": "ANALYTICS", "subdivision": "SUBDIVISION", "execute": "EXECUTE SPLIT", "reset": "RESET ALL", "area": "Area", "mark_gps": "MARK GPS LOCATION", "undo": "UNDO POINT"}
}

# --- App Execution ---
if st.session_state.lang is None:
    st.markdown("<div class='main-header'><h1>LANKALAND PRO</h1><h3>Select Language / භාෂාව තෝරන්න</h3></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("සිංහල"): st.session_state.lang = "si"; st.rerun()
    if c2.button("English"): st.session_state.lang = "en"; st.rerun()
else:
    T = T_DICT[st.session_state.lang]
    if st.sidebar.button("BACK TO MENU"):
        st.session_state.update({"method":None, "points":[], "final_plots":[]})
        st.rerun()

    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>Enterprise Surveying Suite</p></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🗺️ MANUAL MARKING"): st.session_state.method = "manual"; st.rerun()
        if c2.button("🛰️ GPS LIVE SURVEY"): st.session_state.method = "gps"; st.rerun()
    else:
        col_map, col_tools = st.columns([2.5, 1])
        with col_map:
            m = folium.Map(location=[7.8731, 80.7718], zoom_start=19, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
            LocateControl(auto_start=(st.session_state.method == "gps")).add_to(m)
            Draw(export=True).add_to(m)
            Fullscreen().add_to(m); MeasureControl().add_to(m)

            # Draw Final Plots
            for item in st.session_state.final_plots:
                if hasattr(item, 'exterior'):
                    a_val = get_actual_area_perch(item)
                    folium.Polygon(locations=[(lat, lon) for lon, lat in item.exterior.coords], color="#00ff00", weight=2, fill=True, fill_opacity=0.4, tooltip=f"{a_val:.2f} P").add_to(m)

            # Draw Boundary & Distances
            if len(st.session_state.points) >= 2:
                folium.Polygon(locations=st.session_state.points, color="yellow", weight=3, fill=False).add_to(m)
                for i in range(len(st.session_state.points)):
                    p1, p2 = st.session_state.points[i], st.session_state.points[(i+1)%len(st.session_state.points)]
                    mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]
                    dist = get_distance_meters(p1, p2)
                    folium.Marker(mid, icon=folium.DivIcon(html=f'<div style="font-size:8pt; color:white; background:black; padding:2px; border-radius:3px;">{dist:.1f}m</div>')).add_to(m)
            
            for p in st.session_state.points:
                folium.Marker(location=p, draggable=True, icon=folium.Icon(color="green")).add_to(m)

            map_data = st_folium(m, height=650, width="100%", key="enterprise_map")
            if map_data['last_clicked'] and st.session_state.method == "manual":
                st.session_state.points.append((map_data['last_clicked']['lat'], map_data['last_clicked']['lng']))
                st.rerun()

        with col_tools:
            if len(st.session_state.points) >= 3:
                # Convert (lat, lon) to (lon, lat) for Shapely
                shp_points = [(p[1], p[0]) for p in st.session_state.points]
                main_poly = Polygon(shp_points)
                total_area = get_actual_area_perch(main_poly)
                
                st.markdown(f"<div class='card'><h3>{T['analytics']}</h3>{T['area']}: <span class='metric-val'>{total_area:.2f} P</span></div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='card'><h3>{T['subdivision']}</h3>", unsafe_allow_html=True)
                target = st.number_input("Target Perch", value=10.0, min_value=1.0)
                if st.button("V - Split"): st.session_state.orientation = "vertical"; st.rerun()
                if st.button("H - Split"): st.session_state.orientation = "horizontal"; st.rerun()
                
                if st.button(T['execute']):
                    st.session_state.final_plots = split_equal_area(main_poly, target, st.session_state.orientation)
                    st.rerun()
                
                if st.button(T['reset']):
                    st.session_state.points = []; st.session_state.final_plots = []; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.method == "gps":
                st.markdown(f"<div class='card'><h3>🛰️ GPS</h3>", unsafe_allow_html=True)
                if st.button(T['mark_gps']):
                    if map_data['last_clicked']:
                        st.session_state.points.append((map_data['last_clicked']['lat'], map_data['last_clicked']['lng']))
                        st.rerun()
                if st.button(T['undo']):
                    if st.session_state.points: st.session_state.points.pop(); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center; opacity:0.3;'>LankaLand Pro Enterprise v3.3 - Stable</p>", unsafe_allow_html=True)
