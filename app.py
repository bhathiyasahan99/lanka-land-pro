import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="LankaLand Pro", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 15px; height: 4em; font-size: 18px; font-weight: bold; background-color: #2e7d32; color: white; }
    .main-title { text-align: center; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌾 LankaLand Pro - Land surveying system</h1>", unsafe_allow_html=True)

if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []

# --- මෙනුව ---
if st.session_state.method is None:
    st.subheader("කරුණාකර මැනුම් ක්‍රමය තෝරන්න:")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📍 සිතියම මත ලකුණු කිරීම"):
            st.session_state.method = "manual"
            st.rerun()
    with col_b:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම (GPS)"):
            st.session_state.method = "gps"
            st.rerun()
else:
    # --- මැනුම් පිටුව ---
    st.sidebar.button("ආපසු මෙනුවට", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col1, col2 = st.columns([2, 1])

    with col1:
        # GPS දත්ත ලබා ගැනීම (JavaScript පාලම)
        loc = None
        if st.session_state.method == "gps":
            st.warning("Location Permission 'Allow' කරන්න.")
            # මෙමගින් පෝන් එකේ GPS එක ඇත්තටම ක්‍රියාත්මක කරවයි
            loc = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(pos => { window.parent.postMessage({lat: pos.coords.latitude, lon: pos.coords.longitude}, '*') });", key="GPS")
            
            if st.button("📍 දැනට ඉන්න තැන ලකුණු කරන්න"):
                # ලොකේෂන් එක ලැබී ඇත්නම් ලැයිස්තුවට එකතු කිරීම
                location = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition( (pos) => { return [pos.coords.latitude, pos.coords.longitude] } )", key="get_loc")
                if location:
                    st.session_state.points.append(tuple(location))
                    st.success("තැන ලකුණු කරගත්තා!")
                    st.rerun()

        # සිතියම පෙන්වීම
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green')).add_to(m)
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="yellow", fill=True).add_to(m)

        map_data = st_folium(m, height=450, width="100%")

        if st.session_state.method == "manual" and map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col2:
        st.subheader("📊 විස්තර")
        st.write(f"ලකුණු ප්‍රමාණය: {len(st.session_state.points)}")
        if st.button("🔄 මකන්න"):
            st.session_state.points = []
            st.rerun()
        
        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            # සරල වර්ගඵල ගණනය (දළ වශයෙන්)
            st.metric("වර්ගඵලය", "ගණනය කරමින්...")

st.markdown("---")
st.caption("Developed by Bhathiya")
