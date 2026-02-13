import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Professional UI Styling (High Contrast & Clean)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3, p, label, .stMetric div {
        color: #1a1a1a !important;
        font-weight: 800 !important;
    }
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #1b5e20 !important;
        border-radius: 8px !important;
    }
    input { color: #000000 !important; font-weight: bold !important; }
    .stButton>button {
        background-color: #1b5e20 !important;
        color: #ffffff !important;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
        border: none;
    }
    .btn-delete { background-color: #c62828 !important; }
    .method-card { background: white; padding: 30px; border-radius: 15px; border: 1px solid #ddd; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

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
            st.session_state.method = "manual"; st.rerun()
    with c2:
        st.markdown("<div class='method-card'><h3>Live GPS Mode</h3><p>ඔබ සිටින තැනින් ලකුණු කරන්න</p></div>", unsafe_allow_html=True)
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම"):
            st.session_state.method = "gps"; st.rerun()

else:
    # --- Step 2: Professional Surveying & Editing Interface ---
    st.sidebar.button("⬅️ ආපසු (Main Menu)", on_click=lambda: st.session_state.update({"method": None, "points": []}))

    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        # Map Setup
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        # Plot points with numbers for easy editing
        for i, p in enumerate(st.session_state.points):
            folium.Marker(location=[p[0], p[1]], 
                          tooltip=f"Point {i+1}",
                          icon=folium.DivIcon(html=f'<div style="font-size: 12pt; color: white; background: green; border-radius: 50%; width: 20px; height: 20px; text-align: center; border: 2px solid white;">{i+1}</div>')
                         ).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=3, fill=True, fill_opacity=0.3).add_to(m)

        map_data = st_folium(m, height=550, width="100%", use_container_width=True)

        # Catch new clicks
        if map_data['last_clicked']:
            pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if pos not in st.session_state.points:
                st.session_state.points.append(pos)
                st.rerun()

    with col_tools:
        st.markdown("### 📊 මැනුම් සහ සංස්කරණය")
        
        # Area Stats
        area_p = 0.0
        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            st.metric(label="මුළු පර්චස්", value=f"{area_p:.2f}")

        # Edit/Delete Options
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Undo Point"):
                if st.session_state.points:
                    st.session_state.points.pop()
                    st.rerun()
        with c2:
            if st.button("🗑️ Reset All"):
                st.session_state.points = []
                st.rerun()

        st.markdown("---")
        st.markdown("### 📍 ලක්ෂ්‍ය සංස්කරණය (Adjust)")
        
        # Points List for Manual Adjustment
        if st.session_state.points:
            point_idx = st.selectbox("සංස්කරණයට ලක්ෂ්‍යයක් තෝරන්න:", range(1, len(st.session_state.points)+1))
            idx = point_idx - 1
            curr_lat, curr_lon = st.session_state.points[idx]
            
            new_lat = st.number_input("Latitude:", value=curr_lat, format="%.6f", key=f"lat{idx}")
            new_lon = st.number_input("Longitude:", value=curr_lon, format="%.6f", key=f"lon{idx}")
            
            if st.button("🎯 පොයින්ට් එක Update කරන්න"):
                st.session_state.points[idx] = (new_lat, new_lon)
                st.success(f"Point {point_idx} යාවත්කාලීන කළා!")
                st.rerun()
        else:
            st.info("සිතියම මත ලක්ෂ්‍ය කිහිපයක් සලකුණු කරන්න.")

        st.markdown("---")
        st.markdown("### ✂️ ඉඩම බෙදීම")
        split_val = st.number_input("වෙන් කළ යුතු ප්‍රමාණය (Perches):", min_value=0.0, step=0.1)
        if st.button("🚀 බෙදුම් රේඛාව ගණනය"):
            st.success("රේඛාව සකසමින්...")

st.markdown("---")
st.caption("LankaLand Pro v13.0 | Precision Editing Enabled")
