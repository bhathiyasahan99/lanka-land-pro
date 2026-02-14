import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl, Draw
from shapely.geometry import Polygon, MultiPolygon, box, shape, Point, LineString
from shapely.ops import split
import math
import numpy as np
from datetime import datetime
import json
import time

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
        box-shadow: 0 4px 20px rgba(13, 71, 161, 0.3);
    }
    .card { 
        background: #1d2129; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #30363d; 
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .metric-val { font-size: 24px; font-weight: 800; color: #4caf50; }
    .plot-card { 
        background: #252a33; 
        padding: 12px; 
        border-radius: 8px; 
        margin: 8px 0; 
        border-left: 4px solid #4caf50;
        transition: all 0.3s ease;
    }
    .plot-card:hover { 
        background: #2d323d; 
        transform: translateX(5px);
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background: #2e7d32 !important; 
        font-weight: 800; 
        color: white !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #1b5e20 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4);
    }
    .warning-box { 
        background: #ff9800; 
        color: black; 
        padding: 10px; 
        border-radius: 8px; 
        margin: 10px 0; 
        font-weight: 600;
    }
    .success-box { 
        background: #4caf50; 
        color: white; 
        padding: 10px; 
        border-radius: 8px; 
        margin: 10px 0; 
        font-weight: 600;
    }
    .error-box {
        background: #f44336;
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        font-weight: 600;
    }
    .coord-display { 
        background: #1a1f2e; 
        padding: 8px; 
        border-radius: 6px; 
        font-family: monospace; 
        font-size: 11px; 
        margin-top: 10px;
    }
    .surveyor-animation {
        text-align: center;
        font-size: 40px;
        animation: walk 2s infinite;
        margin: 20px 0;
    }
    @keyframes walk {
        0%, 100% { transform: translateX(-10px); }
        50% { transform: translateX(10px); }
    }
    .progress-bar {
        height: 8px;
        background: #1a1f2e;
        border-radius: 4px;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4caf50, #8bc34a);
        transition: width 0.3s ease;
    }
    .accuracy-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
        margin-left: 8px;
    }
    .badge-perfect { background: #4caf50; color: white; }
    .badge-good { background: #8bc34a; color: white; }
    .badge-fair { background: #ffc107; color: black; }
    .badge-poor { background: #ff5722; color: white; }
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 12px;
    }
    .comparison-table th {
        background: #2e7d32;
        padding: 8px;
        text-align: left;
    }
    .comparison-table td {
        background: #1d2129;
        padding: 8px;
        border-bottom: 1px solid #30363d;
    }
    .stat-mini {
        display: inline-block;
        background: #252a33;
        padding: 5px 10px;
        border-radius: 6px;
        margin: 3px;
        font-size: 11px;
    }
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
if 'subdivision_method' not in st.session_state: st.session_state.subdivision_method = "equal_area"
if 'show_cutting_lines' not in st.session_state: st.session_state.show_cutting_lines = True

# --- Advanced Calculations ---
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
            poly = poly.buffer(0)
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
    if amount >= 10000000:
        return f"රු. {amount/10000000:.2f} කෝටි"
    elif amount >= 100000:
        return f"රු. {amount/100000:.2f} ලක්ෂ"
    else:
        return f"රු. {amount:,.2f}"

def get_accuracy_badge(actual, target):
    """නිවැරදිතා මට්ටම ලකුණු කරනවා"""
    if target == 0:
        return ""
    diff_percent = abs(actual - target) / target * 100
    if diff_percent < 1:
        return "<span class='accuracy-badge badge-perfect'>✓ Perfect</span>"
    elif diff_percent < 3:
        return "<span class='accuracy-badge badge-good'>✓ Good</span>"
    elif diff_percent < 5:
        return "<span class='accuracy-badge badge-fair'>! Fair</span>"
    else:
        return "<span class='accuracy-badge badge-poor'>✗ Poor</span>"

# --- ACCURATE SUBDIVISION ALGORITHM ---
def accurate_subdivision(main_polygon, target_area_perch, orientation="vertical", progress_callback=None):
    """
    නිවැරදි කට්ටි කිරීමේ algorithm - binary search භාවිතා කරනවා
    """
    try:
        plots = []
        remaining = main_polygon
        min_lat, min_lon, max_lat, max_lon = main_polygon.bounds
        
        total_area_perch, _ = calculate_detailed_area(list(main_polygon.exterior.coords))
        num_plots = int(total_area_perch / target_area_perch)
        
        for plot_num in range(num_plots):
            if progress_callback:
                progress_callback(plot_num, num_plots)
            
            if remaining.is_empty or remaining.area < 0.00001:
                break
            
            # Binary search හරහා නිවැරදි cutting position එක සොයනවා
            if orientation == "vertical":
                left, right = min_lon, max_lon
            else:
                left, right = min_lat, max_lat
            
            best_cut = None
            tolerance = 0.000001  # GPS accuracy
            max_iterations = 50
            
            for iteration in range(max_iterations):
                mid = (left + right) / 2
                
                # Cutting line එක හදනවා
                if orientation == "vertical":
                    cut_line = LineString([(mid, min_lat - 1), (mid, max_lat + 1)])
                else:
                    cut_line = LineString([(min_lon - 1, mid), (max_lon + 1, mid)])
                
                # කට්ටිය කපනවා
                try:
                    # Extended box for cutting
                    if orientation == "vertical":
                        left_box = box(min_lat - 1, min_lon - 1, max_lat + 1, mid)
                    else:
                        left_box = box(min_lat - 1, min_lon - 1, mid, max_lon + 1)
                    
                    piece = remaining.intersection(left_box)
                    
                    if piece.is_empty:
                        if orientation == "vertical":
                            left = mid
                        else:
                            left = mid
                        continue
                    
                    # Area check කරනවා
                    if isinstance(piece, (Polygon, MultiPolygon)):
                        if isinstance(piece, MultiPolygon):
                            # Largest piece එක ගන්නවා
                            piece = max(piece.geoms, key=lambda p: p.area)
                        
                        piece_coords = list(piece.exterior.coords)
                        piece_area, _ = calculate_detailed_area(piece_coords)
                        
                        diff = piece_area - target_area_perch
                        
                        if abs(diff) < 0.05:  # 0.05 perch tolerance
                            best_cut = piece
                            break
                        elif diff > 0:
                            if orientation == "vertical":
                                right = mid
                            else:
                                right = mid
                        else:
                            if orientation == "vertical":
                                left = mid
                            else:
                                left = mid
                    else:
                        break
                        
                except Exception as e:
                    break
            
            # Best cut එක save කරනවා
            if best_cut and isinstance(best_cut, Polygon):
                plots.append({
                    'coords': list(best_cut.exterior.coords),
                    'plot_number': plot_num + 1
                })
                
                # Remaining area update කරනවා
                try:
                    if orientation == "vertical":
                        remaining_box = box(min_lat - 1, mid, max_lat + 1, max_lon + 1)
                    else:
                        remaining_box = box(mid, min_lon - 1, max_lat + 1, max_lon + 1)
                    remaining = remaining.intersection(remaining_box)
                    
                    if isinstance(remaining, MultiPolygon):
                        remaining = max(remaining.geoms, key=lambda p: p.area)
                except:
                    break
        
        # Remaining area එකත් add කරනවා (ඉතිරිය)
        if not remaining.is_empty and isinstance(remaining, Polygon):
            remaining_coords = list(remaining.exterior.coords)
            remaining_area, _ = calculate_detailed_area(remaining_coords)
            if remaining_area > 0.5:  # 0.5 perch ට වඩා වැඩි නම් විතරක්
                plots.append({
                    'coords': remaining_coords,
                    'plot_number': len(plots) + 1,
                    'is_remainder': True
                })
        
        return plots
        
    except Exception as e:
        st.error(f"Subdivision error: {e}")
        return []

def export_project_data():
    """Project data JSON format එකට export කරනවා"""
    try:
        # Plot details with actual measurements
        plot_details = []
        for plot in st.session_state.final_plots:
            area_p, peri = calculate_detailed_area(plot['coords'])
            plot_details.append({
                'plot_number': plot.get('plot_number', 0),
                'area_perch': round(area_p, 2),
                'area_sqm': round(area_p * 25.29, 2),
                'perimeter_m': round(peri, 2),
                'coordinates': plot['coords'],
                'is_remainder': plot.get('is_remainder', False)
            })
        
        data = {
            "project_name": st.session_state.project_name,
            "timestamp": datetime.now().isoformat(),
            "language": st.session_state.lang,
            "main_boundary": st.session_state.points,
            "total_area_perch": round(calculate_detailed_area(st.session_state.points)[0], 2),
            "plots": plot_details,
            "orientation": st.session_state.orientation,
            "subdivision_method": st.session_state.subdivision_method,
            "price_per_perch": st.session_state.price_per_perch,
            "total_plots": len(st.session_state.final_plots)
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
        "execute": "🚀 නිවැරදිව කට්ටි කරන්න",
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
        "plot_details": "කට්ටි විස්තර",
        "calculating": "ගණනය කරමින්...",
        "surveying": "මැනුම් කරමින්...",
        "accuracy": "නිවැරදිතාව",
        "target": "ඉලක්කය",
        "actual": "ඇත්ත",
        "difference": "වෙනස",
        "method": "ක්‍රමය"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS | Enterprise",
        "subtitle": "International Infrastructure & Land Planning",
        "manual": "🗺️ MANUAL MARKING",
        "gps": "🛰️ LIVE GPS SURVEY",
        "analytics": "📊 SURVEY ANALYTICS",
        "subdivision": "🏗️ SUBDIVISION ENGINE",
        "execute": "🚀 EXECUTE ACCURATE SPLIT",
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
        "plot_details": "Plot Details",
        "calculating": "Calculating...",
        "surveying": "Surveying...",
        "accuracy": "Accuracy",
        "target": "Target",
        "actual": "Actual",
        "difference": "Difference",
        "method": "Method"
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
        
        # Subdivision method selection
        st.markdown("#### " + T['method'])
        st.session_state.subdivision_method = st.radio(
            "",
            ["equal_area", "simple"],
            format_func=lambda x: "🎯 Accurate (Binary Search)" if x == "equal_area" else "⚡ Simple (Fast)",
            index=0 if st.session_state.subdivision_method == "equal_area" else 1
        )
        
        st.session_state.show_cutting_lines = st.checkbox("Show Cutting Lines", value=st.session_state.show_cutting_lines)
        
        if st.session_state.points:
            st.markdown(f"**{T['points_marked']}:** {len(st.session_state.points)}")
            
        if st.session_state.final_plots:
            st.markdown(f"**{T['plot_details']}:** {len(st.session_state.final_plots)} plots")
            total_area = sum(calculate_detailed_area(p['coords'])[0] for p in st.session_state.final_plots)
            st.markdown(f"**Total Area:** {total_area:.2f} P")

    if st.session_state.method is None:
        st.markdown(f"<div class='main-header'><h1>{T['title']}</h1><p>{T['subtitle']}</p></div>", unsafe_allow_html=True)
        
        # Feature highlights
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class='card' style='text-align:center;'>
                <h2>🎯</h2>
                <h4>Accurate Subdivision</h4>
                <p style='font-size:12px;'>Binary search algorithm for precise plot division</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='card' style='text-align:center;'>
                <h2>📊</h2>
                <h4>Real-time Analytics</h4>
                <p style='font-size:12px;'>Live area calculations with accuracy metrics</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class='card' style='text-align:center;'>
                <h2>🗺️</h2>
                <h4>GPS Integration</h4>
                <p style='font-size:12px;'>Walk-and-mark with satellite imagery</p>
            </div>
            """, unsafe_allow_html=True)
        
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
                # Map center එක calculate කරනවා
                if st.session_state.points:
                    center_lat = sum(p[0] for p in st.session_state.points) / len(st.session_state.points)
                    center_lon = sum(p[1] for p in st.session_state.points) / len(st.session_state.points)
                    map_center = [center_lat, center_lon]
                else:
                    map_center = [7.8731, 80.7718]
                
                m = folium.Map(
                    location=map_center, 
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

                # කට්ටි අඳින්න (වර්ණ කේතයක් සමඟ)
                colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4', '#FFEB3B', '#795548', '#FF5722', '#607D8B']
                for idx, item in enumerate(st.session_state.final_plots):
                    color = colors[idx % len(colors)]
                    area_p, peri = calculate_detailed_area(item['coords'])
                    value = area_p * st.session_state.price_per_perch
                    is_remainder = item.get('is_remainder', False)
                    
                    folium.Polygon(
                        locations=item['coords'], 
                        color=color, 
                        weight=3, 
                        fill=True, 
                        fill_opacity=0.5,
                        popup=f"<b>{'Remainder' if is_remainder else f'Plot #{idx+1}'}</b><br>Area: {area_p:.2f} P<br>Perimeter: {peri:.1f} m<br>Value: {format_currency(value)}"
                    ).add_to(m)
                    
                    # Plot label
                    center = calculate_plot_center(item['coords'])
                    label = "R" if is_remainder else str(idx+1)
                    folium.Marker(
                        center, 
                        icon=folium.DivIcon(
                            html=f'<div style="font-size:14pt; font-weight:bold; color:white; background:{color}; padding:5px; border-radius:50%; width:35px; height:35px; text-align:center; line-height:35px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">{label}</div>'
                        )
                    ).add_to(m)

                # ප්‍රධාන මායිම අඳින්න
                if len(st.session_state.points) >= 2:
                    folium.Polygon(
                        locations=st.session_state.points, 
                        color="yellow", 
                        weight=5, 
                        fill=False,
                        dashArray="10, 10"
                    ).add_to(m)
                    
                    # දුර ලේබල්
                    for i in range(len(st.session_state.points)):
                        p1, p2 = st.session_state.points[i], st.session_state.points[(i+1)%len(st.session_state.points)]
                        mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]
                        dist = get_distance_meters(p1, p2)
                        folium.Marker(
                            mid, 
                            icon=folium.DivIcon(
                                html=f'<div style="font-size:10pt; color:white; background:rgba(0,0,0,0.8); padding:5px; border-radius:5px; font-weight:bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">{dist:.1f}m</div>'
                            )
                        ).add_to(m)

                # Point markers
                for i, p in enumerate(st.session_state.points):
                    folium.Marker(
                        location=p, 
                        draggable=True, 
                        icon=folium.Icon(color="green", icon="info-sign", prefix='fa'),
                        popup=f"<b>Point {i+1}</b><br>Lat: {p[0]:.6f}<br>Lon: {p[1]:.6f}"
                    ).add_to(m)

                map_data = st_folium(m, height=650, width="100%", key="main_map")

                # Click කර ලක්ෂ්‍ය එකතු කිරීම
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
                st.markdown(f"<span class='stat-mini'>({area_p * 25.29:.2f} m²)</span>", unsafe_allow_html=True)
                st.markdown(f"{T['perimeter']}: <span class='metric-val' style='color:#ffa726'>{peri_m:.1f} m</span>", unsafe_allow_html=True)
                
                if st.session_state.price_per_perch > 0:
                    st.markdown(f"{T['total_value']}: <span class='metric-val' style='color:#66bb6a'>{format_currency(total_value)}</span>", unsafe_allow_html=True)
            else:
                st.info("අවම වශයෙන් ලක්ෂ්‍ය 3ක් සලකුණු කරන්න" if st.session_state.lang == "si" else "Mark at least 3 points")
            
            st.markdown("</div>", unsafe_allow_html=True)

            # GPS Control
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
                target = st.number_input("Target Perch (P)", min_value=1.0, value=10.0, step=0.5, key="target_input")
                
                c1, c2 = st.columns(2)
                vert_active = "🟢" if st.session_state.orientation == "vertical" else ""
                horz_active = "🟢" if st.session_state.orientation == "horizontal" else ""
                
                if c1.button(f"{vert_active} සිරස්", use_container_width=True): 
                    st.session_state.orientation = "vertical"
                    st.rerun()
                if c2.button(f"{horz_active} තිරස්", use_container_width=True): 
                    st.session_state.orientation = "horizontal"
                    st.rerun()

                if st.button(T['execute'], use_container_width=True, type="primary"):
                    area_p, _ = calculate_detailed_area(st.session_state.points)
                    
                    if area_p < target:
                        st.error(f"මුළු වර්ගඵලය ({area_p:.2f} P) target එකට වඩා අඩුයි!")
                    else:
                        # Animation placeholder
                        progress_placeholder = st.empty()
                        surveyor_placeholder = st.empty()
                        
                        # Surveyor animation
                        surveyor_placeholder.markdown("<div class='surveyor-animation'>🚶‍♂️📏</div>", unsafe_allow_html=True)
                        
                        def update_progress(current, total):
                            progress = (current / total) * 100
                            progress_placeholder.markdown(f"""
                            <div style='margin: 10px 0;'>
                                <small>{T['calculating']} {current}/{total}</small>
                                <div class='progress-bar'>
                                    <div class='progress-fill' style='width: {progress}%'></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        try:
                            main_poly = Polygon(st.session_state.points)
                            if not main_poly.is_valid:
                                main_poly = main_poly.buffer(0)
                            
                            if st.session_state.subdivision_method == "equal_area":
                                # Accurate subdivision
                                st.session_state.final_plots = accurate_subdivision(
                                    main_poly, 
                                    target, 
                                    st.session_state.orientation,
                                    update_progress
                                )
                            else:
                                # Simple subdivision (original method)
                                min_lat, min_lon, max_lat, max_lon = main_poly.bounds
                                num = max(1, int(area_p // target))
                                st.session_state.final_plots = []
                                
                                if st.session_state.orientation == "vertical":
                                    cuts = np.linspace(min_lon, max_lon, num + 1)
                                    for i in range(len(cuts)-1):
                                        update_progress(i, num)
                                        blade = box(min_lat-0.01, cuts[i], max_lat+0.01, cuts[i+1])
                                        intersect = main_poly.intersection(blade)
                                        if not intersect.is_empty:
                                            if isinstance(intersect, Polygon): 
                                                st.session_state.final_plots.append({'coords': list(intersect.exterior.coords), 'plot_number': i+1})
                                            elif isinstance(intersect, MultiPolygon):
                                                for part in intersect.geoms: 
                                                    st.session_state.final_plots.append({'coords': list(part.exterior.coords), 'plot_number': i+1})
                                else:
                                    cuts = np.linspace(min_lat, max_lat, num + 1)
                                    for i in range(len(cuts)-1):
                                        update_progress(i, num)
                                        blade = box(cuts[i], min_lon-0.01, cuts[i+1], max_lon+0.01)
                                        intersect = main_poly.intersection(blade)
                                        if not intersect.is_empty:
                                            if isinstance(intersect, Polygon): 
                                                st.session_state.final_plots.append({'coords': list(intersect.exterior.coords), 'plot_number': i+1})
                                            elif isinstance(intersect, MultiPolygon):
                                                for part in intersect.geoms: 
                                                    st.session_state.final_plots.append({'coords': list(part.exterior.coords), 'plot_number': i+1})
                            
                            time.sleep(0.5)
                            progress_placeholder.empty()
                            surveyor_placeholder.empty()
                            st.rerun()
                            
                        except Exception as e:
                            progress_placeholder.empty()
                            surveyor_placeholder.empty()
                            st.error(f"Subdivision error: {e}")

                # Results display
                if st.session_state.final_plots:
                    area_p, _ = calculate_detailed_area(st.session_state.points)
                    total_plots_area = sum(calculate_detailed_area(p['coords'])[0] for p in st.session_state.final_plots)
                    
                    st.markdown(f"<div class='success-box'>✓ කට්ටි ගණන: {len(st.session_state.final_plots)}</div>", unsafe_allow_html=True)
                    
                    # Accuracy comparison table
                    with st.expander("📊 Accuracy Report", expanded=True):
                        st.markdown("<table class='comparison-table'>", unsafe_allow_html=True)
                        st.markdown("<tr><th>Plot</th><th>Target</th><th>Actual</th><th>Diff</th><th>Status</th></tr>", unsafe_allow_html=True)
                        
                        for idx, plot in enumerate(st.session_state.final_plots):
                            plot_area, _ = calculate_detailed_area(plot['coords'])
                            is_remainder = plot.get('is_remainder', False)
                            diff = plot_area - target
                            diff_percent = (diff / target * 100) if target > 0 else 0
                            badge = get_accuracy_badge(plot_area, target) if not is_remainder else ""
                            
                            label = "Remainder" if is_remainder else f"#{idx+1}"
                            target_display = "-" if is_remainder else f"{target:.2f} P"
                            
                            st.markdown(f"""
                            <tr>
                                <td><b>{label}</b></td>
                                <td>{target_display}</td>
                                <td>{plot_area:.2f} P</td>
                                <td style='color: {"#4caf50" if abs(diff) < 0.5 else "#ff9800"}'>{diff:+.2f} P</td>
                                <td>{badge if not is_remainder else "Remainder"}</td>
                            </tr>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</table>", unsafe_allow_html=True)
                        
                        # Overall statistics
                        st.markdown(f"""
                        <div style='margin-top: 15px; padding: 10px; background: #252a33; border-radius: 8px;'>
                            <small><b>සාරාංශය / Summary:</b></small><br>
                            <span class='stat-mini'>Original: {area_p:.2f} P</span>
                            <span class='stat-mini'>Allocated: {total_plots_area:.2f} P</span>
                            <span class='stat-mini'>Difference: {abs(area_p - total_plots_area):.2f} P</span>
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

    st.markdown("<p style='text-align:center; opacity:0.3; margin-top:30px;'>🌍 LankaLand Pro Enterprise v5.0 | Accurate Subdivision Edition</p>", unsafe_allow_html=True)
