import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon

st.set_page_config(page_title="LankaLand Pro", layout="wide")

# Custom UI for Professional look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 15px; height: 4em; font-size: 18px; font-weight: bold; }
    .main-title { text-align: center; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌾 LankaLand Pro - Smart Surveyor</h1>", unsafe_allow_html=True)

# 1. පියවර: මැනුම් ක්‍රමය තෝරාගැනීම
if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []

if st.session_state.method is None:
    st.subheader("කරුණාකර මැනුම් ක්‍රමය තෝරන්න (Select Method):")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("📍 සිතියම මත ලකුණු කිරීම\n(Manual Marking)"):
            st.session_state.method = "manual"
            st.rerun()
            
    with col_b:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම\n(GPS Walking)"):
            st.session_state.method = "gps"
            st.rerun()
else:
    # 2. පියවර: තෝරාගත් ක්‍රමය අනුව වැඩේ පටන් ගැනීම
    st.sidebar.write(f"තෝරාගත් ක්‍රමය: **{st.session_state.method}**")
    if st.sidebar.button("ආපසු මෙනුවට (Back to Menu)"):
        st.session_state.method = None
        st.session_state.points = []
        st.rerun()

    col1, col2 = st.columns([2, 1])

    with col1:
        # Map Setup
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        # Markers ඇඳීම
        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="yellow", fill=True, fill_opacity=0.4).add_to(m)

        m.add_child(folium.LatLngPopup())
        map_data = st_folium(m, height=450, width="100%")

        # GPS ක්‍රමය නම් වෙනම බටන් එකක් දීම
        if st.session_state.method == "gps":
            st.warning("කුඹුරේ මායිම දිගේ ගොස් පහත බටන් එක ඔබන්න")
            if st.button("📍 මම දැන් ඉන්න තැන ලකුණු කරන්න"):
                # මෙතනට GPS logic එක එනවා
                st.info("පිහිටීම ලබා ගනිමින්...")

        # Manual ක්‍රමය නම් ක්ලික් එකෙන් වැඩේ වීම
        if st.session_state.method == "manual" and map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col2:
        st.subheader("📊 ඉඩමේ විස්තර")
        st.write(f"ලකුණු කළ ප්‍රමාණය: **{len(st.session_state.points)}**")
        
        if st.button("🔄 මකන්න (Reset)"):
            st.session_state.points = []
            st.rerun()

        if len(st.session_state.points) >= 3:
            st.success("✅ ඉඩම හඳුනාගන්නා ලදී")
            st.write("---")
            st.subheader("✂️ ඉඩම බෙදීම (Splitting)")
            st.number_input("වෙන් කළ යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0)
            st.button("බෙදුම් රේඛාව පෙන්වන්න")

st.markdown("---")
st.caption("Developed by Bhathiya | Built for Sri Lankan Farmers")
