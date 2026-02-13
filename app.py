import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# Custom Styling (Keeping the clean look you liked)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3, p, label { color: #1a1a1a !important; font-weight: 800 !important; }
    .stButton>button { background-color: #1b5e20 !important; color: white !important; border-radius: 8px; font-weight: bold; }
    .edit-mode { background-color: #fff3e0; padding: 10px; border-radius: 10px; border: 2px solid #ff9800; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

# Session States
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = None

col_map, col_tools = st.columns([2.5, 1])

with col_map:
    # සිතියම නිර්මාණය
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
    LocateControl(auto_start=False, flyTo=True).add_to(m)

    # පොයින්ට්ස් ලකුණු කිරීම
    for i, p in enumerate(st.session_state.points):
        # එඩිට් කරන පොයින්ට් එක රතු පාටින් පෙන්වන්න
        color = 'orange' if st.session_state.edit_idx == i else 'green'
        folium.Marker(
            location=[p[0], p[1]],
            tooltip=f"Point {i+1} (ටච් කර තෝරන්න)",
            icon=folium.DivIcon(html=f'<div style="font-size: 12pt; color: white; background: {color}; border-radius: 50%; width: 24px; height: 24px; text-align: center; border: 2px solid white; line-height: 24px;">{i+1}</div>')
        ).add_to(m)
    
    if len(st.session_state.points) >= 3:
        folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=3, fill=True, fill_opacity=0.3).add_to(m)

    map_data = st_folium(m, height=550, width="100%", use_container_width=True)

    # --- මාරු කිරීමේ Logic එක ---
    if map_data['last_clicked']:
        clicked_pos = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
        
        # 1. යම් පොයින්ට් එකක් මාරු කිරීමට තෝරාගෙන තිබේද? (Move Logic)
        if st.session_state.edit_idx is not None:
            st.session_state.points[st.session_state.edit_idx] = clicked_pos
            st.toast(f"Point {st.session_state.edit_idx + 1} අලුත් තැනට මාරු කළා!", icon="🎯")
            st.session_state.edit_idx = None # Reset edit mode
            st.rerun()
        
        # 2. අලුත් පොයින්ට් එකක් එකතු කිරීම
        else:
            # පරණ පොයින්ට් එකක් උඩම ක්ලික් කරාදැයි පරීක්ෂාව (Selection Logic)
            found = False
            for i, p in enumerate(st.session_state.points):
                if abs(p[0] - clicked_pos[0]) < 0.0001 and abs(p[1] - clicked_pos[1]) < 0.0001:
                    st.session_state.edit_idx = i
                    st.toast(f"Point {i+1} තෝරාගත්තා. දැන් එය තිබිය යුතු 'අලුත් තැන' මත ක්ලික් කරන්න.", icon="📍")
                    found = True
                    st.rerun()
            
            if not found:
                st.session_state.points.append(clicked_pos)
                st.rerun()

with col_tools:
    st.markdown("### 📊 පාලක පුවරුව")
    
    # Edit Mode එකේ ඉන්නවා නම් ඒක පෙන්වන්න
    if st.session_state.edit_idx is not None:
        st.markdown(f"""<div class='edit-mode'><b>Point {st.session_state.edit_idx + 1} තෝරා ඇත.</b><br>සිතියම මත එය තිබිය යුතු 'අලුත් තැන' මත ක්ලික් කරන්න.</div>""", unsafe_allow_html=True)
        if st.button("❌ මාරු කිරීම අවලංගු කරන්න"):
            st.session_state.edit_idx = None
            st.rerun()

    # වර්ගඵලය
    if len(st.session_state.points) >= 3:
        poly = Polygon(st.session_state.points)
        area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
        area_p = area_m2 / 25.29
        st.metric(label="මුළු පර්චස්", value=f"{area_p:.2f}")

    # Buttons
    if st.button("⬅️ Undo (අන්තිම එක මකන්න)"):
        if st.session_state.points: st.session_state.points.pop(); st.rerun()
    
    if st.button("🗑️ Reset All"):
        st.session_state.points = []; st.session_state.edit_idx = None; st.rerun()

    st.markdown("---")
    st.markdown("### ✂️ ඉඩම බෙදීම")
    st.number_input("Perches:", min_value=0.0, step=0.1)
    st.button("🚀 බෙදුම් රේඛාව අඳින්න")

st.markdown("---")
st.caption("LankaLand Pro v14.0 | Easy Point Adjustment")
