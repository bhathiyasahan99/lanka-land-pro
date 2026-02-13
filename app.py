import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# Page Setup
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# --- Professional UI Logic (Styles) ---
st.markdown("""
    <style>
    /* මුළු interface එකටම පිරිසිදු සුදු පසුබිමක් */
    .stApp { background-color: #f8f9fa; }

    /* පට්ට තද අකුරු (High Contrast Black) */
    h1, h2, h3, p, label, .stMetric div {
        color: #1a1a1a !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
    }

    /* Input Boxes - පිරිසිදු සුදු පසුබිමක කළු අකුරු */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #1b5e20 !important;
        border-radius: 8px !important;
    }
    input {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* Buttons - Professional Green */
    .stButton>button {
        background-color: #1b5e20 !important;
        color: #ffffff !important;
        border-radius: 8px;
        height: 3.8em;
        font-size: 16px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Selection Cards */
    .method-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #ddd;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# App Title
st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

if 'method' not in st.session_state:
    st.session_state.method = None
if 'points' not in st.session_state:
    st.session_state.points = []

# --- Step 1: Selection Menu ---
if st.session_state.method is None:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='method-card'><h3>Manual Mode</h3><p>සිතියම මත ටච් කර ලකුණු කරන්න</p></div>", unsafe_allow_html=True)
        if st.button("📍 සිතියම මත ලකුණු කිරීම"):
            st.session_state.method = "manual"
            st.rerun()
    with c2:
        st.markdown("<div class='method-card'><h3>Live GPS Mode</h3><p>ඔබ සිටින තැනින් ලකුණු කරන්න</p></div>", unsafe_allow_html=True)
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම"):
            st.session_state.method = "gps"
            st.rerun()

else:
    # --- Step 2: Surveying Interface ---
    st.sidebar.button("⬅️ Back to Menu", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        # Map configuration
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        # Locate Control (The Target Icon)
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        # Plot existing markers
        for p in st.session_state.points:
            folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green', icon='info-sign')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=3, fill=True, fill_opacity=0.3).add_to(m)

        # Show map and capture input
        map_data = st_folium(m, height=550, width="100%", use_container_width=True)

        if map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col_tools:
        st.markdown("### 📊 මැනුම් දත්ත")
        
        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            st.metric(label="මුළු පර්චස්", value=f"{area_p:.2f}")
        else:
            st.warning("ලක්ෂ්‍ය 3ක් ලකුණු කරන්න.")

        if st.button("🔄 සියල්ල මකන්න"):
            st.session_state.points = []
            st.rerun()

        st.markdown("---")
        st.markdown("### ✂️ ඉඩම බෙදීම")
        
        split_val = st.number_input("වෙන් කළ යුතු ප්‍රමාණය (Perches):", min_value=0.0, step=0.1)
        portion_name = st.text_input("කොටසේ නම:", value="පර්චස් " + str(split_val))
        
        if st.button("🚀 බෙදුම් රේඛාව ගණනය"):
            if len(st.session_state.points) >= 3:
                st.success(f"බෙදුම් රේඛාව අඳිමින්...")
            else:
                st.error("පළමුව සිතියම ලකුණු කරන්න.")

st.markdown("---")
st.caption("LankaLand Pro | Professional Grade UI")
