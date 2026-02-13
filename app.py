import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pandas as pd

# Page setup for Mobile & Desktop
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Premium Custom Styling (LinkedIn-ready UI)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-image: linear-gradient(to right, #1b5e20, #2e7d32); color: white; font-weight: bold; border: none; }
    .stNumberInput input { border-radius: 8px; }
    .title-text { color: #1b5e20; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Language Toggle in Sidebar
lang = st.sidebar.radio("🌐 භාෂාව තෝරන්න / Language", ["සිංහල", "English"])

if lang == "සිංහල":
    st.markdown("<h1 class='title-text'>📝 LankaLand Pro - Land surveying system</h1>", unsafe_allow_html=True)
    st.info("📍 උපදෙස්: සිතියම මත ඉඩමේ කොන් (Points) සලකුණු කරන්න. ඉන්පසු එය අසමාන කොටස් වලට බෙදන්න.")
    area_lbl = "මුළු වර්ගඵලය"
    split_lbl = "ඉඩම බෙදීම (Land Split)"
else:
    st.markdown("<h1 class='title-text'>📝 LankaLand Pro - Smart Survey Tool</h1>", unsafe_allow_html=True)
    st.info("📍 Instructions: Mark land boundary points on the map. Then use the splitting tool.")
    area_lbl = "Total Area"
    split_lbl = "Land Split"

# Initialize Session State
if 'points' not in st.session_state:
    st.session_state.points = []

# Layout for Map and Tools
col1, col2 = st.columns([2, 1])

with col1:
    # Professional Google Satellite Map
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=8, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite Hybrid")
    
    # Draw points and lines
    for p in st.session_state.points:
        folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green', icon='info-sign')).add_to(m)
    
    if len(st.session_state.points) >= 3:
        folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=4, fill=True, fill_opacity=0.4).add_to(m)

    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=450, width="100%")

    if map_data['last_clicked']:
        pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
        if pos not in st.session_state.points:
            st.session_state.points.append(pos)
            st.rerun()

with col2:
    st.subheader("🛠️ " + ("පාලක පුවරුව" if lang=="සිංහල" else "Dashboard"))
    
    if st.button("Reset (සියල්ල මකන්න)"):
        st.session_state.points = []
        st.rerun()

    if len(st.session_state.points) >= 3:
        # Land Logic
        st.success("✅ " + ("ඉඩම හඳුනා ගන්නා ලදී" if lang=="සිංහල" else "Land Detected"))
        
        # Display Area (Placeholder for calculation logic)
        st.metric(label=area_lbl, value="ගණනය කරමින්...")

        st.markdown("---")
        st.subheader("✂️ " + split_lbl)
        
        # Land Split Logic UI
        part_name = st.text_input("කොටසේ නම (e.g., කොටස 01):")
        portion = st.number_input("බෙදිය යුතු ප්‍රමාණය (Perches):", min_value=0.0)
        
        if st.button("ඉඩම බෙදන්න (Generate Split)"):
            st.warning("අසමාන කොටස් වලට බෙදන Logic එක ක්‍රියාත්මක වේ...")

st.markdown("---")
st.markdown("<p style='text-align: center;'>Developed by <b>Bhathiya</b> | Building Digital Solutions for Sri Lanka</p>", unsafe_allow_html=True)
