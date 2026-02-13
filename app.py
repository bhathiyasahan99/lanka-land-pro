import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# High Contrast UI Styling - No more green mess
st.markdown("""
    <style>
    /* මුළු interface එකේම පසුබිම සහ අකුරු */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Input Boxes - සුදු පසුබිම සහ තද කළු අකුරු */
    input[type="text"], input[type="number"], .stNumberInput div, .stTextInput div {
        background-color: #f9f9f9 !important;
        color: #000000 !important;
        border: 2px solid #333333 !important; /* තද බෝඩර් එකක් */
        font-size: 18px !important;
        font-weight: bold !important;
    }
    
    /* Labels - තද කළු පාට */
    label, p, h1, h2, h3 {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* Buttons - පැහැදිලිව පෙනෙන ලෙස */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none;
        font-size: 16px;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #1b5e20 !important;
        font-size: 30px !important;
    }
    
    .selection-box {
        text-align: center;
        padding: 40px;
        background-color: #f0f2f6;
        border-radius: 15px;
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
    st.subheader("කරුණාකර ක්‍රමය තෝරන්න")
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
    # --- පියවර 2: වැඩ කරන පිටුව ---
    st.sidebar.button("⬅️ ආපසු (Back)", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col_map, col_tools = st.columns([2, 1])

    with col_map:
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='red')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="yellow", weight=4, fill=True, fill_opacity=0.3).add_to(m)

        map_data = st_folium(m, height=500, width="100%", use_container_width=True)

        if map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col_tools:
        st.subheader("📊 තොරතුරු")
        
        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            st.metric("මුළු පර්චස්", f"{area_p:.2f}")
        
        if st.button("🔄 මකන්න (Reset)"):
            st.session_state.points = []
            st.rerun()

        st.markdown("---")
        st.subheader("✂️ ඉඩම බෙදීම")
        
        # පැහැදිලිව පෙනෙන Input boxes
        split_val = st.number_input("බෙදිය යුතු පර්චස් ගණන:", min_value=0.0, step=0.1)
        portion_name = st.text_input("කොටසේ නම (උදා: කැබැල්ල 1):")
        
        if st.button("🚀 බෙදුම් රේඛාව අඳින්න"):
            if len(st.session_state.points) >= 3:
                st.success(f"{portion_name} සඳහා {split_val} රේඛාව ගණනය කරයි...")
            else:
                st.error("ලක්ෂ්‍ය 3ක් ලකුණු කරන්න.")

st.markdown("---")
st.caption("Developed by Bhathiya | High Contrast Version")
