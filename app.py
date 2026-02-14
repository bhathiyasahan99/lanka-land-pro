import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl
from shapely.geometry import Polygon, MultiPolygon, box, LineString
import math
import numpy as np

# --- Configuration & Styling ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(135deg, #1b5e20 0%, #4caf50 100%); 
        padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 25px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.6); border: 1px solid #2e7d32;
    }
    .card { background: #1d2129; padding: 22px; border-radius: 18px; border: 1px solid #30363d; margin-bottom: 15px; box-shadow: 2px 2px 15px rgba(0,0,0,0.2); }
    .metric-val { font-size: 26px; font-weight: 800; color: #4caf50; display: block; }
    .stButton>button { 
        width: 100%; border-radius: 14px; height: 3.8em; background: #2e7d32 !important; 
        border: none; font-weight: 800; color: white !important; transition: all 0.3s;
    }
    .stButton>button:hover { background: #388e3c !important; transform: scale(1.02); }
    .plot-result { border-left: 5px solid #4caf50; background: #252a33; padding: 15px; border-radius: 8px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State ---
if 'lang' not in st.session_state: st.session_state.lang = None
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'final_plots' not in st.session_state: st.session_state.final_plots = []
if 'orientation' not in st.session_state: st.session_state.orientation = "vertical"

# --- Calculations ---
def get_distance_meters(p1, p2):
    """ලක්ෂ්‍ය දෙකක් අතර දුර මීටර් වලින් ගණනය කරයි"""
    R = 6371000 # Earth radius
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
    perimeter = 0
    for i in range(len(coords)):
        perimeter += get_distance_meters(coords[i], coords[(i+1)%len(coords)])
    return area_m2 / 25.29, perimeter

# --- Language Dictionary ---
texts = {
    "si": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "වෘත්තීය මට්ටමේ භූමි මැනුම් පද්ධතිය",
        "manual": "🗺️ සිතියම මත සලකුණු කිරීම",
        "gps": "🛰️ GPS සජීවී මැනීම (Field Survey)",
        "analytics": "📊 මැනුම් වාර්තාව",
        "total_area": "මුළු වර්ගඵලය",
        "perimeter": "වටප්‍රමාණය",
        "subdivision": "🏗️ කට්ටි කිරීමේ එන්ජිම",
        "execute": "🚀 කට්ටි කර පෙන්වන්න",
        "mark_gps": "📍 ස්ථානය සලකුණු කරන්න",
        "undo": "↩️ අවසන් ලක්ෂ්‍යය මකන්න",
        "reset": "🗑️ සියල්ල මකන්න",
        "val_p": "පර්චසයක මිල:",
        "total_val": "මුළු වටිනාකම"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "Professional Surveying System",
        "manual": "🗺️ MANUAL MARKING",
        "gps": "🛰️ LIVE GPS SURVEY",
        "analytics": "📊 SURVEY ANALYTICS",
        "total_area": "Total Area",
        "perimeter": "Perimeter",
        "subdivision": "🏗️ SUBDIVISION ENGINE",
        "execute": "🚀 EXECUTE SPLIT",
        "mark_gps": "📍 MARK LOCATION",
        "undo": "↩️ UNDO LAST",
        "reset": "🗑️ RESET ALL",
        "val_p": "Value per Perch:",
        "total_val": "Total Value"
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
    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button(T['manual']): st.session_state.method = "manual"; st.rerun()
        if col2.button(T['gps']): st.session_state.method = "gps"; st.rerun()
    else:
        col_map, col_tools = st.columns([2.5, 1])

        with col_map:
            m = folium.Map(location=[7.8731, 80.7718], zoom_start=19, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
            LocateControl(auto_start=(st.session_state.method == "gps")).add_to(m)
            Fullscreen().add_to(m); MeasureControl().add_to(m)

            # කට්ටි සහ මායිම් ලේබල් සමඟ ඇඳීම
            for item in st.session_state.final_plots:
                folium.Polygon(locations=item['coords'], color="#4CAF50", weight=2, fill=True, fill_opacity=0.4).add_to(m)

            if len(st.session_state.points) >= 2:
                folium.PolyLine(locations=st.session_state.points + ([st.session_state.points[0]] if len(st.session_state.points)>2 else []), color="yellow", weight=4).add_to(m)
                
                # මායිම් වල දිග පෙන්වීම (Labels)
                for i in range(len(st.session_state.points)):
                    p1 = st.session_state.points[i]
                    p2 = st.session_state.points[(i+1)%len(st.session_state.points)]
                    mid_lat, mid_lon = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
                    dist = get_distance_meters(p1, p2)
                    if dist > 0.5: # ඉතා කුඩා දුරවල් මඟ හරින්න
                        folium.Marker([mid_lat, mid_lon], icon=folium.DivIcon(html=f'<div style="font-size: 10pt; color: white; background: rgba(0,0,0,0.5); padding: 2px; border-radius: 4px;">{dist:.1f}m</div>')).add_to(m)

            for i, p in enumerate(st.session_state.points):
                folium.Marker(location=p, draggable=True, icon=folium.Icon(color="green", icon="dot")).add_to(m)

            map_data = st_folium(m, height=650, width="100%", key="gis_map")

            if map_data['last_clicked'] and st.session_state.method == "manual":
                st.session_state.points.append((map_data['last_clicked']['lat'], map_data['last_clicked']['lng']))
                st.rerun()

        with col_tools:
            st.sidebar.button("🔙 MENU", on_click=lambda: st.session_state.update({"method": None, "points": [], "final_plots": []}))
            
            # --- Survey Controls ---
            if st.session_state.method == "gps":
                st.markdown(f"<div class='card'><h3>🛰️ GPS SURVEY</h3>", unsafe_allow_html=True)
                if st.button(T['mark_gps']):
                    if map_data['last_clicked']:
                        st.session_state.points.append((map_data['last_clicked']['lat'], map_data['last_clicked']['lng']))
                        st.rerun()
                if st.button(T['undo']):
                    if st.session_state.points: st.session_state.points.pop(); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Analytics Report ---
            st.markdown(f"<div class='card'><h3>{T['analytics']}</h3>", unsafe_allow_html=True)
            area_p, peri_m = calculate_detailed_area(st.session_state.points)
            st.markdown(f"{T['total_area']}: <span class='metric-val'>{area_p:.2f} P</span>", unsafe_allow_html=True)
            st.markdown(f"{T['perimeter']}: <span class='metric-val' style='color:#ffa726'>{peri_m:.1f} m</span>", unsafe_allow_html=True)
            val_per_p = st.number_input(T['val_p'], value=100000)
            st.markdown(f"{T['total_val']}: <h4 style='color:#4caf50'>රු. {(area_p * val_per_p):,.0f}</h4>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # --- Subdivision Engine ---
            st.markdown(f"<div class='card'><h3>{T['subdivision']}</h3>", unsafe_allow_html=True)
            target = st.number_input("කට්ටි ප්‍රමාණය (P)", value=10.0)
            c1, c2 = st.columns(2)
            if c1.button("සිරස්"): st.session_state.orientation = "vertical"
            if c2.button("තිරස්"): st.session_state.orientation = "horizontal"

            if st.button(T['execute']):
                if len(st.session_state.points) >= 3:
                    main_poly = Polygon(st.session_state.points)
                    min_lat, min_lon, max_lat, max_lon = main_poly.bounds
                    num = int(area_p // target)
                    st.session_state.final_plots = []
                    cuts = np.linspace(min_lon, max_lon, num + 1) if st.session_state.orientation == "vertical" else np.linspace(min_lat, max_lat, num + 1)
                    for i in range(len(cuts)-1):
                        blade = box(min_lat-0.1, cuts[i], max_lat+0.1, cuts[i+1]) if st.session_state.orientation == "vertical" else box(cuts[i], min_lon-0.1, cuts[i+1], max_lon+0.1)
                        intersect = main_poly.intersection(blade)
                        if not intersect.is_empty:
                            if isinstance(intersect, Polygon): st.session_state.final_plots.append({'coords': list(intersect.exterior.coords)})
                            elif isinstance(intersect, MultiPolygon):
                                for part in intersect.geoms: st.session_state.final_plots.append({'coords': list(part.exterior.coords)})
                    st.rerun()

            if st.button(T['reset']): st.session_state.points = []; st.session_state.final_plots = []; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; opacity:0.3;'>LankaLand Pro | Enterprise GIS Edition</p>", unsafe_allow_html=True)
