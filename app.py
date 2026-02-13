import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import math
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 4em; font-weight: bold; background-image: linear-gradient(to right, #1b5e20, #2e7d32); color: white; border: none; }
    .main-title { text-align: center; color: #1b5e20; font-weight: bold; }
    .status-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 1px solid #2e7d32; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌾 LankaLand Pro - Professional</h1>", unsafe_allow_html=True)

# Session States
if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []

# --- පියවර 1: මැනුම් ක්‍රමය තෝරාගැනීම (The Menu) ---
if st.session_state.method is None:
    st.subheader("කරුණාකර ක්‍රමවේදය තෝරන්න:")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📍 සිතියම මත ලකුණු කිරීම (Manual)"):
            st.session_state.method = "manual"
            st.rerun()
    with c2:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම (GPS)"):
            st.session_state.method = "gps"
            st.rerun()

else:
    # --- පියවර 2: වැඩ කරන පිටුව ---
    st.sidebar.button("⬅️ ආපසු මෙනුවට", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col1, col2 = st.columns([2, 1])

    with col1:
        if st.session_state.method == "gps":
            st.markdown("<div class='status-box'><b>GPS මාදිලිය:</b> ඉඩමේ හැරෙන ස්ථානයට (Corner) ගොස් බටන් එක ඔබන්න.</div>", unsafe_allow_html=True)
            
            # Real-time GPS Fetching using JS Eval
            # බටන් එක එබුවම විතරක් ලොකේෂන් එක ගන්නා ක්‍රමය
            if st.button("📍 දැන් මම ඉන්න තැන මායිමට එකතු කරන්න"):
                location = streamlit_js_eval(js_expressions="new Promise(resolve => navigator.geolocation.getCurrentPosition(pos => resolve([pos.coords.latitude, pos.coords.longitude])))", key="get_location")
                if location:
                    new_p = tuple(location)
                    if new_p not in st.session_state.points:
                        st.session_state.points.append(new_p)
                        st.success(f"කොණ ලකුණු කළා: {new_p[0]:.6f}")
                        st.rerun()

        # Map Setup
        # අන්තිමට ලකුණු කළ තැනට සිතියම Zoom කිරීම
        map_center = st.session_state.points[-1] if st.session_state.points else [7.8731, 80.7718]
        m = folium.Map(location=map_center, zoom_start=19, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green', icon='map-pin', prefix='fa')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=4, fill=True, fill_opacity=0.4).add_to(m)

        map_data = st_folium(m, height=450, width="100%", key="main_map")

        # Manual Click Logic
        if st.session_state.method == "manual" and map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col2:
        st.subheader("📊 සාරාංශය")
        st.write(f"ලකුණු කළ ප්‍රමාණය: **{len(st.session_state.points)}**")
        
        if st.button("🔄 සියල්ල මකන්න"):
            st.session_state.points = []
            st.rerun()

        if len(st.session_state.points) >= 3:
            # Area Calculation
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.8))
            perches = area_m2 / 25.29
            
            st.success("✅ මායිම් තහවුරුයි")
            st.metric("මුළු වර්ගඵලය", f"{perches:.2f} Perches")
            
            st.write("---")
            st.subheader("✂️ ඉඩම බෙදීම")
            split_val = st.number_input("වෙන් කළ යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0)
            if st.button("බෙදුම් රේඛාව ගණනය කරන්න"):
                st.info("ඉඩමේ හැඩය අනුව බෙදුම් රේඛාව සකසමින්...")

st.markdown("---")
st.caption("Developed by Bhathiya | Professional Grade v4.5")
