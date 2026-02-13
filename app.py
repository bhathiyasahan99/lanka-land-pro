import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #1b5e20; color: white; }
    .main-title { text-align: center; color: #1b5e20; }
    .instruction { background-color: #fff9c4; padding: 15px; border-radius: 10px; border-left: 5px solid #fbc02d; margin-bottom: 20px; color: #333; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

if 'points' not in st.session_state:
    st.session_state.points = []

# --- පියවර 1: උපදෙස් ---
st.markdown("""
<div class='instruction'>
    <b>සිතියමේ ඔබ ඉන්න තැන පෙන්වීමට:</b><br>
    සිතියමේ වම් පැත්තේ ඇති <b>[Target Icon]</b> එක ක්ලික් කරන්න. එවිට නිල් පාට තිතකින් ඔබ ඉන්න තැන පෙන්වන අතර සිතියම එතැනට ගමන් කරයි.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    # සිතියම නිර්මාණය (මූලිකව ලංකාව මැද පෙන්වයි)
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=8, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
    
    # 🌟 මෙමගින් සිතියම මත Live Location එක පෙන්වන අයිකනය ලබා දෙයි
    # මෙය එබූ සැණින් සිතියම ඔබ ඉන්න තැනට Autoම ගමන් කරයි (Fly To)
    LocateControl(
        auto_start=False, 
        flyTo=True, 
        keepCurrentZoomLevel=False, 
        strings={"title": "මම ඉන්න තැන පෙන්වන්න"}
    ).add_to(m)

    # දැනට සලකුණු කර ඇති Points ඇඳීම
    for p in st.session_state.points:
        folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green', icon='map-pin', prefix='fa')).add_to(m)
    
    if len(st.session_state.points) >= 3:
        folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=4, fill=True, fill_opacity=0.4).add_to(m)

    # සිතියම Streamlit එකේ පෙන්වීම
    # 'use_container_width=True' මගින් ෆෝන් එකට ගැලපෙන සේ සැකසේ
    map_data = st_folium(m, height=500, width=None, use_container_width=True)

    # සිතියම මත ඔබ ඉන්න නිල් තිත උඩ ක්ලික් කළ විට එය මායිමට එකතු වේ
    if map_data['last_clicked']:
        pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
        if pos not in st.session_state.points:
            st.session_state.points.append(pos)
            st.rerun()

with col2:
    st.subheader("📊 සාරාංශය")
    st.write(f"සලකුණු කළ ප්‍රමාණය: **{len(st.session_state.points)}**")
    
    if st.button("🔄 සියල්ල මකන්න"):
        st.session_state.points = []
        st.rerun()

    if len(st.session_state.points) >= 3:
        poly = Polygon(st.session_state.points)
        area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.8))
        perches = area_m2 / 25.29
        st.success(f"වර්ගඵලය: {perches:.2f} Perches")
        
        st.markdown("---")
        st.subheader("✂️ ඉඩම බෙදීම")
        st.number_input("වෙන් කළ යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0)
        st.button("බෙදුම් රේඛාව අඳින්න")

st.markdown("---")
st.caption("Developed by Bhathiya | Professional Grade Surveyor")
