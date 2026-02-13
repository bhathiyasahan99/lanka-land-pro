import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import math
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Premium Styling
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 4.5em; font-weight: bold; background-image: linear-gradient(to right, #1b5e20, #2e7d32); color: white; border: none; font-size: 16px; }
    .gps-info { background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌾 LankaLand Pro - Professional Surveyor")

if 'points' not in st.session_state:
    st.session_state.points = []

# --- පියවර 1: GPS දත්ත ලබා ගැනීම (Invisible logic) ---
# High Accuracy GPS එකක් මෙතනදී පාවිච්චි වෙනවා
loc = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(pos => { window.parent.postMessage({lat: pos.coords.latitude, lon: pos.coords.longitude}, '*') });", key="GPS_TRACKER")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='gps-info'><b>GPS මාදිලිය:</b> ඉඩමේ හැරෙන ස්ථානයට (Corner) ගොස් පහත බටන් එක ඔබන්න.</div>", unsafe_allow_html=True)
    
    # GPS එකෙන් ලොකේෂන් එක අරගන්න බටන් එක
    if st.button("📍 දැන් මම ඉන්න තැන මායිමට එකතු කරන්න"):
        # JavaScript එකෙන් කෙලින්ම Latitude/Longitude අරගන්නා බටන් එක
        location = streamlit_js_eval(js_expressions="new Promise(resolve => navigator.geolocation.getCurrentPosition(pos => resolve([pos.coords.latitude, pos.coords.longitude])))", key="get_loc_btn")
        
        if location:
            new_point = tuple(location)
            if new_point not in st.session_state.points:
                st.session_state.points.append(new_point)
                st.toast(f"ලක්ෂණය එකතු කළා: {new_point[0]:.5f}", icon="✅")
                st.rerun()

    # සිතියම (Satellite view)
    start_loc = st.session_state.points[-1] if st.session_state.points else [7.8731, 80.7718]
    m = folium.Map(location=start_loc, zoom_start=19, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
    
    for p in st.session_state.points:
        folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green', icon='map-pin', prefix='fa')).add_to(m)
    
    if len(st.session_state.points) >= 3:
        folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=4, fill=True, fill_opacity=0.4).add_to(m)

    st_folium(m, height=450, width="100%", key="land_map")

with col2:
    st.subheader("📊 ඉඩමේ වාර්තාව")
    st.write(f"සලකුණු කළ කොන් ගණන: **{len(st.session_state.points)}**")
    
    if st.button("🔄 සියල්ල මකන්න (Reset)"):
        st.session_state.points = []
        st.rerun()

    if len(st.session_state.points) >= 3:
        # සැබෑ පර්චස් ගණනය කිරීම
        poly = Polygon(st.session_state.points)
        area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.8))
        perches = area_m2 / 25.29
        
        st.success("✅ මායිම් තහවුරුයි")
        st.metric("මුළු වර්ගඵලය", f"{perches:.2f} Perches")
        
        st.write("---")
        st.subheader("✂️ ඉඩම බෙදීම")
        split_val = st.number_input("වෙන් කළ යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0)
        if st.button("බෙදුම් මායිම ගණනය කරන්න"):
            # අසමාන බෙදුම් ලොජික් එක මෙතනට
            st.info("ඉඩමේ හැඩය අනුව බෙදුම් රේඛාව සකසමින්...")

st.markdown("---")
st.caption("Developed by Bhathiya | LankaLand Pro v4.0")
