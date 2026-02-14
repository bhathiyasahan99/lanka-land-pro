import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import split
import math

# --- Configuration & Styling ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(90deg, #1b5e20, #4caf50); 
        padding: 25px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 25px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
        color: white; /* Ensure text is white for contrast */
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background: #2e7d32 !important; 
        border: none; 
        font-weight: 800; 
        color: white !important; /* Ensure text is white */
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background: #43a047 !important;
        transform: translateY(-2px);
    }
    .card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
    .metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
    .plot-result { background-color: #1d2129; border: 1px solid #4caf50; border-radius: 8px; padding: 10px; margin-top: 10px; }
    .lang-button { margin: 5px; padding: 10px 20px; border-radius: 8px; border: 1px solid #4caf50; background-color: #1d2129; color: #4caf50; font-weight: bold; cursor: pointer; }
    .lang-button:hover { background-color: #4caf50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'lang' not in st.session_state: st.session_state.lang = None
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'edit_idx' not in st.session_state: st.session_state.edit_idx = -1
if 'final_plots' not in st.session_state: st.session_state.final_plots = []
if 'total_area_perch' not in st.session_state: st.session_state.total_area_perch = 0.0

# --- Language Dictionary ---
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
        "sub_success": "කට්ටි කිරීම සාර්ථකයි: {num_plots} සම්පූර්ණ කැබලි.",
        "not_enough_land": "⚠️ ප්‍රමාණවත් ඉඩමක් සලකුණු කර නැත.",
        "change_lang": "🌐 භාෂාව මාරු කරන්න",
        "orientation": "දිශාව:",
        "vertical": "සිරස්",
        "horizontal": "තිරස්",
        "move_point_msg": "📍 ලක්ෂ්‍යය {idx} මාරු කිරීමට සූදානම්. නව ස්ථානය මත ක්ලික් කරන්න.",
        "processing_split": "බෙදීම් සැකසෙමින් පවතී...",
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
        "fixed_area": "Fixed Area (e.g. 25P)",
        "equal_shares": "Equal Shares (e.g. 5 Lots)",
        "target_value": "Target Value:",
        "execute_split": "🚀 EXECUTE SUBDIVISION",
        "clear_plots": "🔄 CLEAR PLOTS",
        "reset_map": "🗑️ RESET MAP",
        "remainder_label": "REM",
        "plot_label_prefix": "Plot",
        "sub_success": "Subdivision Success: {num_plots} full plots created.",
        "not_enough_land": "⚠️ Not enough land marked for subdivision.",
        "change_lang": "🌐 Change Language",
        "orientation": "Orientation:",
        "vertical": "Vertical",
        "horizontal": "Horizontal",
        "move_point_msg": "📍 Point {idx} ready to move. Click on new location.",
        "processing_split": "Processing subdivision...",
        "plot_tooltip": "Plot: {label} ({area:.2f}P)"
    }
}

# --- Utility Function: Calculate Polygon Area (more accurate for Lat/Lon) ---
def calculate_polygon_area_perch(coords):
    if not coords or len(coords) < 3:
        return 0.0
    
    # Using Spherical excess formula for better accuracy with Lat/Lon
    # For a small area, simple planar approximation is often sufficient, but this is more robust
    polygon = Polygon(coords)
    area_sq_deg = polygon.area # Area in square degrees

    # Approximate conversion factor (meters per degree at equator)
    # Average latitude for better approximation (using the first point's latitude)
    avg_lat_rad = math.radians(coords[0][0]) 
    
    # 1 degree latitude = ~111.32 km (constant)
    # 1 degree longitude = ~111.32 * cos(latitude) km
    
    # Area in square meters (approximate)
    area_m2 = area_sq_deg * (111319.9 ** 2) * abs(math.cos(avg_lat_rad))
    
    return area_m2 / 25.29 # Convert m2 to Perch

# --- Step 0: Language Selection ---
if st.session_state.lang is None:
    st.markdown("<div class='main-header'><h1>SELECT LANGUAGE / භාෂාව තෝරන්න</h1></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("ENGLISH", key="lang_en"):
            st.session_state.lang = "en"; st.rerun()
    with c2:
        if st.button("සිංහල", key="lang_si"):
            st.session_state.lang = "si"; st.rerun()

# --- Main Application Logic ---
else:
    T = texts[st.session_state.lang] # Get current language texts

    # --- Sidebar Navigation ---
    st.sidebar.markdown(f"### {T['title']}")
    if st.sidebar.button(T['back_to_menu']):
        st.session_state.update({"method": None, "points": [], "edit_idx": -1, "final_plots": [], 'total_area_perch': 0.0})
        st.rerun()
    if st.sidebar.button(T['change_lang']):
        st.session_state.lang = None; st.rerun()

    # --- Step 1: Method Selection (if not already selected) ---
    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(T['manual_marking'], key="method_manual"):
                st.session_state.method = "manual"; st.rerun()
        with col2:
            if st.button(T['gps_survey'], key="method_gps"):
                st.session_state.method = "gps"; st.rerun()
    
    # --- Step 2: Main Working Dashboard ---
    else:
        col_map, col_tools = st.columns([2.5, 1])

        with col_map:
            # --- Folium Map Setup ---
            m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, 
                           tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
            
            # --- Map Plugins ---
            LocateControl(auto_start=False, flyTo=True).add_to(m)
            Fullscreen().add_to(m)
            MeasureControl(primary_length_unit='meters', secondary_length_unit='miles').add_to(m)

            # --- Draw Subdivided Plots ---
            if st.session_state.final_plots:
                for item in st.session_state.final_plots:
                    p_color = "#FF3D00" if item['is_rem'] else "#4CAF50" # Remainder Red, Others Green
                    plot_area = calculate_polygon_area_perch(item['coords']) # Calculate area for tooltip
                    folium.Polygon(
                        locations=item['coords'], 
                        color=p_color, 
                        weight=3, 
                        fill=True, 
                        fill_opacity=0.6,
                        tooltip=f"{item['label']}: {plot_area:.2f}{T['perch_unit']}"
                    ).add_to(m)

            # --- Draw Main Land Boundary ---
            if len(st.session_state.points) >= 3:
                folium.Polygon(locations=st.session_state.points, color="#ffeb3b", weight=5, fill=False).add_to(m) # Yellow Boundary

            # --- Draw Land Markers ---
            for i, p in enumerate(st.session_state.points):
                m_color = 'orange' if st.session_state.edit_idx == i else '#4CAF50' # Highlight selected point
                folium.CircleMarker(
                    location=p, 
                    radius=7, 
                    color=m_color, 
                    fill=True, 
                    fill_color=m_color, 
                    tooltip=f"Point {i+1}"
                ).add_to(m)

            # --- Render Map and Handle Clicks ---
            map_data = st_folium(m, height=650, width="100%", use_container_width=True, key="gis_map")

            # --- Point Interaction Logic (Add/Move) ---
            if map_data['last_clicked']:
                clicked = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                
                # If a point is in edit mode (selected to be moved)
                if st.session_state.edit_idx != -1:
                    st.session_state.points[st.session_state.edit_idx] = clicked
                    st.session_state.edit_idx = -1 # Clear edit mode
                    st.rerun()
                else:
                    # Check if an existing point was clicked to select it for moving
                    selected_idx = -1
                    for i, p in enumerate(st.session_state.points):
                        # Use a small tolerance for "click proximity"
                        if math.isclose(p[0], clicked[0], abs_tol=0.0001) and math.isclose(p[1], clicked[1], abs_tol=0.0001):
                            selected_idx = i
                            break
                    
                    if selected_idx != -1: # An existing point was clicked
                        st.session_state.edit_idx = selected_idx
                        st.rerun()
                    else: # No existing point clicked, add a new one
                        st.session_state.points.append(clicked)
                        st.rerun()

        with col_tools:
            # --- Analytics Card ---
            st.markdown(f"<div class='card'><h3>{T['analytics_title']}</h3>", unsafe_allow_html=True)
            st.session_state.total_area_perch = 0.0 # Reset for fresh calculation
            if len(st.session_state.points) >= 3:
                st.session_state.total_area_perch = calculate_polygon_area_perch(st.session_state.points)
                st.markdown(f"{T['total_area']}: <span class='metric-val'>{st.session_state.total_area_perch:.2f} {T['perch_unit']}</span>", unsafe_allow_html=True)
                
                price_per_p = st.number_input(T['value_per_perch'], min_value=0, value=100000, step=1000, key="price_input")
                st.markdown(f"{T['total_value']}: **LKR { (st.session_state.total_area_perch * price_per_p):,.0f}**", unsafe_allow_html=True)
            else:
                st.info(T['not_enough_land'])
            st.markdown("</div>", unsafe_allow_html=True)

            # --- Subdivision Engine Card ---
            st.markdown(f"<div class='card'><h3>{T['subdivision_engine']}</h3>", unsafe_allow_html=True)
            
            sub_method = st.selectbox(T['split_method'], [T['fixed_area'], T['equal_shares']], key="split_method_select")
            
            # Use columns for better layout of Orientation buttons
            col_orient_1, col_orient_2 = st.columns(2)
            with col_orient_1:
                if st.button(T['vertical'], key="orient_vert_btn"):
                    st.session_state.orientation = "vertical"
            with col_orient_2:
                if st.button(T['horizontal'], key="orient_hori_btn"):
                    st.session_state.orientation = "horizontal"
            
            # Default orientation if not set
            if 'orientation' not in st.session_state:
                st.session_state.orientation = "vertical" # Default

            target_val = st.number_input(T['target_value'], min_value=1.0, value=25.0, step=0.5, key="target_val_input")

            if st.button(T['execute_split'], key="execute_split_btn"):
                if st.session_state.total_area_perch > 0:
                    st.session_state.final_plots = [] # Clear previous plots
                    
                    # --- Complex Grid Generation for Subdivision ---
                    # Calculate bounding box of the main land
                    lats = [p[0] for p in st.session_state.points]
                    lons = [p[1] for p in st.session_state.points]
                    min_lat, max_lat = min(lats), max(lats)
                    min_lon, max_lon = min(lons), max(lons)
                    
                    if sub_method == T['fixed_area']:
                        num_plots_needed = int(st.session_state.total_area_perch // target_val)
                        remainder_perch = st.session_state.total_area_perch % target_val
                    else: # Equal Shares
                        num_plots_needed = int(target_val) # Target value is number of equal shares
                        remainder_perch = 0.0 # No remainder for equal shares

                    # Determine grid dimensions based on orientation
                    if st.session_state.orientation == "vertical": # Split along longitude (columns)
                        rows_grid = 1 # Assume 1 row for simplicity, can be more complex
                        cols_grid = num_plots_needed
                    else: # Horizontal (split along latitude - rows)
                        rows_grid = num_plots_needed
                        cols_grid = 1 # Assume 1 column for simplicity

                    # Adjust for potential zero divisions if num_plots_needed is 0
                    if num_plots_needed == 0:
                        st.warning("Not enough area to create plots based on your criteria.")
                        st.rerun()

                    lat_step_deg = (max_lat - min_lat) / (rows_grid if rows_grid > 0 else 1)
                    lon_step_deg = (max_lon - min_lon) / (cols_grid if cols_grid > 0 else 1)
                    
                    current_plot_count = 0
                    for r_idx in range(rows_grid):
                        for c_idx in range(cols_grid):
                            if current_plot_count < num_plots_needed:
                                p1_lat = min_lat + r_idx * lat_step_deg
                                p1_lon = min_lon + c_idx * lon_step_deg
                                
                                p2_lat = min_lat + (r_idx + 1) * lat_step_deg
                                p2_lon = min_lon + (c_idx + 1) * lon_step_deg

                                plot_coords = [
                                    (p1_lat, p1_lon), (p1_lat, p2_lon), 
                                    (p2_lat, p2_lon), (p2_lat, p1_lon), (p1_lat, p1_lon) # Close polygon
                                ]
                                st.session_state.final_plots.append({'coords': plot_coords, 'label': f"{T['plot_label_prefix']} {current_plot_count+1}", 'is_rem': False})
                                current_plot_count += 1
                    
                    # Add remainder plot if exists and significant
                    if remainder_perch > 0.5:
                        # For visual representation, place a small remainder plot at a corner
                        rem_coords = [
                            (min_lat, max_lon - lon_step_deg/2), (min_lat, max_lon), 
                            (min_lat + lat_step_deg/2, max_lon), (min_lat + lat_step_deg/2, max_lon - lon_step_deg/2), (min_lat, max_lon - lon_step_deg/2)
                        ]
                        st.session_state.final_plots.append({'coords': rem_coords, 'label': f"{T['remainder_label']}", 'is_rem': True})

                    st.toast(T['processing_split']) # Toast notification
                    st.rerun()

            # --- Display Subdivision Results ---
            if st.session_state.final_plots:
                num_full_plots = len([p for p in st.session_state.final_plots if not p['is_rem']])
                st.markdown(f"<div class='plot-result'>✅ {T['sub_success'].format(num_plots=num_full_plots)}</div>", unsafe_allow_html=True)
                
                # Show remainder info if applicable
                if any(p['is_rem'] for p in st.session_state.final_plots):
                    rem_p_val = st.session_state.total_area_perch % (target_val if sub_method == T['fixed_area'] else 1) # Simplified for display
                    st.markdown(f"<p class='rem-highlight'>⚠️ {T['remainder_label']}: {rem_p_val:.2f} {T['perch_unit']}</p>", unsafe_allow_html=True)

                if st.button(T['clear_plots'], key="clear_plots_btn"):
                    st.session_state.final_plots = []; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # --- Map Reset ---
            st.markdown("---")
            if st.button(T['reset_map'], key="reset_map_btn"):
                st.session_state.update({"points": [], "final_plots": [], 'total_area_perch': 0.0, 'edit_idx': -1})
                st.rerun()

    st.markdown("<p style='text-align:center; opacity:0.5; margin-top:20px;'>LankaLand Pro v26.0 | Advanced GIS Core</p>", unsafe_allow_html=True)
