import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# Page Setup
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Professional UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3, p, label { color: #1a1a1a !important; font-weight: 800 !important; }
    .stButton>button { background-color: #1b5e20 !important; color: white !important; border-radius: 8px; font-weight: bold; height: 3.5em; }
    .method-card { background: white; padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-top: 50px; }
    .edit-mode-box { background-color: #fff3e0; padding: 10px; border-radius: 10px; border: 2px solid #ff9800; margin-bottom: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

# Session States initialization
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = None

# --- පියවර 1: මෙනුව (Selection Screen) ---
if st.session_state.method is None:
    st.markdown("<div class='method-card'>", unsafe_allow_html=True)
    st.subheader("මැනුම් ක්‍රමවේදය තෝරන්න")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📍 සිතියම මත ලකුණු කිරීම"):
            st.session_state.method = "manual"; st.rerun()
    with col_b:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම (GPS)"):
            st.session_state.method = "gps"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- පියවර 2: වැඩ කරන පිටුව ---
    st.sidebar.button("⬅️ Back to Menu", on_click=lambda: st.session_state.update({"method": None, "points": [], "edit_idx": None}))

    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        # Map configuration
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        # GPS Tracker
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        # Plot points with Touch-Selection Logic
        for i, p in enumerate(st.session_state.points):
            color = 'orange' if st.session_state.edit_idx == i else 'green'
            folium.Marker(
                location=[p[0], p[1]],
                icon=folium.DivIcon(html=f'<div style="font-size: 12pt; color: white; background: {color}; border-radius: 50%; width: 24px; height: 24px; text-align: center; border: 2px solid white; line-height: 24px;">{i+1}</div>')
            ).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=3, fill=True, fill_opacity=0.3).add_to(m)

        map_data = st_folium(m, height=550, width="100%", use_container_width=True)

        # --- Click/Touch Logic (Adding & Adjusting) ---
        if map_data['last_clicked']:
            clicked_pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            
            # මාරු කිරීම (Move)
            if st.session_state.edit_idx is not None:
                st.session_state.points[st.session_state.edit_idx] = clicked_pos
                st.session_state.edit_idx = None
                st.rerun()
            
            # තෝරාගැනීම හෝ අලුතින් එක් කිරීම
            else:
                found = False
                for i, p in enumerate(st.session_state.points):
                    # පරණ පොයින්ට් එකක් උඩ ක්ලික් කළාදැයි පරීක්ෂාව
                    if abs(p[0] - clicked_pos[0]) < 0.00015 and abs(p[1] - clicked_pos[1]) < 0.00015:
                        st.session_state.edit_idx = i
                        found = True
                        st.rerun()
                
                if not found:
                    st.session_state.points.append(clicked_pos)
                    st.rerun()

    with col_tools:
        st.markdown(f"### 📊 වාර්තාව ({st.session_state.method.upper()})")
        
        if st.session_state.edit_idx is not None:
            st.markdown(f"<div class='edit-mode-box'><b>Point {st.session_state.edit_idx + 1} තෝරා ඇත</b><br>දැන් එය තිබිය යුතු තැන මත ක්ලික් කරන්න.</div>", unsafe_allow_html=True)
            if st.button("❌ අවලංගු කරන්න"):
                st.session_state.edit_idx = None; st.rerun()

        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            st.metric(label="මුළු පර්චස්", value=f"{area_p:.2f}")

        st.markdown("---")
        if st.button("⬅️ Undo (අන්තිම එක මකන්න)"):
            if st.session_state.points: st.session_state.points.pop(); st.rerun()
        
        if st.button("🗑️ Reset All"):
            st.session_state.points = []; st.session_state.edit_idx = None; st.rerun()

        st.markdown("---")
        st.subheader("✂️ ඉඩම බෙදීම")
        st.number_input("පර්චස් ප්‍රමාණය:", min_value=0.0, step=0.1)
        st.button("🚀 බෙදුම් රේඛාව අඳින්න")

st.markdown("---")
st.caption("LankaLand Pro v15.0 | All Features Integrated")
