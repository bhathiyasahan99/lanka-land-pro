import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# Page Config
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Premium CSS Styling
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 15px; border-bottom: 5px solid #2e7d32; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; transition: 0.3s; }
    .btn-reset { background-color: #ffebee !important; color: #c62828 !important; border: 1px solid #c62828 !important; }
    .btn-calculate { background-color: #1b5e20 !important; color: white !important; }
    .sidebar-content { background-color: #ffffff; padding: 20px; border-radius: 20px; }
    h1, h2, h3 { color: #1b5e20; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# App Header
st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>ස්මාර්ට් ඉඩම් මැනුම් සහ බෙදුම් පද්ධතිය</p>", unsafe_allow_html=True)

if 'points' not in st.session_state:
    st.session_state.points = []

# Main Layout: 2 Columns
col_map, col_tools = st.columns([2, 1])

with col_map:
    # සිතියම නිර්මාණය
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite Hybrid")
    
    # Live Location Tracker (The Blue Dot & Fly-to)
    LocateControl(auto_start=False, flyTo=True, keepCurrentZoomLevel=False, 
                  strings={"title": "මගේ ස්ථානය සොයන්න"}).add_to(m)

    # Markers & Polygons
    for i, p in enumerate(st.session_state.points):
        folium.Marker(location=[p[0], p[1]], 
                      popup=f"Point {i+1}",
                      icon=folium.Icon(color='green', icon='map-pin', prefix='fa')).add_to(m)
    
    if len(st.session_state.points) >= 3:
        folium.Polygon(locations=st.session_state.points, color="#FFEB3B", weight=5, 
                       fill=True, fill_opacity=0.3, fill_color="#FFEB3B").add_to(m)

    # Display Map
    map_data = st_folium(m, height=550, width="100%", use_container_width=True)

    # Manual / GPS Spot Logic
    if map_data['last_clicked']:
        pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
        if pos not in st.session_state.points:
            st.session_state.points.append(pos)
            st.rerun()

with col_tools:
    st.markdown("### 🛠️ පාලක පුවරුව")
    
    # Metrics Section
    m1, m2 = st.columns(2)
    area_p = 0.0
    area_sqft = 0.0
    
    if len(st.session_state.points) >= 3:
        poly = Polygon(st.session_state.points)
        # Accurate area calculation for Sri Lanka latitude
        area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
        area_p = area_m2 / 25.29
        area_sqft = area_m2 * 10.7639

    m1.metric(label="මුළු පර්චස්", value=f"{area_p:.2f}")
    m2.metric(label="වර්ග අඩි", value=f"{area_sqft:.0f}")

    st.markdown("---")
    
    # Controls
    st.write(f"📍 ලකුණු කර ඇති කොන් ගණන: **{len(st.session_state.points)}**")
    
    if st.button("🔄 සියල්ල මකන්න (Reset)", key="reset", help="සිතියමේ සියලු සලකුණු ඉවත් කරයි"):
        st.session_state.points = []
        st.rerun()

    st.markdown("### ✂️ ඉඩම බෙදීම (Land Split)")
    with st.container():
        st.markdown("<div style='background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd;'>", unsafe_allow_html=True)
        split_val = st.number_input("වෙන් කළ යුතු ප්‍රමාණය (Perches):", min_value=0.0, step=0.5)
        portion_name = st.text_input("කොටසේ නම (උදා: කොටස A):")
        
        if st.button("🚀 බෙදුම් රේඛාව ගණනය කරන්න", key="calc"):
            if len(st.session_state.points) < 3:
                st.error("කරුණාකර ඉඩම මැන අවසන් කරන්න.")
            elif split_val >= area_p:
                st.error("බෙදිය යුතු ප්‍රමාණය මුළු වර්ගඵලයට වඩා කුඩා විය යුතුය.")
            else:
                st.info(f"{portion_name} සඳහා පර්චස් {split_val} ක ප්‍රමාණයක් වෙන් කරමින්...")
                # මෙතනට මම ඊළඟට දෙනවා ඉඩම හරියටම බෙදන ගණිතමය පියවර (Splitting Logic)
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>Designed by <b>Bhathiya</b> | Powered by Geospatial Intelligence</p>", unsafe_allow_html=True)
