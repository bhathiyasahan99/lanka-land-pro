import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from shapely.geometry import Polygon
import math

# Page Setup
st.set_page_config(page_title="LankaLand Pro", layout="wide", page_icon="🌾")

# UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3, p, label { color: #1a1a1a !important; font-weight: 800 !important; }
    .stButton>button { background-color: #1b5e20 !important; color: white !important; border-radius: 8px; font-weight: bold; }
    .plot-info { background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌾 LankaLand Pro</h1>", unsafe_allow_html=True)

# Session States
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = -1
if 'split_data' not in st.session_state: st.session_state.split_data = None

# --- Step 1: Selection Menu ---
if st.session_state.method is None:
    st.markdown("<div style='text-align:center; padding:50px; background:white; border-radius:20px; box-shadow:0 10px 25px rgba(0,0,0,0.1); margin-top:50px;'>", unsafe_allow_html=True)
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
    # --- Step 2: Main Interface ---
    st.sidebar.button("⬅️ ආපසු", on_click=lambda: st.session_state.update({"method": None, "points": [], "edit_idx": -1, "split_data": None}))

    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        LocateControl(auto_start=False, flyTo=True).add_to(m)

        # Draw Main Points
        for i, p in enumerate(st.session_state.points):
            color = 'orange' if st.session_state.edit_idx == i else 'green'
            folium.Marker(location=p, icon=folium.DivIcon(html=f'<div style="font-size:10pt; color:white; background:{color}; border-radius:50%; width:22px; height:22px; text-align:center; border:2px solid white; line-height:22px;">{i+1}</div>')).add_to(m)
        
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffff00", weight=2, fill=True, fill_opacity=0.1).add_to(m)

        # --- Display Split Plots ---
        if st.session_state.split_data:
            plots = st.session_state.split_data['plots']
            colors = ['#FF5722', '#2196F3', '#9C27B0', '#FFEB3B', '#00BCD4', '#4CAF50']
            for idx, plot in enumerate(plots):
                folium.Polygon(locations=plot, color=colors[idx % len(colors)], weight=3, fill=True, fill_opacity=0.4, 
                               tooltip=f"කොටස {idx+1} ({st.session_state.split_data['each_p']} Perch)").add_to(m)

        map_data = st_folium(m, height=550, width="100%", use_container_width=True)

        # Point Move/Add Logic
        if map_data['last_clicked']:
            clicked = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if st.session_state.edit_idx != -1:
                st.session_state.points[st.session_state.edit_idx] = clicked
                st.session_state.edit_idx = -1; st.rerun()
            else:
                found = False
                for i, p in enumerate(st.session_state.points):
                    if math.sqrt((p[0]-clicked[0])**2 + (p[1]-clicked[1])**2) < 0.0002:
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
            st.metric("මුළු පර්චස්", f"{area_p:.2f}")

        st.markdown("---")
        st.subheader("✂️ ඉඩම කොටස් කිරීම")
        each_p = st.number_input("කැබැල්ලක ප්‍රමාණය (Perches):", min_value=1.0, step=1.0)
        
        if st.button("🚀 කොටස්වලට බෙදන්න"):
            if area_p > each_p:
                num_plots = int(area_p // each_p)
                remainder = area_p % each_p
                
                # Simple Visual Split Logic (Latitudinal slicing)
                lats = [p[0] for p in st.session_state.points]
                min_l, max_l = min(lats), max(lats)
                step = (max_l - min_l) / (area_p / each_p)
                
                all_plots = []
                for i in range(num_plots):
                    p_min = min_l + (i * step)
                    p_max = min_l + ((i+1) * step)
                    # කොටසක් ලෙස සරලව lat slice එකක් පෙන්වීම
                    plot_coords = [p for p in st.session_state.points if p_min <= p[0] <= p_max]
                    if len(plot_coords) >= 3: all_plots.append(plot_coords)
                
                st.session_state.split_data = {'plots': all_plots, 'remainder': remainder, 'count': num_plots, 'each_p': each_p}
                st.rerun()

        if st.session_state.split_data:
            d = st.session_state.split_data
            st.markdown(f"""
            <div class='plot-info'>
            <b>බෙදුම් ප්‍රතිඵල:</b><br>
            ✅ පර්චස් {d['each_p']} කෑලි: {d['count']}<br>
            ⚠️ ඉතිරි ප්‍රමාණය: {d['remainder']:.2f} Perch
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 බෙදීම් මකන්න"):
                st.session_state.split_data = None; st.rerun()

        st.button("🗑️ Reset All", on_click=lambda: st.session_state.update({"points": [], "split_data": None, "edit_idx": -1}))

st.markdown("---")
st.caption("LankaLand Pro v19.0 | Smart Multi-Plot Division")
