import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl
from shapely.geometry import Polygon
import math

# --- Premium Global Standard UI ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { background: linear-gradient(90deg, #1b5e20, #4caf50); padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: #2e7d32 !important; border: none; font-weight: 800; transition: 0.3s; }
    .stButton>button:hover { background: #43a047 !important; transform: translateY(-2px); }
    .card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
    .metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
    .rem-highlight { color: #ff5252; font-weight: bold; border-left: 4px solid #ff5252; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- Initializing Engine ---
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = -1
if 'final_plots' not in st.session_state: st.session_state.final_plots = []

# --- Landing Page ---
if st.session_state.method is None:
    st.markdown("<div class='main-header'><h1>🌍 LANKALAND PRO GIS v24.0</h1><p>International Standard Land Surveying & Subdivision System</p></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗺️ MANUAL SATELLITE MARKING"):
            st.session_state.method = "manual"; st.rerun()
    with col2:
        if st.button("🛰️ LIVE GPS FIELD SURVEY"):
            st.session_state.method = "gps"; st.rerun()
else:
    # --- Professional Dashboard ---
    st.sidebar.markdown("### 🛠️ NAVIGATION")
    if st.sidebar.button("🔙 EXIT TO MAIN MENU"):
        st.session_state.update({"method": None, "points": [], "edit_idx": -1, "final_plots": []})
        st.rerun()

    col_map, col_tools = st.columns([2.5, 1])

    with col_map:
        # High Resolution Map
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
        
        # Pro Tools
        LocateControl(auto_start=False, flyTo=True).add_to(m)
        Fullscreen().add_to(m)
        MeasureControl(primary_length_unit='meters', secondary_length_unit='miles').add_to(m)

        # Plot Subdivided Blocks
        if st.session_state.final_plots:
            for item in st.session_state.final_plots:
                p_color = "#ff5252" if item['is_rem'] else "#4caf50"
                folium.Polygon(
                    locations=item['coords'], 
                    color=p_color, weight=3, fill=True, fill_opacity=0.4,
                    tooltip=f"BLOCK: {item['label']}"
                ).add_to(m)

        # Main Boundary & Markers
        if len(st.session_state.points) >= 3:
            folium.Polygon(locations=st.session_state.points, color="#ffeb3b", weight=4, fill=False).add_to(m)

        for i, p in enumerate(st.session_state.points):
            m_color = 'orange' if st.session_state.edit_idx == i else '#4caf50'
            folium.CircleMarker(location=p, radius=6, color=m_color, fill=True, tooltip=f"Point {i+1}").add_to(m)

        map_data = st_folium(m, height=650, width="100%", use_container_width=True)

        # Interaction Logic
        if map_data['last_clicked']:
            clicked = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
            if st.session_state.edit_idx != -1:
                st.session_state.points[st.session_state.edit_idx] = clicked
                st.session_state.edit_idx = -1; st.rerun()
            else:
                found = False
                for i, p in enumerate(st.session_state.points):
                    if math.isclose(p[0], clicked[0], abs_tol=0.0001):
                        st.session_state.edit_idx = i; found = True; st.rerun()
                if not found: st.session_state.points.append(clicked); st.rerun()

    with col_tools:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📊 ANALYTICS")
        area_p = 0.0
        if len(st.session_state.points) >= 3:
            main_poly = Polygon(st.session_state.points)
            # Global standard area calc (m2 to perch)
            area_m2 = abs(main_poly.area) * (111319.9 ** 2) * math.cos(math.radians(st.session_state.points[0][0]))
            area_p = area_m2 / 25.29
            st.markdown(f"Total Area: <span class='metric-val'>{area_p:.2f} P</span>", unsafe_allow_html=True)
            
            # Smart Value Calc
            price_per_p = st.number_input("Value per Perch (LKR):", min_value=0, value=100000, step=1000)
            st.markdown(f"Total Value: **LKR { (area_p * price_per_p):,.0f}**")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='split-panel'>", unsafe_allow_html=True)
        st.markdown("### 🏗️ SUBDIVISION ENGINE")
        
        mode = st.selectbox("Split Method:", ["Fixed Area (e.g. 25P)", "Equal Shares (e.g. 5 Lots)"])
        target = st.number_input("Target Value:", min_value=1.0, value=25.0)

        if st.button("🚀 EXECUTE SUBDIVISION"):
            if area_p > 0:
                st.session_state.final_plots = []
                lats = [p[0] for p in st.session_state.points]
                lons = [p[1] for p in st.session_state.points]
                
                num_plots = int(area_p // target) if mode == "Fixed Area (e.g. 25P)" else int(target)
                rem_p = area_p % target if mode == "Fixed Area (e.g. 25P)" else 0
                
                # Grid Generation Engine
                cols = math.ceil(math.sqrt(num_plots))
                rows = math.ceil(num_plots / cols)
                lat_s, lon_s = (max(lats)-min(lats))/rows, (max(lons)-min(lons))/cols
                
                c = 0
                for r in range(rows):
                    for _c in range(cols):
                        if c < num_plots:
                            base = [min(lats) + r*lat_s, min(lons) + _c*lon_s]
                            coords = [[base[0], base[1]], [base[0], base[1]+lon_s], [base[0]+lat_s, base[1]+lon_s], [base[0]+lat_s, base[1]]]
                            st.session_state.final_plots.append({'coords': coords, 'label': f"Plot {c+1}", 'is_rem': False})
                            c += 1
                
                if rem_p > 0.5:
                    st.session_state.final_plots.append({'coords': [[max(lats), max(lons)], [max(lats)-lat_s, max(lons)], [max(lats), max(lons)-lon_s]], 'label': f"REM {rem_p:.1f}P", 'is_rem': True})
                st.rerun()

        if st.session_state.final_plots:
            st.info(f"Subdivision Success: {len(st.session_state.final_plots)-1 if rem_p > 0.5 else len(st.session_state.final_plots)} Full Plots created.")
            if st.button("🔄 CLEAR PLOTS"):
                st.session_state.final_plots = []; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🗑️ RESET MAP"):
            st.session_state.update({"points": [], "final_plots": []}); st.rerun()

st.markdown("<br><p style='text-align:center; opacity:0.5;'>LankaLand Pro v24.0 | Advanced GIS Core</p>", unsafe_allow_html=True)
