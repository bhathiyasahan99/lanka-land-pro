import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; }
    .main-title { text-align: center; color: #1b5e20; }
    .gps-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 1px solid #2e7d32; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []

# --- පියවර 1: මෙනුව ---
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
    # --- පියවර 2: මැනුම් පිටුව ---
    st.sidebar.button("⬅️ ආපසු මෙනුවට", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col1, col2 = st.columns([2, 1])

    with col1:
        # GPS Auto-Marking Logic using JavaScript
        if st.session_state.method == "gps":
            st.markdown("<div class='gps-box'><b>GPS මාදිලිය:</b> මායිම දිගේ ගොස් පහත බටන් එක ඔබන්න.</div>", unsafe_allow_html=True)
            
            # JavaScript component to fetch and return location
            result = st.components.v1.html("""
                <script>
                function getLocation() {
                    navigator.geolocation.getCurrentPosition(
                        (pos) => {
                            const coords = pos.coords.latitude + "," + pos.coords.longitude;
                            window.parent.postMessage({
                                type: 'streamlit:setComponentValue',
                                value: coords
                            }, '*');
                        },
                        (err) => { alert("GPS වැඩ කරන්නේ නැත. කරුණාකර Location On කරන්න."); },
                        { enableHighAccuracy: true }
                    );
                }
                </script>
                <button onclick="getLocation()" style="width: 100%; height: 60px; background-color: #1b5e20; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer;">
                    🌍 දැනට ඉන්න තැන මායිමට එකතු කරන්න (Mark My Spot)
                </button>
            """, height=80)

            # බටන් එක එබූ විට ලැබෙන දත්ත Python වලට ලබා ගැනීම
            # සටහන: streamlit_folium හෝ වෙනත් ක්‍රම මගින් අගය වෙනස් වීම නිරීක්ෂණය කරයි
            input_val = st.text_input("GPS Sync (සැඟවුණු)", key="gps_sync", label_visibility="collapsed")
            
            if input_val and "gps_last" not in st.session_state or st.session_state.get("gps_last") != input_val:
                lat, lon = map(float, input_val.split(","))
                st.session_state.points.append((lat, lon))
                st.session_state.gps_last = input_val
                st.rerun()

        # සිතියම පෙන්වීම
        # අවසානයට ලකුණු කළ තැනට සිතියම Zoom කිරීම
        start_loc = st.session_state.points[-1] if st.session_state.points else [7.8731, 80.7718]
        
        m = folium.Map(location=start_loc, zoom_start=19, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green', icon='map-marker')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="yellow", weight=3, fill=True, fill_opacity=0.4).add_to(m)

        map_data = st_folium(m, height=450, width="100%")

        if st.session_state.method == "manual" and map_data['last_clicked']:
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
            st.success("✅ ඉඩම හඳුනාගත්තා!")
            # සරල වර්ගඵල ගණනය (Approximate)
            poly = Polygon(st.session_state.points)
            st.metric("ලකුණු කළ ප්‍රමාණය", f"{len(st.session_state.points)} Points")
            
            st.write("---")
            st.subheader("✂️ ඉඩම බෙදීම")
            st.number_input("වෙන් කළ යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0)
            st.button("බෙදුම් රේඛාව පෙන්වන්න")

st.markdown("---")
st.caption("Developed by Bhathiya | LankaLand Pro v3.5")
