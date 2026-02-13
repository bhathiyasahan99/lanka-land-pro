import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# Page Setup
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Standard High Contrast Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3, p, label { color: #1a1a1a !important; font-weight: 800 !important; }
    .stButton>button { background-color: #1b5e20 !important; color: white !important; border-radius: 8px; font-weight: bold; }
    .edit-active { background-color: #d32f2f !important; color: white !important; }
    .status-msg { padding: 10px; border-radius: 8px; background-color: #fff3e0; border: 1px solid #ff9800; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

# Session States
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_mode' in st.session_state == False: st.session_state.edit_mode = -1

# --- පියවර 1: මෙනුව ---
if st.session_state.method is None:
    st.markdown("<br><div style='text-align:center; padding:50px; background:white; border-radius:20px; box-shadow:0 5px 15px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.subheader("ක්‍රමවේදය තෝරන්න")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📍 සිතියම මත ලකුණු කිරීම"):
            st.session_state.method = "manual"; st.rerun()
    with c2:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම (GPS)"):
            st.session_state.method = "gps"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- පියවර 2: Surveying Page ---
    st.sidebar.button("⬅️ Back to Menu", on_click=lambda: st.session_state.update({"method": None, "points": [], "edit_mode": -1}))

    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        # Map Create
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        # Draw Points
        for i, p in enumerate(st.session_state.points):
            is_editing = (st.session_state.get('edit_mode', -1) == i)
            color = "orange" if is_editing else "green"
            folium.Marker(
                location=[p[0], p[1]],
                icon=folium.DivIcon(html=f'<div style="font-size: 12pt; color: white; background: {color}; border-radius: 50%; width: 26px; height: 26px; text-align: center; border: 2px solid white; line-height: 26px; font-weight:bold;">{i+1}</div>'),
            ).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=3, fill=True, fill_opacity=0.3).add_to(m)

        # Map display
        map_data = st_folium(m, height=550, width="100%", use_container_width=True, key="survey_map")

        # --- SMART MOVE LOGIC ---
        if map_data['last_clicked']:
            new_pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            
            # 1. පරණ එකක් තෝරාගෙන තිබේ නම් එය මාරු කරන්න
            if st.session_state.get('edit_mode', -1) != -1:
                idx = st.session_state.edit_mode
                st.session_state.points[idx] = new_pos
                st.session_state.edit_mode = -1 # Clear edit mode
                st.rerun()
            
            # 2. අලුතින් පොයින්ට් එකක් එකතු කිරීම
            else:
                # චෙක් කරනවා පරණ එකක් උඩද ක්ලික් කළේ කියලා (Selection)
                found = False
                for i, p in enumerate(st.session_state.points):
                    dist = math.sqrt((p[0]-new_pos[0])**2 + (p[1]-new_pos[1])**2)
                    if dist < 0.0002: # ඉතා ආසන්න නම්
                        st.session_state.edit_mode = i
                        found = True
                        st.rerun()
                
                if not found:
                    st.session_state.points.append(new_pos)
                    st.rerun()

    with col_tools:
        st.markdown(f"### 📊 දත්ත වාර්තාව")
        
        # Edit Message
        if st.session_state.get('edit_mode', -1) != -1:
            st.markdown(f"<div class='status-msg'>📍 Point {st.session_state.edit_mode + 1} තෝරා ඇත. <br>එය තිබිය යුතු <b>අලුත් තැන</b> සිතියම මත ටච් කරන්න.</div>", unsafe_allow_html=True)
            if st.button("❌ අවලංගු කරන්න"):
                st.session_state.edit_mode = -1; st.rerun()

        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            st.metric(label="මුළු පර්චස්", value=f"{area_p:.2f}")

        st.markdown("---")
        if st.button("⬅️ Undo Last"):
            if st.session_state.points: st.session_state.points.pop(); st.rerun()
        
        if st.button("🗑️ Reset All"):
            st.session_state.points = []; st.session_state.edit_mode = -1; st.rerun()

        st.markdown("---")
        st.subheader("✂️ ඉඩම බෙදීම")
        st.number_input("පර්චස්:", min_value=0.0)
        st.button("🚀 රේඛාව අඳින්න")

st.markdown("---")
st.caption("LankaLand Pro v16.0 | Built for Precision")
