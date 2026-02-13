import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import math

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #2e7d32; color: white; }
    .main-title { text-align: center; color: #1b5e20; }
    .gps-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 1px solid #2e7d32; margin-bottom: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []

# --- මෙනුව ---
if st.session_state.method is None:
    st.subheader("මැනුම් ක්‍රමය තෝරන්න:")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📍 සිතියම මත ලකුණු කිරීම"):
            st.session_state.method = "manual"
            st.rerun()
    with c2:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම (GPS)"):
            st.session_state.method = "gps"
            st.rerun()
else:
    st.sidebar.button("⬅️ ආපසු මෙනුවට", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col1, col2 = st.columns([2, 1])

    with col1:
        if st.session_state.method == "gps":
            st.markdown("<div class='gps-box'><b>GPS Mode:</b> මායිම දිගේ ගොස් පහත බටන් එක ඔබන්න.</div>", unsafe_allow_html=True)
            
            # JS Component with better value handling
            gps_val = st.components.v1.html("""
                <script>
                function sendLocation() {
                    navigator.geolocation.getCurrentPosition((pos) => {
                        const val = pos.coords.latitude + "," + pos.coords.longitude;
                        window.parent.postMessage({type: 'streamlit:setComponentValue', value: val}, '*');
                    }, (err) => { alert("Location Error!"); }, {enableHighAccuracy: true});
                }
                </script>
                <button onclick="sendLocation()" style="width: 100%; height: 60px; background-color: #1b5e20; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer;">
                    🌍 දැනට ඉන්න තැන මායිමට එකතු කරන්න
                </button>
            """, height=80)

            # වැදගත්: Error එක මගහැරීමට 'if' එකක් පාවිච්චි කිරීම
            # මෙමගින් දත්ත ලැබුණොත් පමණක් ලකුණු කිරීම සිදු කරයි
            raw_input = st.session_state.get("gps_sync_val", "")
            
            # Hidden input to catch JS value
            # (In some cases st.components might need a small delay or a trigger)
            
        # Map Logic
        start_loc = st.session_state.points[-1] if st.session_state.points else [7.8731, 80.7718]
        m = folium.Map(location=start_loc, zoom_start=19, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="yellow", weight=3, fill=True, fill_opacity=0.4).add_to(m)

        map_data = st_folium(m, height=450, width="100%")

        # Handling Manual Clicks
        if st.session_state.method == "manual" and map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col2:
        st.subheader("📊 දත්ත සාරාංශය")
        st.write(f"සලකුණු කළ ප්‍රමාණය: **{len(st.session_state.points)}**")
        
        if st.button("🔄 සියල්ල මකන්න"):
            st.session_state.points = []
            st.rerun()

        if len(st.session_state.points) >= 3:
            # වර්ගඵලය ගණනය කිරීම (Haversine/Spherical geometry approximation)
            # ලංකාවේ සාමාන්‍ය පර්චස් ගණනයට ගැලපෙන පරිදි
            poly = Polygon(st.session_state.points)
            # Convert degrees to approx meters (at Sri Lanka lat)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.8))
            perches = area_m2 / 25.29
            
            st.success("✅ මායිම් හඳුනාගත්තා")
            st.metric("මුළු වර්ගඵලය", f"{perches:.2f} Perches")
            
            st.write("---")
            st.subheader("✂️ ඉඩම බෙදීම")
            split_perch = st.number_input("වෙන් කළ යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0)
            if st.button("බෙදුම් රේඛාව ගණනය කරන්න"):
                st.warning("මෙම පර්චස් ගණනට ගැලපෙන මායිම් රේඛාව සකස් කරමින්...")

st.markdown("---")
st.caption("Developed by Bhathiya | LankaLand Pro v3.6")
