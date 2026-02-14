import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl, Draw
from shapely.geometry import Polygon, MultiPolygon, box, shape, Point
import math
import numpy as np
from datetime import datetime
import json

# --- Configuration & Styling ---
st.set_page_config(page_title="LankaLand Pro GIS | Enterprise", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(135deg, #0d47a1 0%, #1b5e20 100%); 
        padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; color: white;
    }
    .card { background: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
    .metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
    .plot-card { background: #252a33; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #4caf50; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; background: #2e7d32 !important; 
        font-weight: 800; color: white !important;
    }
    .warning-box { background: #ff9800; color: black; padding: 10px; border-radius: 8px; margin: 10px 0; font-weight: 600; }
    .success-box { background: #4caf50; color: white; padding: 10px; border-radius: 8px; margin: 10px 0; font-weight: 600; }
    .coord-display { background: #1a1f2e; padding: 8px; border-radius: 6px; font-family: monospace; font-size: 11px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'lang' not in st.session_state: st.session_state.lang = None
if 'method' not in st.session_state: st.session_state.method = None
if 'points' not in st.session_state: st.session_state.points = []
if 'final_plots' not in st.session_state: st.session_state.final_plots = []
if 'orientation' not in st.session_state: st.session_state.orientation = "vertical"
if 'history' not in st.session_state: st.session_state.history = []
if 'price_per_perch' not in st.session_state: st.session_state.price_per_perch = 0.0
if 'project_name' not in st.session_state: st.session_state.project_name = f"Project_{datetime.now().strftime('%Y%m%d_%H%M')}"

# --- Calculations ---
def get_distance_meters(p1, p2):
    """Haversine formula භාවිතා කරලා දුර ගණනය කරනවා"""
    try:
        R = 6371000
        lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))
    except Exception as e:
        st.error(f"Distance calculation error: {e}")
        return 0.0

def calculate_detailed_area(coords):
    """වර්ගඵලය සහ වටප්‍රමාණය ගණනය කරනවා"""
    if len(coords) < 3: return 0.0, 0.0
    try:
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)  # Fix invalid polygons
        avg_lat = math.radians(coords[0][0])
        area_m2 = poly.area * (111319.9 ** 2) * abs(math.cos(avg_lat))
        perimeter = sum(get_distance_meters(coords[i], coords[(i+1)%len(coords)]) for i in range(len(coords)))
        return area_m2 / 25.29, perimeter
    except Exception as e:
        st.error(f"Area calculation error: {e}")
        return 0.0, 0.0

def calculate_plot_center(coords):
    """කට්ටියේ මධ්‍ය ලක්ෂ්‍යය සොයනවා"""
    try:
        poly = Polygon(coords)
        centroid = poly.centroid
        return (centroid.y, centroid.x)
    except:
        return (coords[0][0], coords[0][1])

def format_currency(amount):
    """මුදල් format කරනවා"""
    if amount >= 10000000:  # 1 කෝටිය
        return f"රු. {amount/10000000:.2f} කෝටි"
    elif amount >= 100000:  # 1 ලක්ෂය
        return f"රු. {amount/100000:.2f} ලක්ෂ"
    else:
        return f"රු. {amount:,.2f}"

def export_project_data():
    """Project data JSON format එකට export කරනවා"""
    try:
        data = {
            "project_name": st.session_state.project_name,
            "timestamp": datetime.now().isoformat(),
            "language": st.session_state.lang,
            "main_boundary": st.session_state.points,
            "plots": st.session_state.final_plots,
            "orientation": st.session_state.orientation,
            "price_per_perch": st.session_state.price_per_perch,
            "total_area_perch": calculate_detailed_area(st.session_state.points)[0]
        }
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Export error: {e}"

# --- Language Dictionary ---
texts = {
    "si": {
        "title": "🌍 LANKALAND PRO GIS | Enterprise",
        "subtitle": "ජාත්‍යන්තර ප්‍රමිතියේ යටිතල පහසුකම් සහ ඉඩම් සැලසුම්කරණය",
        "manual": "🗺️ සිතියම මත සලකුණු කිරීම",
        "gps": "🛰️ GPS මගින් ඇවිද ගොස් මැනීම",
        "analytics": "📊 මැනුම් වාර්තාව",
        "subdivision": "🏗️ කට්ටි කිරීමේ එන්ජිම",
        "execute": "🚀 කට්ටි කර පෙන්වන්න",
        "reset": "🗑️ සියල්ල මකන්න",
        "val_p": "පර්චසයක මිල (රු.):",
        "mark_gps": "📍 ස්ථානය සලකුණු කරන්න",
        "undo": "↩️ අවසන් ලක්ෂ්‍යය මකන්න",
        "total_area": "මුළු වර්ගඵලය",
        "perimeter": "වටප්‍රමාණය",
        "remainder": "ඉතිරිය",
        "plot": "කට්ටිය",
        "total_value": "මුළු වටිනාකම",
        "export": "📥 Project Data Export කරන්න",
        "project_name": "Project නම",
        "coords": "GPS ඛණ්ඩාංක",
        "points_marked": "සලකුණු කළ ලක්ෂ්‍ය",
        "plot_details": "කට්ටි විස්තර"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS | Enterprise",
        "subtitle": "International Infrastructure & Land Planning",
        "manual": "🗺️ MANUAL MARKING",
        "gps": "🛰️ LIVE GPS SURVEY",
        "analytics": "📊 SURVEY ANALYTICS",
        "subdivision": "🏗️ SUBDIVISION ENGINE",
        "execute": "🚀 EXECUTE SPLIT",
        "reset": "🗑️ RESET ALL",
        "val_p": "Value per Perch (Rs.):",
        "mark_gps": "📍 MARK LOCATION",
        "undo": "UNDO LAST",
        "total_area": "Total Area",
        "perimeter": "Perimeter",
        "remainder": "Remainder",
        "plot": "Plot",
        "total_value": "Total Value",
        "export": "📥 Export Project Data",
        "project_name": "Project Name",
        "coords": "GPS Coordinates",
        "points_marked": "Points Marked",
        "plot_details": "Plot Details"
    }
}

# --- Main App Logic ---
if st.session_state.lang is None:
    st.markdown("<div class='main-header'><h1>🗺️ LANKALAND PRO GIS</h1><h3>භාෂාව තෝරන්න / Select Language</h3></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🇱🇰 සිංහල", use_container_width=True): 
        st.session_state.lang = "si"
        st.rerun()
    if c2.button("🌐 ENGLISH", use_container_width=True): 
        st.session_state.lang = "en"
        st.rerun()
else:
    T = texts[st.session_state.lang]
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        if st.button("🔙 Main Menu", use_container_width=True):
            st.session_state.update({"method": None, "points": [], "final_plots": [], "history": []})
            st.rerun()
        
        st.markdown("---")
        st.session_state.project_name = st.text_input(T['project_name'], st.session_state.project_name)
        st.session_state.price_per_perch = st.number_input(T['val_p'], min_value=0.0, value=st.session_state.price_per_perch, step=10000.0)
        
        if st.session_state.points:
            st.markdown(f"**{T['points_marked']}:** {len(st.session_state.points)}")
            
        if st.session_state.final_plots:
            st.markdown(f"**{T['plot_details']}:** {len(st.session_state.final_plots)} plots")

    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button(T['manual'], use_container_width=True): 
            st.session_state.method = "manual"
            st.rerun()
        if col2.button(T['gps'], use_container_width=True): 
            st.session_state.method = "gps"
            st.rerun()
    else:
        col_map, col_tools = st.columns([2.5, 1])

        with col_map:
            try:
                m = folium.Map(
                    location=[7.8731, 80.7718], 
                    zoom_start=19, 
                    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                    attr="Google Satellite"
                )
                
                LocateControl(auto_start=(st.session_state.method == "gps")).add_to(m)
                Draw(
                    export=True, 
                    draw_options={
                        'polyline': {'shapeOptions': {'color': '#ff5722', 'weight': 8}}, 
                        'circle': False, 
                        'marker': True
                    }
                ).add_to(m)
                Fullscreen().add_to(m)
                MeasureControl().add_to(m)

                # 1. පවතින කට්ටි අඳින්න (වර්ණ කේතයක් සමඟ)
                colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4', '#FFEB3B', '#795548']
                for idx, item in enumerate(st.session_state.final_plots):
                    color = colors[idx % len(colors)]
                    area_p, _ = calculate_detailed_area(item['coords'])
                    value = area_p * st.session_state.price_per_perch
                    
                    folium.Polygon(
                        locations=item['coords'], 
                        color=color, 
                        weight=3, 
                        fill=True, 
                        fill_opacity=0.4,
                        popup=f"<b>Plot #{idx+1}</b><br>Area: {area_p:.2f} P<br>Value: {format_currency(value)}"
                    ).add_to(m)
                    
                    # Plot number label
                    center = calculate_plot_center(item['coords'])
                    folium.Marker(
                        center, 
                        icon=folium.DivIcon(
                            html=f'<div style="font-size:14pt; font-weight:bold; color:white; background:{color}; padding:5px; border-radius:50%; width:30px; height:30px; text-align:center;">{idx+1}</div>'
                        )
                    ).add_to(m)

                # 2. ප්‍රධාන ඉඩම් මායිම අඳින්න
                if len(st.session_state.points) >= 2:
                    folium.Polygon(
                        locations=st.session_state.points, 
                        color="yellow", 
                        weight=4, 
                        fill=False
                    ).add_to(m)
                    
                    # දුර ලේබල්
                    for i in range(len(st.session_state.points)):
                        p1, p2 = st.session_state.points[i], st.session_state.points[(i+1)%len(st.session_state.points)]
                        mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]
                        dist = get_distance_meters(p1, p2)
                        folium.Marker(
                            mid, 
                            icon=folium.DivIcon(
                                html=f'<div style="font-size:9pt; color:white; background:rgba(0,0,0,0.8); padding:4px; border-radius:4px; font-weight:bold;">{dist:.1f}m</div>'
                            )
                        ).add_to(m)

                # 3. Point markers with labels
                for i, p in enumerate(st.session_state.points):
                    folium.Marker(
                        location=p, 
                        draggable=True, 
                        icon=folium.Icon(color="green", icon="info-sign"),
                        popup=f"Point {i+1}<br>Lat: {p[0]:.6f}<br>Lon: {p[1]:.6f}"
                    ).add_to(m)

                map_data = st_folium(m, height=650, width="100%", key="main_map")

                # Click කර ලක්ෂ්‍ය එකතු කිරීම (Manual mode එකේදී පමණයි)
                if map_data and map_data.get('last_clicked') and st.session_state.method == "manual":
                    new_point = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                    if new_point not in st.session_state.points:
                        st.session_state.points.append(new_point)
                        st.session_state.history.append(("add_point", new_point))
                        st.rerun()

            except Exception as e:
                st.error(f"Map rendering error: {e}")

        with col_tools:
            # Analytics Card
            st.markdown(f"<div class='card'><h3>{T['analytics']}</h3>", unsafe_allow_html=True)
            
            if len(st.session_state.points) >= 3:
                area_p, peri_m = calculate_detailed_area(st.session_state.points)
                total_value = area_p * st.session_state.price_per_perch
                
                st.markdown(f"{T['total_area']}: <span class='metric-val'>{area_p:.2f} P</span>", unsafe_allow_html=True)
                st.markdown(f"<small>({area_p * 25.29:.2f} m²)</small>", unsafe_allow_html=True)
                st.markdown(f"{T['perimeter']}: <span class='metric-val' style='color:#ffa726'>{peri_m:.1f} m</span>", unsafe_allow_html=True)
                
                if st.session_state.price_per_perch > 0:
                    st.markdown(f"{T['total_value']}: <span class='metric-val' style='color:#66bb6a'>{format_currency(total_value)}</span>", unsafe_allow_html=True)
            else:
                st.info("අවම වශයෙන් ලක්ෂ්‍ය 3ක් සලකුණු කරන්න" if st.session_state.lang == "si" else "Mark at least 3 points")
            
            st.markdown("</div>", unsafe_allow_html=True)

            # GPS Control (GPS Mode එකේදී පමණයි)
            if st.session_state.method == "gps":
                st.markdown(f"<div class='card'><h3>🛰️ GPS CONTROL</h3>", unsafe_allow_html=True)
                if st.button(T['mark_gps'], use_container_width=True):
                    if map_data and map_data.get('last_clicked'):
                        new_point = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                        st.session_state.points.append(new_point)
                        st.session_state.history.append(("add_point", new_point))
                        st.rerun()
                    else:
                        st.warning("Map click කරන්න")
                        
                if st.button(T['undo'], use_container_width=True):
                    if st.session_state.points: 
                        removed = st.session_state.points.pop()
                        st.session_state.history.append(("remove_point", removed))
                        st.rerun()
                    else:
                        st.warning("Points නෑ")
                st.markdown("</div>", unsafe_allow_html=True)

            # Subdivision Card
            st.markdown(f"<div class='card'><h3>{T['subdivision']}</h3>", unsafe_allow_html=True)
            
            if len(st.session_state.points) >= 3:
                target = st.number_input("Target Perch (P)", min_value=1.0, value=10.0, step=0.5)
                
                c1, c2 = st.columns(2)
                vert_active = "🟢" if st.session_state.orientation == "vertical" else ""
                horz_active = "🟢" if st.session_state.orientation == "horizontal" else ""
                
                if c1.button(f"{vert_active} සිරස්", use_container_width=True): 
                    st.session_state.orientation = "vertical"
                    st.rerun()
                if c2.button(f"{horz_active} තිරස්", use_container_width=True): 
                    st.session_state.orientation = "horizontal"
                    st.rerun()

                if st.button(T['execute'], use_container_width=True):
                    try:
                        area_p, _ = calculate_detailed_area(st.session_state.points)
                        
                        if area_p < target:
                            st.error(f"මුළු වර්ගඵලය ({area_p:.2f} P) target එකට වඩා අඩුයි!")
                        else:
                            main_poly = Polygon(st.session_state.points)
                            if not main_poly.is_valid:
                                main_poly = main_poly.buffer(0)
                            
                            min_lat, min_lon, max_lat, max_lon = main_poly.bounds
                            num = max(1, int(area_p // target))
                            st.session_state.final_plots = []
                            
                            if st.session_state.orientation == "vertical":
                                cuts = np.linspace(min_lon, max_lon, num + 1)
                                for i in range(len(cuts)-1):
                                    blade = box(min_lat-0.01, cuts[i], max_lat+0.01, cuts[i+1])
                                    intersect = main_poly.intersection(blade)
                                    if not intersect.is_empty:
                                        if isinstance(intersect, Polygon): 
                                            st.session_state.final_plots.append({'coords': list(intersect.exterior.coords)})
                                        elif isinstance(intersect, MultiPolygon):
                                            for part in intersect.geoms: 
                                                st.session_state.final_plots.append({'coords': list(part.exterior.coords)})
                            else:
                                cuts = np.linspace(min_lat, max_lat, num + 1)
                                for i in range(len(cuts)-1):
                                    blade = box(cuts[i], min_lon-0.01, cuts[i+1], max_lon+0.01)
                                    intersect = main_poly.intersection(blade)
                                    if not intersect.is_empty:
                                        if isinstance(intersect, Polygon): 
                                            st.session_state.final_plots.append({'coords': list(intersect.exterior.coords)})
                                        elif isinstance(intersect, MultiPolygon):
                                            for part in intersect.geoms: 
                                                st.session_state.final_plots.append({'coords': list(part.exterior.coords)})
                            
                            st.rerun()
                    except Exception as e:
                        st.error(f"Subdivision error: {e}")

                if st.session_state.final_plots:
                    rem = area_p % target
                    st.markdown(f"<div class='success-box'>කට්ටි ගණන: {len(st.session_state.final_plots)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='warning-box'>{T['remainder']}: {rem:.2f} P ({rem*25.29:.1f} m²)</div>", unsafe_allow_html=True)
                    
                    # Individual plot details
                    with st.expander("📋 සියලු කට්ටි විස්තර"):
                        for idx, plot in enumerate(st.session_state.final_plots):
                            plot_area, plot_peri = calculate_detailed_area(plot['coords'])
                            plot_value = plot_area * st.session_state.price_per_perch
                            st.markdown(f"""
                            <div class='plot-card'>
                                <b>Plot #{idx+1}</b><br>
                                Area: {plot_area:.2f} P ({plot_area*25.29:.1f} m²)<br>
                                Perimeter: {plot_peri:.1f} m<br>
                                Value: {format_currency(plot_value)}
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("ප්‍රථමයෙන් ඉඩම් මායිම සලකුණු කරන්න")

            if st.button(T['reset'], use_container_width=True):
                st.session_state.update({"points": [], "final_plots": [], "history": []})
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Export functionality
            if st.session_state.points or st.session_state.final_plots:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                if st.button(T['export'], use_container_width=True):
                    json_data = export_project_data()
                    st.download_button(
                        label="💾 Download JSON",
                        data=json_data,
                        file_name=f"{st.session_state.project_name}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Coordinates display
            if st.session_state.points:
                with st.expander("🗺️ GPS Coordinates"):
                    st.markdown("<div class='coord-display'>", unsafe_allow_html=True)
                    for i, p in enumerate(st.session_state.points):
                        st.text(f"P{i+1}: {p[0]:.6f}, {p[1]:.6f}")
                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; opacity:0.3; margin-top:30px;'>🌍 LankaLand Pro Enterprise v4.0 | Enhanced Edition</p>", unsafe_allow_html=True)
