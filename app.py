import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import math

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Custom CSS for buttons
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; font-size: 16px; }
    .btn-gps { background-image: linear-gradient(to right, #004d40, #00796b) !important; color: white !important; }
    .btn-add { background-image: linear-gradient(to right, #1b5e20, #43a047) !important; color: white !important; }
    .main-title { text-align: center; color: #1b5e20; border-bottom: 2px solid #1b5e20; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌾 LankaLand Pro - Live Tracker</h1>", unsafe_allow_html=True)

# Session initialization
if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []
if 'user_location' not in st.session_state:
    st.session_state.user_location = None

# --- පියවර 1: මෙනුව (Menu) ---
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
    st.sidebar.button("⬅️ ආපසු මෙනුවට", on_click=lambda: st.session_state.update({"method": None, "points": [], "user_location": None}))

    col1, col2 = st.columns([2, 1])

    with col1:
        if st.session_state.method == "gps":
            # 1. Location On/Track කරන JavaScript එක
            st.markdown("### 1. ලොකේෂන් එක On කරන්න")
            loc_data = st.components.v1.html("""
                <script>
                function getLocation() {
                    navigator.geolocation.getCurrentPosition(
                        (pos) => {
                            const lat = pos.coords.latitude;
                            const lon = pos.coords.longitude;
                            window.parent.postMessage({
                                type: 'streamlit:setComponentValue',
                                value: {lat: lat, lon: lon}
                            }, '*');
                        },
                        (err) => { alert("කරුණාකර Phone එකේ GPS On කර 'Allow' දෙන්න."); },
                        { enableHighAccuracy: true }
                    );
                }
                </script>
                <button onclick="getLocation()" style="width: 100%; height: 50px; background: #004d40; color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer;">
                    🛰️ මම ඉන්න තැන පෙන්වන්න (Get My Location)
                </button>
            """, height=70)

            # ලැබෙන දත්ත Python වලට ගැනීම
            if loc_data:
                # සටහන: මෙහිදී සිතියම අලුත් වීමට rerun එකක් අවශ්‍යයි
                pass

            st.markdown("---")
            st.markdown("### 2. මායිම ලකුණු කරන්න")
            lat_input = st.number_input("Latitude", key="lat_val", format="%.6f")
            lon_input = st.number_input("Longitude", key="lon_val", format="%.6f")

            if st.button("➕ මෙම ස්ථානය මායිමට එක් කරන්න", key="add_btn"):
                if lat_input and lon_input:
                    new_p = (lat_input, lon_input)
                    if new_p not in st.session_state.points:
                        st.session_state.points.append(new_p)
                        st.success("කොණ ලකුණු කළා!")
                        st.rerun()

        # සිතියම සකස් කිරීම
        center = [7.8731, 80.7718]
        if st.session_state.points:
            center = st.session_state.points[-1]
        
        m = folium.Map(location=center, zoom_start=19, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        # දැනට ලකුණු කර ඇති points
        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green', icon='map-pin', prefix='fa')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=4, fill=True, fill_opacity=0.4).add_to(m)

        map_data = st_folium(m, height=450, width="100%", key="land_map")

        # Manual Marking
        if st.session_state.method == "manual" and map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col2:
        st.subheader("📊 දත්ත වාර්තාව")
        st.write(f"සලකුණු කළ කොන්: **{len(st.session_state.points)}**")
        
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
            st.number_input("බෙදිය යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0)
            st.button("බෙදුම් මායිම අඳින්න")

st.markdown("---")
st.caption("Developed by Bhathiya | LankaLand Pro v5.0")
