import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl
from shapely.geometry import Polygon, MultiPolygon, box
import math
import numpy as np

# --- Configuration & Styling (මුල් පිටපත එලෙසමයි) ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(90deg, #1b5e20, #4caf50); 
        padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); color: white;
    }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; background: #2e7d32 !important; 
        border: none; font-weight: 800; color: white !important; transition: 0.3s ease;
    }
    .stButton>button:hover { background: #43a047 !important; transform: translateY(-2px); }
    .card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
    .metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
    .plot-result { background-color: #1d2129; border: 1px solid #4caf50; border-radius: 8px; padding: 10px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'lang' not in st.session_state: st.session_state.lang = None
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = -1
if 'final_plots' not in st.session_state: st.session_state.final_plots = []
if 'total_area_perch' not in st.session_state: st.session_state.total_area_perch = 0.0
if 'orientation' not in st.session_state: st.session_state.orientation = "vertical"

# --- Language Dictionary (මුල් පිටපත එලෙසමයි) ---
texts = {
    "si": {
        "title": "🌍 ලංකාලෑන්ඩ් ප්‍රෝ GIS",
        "subtitle": "ජාත්‍යන්තර මට්ටමේ ඉඩම් මැනුම් සහ කට්ටි කිරීමේ පද්ධතිය",
        "select_lang": "භාෂාව තෝරන්න",
        "manual_marking": "🗺️ සිතියම මත ලකුණු කිරීම",
        "gps_survey": "🛰️ GPS මගින් මැනීම",
        "back_to_menu": "🔙 මුල් මෙනුවට",
        "analytics_title": "📊 දත්ත වාර්තාව",
        "total_area": "මුළු ප්‍රමාණය",
        "perch_unit": "P",
        "value_per_perch": "පර්චසයක මිල (රු.):",
        "total_value": "මුළු වටිනාකම",
        "subdivision_engine": "🏗️ ඉඩම් කට්ටි කිරීමේ එන්ජිම",
        "split_method": "බෙදුම් ක්‍රමය:",
        "fixed_area": "පර්චස් ප්‍රමාණය අනුව",
        "equal_shares": "සමාන කොටස් ගණන අනුව",
        "target_value": "අගය:",
        "execute_split": "🚀 කට්ටි කර පෙන්වන්න",
        "clear_plots": "🔄 බෙදීම් මකන්න",
        "reset_map": "🗑️ සියල්ල මකන්න",
        "remainder_label": "ඉතිරිය",
        "plot_label_prefix": "කැබැල්ල",
        "sub_success": "කට්ටි කිරීම සාර්ථකයි: කට්ටි {num_plots} ක් නිර්මාණය විය.",
        "not_enough_land": "⚠️ ප්‍රමාණවත් ඉඩමක් සලකුණු කර නැත.",
        "change_lang": "🌐 භාෂාව මාරු කරන්න",
        "vertical": "සිරස්",
        "horizontal": "තිරස්",
        "plot_tooltip": "කැබැල්ල: {label} ({area:.2f}P)"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "International Standard Surveying & Subdivision System",
        "select_lang": "SELECT LANGUAGE",
        "manual_marking": "🗺️ MANUAL SATELLITE MARKING",
        "gps_survey": "🛰️ LIVE GPS FIELD SURVEY",
        "back_to_menu": "🔙 BACK TO MAIN MENU",
        "analytics_title": "📊 ANALYTICS",
        "total_area": "Total Area",
        "perch_unit": "P",
        "value_per_perch": "Value per Perch (LKR):",
        "total_value": "Total Value",
        "subdivision_engine": "🏗️ SUBDIVISION ENGINE",
        "split_method": "Split Method:",
        "fixed_area": "Fixed Area",
        "equal_shares": "Equal Shares",
        "target_value": "Target Value:",
        "execute_split": "🚀 EXECUTE SUBDIVISION",
        "clear_plots": "🔄 CLEAR PLOTS",
        "reset_map": "🗑️ RESET MAP",
        "remainder_label": "REM",
        "plot_label_prefix": "Plot",
        "sub_success": "Subdivision Success: {num_plots} plots created.",
        "not_enough_land": "⚠️ Not enough land marked.",
        "change_lang": "🌐 Change Language",
        "vertical": "Vertical",
        "horizontal": "Horizontal",
        "plot_tooltip": "Plot: {label} ({area:.2f}P)"
    }
}

def calculate_polygon_area_perch(coords):
    if not coords or len(coords) < 3: return 0.0
    poly = Polygon(coords)
    avg_lat_rad = math.radians(coords[0][0])
    area_m2 = poly.area * (111319.9 ** 2) * abs(math.cos(avg_lat_rad))
    return area_m2 / 25.29

# --- Main Logic ---
if st.session_state.lang is None:
    st.markdown("<div class='main-header'><h1>SELECT LANGUAGE / භාෂාව තෝරන්න</h1></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("ENGLISH"): st.session_state.lang = "en"; st.rerun()
    if c2.button("සිංහල"): st.session_state.lang = "si"; st.rerun()

else:
    T = texts[st.session_state.lang]
    st.sidebar.markdown(f"### {T['title']}")
    if st.sidebar.button(T['back_to_menu']):
        st.session_state.update({"method": None, "points": [], "final_plots": []})
        st.rerun()
    if st.sidebar.button(T['change_lang']):
        st.session_state.lang = None; st.rerun()

    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button(T['manual_marking']): st.session_state.method = "manual"; st.rerun()
        if col2.button(T['gps_survey']): st.session_state.method = "gps"; st.rerun()
    
    else:
        col_map, col_tools = st.columns([2.5, 1])

        with col_map:
            m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
            LocateControl().add_to(m); Fullscreen().add_to(m); MeasureControl().add_to(m)

            for item in st.session_state.final_plots:
                folium.Polygon(locations=item['coords'], color="#4CAF50", weight=3, fill=True, fill_opacity=0.6, tooltip=item['label']).add_to(m)

            if len(st.session_state.points) >= 3:
                folium.Polygon(locations=st.session_state.points, color="#ffeb3b", weight=5, fill=False).add_to(m)

            for i, p in enumerate(st.session_state.points):
                folium.CircleMarker(location=p, radius=7, color='#4CAF50', fill=True).add_to(m)

            map_data = st_folium(m, height=650, width="100%", use_container_width=True, key="gis_map")

            if map_data['last_clicked']:
                clicked = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                st.session_state.points.append(clicked)
                st.rerun()

        with col_tools:
            st.markdown(f"<div class='card'><h3>{T['analytics_title']}</h3>", unsafe_allow_html=True)
            if len(st.session_state.points) >= 3:
                st.session_state.total_area_perch = calculate_polygon_area_perch(st.session_state.points)
                st.markdown(f"{T['total_area']}: <span class='metric-val'>{st.session_state.total_area_perch:.2f} {T['perch_unit']}</span>", unsafe_allow_html=True)
                price_per_p = st.number_input(T['value_per_perch'], min_value=0, value=100000, step=1000)
                st.markdown(f"{T['total_value']}: **LKR { (st.session_state.total_area_perch * price_per_p):,.0f}**", unsafe_allow_html=True)
            else:
                st.info(T['not_enough_land'])
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(f"<div class='card'><h3>{T['subdivision_engine']}</h3>", unsafe_allow_html=True)
            sub_method = st.selectbox(T['split_method'], [T['fixed_area'], T['equal_shares']])
            
            c1, c2 = st.columns(2)
            if c1.button(T['vertical']): st.session_state.orientation = "vertical"
            if c2.button(T['horizontal']): st.session_state.orientation = "horizontal"
            
            target_val = st.number_input(T['target_value'], min_value=1.0, value=25.0)

            if st.button(T['execute_split']):
                if len(st.session_state.points) >= 3:
                    main_poly = Polygon(st.session_state.points)
                    min_lat, min_lon, max_lat, max_lon = main_poly.bounds
                    num_plots = int(st.session_state.total_area_perch // target_val) if sub_method == T['fixed_area'] else int(target_val)
                    
                    st.session_state.final_plots = []
                    cuts = np.linspace(min_lon, max_lon, num_plots + 1) if st.session_state.orientation == "vertical" else np.linspace(min_lat, max_lat, num_plots + 1)
                    
                    for i in range(len(cuts)-1):
                        blade = box(min_lat-0.1, cuts[i], max_lat+0.1, cuts[i+1]) if st.session_state.orientation == "vertical" else box(cuts[i], min_lon-0.1, cuts[i+1], max_lon+0.1)
                        intersect = main_poly.intersection(blade)
                        if not intersect.is_empty:
                            if isinstance(intersect, MultiPolygon):
                                for part in intersect.geoms:
                                    st.session_state.final_plots.append({'coords': list(part.exterior.coords), 'label': f"{T['plot_label_prefix']} {i+1}"})
                            elif isinstance(intersect, Polygon):
                                st.session_state.final_plots.append({'coords': list(intersect.exterior.coords), 'label': f"{T['plot_label_prefix']} {i+1}"})
                    st.rerun()

            if st.session_state.final_plots:
                st.markdown(f"<div class='plot-result'>✅ {T['sub_success'].format(num_plots=len(st.session_state.final_plots))}</div>", unsafe_allow_html=True)
                rem_val = st.session_state.total_area_perch % (target_val if sub_method == T['fixed_area'] else (st.session_state.total_area_perch / target_val))
                st.write(f"⚠️ {T['remainder_label']}: {rem_val:.2f} {T['perch_unit']}")

            if st.button(T['clear_plots']): st.session_state.final_plots = []; st.rerun()
            if st.button(T['reset_map']): st.session_state.points = []; st.session_state.final_plots = []; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; opacity:0.5;'>LankaLand Pro v26.0</p>", unsafe_allow_html=True)
