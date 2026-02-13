import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
from streamlit_js_eval import streamlit_js_eval, get_geolocation

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Custom Styling
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; }
    .gps-btn { background-color: #d32f2f !important; color: white !important; }
    .main-title { text-align: center; color: #2e7d32; font-family: sans-serif; }
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
    # --- වැඩ කරන පිටුව ---
    st.sidebar.button("⬅️ ආපසු මෙනුවට", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col1, col2 = st.columns([2, 1])

    with col1:
        # GPS වැඩේ මෙතනින්:
        if st.session_state.method == "gps":
            st.info("පහත බටන් එක ඔබා Location Access 'Allow' කරන්න.")
            
            # මෙන්න මේක තමයි ලොකේෂන් ගන්න බටන් එක
            loc = get_geolocation(label="දැන් මම ඉන්න තැන ලකුණු කරන්න (Get Current Location)")
            
            if loc:
                lat = loc['coords']['latitude']
                lon = loc['coords']['longitude']
                current_pos = (lat, lon)
                
                # අලුත්ම පසිෂන් එක ඇඩ් කරන්න බටන් එකක්
                if st.button("✅ මෙම ස්ථානය මායිමට එකතු කරන්න"):
                    if current_pos not in st.session_state.points:
                        st.session_state.points.append(current_pos)
                        st.success(f"ලකුණු කළා: {lat:.5f}, {lon:.5f}")
                        st.rerun()

        # සිතියම (Satellite View)
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green', icon='map-pin', prefix='fa')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="yellow", weight=3, fill=True, fill_opacity=0.4).add_to(m)

        map_data = st_folium(m, height=450, width="100%")

        # Manual marking logic
        if st.session_state.method == "manual" and map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col2:
        st.subheader("📊 විස්තර")
        st.write(f"සලකුණු කළ ප්‍රමාණය: **{len(st.session_state.points)}**")
        
        if st.button("🔄 සියල්ල මකන්න"):
            st.session_state.points = []
            st.rerun()
        
        if len(st.session_state.points) >= 3:
            st.success("✅ ඉඩම හඳුනාගත්තා!")
            # වර්ගඵලය ගණනය කිරීමේ Logic එක මෙතනට එනවා
            st.metric("වර්ගඵලය", "පර්චස් ...")
            
            st.write("---")
            st.subheader("✂️ ඉඩම බෙදීම")
            st.number_input("වෙන් කළ යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0)
            st.button("බෙදුම් මායිම් අඳින්න")

st.markdown("---")
st.caption("Developed by Bhathiya | LankaLand Pro v2.5")
