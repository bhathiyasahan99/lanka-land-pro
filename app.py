import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# Page Config
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Professional Green Theme with High-Contrast Text
st.markdown("""
    <style>
    /* මුළු App එකේම අකුරු කළු පාටට lock කිරීම */
    [data-testid="stAppViewContainer"] * {
        color: #000000 !important;
    }
    
    /* Headers සහ Labels තද කොළ පාටින් */
    h1, h2, h3, label {
        color: #1b5e20 !important;
        font-weight: 900 !important;
    }

    /* Input Boxes - සුදු පසුබිම සහ තද කළු අකුරු */
    .stNumberInput input, .stTextInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 2px solid #1b5e20 !important;
    }

    /* Buttons - කලින් තිබුණ ලස්සන Green එක */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        font-weight: bold;
        background-image: linear-gradient(to right, #1b5e20, #2e7d32);
        color: white !important; /* බටන් අකුරු විතරක් සුදුයි */
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    /* Metric Cards - දත්ත පුවරුව */
    div[data-testid="stMetricValue"] {
        color: #1b5e20 !important;
        font-weight: 800 !important;
    }

    .selection-box {
        text-align: center;
        padding: 50px;
        background-color: #e8f5e9;
        border-radius: 20px;
        border: 2px solid #1b5e20;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []

# --- පියවර 1: මෙනුව ---
if st.session_state.method is None:
    st.markdown("<div class='selection-box'>", unsafe_allow_html=True)
    st.subheader("කරුණාකර මැනුම් ක්‍රමවේදය තෝරන්න")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📍 සිතියම මත ලකුණු කිරීම"):
            st.session_state.method = "manual"
            st.rerun()
    with col_b:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම"):
            st.session_state.method = "gps"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # Sidebar back button
    st.sidebar.button("⬅️ Back to Menu", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col_map, col_tools = st.columns([2, 1])

    with col_map:
        # Map
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        # Locate Control (The Target Icon)
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="yellow", weight=4, fill=True, fill_opacity=0.3).add_to(m)

        map_data = st_folium(m, height=500, width="100%", use_container_width=True)

        if map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col_tools:
        st.subheader("📊 දත්ත වාර්තාව")
        
        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            st.metric("මුළු පර්චස්", f"{area_p:.2f}")
        
        if st.button("🔄 Reset Map"):
            st.session_state.points = []
            st.rerun()

        st.markdown("---")
        st.subheader("✂️ ඉඩම බෙදීම")
        
        # High contrast inputs with green borders
        split_val = st.number_input("වෙන් කළ යුතු පර්චස්:", min_value=0.0, step=0.1)
        portion_name = st.text_input("කොටසේ නම:", value="Part 01")
        
        if st.button("🚀 Calculate Split"):
            if len(st.session_state.points) >= 3:
                st.success(f"{portion_name} සඳහා {split_val} වෙන් කරමින්...")
            else:
                st.error("ලක්ෂ්‍ය 3ක් ලකුණු කරන්න.")

st.markdown("---")
st.caption("Developed by Bhathiya | Professional & Stylish v11.0")
