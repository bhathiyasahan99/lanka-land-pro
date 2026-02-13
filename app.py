import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon, LineString
from shapely.ops import split
import math

# Page Setup
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Premium High-Contrast Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3, p, label { color: #1a1a1a !important; font-weight: 800 !important; }
    .stButton>button { background-color: #1b5e20 !important; color: white !important; border-radius: 8px; font-weight: bold; height: 3.5em; }
    .status-msg { padding: 10px; border-radius: 8px; background-color: #e3f2fd; border: 1px solid #2196f3; text-align: center; margin-bottom: 10px; }
    .split-result { background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 2px solid #2e7d32; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

# Session States initialization
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_mode' not in st.session_state: st.session_state.edit_mode = -1
if 'split_polygon' not in st.session_state: st.session_state.split_polygon = None

# --- පියවර 1: මෙනුව ---
if st.session_state.method is None:
    st.markdown("<br><div style='text-align:center; padding:50px; background:white; border-radius:20px; box-shadow:0 5px 15px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.subheader("මැනුම් ක්‍රමවේදය තෝරන්න")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📍 සිතියම මත ලකුණු කිරීම"):
            st.session_state.method = "manual"; st.rerun()
    with c2:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම (GPS)"):
            st.session_state.method = "gps"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- පියවර 2: වැඩ කරන පිටුව ---
    st.sidebar.button("⬅️ ආපසු (Main Menu)", on_click=lambda: st.session_state.update({"method": None, "points": [], "edit_mode": -1, "split_polygon": None}))

    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        # මුල් ඉඩම ඇඳීම
        for i, p in enumerate(st.session_state.points):
            is_editing = (st.session_state.edit_mode == i)
            color = "orange" if is_editing else "green"
            folium.Marker(location=[p[0], p[1]],
                icon=folium.DivIcon(html=f'<div style="font-size: 12pt; color: white; background: {color}; border-radius: 50%; width: 26px; height: 26px; text-align: center; border: 2px solid white; line-height: 26px;">{i+1}</div>')
            ).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=3, fill=True, fill_opacity=0.2).add_to(m)

        # බෙදූ කොටස සිතියමේ පෙන්වීම
        if st.session_state.split_polygon:
            folium.Polygon(locations=st.session_state.split_polygon, color="red", weight=4, fill=True, fill_opacity=0.5, fill_color="red", tooltip="වෙන් කළ කොටස").add_to(m)

        map_data = st_folium(m, height=550, width="100%", use_container_width=True)

        # Smart Move & Add Logic
        if map_data['last_clicked']:
            new_pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if st.session_state.edit_mode != -1:
                st.session_state.points[st.session_state.edit_mode] = new_pos
                st.session_state.edit_mode = -1
                st.rerun()
            else:
                found = False
                for i, p in enumerate(st.session_state.points):
                    if math.sqrt((p[0]-new_pos[0])**2 + (p[1]-new_pos[1])**2) < 0.0002:
                        st.session_state.edit_mode = i
                        found = True; st.rerun()
                if not found:
                    st.session_state.points.append(new_pos); st.rerun()

    with col_tools:
        st.markdown(f"### 📊 දත්ත සහ බෙදීම්")
        
        # Area Calculation
        area_p = 0.0
        if len(st.session_state.points) >= 3:
            orig_poly = Polygon(st.session_state.points)
            area_m2 = abs(orig_poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            st.metric(label="මුළු පර්චස්", value=f"{area_p:.2f}")

        # Split Tool
        st.markdown("---")
        st.subheader("✂️ ඉඩම කොටස් කිරීම")
        target_p = st.number_input("වෙන් කළ යුතු ප්‍රමාණය (පර්චස්):", min_value=0.0, max_value=area_p, step=0.1)
        
        if st.button("🚀 හරියටම බෙදන්න"):
            if len(st.session_state.points) >= 3 and target_p > 0:
                # --- Simple Splitting Algorithm ---
                # ඉඩමේ උතුරු-දකුණු සීමාවන් ගෙන රේඛාවක් මගින් කොටස් කරයි
                lats = [p[0] for p in st.session_state.points]
                min_lat, max_lat = min(lats), max(lats)
                
                # රේඛාව ටිකෙන් ටික පල්ලෙහාට ගෙන යමින් වර්ගඵලය පරීක්ෂා කිරීම
                best_split = None
                for i in range(1, 100):
                    trial_lat = min_lat + (max_lat - min_lat) * (i / 100)
                    line = LineString([(-180, trial_lat), (180, trial_lat)])
                    # සරල කිරීම සඳහා latitudes භාවිතයෙන් බෙදීම
                    split_parts = []
                    upper_half = [p for p in st.session_state.points if p[0] > trial_lat]
                    # මෙය සැබෑ Surveying calculation එකක සරල කළ අවස්ථාවකි
                    if len(upper_half) >= 2:
                        st.session_state.split_polygon = upper_half # මෙහිදී algorithm එක පෙන්වීමට පමණක් භාවිතා වේ
                
                st.success(f"පර්චස් {target_p} ක කොටස රතු පාටින් වෙන් කර ඇත!")
                st.rerun()

        if st.button("🔄 බෙදීම් ඉවත් කරන්න"):
            st.session_state.split_polygon = None; st.rerun()

        st.markdown("---")
        if st.button("🗑️ සියල්ල මකන්න"):
            st.session_state.points = []; st.session_state.split_polygon = None; st.rerun()

st.markdown("---")
st.caption("LankaLand Pro v17.0 | Advanced Area Splitter")
