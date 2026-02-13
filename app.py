import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# Page Config
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Adaptive Premium CSS Styling
st.markdown("""
    <style>
    /* මුළු App එකේම අකුරු වල වර්ණය ස්ථාවර කිරීම */
    html, body, [class*="st-"] {
        color: #1b5e20;
    }
    
    /* Input Boxes වල අකුරු සහ පසුබිම Dark Mode එකට ගැලපීම */
    .stNumberInput input, .stTextInput input {
        color: #1b5e20 !important;
        background-color: #ffffff !important;
        border: 2px solid #2e7d32 !important;
    }
    
    /* Metric Cards - දත්ත පුවරුවේ පෙනුම */
    div[data-metric-label] {
        color: #2e7d32 !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetricValue"] {
        color: #000000 !important;
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        border-bottom: 5px solid #2e7d32;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Buttons Styling */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        font-weight: bold;
        transition: 0.3s;
    }
    
    /* Dialog / Tool Containers */
    .tool-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        margin-top: 10px;
        color: #222 !important; /* කළු පැහැති අකුරු */
    }
    
    .tool-box h3, .tool-box p, .tool-box label {
        color: #1b5e20 !important;
    }

    h1 { color: #1b5e20 !important; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# App Header
st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

if 'points' not in st.session_state:
    st.session_state.points = []

# Main Layout: 2 Columns
col_map, col_tools = st.columns([2, 1])

with col_map:
    # සිතියම නිර්මාණය
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
    
    # Live Location Tracker
    LocateControl(auto_start=False, flyTo=True, strings={"title": "මගේ ස්ථානය සොයන්න"}).add_to(m)

    # Markers & Polygon
    for i, p in enumerate(st.session_state.points):
        folium.Marker(location=[p[0], p[1]], 
                      icon=folium.Icon(color='green', icon='map-pin', prefix='fa')).add_to(m)
    
    if len(st.session_state.points) >= 3:
        folium.Polygon(locations=st.session_state.points, color="#FFEB3B", weight=5, 
                       fill=True, fill_opacity=0.3, fill_color="#FFEB3B").add_to(m)

    # Map Display
    map_data = st_folium(m, height=550, width="100%", use_container_width=True)

    if map_data['last_clicked']:
        pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
        if pos not in st.session_state.points:
            st.session_state.points.append(pos)
            st.rerun()

with col_tools:
    st.markdown("### 📊 මැනුම් වාර්තාව")
    
    m1, m2 = st.columns(2)
    area_p = 0.0
    area_sqft = 0.0
    
    if len(st.session_state.points) >= 3:
        poly = Polygon(st.session_state.points)
        area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
        area_p = area_m2 / 25.29
        area_sqft = area_m2 * 10.7639

    m1.metric(label="මුළු පර්චස්", value=f"{area_p:.2f}")
    m2.metric(label="වර්ග අඩි", value=f"{area_sqft:.0f}")

    # Reset Button
    if st.button("🔄 සිතියම මකන්න", key="reset"):
        st.session_state.points = []
        st.rerun()

    st.markdown("---")
    
    # Land Splitting Section (With Explicit Contrast)
    st.markdown("""
        <div class="tool-box">
            <h3 style="margin-top:0;">✂️ ඉඩම බෙදීම</h3>
            <p style="font-size: 0.9em; margin-bottom: 10px;">වෙන් කළ යුතු පර්චස් ප්‍රමාණය ඇතුළත් කරන්න.</p>
        </div>
    """, unsafe_allow_html=True)
    
    split_val = st.number_input("Perches:", min_value=0.0, step=0.1, key="split_in")
    portion_name = st.text_input("කොටසේ නම:", value="කොටස 01", key="name_in")
    
    if st.button("🚀 බෙදුම් රේඛාව ගණනය කරන්න", key="calc"):
        if len(st.session_state.points) < 3:
            st.error("කරුණාකර ඉඩම මැන අවසන් කරන්න.")
        elif split_val >= area_p:
            st.error("බෙදිය යුතු ප්‍රමාණය මුළු ඉඩමට වඩා කුඩා විය යුතුය.")
        else:
            st.success(f"{portion_name} සඳහා පර්චස් {split_val} ක් වෙන් කරන රේඛාව සකසමින්...")

st.markdown("---")
st.caption("Developed by Bhathiya | Optimized for High Contrast & Professional Use")
