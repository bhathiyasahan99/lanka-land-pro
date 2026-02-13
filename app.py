import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# Page Config
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# High-Contrast Adaptive CSS
st.markdown("""
    <style>
    /* Dark mode එකේදී අකුරු නොපෙනෙන ප්‍රශ්නය විසඳීම */
    html, body, [class*="st-"] {
        color: #1b5e20;
    }
    
    /* Input Boxes වල අකුරු සහ Background ස්ථාවර කිරීම */
    input[type="text"], input[type="number"], .stNumberInput div, .stTextInput div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    label {
        color: #1b5e20 !important;
        font-weight: bold !important;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 4em;
        font-weight: bold;
        background-image: linear-gradient(to right, #1b5e20, #2e7d32);
        color: white;
        border: none;
    }

    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        border-bottom: 5px solid #2e7d32;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .selection-box {
        text-align: center;
        padding: 40px;
        background-color: #ffffff;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# App Header
st.markdown("<h1 style='text-align: center; color: #1b5e20;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

# Session States initialization
if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []

# --- පියවර 1: මෙනුව (Selection Screen) ---
if st.session_state.method is None:
    st.markdown("<div class='selection-box'>", unsafe_allow_html=True)
    st.subheader("කරුණාකර මැනුම් ක්‍රමවේදය තෝරන්න")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("📍 සිතියම මත ලකුණු කිරීම\n(Manual Marking)"):
            st.session_state.method = "manual"
            st.rerun()
            
    with col_b:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම\n(Live GPS Tracking)"):
            st.session_state.method = "gps"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- පියවර 2: ප්‍රධාන මැනුම් Interface එක ---
    st.sidebar.button("⬅️ ආපසු මෙනුවට (Main Menu)", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col_map, col_tools = st.columns([2, 1])

    with col_map:
        # සිතියම නිර්මාණය
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        # Live GPS Tracker Icon
        LocateControl(auto_start=False, flyTo=True, strings={"title": "මම ඉන්න තැන පෙන්වන්න"}).add_to(m)

        # Markers ඇඳීම
        for i, p in enumerate(st.session_state.points):
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green', icon='map-pin', prefix='fa')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#FFEB3B", weight=5, fill=True, fill_opacity=0.3).add_to(m)

        map_data = st_folium(m, height=550, width="100%", use_container_width=True)

        # ලොකේෂන් ලකුණු කිරීමේ ලොජික් එක
        if map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col_tools:
        st.markdown(f"### 📊 වාර්තාව ({st.session_state.method.upper()})")
        
        area_p = 0.0
        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            
            st.metric(label="මුළු පර්චස් ගණන", value=f"{area_p:.2f}")
            st.metric(label="සලකුණු කළ ලක්ෂ්‍ය", value=f"{len(st.session_state.points)}")
        else:
            st.info("ඉඩම මැනීම සඳහා අවම වශයෙන් ලක්ෂ්‍ය 3ක් ලකුණු කරන්න.")

        if st.button("🔄 සිතියම මකන්න (Reset)"):
            st.session_state.points = []
            st.rerun()

        st.markdown("---")
        
        # ඉඩම බෙදීම - Dark Mode එකට ගැලපෙන පරිදි
        st.subheader("✂️ ඉඩම බෙදීම")
        with st.container():
            split_val = st.number_input("වෙන් කළ යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0, step=0.1)
            portion_name = st.text_input("කොටසේ නම:", value="කොටස A")
            
            if st.button("🚀 බෙදුම් රේඛාව ගණනය කරන්න"):
                if len(st.session_state.points) < 3:
                    st.error("පළමුව ඉඩම මැන අවසන් කරන්න.")
                else:
                    st.success(f"{portion_name} සඳහා රේඛාව සකසමින්...")

st.markdown("---")
st.caption("Developed by Bhathiya | All-in-One Professional Surveying Tool")
