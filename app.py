import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import time

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Custom UI for Mobile
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌾 LankaLand Pro")

# Session State for points
if 'points' not in st.session_state:
    st.session_state.points = []

# Sidebar for Logic
st.sidebar.header("🕹️ පාලක පුවරුව")
mode = st.sidebar.radio("මැනුම් ක්‍රමය තෝරන්න:", ["සිතියම මත ලකුණු කිරීම (Manual)", "ඇවිදිමින් ලකුණු කිරීම (GPS Walking)"])

# GPS Walking Mode UI
if mode == "ඇවිදිමින් ලකුණු කිරීම (GPS Walking)":
    st.warning("📍 මෙම ක්‍රමයේදී ඔබ ඉඩමේ මායිම දිගේ ඇවිද යා යුතුය.")
    if st.button("දැන් මම ඉන්න තැන ලකුණු කරන්න (Add My Location)"):
        # JavaScript පාවිච්චි කරලා Phone එකේ GPS එක ගන්න එක මෙතනදී වෙන්නේ
        st.info("පෝන් එකේ GPS දත්ත ලබා ගනිමින්... (මොහොතක් රැඳෙන්න)")
        # සටහන: Browser එකේ Location permissions ඕනේ. 
        # දැනට අපි simulation එකක් පාවිච්චි කරමු. ඇත්තම GPS එක Browser API එකෙන් එන්නේ.

# Main Columns
col1, col2 = st.columns([2, 1])

with col1:
    # Map Setup
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
    
    # Draw logic
    for p in st.session_state.points:
        folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green')).add_to(m)
    
    if len(st.session_state.points) >= 3:
        folium.Polygon(locations=st.session_state.points, color="yellow", fill=True, fill_opacity=0.4).add_to(m)

    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=450, width="100%")

    # Manual Click Logic
    if mode == "සිතියම මත ලකුණු කිරීම (Manual)" and map_data['last_clicked']:
        pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
        if pos not in st.session_state.points:
            st.session_state.points.append(pos)
            st.rerun()

with col2:
    st.subheader("📊 දත්ත සාරාංශය")
    st.write(f"ලකුණු කළ ප්‍රමාණය: **{len(st.session_state.points)}**")
    
    if st.button("සියල්ල මකන්න (Reset)"):
        st.session_state.points = []
        st.rerun()

    if len(st.session_state.points) >= 3:
        st.success("✅ මායිම් හඳුනාගන්නා ලදී!")
        st.write("---")
        st.subheader("✂️ ඉඩම බෙදීම")
        st.number_input("බෙදිය යුතු පර්චස් ප්‍රමාණය:", min_value=0.0)
        st.button("බෙදුම් මායිම් ගණනය කරන්න")

st.markdown("---")
st.caption("Developed by Bhathiya | LankaLand Pro v2.0")
