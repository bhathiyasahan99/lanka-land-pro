import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import json

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Professional UI Styling
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 4em; font-weight: bold; background-color: #2e7d32; color: white; }
    .main-title { text-align: center; color: #1b5e20; }
    .gps-box { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border: 2px dashed #2e7d32; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []

# --- මෙනුව (Selection Menu) ---
if st.session_state.method is None:
    st.subheader("කරුණාකර මැනුම් ක්‍රමය තෝරන්න:")
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
    # --- ප්‍රධාන වැඩ කරන කොටස ---
    st.sidebar.button("⬅️ ආපසු මෙනුවට", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col1, col2 = st.columns([2, 1])

    with col1:
        if st.session_state.method == "gps":
            st.markdown("""
                <div class='gps-box'>
                    <h3>ලොකේෂන් එක ලබා ගැනීමට පහත බටන් එක ඔබන්න</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # JavaScript හරහා Location ගන්නා ක්‍රමය
            loc_json = st.components.v1.html("""
                <script>
                function getLocation() {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            const data = {
                                lat: position.coords.latitude,
                                lon: position.coords.longitude
                            };
                            window.parent.postMessage({type: 'streamlit:setComponentValue', value: data}, '*');
                        },
                        (error) => { console.error(error); },
                        { enableHighAccuracy: true }
                    );
                }
                </script>
                <button onclick="getLocation()" style="width: 100%; height: 50px; background-color: #1b5e20; color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer;">
                    🌍 දැනට ඉන්න තැන ලකුණු කරන්න (Click to Allow Location)
                </button>
            """, height=70)
            
            # මෙතනින් තමයි JS එකේ දත්ත Python වලට ගන්නේ
            if loc_json:
                # සටහන: මෙය ක්‍රියාත්මක වීමට නම් User බටන් එක එබිය යුතුයි
                pass

        # සිතියම පෙන්වීම
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="yellow", weight=3, fill=True, fill_opacity=0.4).add_to(m)

        map_data = st_folium(m, height=450, width="100%")

        # Manual Click Logic
        if st.session_state.method == "manual" and map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col2:
        st.subheader("📊 දත්ත පුවරුව")
        st.write(f"සලකුණු කළ ප්‍රමාණය: **{len(st.session_state.points)}**")
        
        # අතින් ඛණ්ඩාංක එකතු කිරීමට (GPS වැඩ නොකරන වෙලාවට Backup එකක් ලෙස)
        if st.session_state.method == "gps":
            with st.expander("ලොකේෂන් එක ලැබුණේ නැද්ද?"):
                lat_manual = st.number_input("Latitude", format="%.6f")
                lon_manual = st.number_input("Longitude", format="%.6f")
                if st.button("Add Manual Point"):
                    st.session_state.points.append((lat_manual, lon_manual))
                    st.rerun()

        if st.button("🔄 සියල්ල මකන්න"):
            st.session_state.points = []
            st.rerun()
        
        if len(st.session_state.points) >= 3:
            st.success("✅ ඉඩම හඳුනාගත්තා!")
            st.write("---")
            st.subheader("✂️ ඉඩම බෙදීම")
            st.number_input("පර්චස් ප්‍රමාණය:", min_value=0.0)
            st.button("බෙදුම් රේඛාව අඳින්න")

st.markdown("---")
st.caption("Developed by Bhathiya | LankaLand Pro v3.0")
