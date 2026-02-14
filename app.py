import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl, Draw
from shapely.geometry import Polygon, MultiPolygon, box, shape
import math
import numpy as np

# --- Configuration & Styling (Original preserved) ---
st.set_page_config(page_title="LankaLand Pro GIS | Enterprise", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(135deg, #0d47a1 0%, #1b5e20 100%); 
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

# --- Calculations ---
def get_distance_meters(p1, p2):
    R = 6371000
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def calculate_detailed_area(coords):
    if len(coords) < 3: return 0.0, 0.0
    poly = Polygon(coords)
    avg_lat = math.radians(coords[0][0])
    area_m2 = poly.area * (111319.9 ** 2) * abs(math.cos(avg_lat))
    perimeter = sum(get_distance_meters(coords[i], coords[(i+1)%len(coords)]) for i in range(len(coords)))
    return area_m2 / 25.29, perimeter

# --- Language Dictionary ---
texts = {
    "si": {
        "title": "🌍 LANKALAND PRO GIS | Enterprise",
        "subtitle": "ජාත්‍යන්තර ප්‍රමිතියේ යටිතල පහසුකම් සහ ඉඩම් සැලසුම්කරණය",
        "manual": "🗺️ සිතියම මත සලකුණු කිරීම",
        "gps": "🛰️ GPS සජීවී මැනීම (Field Survey)",
        "analytics": "📊 මැනුම් වාර්තාව",
        "subdivision": "🏗️ කට්ටි කිරීමේ එන්ජිම",
        "execute": "🚀 කට්ටි කර පෙන්වන්න",
        "reset": "🗑️ සියල්ල මකන්න",
        "val_p": "පර්චසයක මිල:",
        "mark_gps": "📍 ස්ථානය සලකුණු කරන්න",
        "undo": "↩️ අවසන් ලක්ෂ්‍යය මකන්න"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS | Enterprise",
        "subtitle": "International Infrastructure & Land Planning",
        "manual": "🗺️ MANUAL MARKING",
        "gps": "🛰️ LIVE GPS SURVEY",
        "analytics": "📊 SURVEY ANALYTICS",
        "subdivision": "🏗️ SUBDIVISION ENGINE",
        "execute": "🚀 EXECUTE SPLIT",
        "reset": "🗑️ RESET ALL",
        "val_p": "Value per Perch:",
        "mark_gps": "📍 MARK LOCATION",
        "undo": "↩️ UNDO LAST"
    }
}

# --- UI Logic ---
if st.session_state.lang is None:
    st.markdown("<div class='main-header'><h1>LANKALAND PRO GIS</h1><h3>භාෂාව තෝරන්න / Select Language</h3></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("සිංහල"): st.session_state.lang = "si"; st.rerun()
    if c2.button("ENGLISH"): st.session_state.lang = "en"; st.rerun()
else:
    T = texts[st.session_state.lang]
    
    if st.sidebar.button("🔙 Main Menu"):
        st.session_state.update({"method": None, "points": [], "final_plots": []})
        st.rerun()

    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button(T['manual']): st.session_state.method = "manual"; st.rerun()
        if col2.button(T['gps']): st.session_state.method = "gps"; st.rerun()
    else:
        col_map, col_tools = st.columns([2.5, 1])

        with col_map:
            m = folium.Map(location=[7.8731, 80.7718], zoom_start=19, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
            
            # පවතින Locate Control එක
            LocateControl(auto_start=(st.session_state.method == "gps")).add_to(m)
            
            # ජාත්‍යන්තර මට්ටමේ Drawing Toolbar එක (පාරවල්, ගොඩනැගිලි ඇඳීමට)
            draw = Draw(
                export=True,
                draw_options={
                    'polyline': {'shapeOptions': {'color': '#ff5722', 'weight': 8}, 'tooltip': 'Draw Roads'},
                    'polygon': {'shapeOptions': {'color': '#3f51b5'}, 'tooltip': 'Mark Zones'},
                    'circle': False, 'rectangle': True, 'marker': True
                }
            ).add_to(m)
            
            Fullscreen().add_to(m)
            MeasureControl(primary_length_unit='meters').add_to(m)

            # කලින් කළ කට්ටි ඇඳීම
            for item in st.session_state.final_plots:
                folium.Polygon(locations=item['coords'], color="#4CAF50", weight=2, fill=True, fill_opacity=0.4).add_to(m)

            # ප්‍රධාන ඉඩම් මායිම සහ දුර ලේබල්
            if len(st.session_state.points) >= 2:
                folium.PolyLine(locations=st.session_state.points + ([st.session_state.points[0]] if len(st.session_state.points)>2 else []), color="yellow", weight=4).add_to(m)
                for i in range(len(st.session_state.points)):
                    p1 = st.session_state.points[i]
                    p2 = st.session_state.points[(i+1)%len(st.session_state.points)]
                    mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]
                    dist = get_distance_meters(p1, p2)
                    folium.Marker(mid, icon=folium.DivIcon(html=f'<div style="font-size: 8pt; color: white; background:black; padding:2px;">{dist:.1f}m</div>')).add_to(m)

            # Draggable Markers
            for i, p in enumerate(st.session_state.points):
                folium.Marker(location=p, draggable=True, icon=folium.Icon(color="green")).add_to(m)

            map_data = st_folium(m, height=700, width="100%", key="main_map")

            if map_data['last_clicked'] and st.session_state.method == "manual":
                st.session_state.points.append((map_data['last_clicked']['lat'], map_data['last_clicked']['lng']))
                st.rerun()

        with col_tools:
            # --- Survey Controls (GPS) ---
            if st.session_state.method == "gps":
                st.markdown(f"<div class='card'><h3>🛰️ GPS SURVEY</h3>", unsafe_allow_html=True)
                if st.button(T['mark_gps']):
                    if map_data['last_clicked']:
                        st.session_state.points.append((map_data['last_clicked']['lat'], map_data['last_clicked']['lng']))
                        st.rerun()
                if st.button(T['undo']):
                    if st.session_state.points: st.session_state.points.pop(); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Infrastructure Info (New) ---
            if map_data and map_data['all_drawings']:
                st.markdown("<div class='card' style='border-color: #ff5722;'><h3>🛣️ Infrastructure</h3>", unsafe_allow_html=True)
                st.write(f"Elements Drawn: {len(map_data['all_drawings'])}")
                st.info("සිතියම මත ඇඳි පාරවල්/කලාප හඳුනාගෙන ඇත.")
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Analytics ---
            st.markdown(f"<div class='card'><h3>{T['analytics']}</h3>", unsafe_allow_html=True)
            area_p, peri_m = calculate_detailed_area(st.session_state.points)
            st.markdown(f"Area: <span class='metric-val'>{area_p:.2f} P</span>", unsafe_allow_html=True)
            st.markdown(f"Perimeter: <span class='metric-val' style='color:#ffa726'>{peri_m:.1f} m</span>", unsafe_allow_html=True)
            val_per_p = st.number_input(T['val_p'], value=100000)
            st.markdown(f"Value: <b>LKR {(area_p * val_per_p):,.0f}</b>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # --- Subdivision ---
            st.markdown(f"<div class='card'><h3>{T['subdivision']}</h3>", unsafe_allow_html=True)
            target = st.number_input("Target Size (P)", value=10.0)
            c1, c2 = st.columns(2)
            if c1.button("සිරස් (V)"): st.session_state.orientation = "vertical"
            if c2.button("තිරස් (H)"): st.session_state.orientation = "horizontal"

            if st.button(T['execute']):
                if len(st.session_state.points) >= 3:
                    main_poly = Polygon(st.session_state.points)
                    
                    # පාරවල් ඇඳ තිබේ නම් ඒවා ඉඩමෙන් ඉවත් කිරීමේ Logic එක
                    combined_roads = None
                    if map_data['all_drawings']:
                        for drawing in map_data['all_drawings']:
                            if drawing['geometry']['type'] in ['Polygon', 'LineString']:
                                road_shape = shape(drawing['geometry'])
                                if combined_roads is None: combined_roads = road_shape
                                else: combined_roads = combined_roads.union(road_shape)
                    
                    # ඉඩමෙන් පාරවල් ඉවත් කරන්න (Difference)
                    operable_poly = main_poly
                    if combined_roads:
                        operable_poly = main_poly.difference(combined_roads)

                    # බෙදීම සිදු කිරීම
                    min_lat, min_lon, max_lat, max_lon = operable_poly.bounds
                    num = int(area_p // target)
                    st.session_state.final_plots = []
                    cuts = np.linspace(min_lon, max_lon, num + 1) if st.session_state.orientation == "vertical" else np.linspace(min_lat, max_lat, num + 1)
                    
                    for i in range(len(cuts)-1):
                        blade = box(min_lat-0.1, cuts[i], max_lat+0.1, cuts[i+1]) if st.session_state.orientation == "vertical" else box(cuts[i], min_lon-0.1, cuts[i+1], max_lon+0.1)
                        intersect = operable_poly.intersection(blade)
                        if not intersect.is_empty:
                            if isinstance(intersect, Polygon): st.session_state.final_plots.append({'coords': list(intersect.exterior.coords)})
                            elif isinstance(intersect, MultiPolygon):
                                for part in intersect.geoms: st.session_state.final_plots.append({'coords': list(part.exterior.coords)})
                    st.rerun()

            if st.button(T['reset']): st.session_state.update({"points": [], "final_plots": []}); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; opacity:0.3;'>LankaLand Pro Enterprise v3.0</p>", unsafe_allow_html=True)
