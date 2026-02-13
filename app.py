import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# --- Configuration & Styling ---
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3, p, label { color: #1a1a1a !important; font-weight: 800 !important; }
    .stButton>button { background-color: #1b5e20 !important; color: white !important; border-radius: 8px; font-weight: bold; }
    .split-panel { background: white; padding: 20px; border-radius: 15px; border: 2px solid #1b5e20; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .rem-box { background-color: #fff3e0; padding: 10px; border-radius: 8px; border: 1px solid #ff9800; margin-top: 10px; font-weight: bold; }
    input { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

# --- Initialization ---
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = -1
if 'split_data' not in st.session_state: st.session_state.split_data = None

# --- Main Selection Menu ---
if st.session_state.method is None:
    st.markdown("<div style='text-align:center; padding:50px; background:white; border-radius:20px; margin-top:50px;'>", unsafe_allow_html=True)
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
    st.sidebar.button("⬅️ ආපසු", on_click=lambda: st.session_state.update({"method": None, "points": [], "edit_idx": -1, "split_data": None}))

    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        # Plot boundary points
        for i, p in enumerate(st.session_state.points):
            color = 'orange' if st.session_state.edit_idx == i else 'green'
            folium.Marker(location=p, icon=folium.DivIcon(html=f'<div style="font-size:11pt; color:white; background:{color}; border-radius:50%; width:24px; height:24px; text-align:center; border:2px solid white; line-height:24px;">{i+1}</div>')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=2, fill=True, fill_opacity=0.1).add_to(m)

        # --- Subdivision Rendering ---
        if st.session_state.split_data:
            plots = st.session_state.split_data['plots']
            rem_plot = st.session_state.split_data['remainder_plot']
            colors = ['#2196F3', '#9C27B0', '#00BCD4', '#4CAF50', '#3F51B5']
            
            # Draw standard plots
            for idx, plot in enumerate(plots):
                folium.Polygon(locations=plot, color=colors[idx % len(colors)], weight=3, fill=True, fill_opacity=0.5, tooltip=f"කොටස {idx+1}").add_to(m)
            
            # Draw Remainder (Vivid Orange for 5 perch like bits)
            if rem_plot:
                folium.Polygon(locations=rem_plot, color="#FF3D00", weight=4, fill=True, fill_opacity=0.7, tooltip="ඉතිරි කොටස (Remainder)").add_to(m)

        map_data = st_folium(m, height=600, width="100%", use_container_width=True)

        # Move/Add Logic
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
                if not found: st.session_state.points.append(clicked); st.rerun()

    with col_tools:
        st.markdown("### 📊 වාර්තාව")
        area_p = 0.0
        if len(st.session_state.points) >= 3:
            poly = Polygon(st.session_state.points)
            area_m2 = abs(poly.area) * (111139 ** 2) * math.cos(math.radians(7.87))
            area_p = area_m2 / 25.29
            st.metric("මුළු ප්‍රමාණය", f"{area_p:.2f} Perch")

        # --- Subdivision Tools ---
        st.markdown("<div class='split-panel'>", unsafe_allow_html=True)
        st.subheader("✂️ ඉඩම බෙදීමේ මෙවලම")
        
        split_type = st.radio("බෙදුම් ක්‍රමය:", ["පර්චස් ප්‍රමාණය අනුව", "සමාන කොටස් ගණන අනුව"])
        orient = st.radio("දිශාව:", ["සිරස් (Vertical)", "තිරස් (Horizontal)"])

        if split_type == "පර්චස් ප්‍රමාණය අනුව":
            val = st.number_input("කැබැල්ලක පර්චස් ගණන:", min_value=1.0, value=25.0)
            btn_label = "පර්චස් ගාණට බෙදන්න"
        else:
            val = st.number_input("බෙදිය යුතු කොටස් ගණන:", min_value=2, step=1)
            btn_label = "සමාන කොටස් වලට බෙදන්න"

        if st.button(btn_label):
            if area_p > 0:
                lats = [p[0] for p in st.session_state.points]
                lons = [p[1] for p in st.session_state.points]
                min_v, max_v = (min(lons), max(lons)) if orient == "සිරස් (Vertical)" else (min(lats), max(lats))
                mode = 1 if orient == "සිරස් (Vertical)" else 0
                
                if split_type == "පර්චස් ප්‍රමාණය අනුව":
                    count = int(area_p // val)
                    rem_area = area_p % val
                    total_steps = area_p / val
                else:
                    count = int(val)
                    rem_area = 0
                    total_steps = val
                
                step = (max_v - min_v) / total_steps
                all_plots = []
                rem_plot = None
                
                for j in range(count):
                    v_low, v_high = min_v + (j * step), min_v + ((j+1) * step)
                    nodes = [p for p in st.session_state.points if v_low <= p[mode] <= v_high]
                    if len(nodes) >= 2: all_plots.append(nodes)
                
                if rem_area > 0:
                    rem_nodes = [p for p in st.session_state.points if (min_v + count * step) <= p[mode] <= max_v]
                    if len(rem_nodes) >= 2: rem_plot = rem_nodes

                st.session_state.split_data = {'plots': all_plots, 'remainder_plot': rem_plot, 'rem_val': rem_area}
                st.rerun()

        if st.session_state.split_data:
            if st.session_state.split_data['rem_val'] > 0:
                st.markdown(f"<div class='rem-box'>⚠️ ඉතිරි කොටස: {st.session_state.split_data['rem_val']:.2f} Perch (රතු පාටින්)</div>", unsafe_allow_html=True)
            if st.button("🔄 බෙදීම් ඉවත් කරන්න"):
                st.session_state.split_data = None; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.button("🗑️ Reset All", on_click=lambda: st.session_state.update({"points": [], "split_data": None}))

st.markdown("---")
st.caption("LankaLand Pro v22.0 | Dual-Mode Subdivision")
