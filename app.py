import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# --- Page Config ---
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# --- UI Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3, p, label { color: #1a1a1a !important; font-weight: 800 !important; }
    .stButton>button { background-color: #1b5e20 !important; color: white !important; border-radius: 8px; font-weight: bold; }
    .split-panel { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #1b5e20; margin-top: 10px; }
    input { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

# --- Session States ---
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = -1
if 'split_data' not in st.session_state: st.session_state.split_data = None

# --- Step 1: Selection Menu ---
if st.session_state.method is None:
    st.markdown("<div style='text-align:center; padding:50px; background:white; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.1); margin-top:50px;'>", unsafe_allow_html=True)
    st.subheader("ඇරඹීමට මැනුම් ක්‍රමවේදයක් තෝරන්න")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📍 සිතියම මත ලකුණු කිරීම"):
            st.session_state.method = "manual"; st.rerun()
    with c2:
        if st.button("🚶 ඇවිදිමින් ලකුණු කිරීම (GPS)"):
            st.session_state.method = "gps"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- Step 2: Main Interface ---
    st.sidebar.button("⬅️ Back to Menu", on_click=lambda: st.session_state.update({"method": None, "points": [], "edit_idx": -1, "split_data": None}))

    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        # Draw Points
        for i, p in enumerate(st.session_state.points):
            color = 'orange' if st.session_state.edit_idx == i else 'green'
            folium.Marker(location=p, icon=folium.DivIcon(html=f'<div style="font-size:11pt; color:white; background:{color}; border-radius:50%; width:24px; height:24px; text-align:center; border:2px solid white; line-height:24px; font-weight:bold;">{i+1}</div>')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=2, fill=True, fill_opacity=0.1).add_to(m)

        # --- Smart Multi-Plot Display ---
        if st.session_state.split_data:
            plots = st.session_state.split_data['plots']
            colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6']
            for idx, plot in enumerate(plots):
                folium.Polygon(locations=plot, color=colors[idx % len(colors)], weight=3, fill=True, fill_opacity=0.5, tooltip=f"කැබැල්ල {idx+1}").add_to(m)

        map_data = st_folium(m, height=600, width="100%", use_container_width=True)

        # Move/Add Points Logic
        if map_data['last_clicked']:
            clicked = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if st.session_state.edit_idx != -1:
                st.session_state.points[st.session_state.edit_idx] = clicked
                st.session_state.edit_idx = -1; st.rerun()
            else:
                found = False
                for i, p in enumerate(st.session_state.points):
                    if math.sqrt((p[0]-clicked[0])**2 + (p[1]-clicked[1])**2) < 0.00015:
                        st.session_state.edit_idx = i; found = True; st.rerun()
                if not found:
                    st.session_state.points.append(clicked); st.rerun()

    with col_tools:
        st.markdown("### 📊 මැනුම් වාර්තාව")
        area_p = 0.0
        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            st.metric("මුළු ප්‍රමාණය", f"{area_p:.2f} Perch")

        # --- Advanced Splitting Tool ---
        st.markdown("<div class='split-panel'>", unsafe_allow_html=True)
        st.subheader("✂️ ඉඩම බෙදීම")
        size = st.number_input("කැබැල්ලක ප්‍රමාණය (Perch):", min_value=1.0, value=20.0)
        direction = st.radio("බෙදිය යුතු දිශාව:", ["සිරස් (Vertical)", "තිරස් (Horizontal)"])
        
        if st.button("🚀 කොටස් වෙන් කරන්න"):
            if area_p > size:
                count = int(area_p // size)
                rem = area_p % size
                lats = [p[0] for p in st.session_state.points]
                lons = [p[1] for p in st.session_state.points]
                
                simulated_plots = []
                # ප්ලොට් එකේ දිශාව තීරණය කිරීම
                if direction == "සිරස් (Vertical)":
                    min_val, max_val = min(lons), max(lons)
                    mode = 1 # Longitude based
                else:
                    min_val, max_val = min(lats), max(lats)
                    mode = 0 # Latitude based
                
                step = (max_val - min_val) / (area_p / size)
                for j in range(count):
                    v_min = min_val + (j * step)
                    v_max = min_val + ((j+1) * step)
                    plot_coords = [p for p in st.session_state.points if v_min <= p[mode] <= v_max]
                    if len(plot_coords) >= 2: simulated_plots.append(plot_coords)
                
                st.session_state.split_data = {'plots': simulated_plots, 'rem': rem, 'count': count}
                st.rerun()

        if st.session_state.split_data:
            st.success(f"කැබලි {st.session_state.split_data['count']} ක් සහ ඉතිරි {st.session_state.split_data['rem']:.2f} Perch වෙන් කළා.")
            if st.button("🔄 බෙදීම් මකන්න"):
                st.session_state.split_data = None; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.button("🗑️ Reset All", on_click=lambda: st.session_state.update({"points": [], "split_data": None, "edit_idx": -1}))

st.markdown("---")
st.caption("LankaLand Pro v21.0 | Professional Plot Partitioning Tool")
