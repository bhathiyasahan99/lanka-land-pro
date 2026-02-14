import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl
from shapely.geometry import Polygon, MultiPolygon, box
import math
import numpy as np

# --- Configuration ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .main-header { background: linear-gradient(90deg, #1b5e20, #4caf50); padding: 20px; border-radius: 15px; text-align: center; color: white; margin-bottom: 20px; }
    .card { background: #1d2129; padding: 15px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }
    .metric-val { font-size: 22px; font-weight: bold; color: #4caf50; }
    .res-box { padding: 10px; background: #2e7d32; border-radius: 5px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State ---
if 'lang' not in st.session_state: st.session_state.lang = "si"
if 'points' not in st.session_state: st.session_state.points = []
if 'final_plots' not in st.session_state: st.session_state.final_plots = []
if 'orientation' not in st.session_state: st.session_state.orientation = "vertical"

texts = {
    "si": {
        "title": "🌍 ලංකාලෑන්ඩ් ප්‍රෝ GIS",
        "total_area": "මුළු ප්‍රමාණය",
        "perch_unit": "P",
        "subdivision": "🏗️ ඉඩම් කට්ටි කිරීම",
        "execute": "🚀 කට්ටි කර පෙන්වන්න",
        "results": "📊 ප්‍රතිඵල",
        "plots_count": "නිර්මාණය වූ කට්ටි ගණන",
        "remainder": "ඉතිරි ප්‍රමාණය",
        "clear": "🗑️ සියල්ල මකන්න"
    }
}
T = texts["si"]

def calculate_area(coords):
    if len(coords) < 3: return 0.0
    poly = Polygon(coords)
    avg_lat = math.radians(coords[0][0])
    area_m2 = poly.area * (111319.9 ** 2) * abs(math.cos(avg_lat))
    return area_m2 / 25.29

# --- UI Layout ---
st.markdown(f"<div class='main-header'><h1>{T['title']}</h1></div>", unsafe_allow_html=True)
col_map, col_tools = st.columns([2, 1])

with col_map:
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
    
    # කට්ටි ඇඳීම
    for item in st.session_state.final_plots:
        folium.Polygon(locations=item['coords'], color="cyan", weight=2, fill=True, fill_opacity=0.4, tooltip=item['label']).add_to(m)

    # මායිම ඇඳීම
    if len(st.session_state.points) >= 3:
        folium.Polygon(locations=st.session_state.points, color="yellow", weight=3).add_to(m)
    
    for p in st.session_state.points:
        folium.CircleMarker(location=p, radius=4, color='orange', fill=True).add_to(m)

    map_data = st_folium(m, height=500, width="100%", key="map")
    if map_data['last_clicked']:
        st.session_state.points.append((map_data['last_clicked']['lat'], map_data['last_clicked']['lng']))
        st.rerun()

with col_tools:
    st.markdown(f"<div class='card'><h3>{T['total_area']}</h3>", unsafe_allow_html=True)
    total_p = calculate_area(st.session_state.points)
    st.markdown(f"<span class='metric-val'>{total_p:.2f} {T['perch_unit']}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='card'><h3>{T['subdivision']}</h3>", unsafe_allow_html=True)
    target = st.number_input("කැබැල්ලක ප්‍රමාණය (P)", min_value=1.0, value=10.0)
    
    c1, c2 = st.columns(2)
    if c1.button("සිරස් (Vert)"): st.session_state.orientation = "vertical"
    if c2.button("තිරස් (Hori)"): st.session_state.orientation = "horizontal"

    if st.button(T['execute']):
        if len(st.session_state.points) >= 3:
            main_poly = Polygon(st.session_state.points)
            min_lat, min_lon, max_lat, max_lon = main_poly.bounds
            
            num_plots = int(total_p // target)
            st.session_state.final_plots = []
            
            # Intersection Logic
            if st.session_state.orientation == "vertical":
                cuts = np.linspace(min_lon, max_lon, num_plots + 1)
                for i in range(len(cuts)-1):
                    blade = box(min_lat-0.01, cuts[i], max_lat+0.01, cuts[i+1])
                    intersect = main_poly.intersection(blade)
                    if not intersect.is_empty:
                        # MultiPolygon නම් කොටස් වලට කඩා ගන්නවා
                        if isinstance(intersect, MultiPolygon):
                            for part in intersect.geoms:
                                st.session_state.final_plots.append({'coords': list(part.exterior.coords), 'label': f"Plot {i+1}"})
                        else:
                            st.session_state.final_plots.append({'coords': list(intersect.exterior.coords), 'label': f"Plot {i+1}"})
            else:
                cuts = np.linspace(min_lat, max_lat, num_plots + 1)
                for i in range(len(cuts)-1):
                    blade = box(cuts[i], min_lon-0.01, cuts[i+1], max_lon+0.01)
                    intersect = main_poly.intersection(blade)
                    if not intersect.is_empty:
                        if isinstance(intersect, MultiPolygon):
                            for part in intersect.geoms:
                                st.session_state.final_plots.append({'coords': list(part.exterior.coords), 'label': f"Plot {i+1}"})
                        else:
                            st.session_state.final_plots.append({'coords': list(intersect.exterior.coords), 'label': f"Plot {i+1}"})
            st.rerun()

    if st.button(T['clear']):
        st.session_state.points = []
        st.session_state.final_plots = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # --- ප්‍රතිඵල පෙන්වන කොටස ---
    if st.session_state.final_plots:
        st.markdown(f"<div class='card'><h3>{T['results']}</h3>", unsafe_allow_html=True)
        count = len(st.session_state.final_plots)
        rem = total_p % target
        st.write(f"✅ {T['plots_count']}: **{count}**")
        st.write(f"⚠️ {T['remainder']}: **{rem:.2f} {T['perch_unit']}**")
        st.markdown("</div>", unsafe_allow_html=True)
