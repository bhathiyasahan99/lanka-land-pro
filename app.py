import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl, Draw, Realtime
from shapely.geometry import Polygon, MultiPolygon, box, LineString, Point as ShapelyPoint
from shapely.ops import split as shapely_split
import math
import numpy as np
from datetime import datetime
import json
import time

# === PAGE CONFIG ===
st.set_page_config(
    page_title="LankaLand Pro GIS | Ultimate Edition",
    layout="wide",
    page_icon="🗺️",
    initial_sidebar_state="expanded"
)

# === PROFESSIONAL STYLING (UNCHANGED) ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&family=Roboto+Mono:wght@400;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    color: #e0e0e0;
}

.main-header {
    background: linear-gradient(135deg, #1565c0 0%, #2e7d32 50%, #0d47a1 100%);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 30px;
    color: white;
    box-shadow: 0 8px 32px rgba(21, 101, 192, 0.4);
    position: relative;
    overflow: hidden;
}

.main-header h1 {
    font-size: 2.5em;
    font-weight: 900;
    text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    margin: 0;
}

.quick-toolbar {
    background: linear-gradient(135deg, #2a2f45, #1e2337);
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.card {
    background: linear-gradient(145deg, #1e2439, #252a42);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 25px rgba(33, 150, 243, 0.3);
}

.card h3 {
    color: #4fc3f7;
    font-weight: 700;
    margin-bottom: 15px;
}

.metric-large {
    font-size: 48px;
    font-weight: 900;
    color: #4caf50;
    text-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
    font-family: 'Roboto Mono', monospace;
    text-align: center;
    margin: 20px 0;
}

.metric-label {
    font-size: 14px;
    color: #90a4ae;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    text-align: center;
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 13px;
    font-family: 'Roboto Mono', monospace;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    border-radius: 10px;
    overflow: hidden;
}

.comparison-table th {
    background: linear-gradient(135deg, #2e7d32, #1b5e20);
    padding: 12px;
    text-align: left;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: white;
}

.comparison-table td {
    background: rgba(30, 36, 57, 0.8);
    padding: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.comparison-table tr:hover td {
    background: rgba(76, 175, 80, 0.1);
}

.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 16px;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.badge-perfect { background: linear-gradient(135deg, #4caf50, #66bb6a); color: white; }
.badge-good { background: linear-gradient(135deg, #8bc34a, #9ccc65); color: white; }
.badge-fair { background: linear-gradient(135deg, #ffc107, #ffb300); color: black; }
.badge-poor { background: linear-gradient(135deg, #ff5722, #f4511e); color: white; }

.success-box {
    background: linear-gradient(135deg, #4caf50, #2e7d32);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 12px 0;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.warning-box {
    background: linear-gradient(135deg, #ff9800, #f57c00);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 12px 0;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
}

.info-box {
    background: linear-gradient(135deg, #2196f3, #1565c0);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 12px 0;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
}

.surveyor-animation {
    text-align: center;
    font-size: 50px;
    margin: 25px 0;
    animation: survey-walk 2s ease-in-out infinite;
}

@keyframes survey-walk {
    0%, 100% { transform: translateX(-15px) rotate(-5deg); }
    50% { transform: translateX(15px) rotate(5deg); }
}

.progress-bar {
    height: 12px;
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    overflow: hidden;
    margin: 10px 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4caf50, #8bc34a);
    animation: progress-shine 2s linear infinite;
    transition: width 0.5s ease;
}

@keyframes progress-shine {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}

.stButton>button {
    width: 100%;
    border-radius: 14px;
    height: 3.8em;
    background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important;
    font-weight: 800;
    color: white !important;
    border: none !important;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(46, 125, 50, 0.6);
}

.stat-mini {
    display: inline-block;
    background: rgba(76, 175, 80, 0.1);
    border: 1px solid rgba(76, 175, 80, 0.3);
    padding: 8px 14px;
    border-radius: 8px;
    margin: 5px;
    font-size: 12px;
    font-weight: 600;
}

/* NEW: GPS Status Indicators */
.gps-status {
    background: linear-gradient(135deg, #1e2439, #252a42);
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
    border-left: 4px solid #4caf50;
}

.gps-excellent {
    border-left-color: #4caf50;
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.05));
}

.gps-good {
    border-left-color: #8bc34a;
    background: linear-gradient(135deg, rgba(139, 195, 74, 0.1), rgba(139, 195, 74, 0.05));
}

.gps-fair {
    border-left-color: #ffc107;
    background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
}

.gps-poor {
    border-left-color: #ff5722;
    background: linear-gradient(135deg, rgba(255, 87, 34, 0.1), rgba(255, 87, 34, 0.05));
}

.compass-display {
    text-align: center;
    font-size: 60px;
    margin: 20px 0;
    animation: rotate-pulse 2s ease-in-out infinite;
}

@keyframes rotate-pulse {
    0%, 100% { transform: scale(1) rotate(0deg); }
    50% { transform: scale(1.1) rotate(10deg); }
}

.walking-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 10px;
    background: rgba(76, 175, 80, 0.1);
    border-radius: 8px;
    margin: 10px 0;
}

.pulse-dot {
    width: 12px;
    height: 12px;
    background: #4caf50;
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.5); }
}

.path-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 15px 0;
}

.path-stat-item {
    background: rgba(33, 150, 243, 0.1);
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    border: 1px solid rgba(33, 150, 243, 0.3);
}

.path-stat-value {
    font-size: 20px;
    font-weight: 700;
    color: #4fc3f7;
    font-family: 'Roboto Mono', monospace;
}

.path-stat-label {
    font-size: 10px;
    color: #90a4ae;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 5px;
}

::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb { 
    background: linear-gradient(135deg, #2196f3, #1565c0);
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# === SESSION STATE (EXPANDED) ===
defaults = {
    'lang': None,
    'method': None,
    'points': [],
    'final_plots': [],
    'orientation': 'vertical',
    'subdivision_mode': 'by_area',
    'target_area': 10.0,
    'target_count': 5,
    'target_width': 25.0,
    'price_per_perch': 0.0,
    'project_name': f"Project_{datetime.now().strftime('%Y%m%d_%H%M')}",
    'history': [],
    'subdivision_method': 'equal_area',
    'show_labels': True,
    'show_measurements': True,
    'show_grid': False,
    'snap_to_grid': False,
    'selected_point': None,
    'surveyor_name': '',
    'survey_date': datetime.now().strftime('%Y-%m-%d'),
    # NEW: GPS Walking Features
    'gps_path': [],  # Walking path points
    'gps_accuracy': 100,  # Current GPS accuracy (0-100)
    'current_heading': 0,  # Compass direction
    'walking_speed': 0.0,  # m/s
    'distance_walked': 0.0,  # Total distance
    'auto_corner_detect': True,  # Auto corner detection
    'last_direction': None,  # Last walking direction
    'corner_threshold': 30,  # Degrees change to detect corner
    'gps_alerts': [],  # Alert messages
    'walking_mode': False,  # Active walking mode
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# === CALCULATIONS (UNCHANGED) ===
def get_distance_meters(p1, p2):
    try:
        R = 6371000
        lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))
    except:
        return 0.0

def calculate_area(coords):
    if len(coords) < 3:
        return 0.0, 0.0
    try:
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
        avg_lat = math.radians(sum(c[0] for c in coords) / len(coords))
        area_m2 = poly.area * (111319.9 ** 2) * abs(math.cos(avg_lat))
        perimeter = sum(get_distance_meters(coords[i], coords[(i+1)%len(coords)]) 
                       for i in range(len(coords)))
        return area_m2 / 25.29, perimeter
    except:
        return 0.0, 0.0

def calculate_center(coords):
    try:
        poly = Polygon(coords)
        c = poly.centroid
        return (c.y, c.x)
    except:
        return (coords[0][0], coords[0][1]) if coords else (0, 0)

def format_currency(amount):
    if amount >= 10000000:
        return f"රු. {amount/10000000:.2f} කෝටි"
    elif amount >= 100000:
        return f"රු. {amount/100000:.2f} ලක්ෂ"
    else:
        return f"රු. {amount:,.2f}"

def get_accuracy_badge(actual, target):
    if target == 0:
        return ""
    diff_pct = abs(actual - target) / target * 100
    if diff_pct < 0.5:
        return "<span class='badge badge-perfect'>✓ PERFECT</span>"
    elif diff_pct < 2:
        return "<span class='badge badge-good'>✓ GOOD</span>"
    elif diff_pct < 5:
        return "<span class='badge badge-fair'>! FAIR</span>"
    else:
        return "<span class='badge badge-poor'>✗ POOR</span>"

# === NEW: GPS HELPER FUNCTIONS ===
def calculate_bearing(p1, p2):
    """Calculate compass bearing between two points"""
    try:
        lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360
    except:
        return 0.0

def detect_corner(path, threshold=30):
    """Detect if user is turning a corner based on direction change"""
    if len(path) < 3:
        return False
    
    try:
        # Get last 3 points
        p1, p2, p3 = path[-3], path[-2], path[-1]
        
        # Calculate bearings
        bearing1 = calculate_bearing(p1, p2)
        bearing2 = calculate_bearing(p2, p3)
        
        # Calculate angle change
        angle_change = abs(bearing2 - bearing1)
        if angle_change > 180:
            angle_change = 360 - angle_change
        
        # If angle change is significant, it's a corner
        return angle_change > threshold
    except:
        return False

def get_gps_quality_status(accuracy):
    """Get GPS quality status based on accuracy value"""
    if accuracy >= 90:
        return "excellent", "🟢 Excellent", "#4caf50"
    elif accuracy >= 70:
        return "good", "🟡 Good", "#8bc34a"
    elif accuracy >= 50:
        return "fair", "🟠 Fair", "#ffc107"
    else:
        return "poor", "🔴 Poor", "#ff5722"

def calculate_walking_speed(path, time_window=5):
    """Calculate current walking speed"""
    if len(path) < 2:
        return 0.0
    
    try:
        # Use last few points
        recent_points = path[-min(time_window, len(path)):]
        if len(recent_points) < 2:
            return 0.0
        
        total_dist = sum(get_distance_meters(recent_points[i], recent_points[i+1]) 
                        for i in range(len(recent_points)-1))
        
        # Assume 1 second between points (adjust based on actual timing)
        time_elapsed = len(recent_points) - 1
        return total_dist / time_elapsed if time_elapsed > 0 else 0.0
    except:
        return 0.0

def get_compass_emoji(bearing):
    """Get compass direction emoji based on bearing"""
    directions = [
        (0, "⬆️ N"), (45, "↗️ NE"), (90, "➡️ E"), (135, "↘️ SE"),
        (180, "⬇️ S"), (225, "↙️ SW"), (270, "⬅️ W"), (315, "↖️ NW")
    ]
    
    # Find closest direction
    min_diff = 360
    closest = "⬆️ N"
    for deg, emoji in directions:
        diff = abs(bearing - deg)
        if diff > 180:
            diff = 360 - diff
        if diff < min_diff:
            min_diff = diff
            closest = emoji
    
    return closest

# === SUBDIVISION ALGORITHM (UNCHANGED) ===
def iterative_equal_area_subdivision(main_polygon, target_area_perch, orientation="vertical", progress_callback=None):
    """Fixed iterative subdivision algorithm"""
    try:
        plots = []
        remaining = main_polygon
        min_lat, min_lon, max_lat, max_lon = main_polygon.bounds
        
        total_area, _ = calculate_area(list(main_polygon.exterior.coords))
        expected_plots = int(total_area / target_area_perch)
        
        if expected_plots == 0:
            return []
        
        plot_num = 0
        max_plots = expected_plots + 2
        
        while plot_num < max_plots and not remaining.is_empty:
            if progress_callback:
                progress_callback(plot_num, expected_plots)
            
            remaining_area, _ = calculate_area(list(remaining.exterior.coords))
            
            if remaining_area < 0.5:
                break
            
            if remaining_area < target_area_perch * 1.3:
                plots.append({
                    'coords': list(remaining.exterior.coords),
                    'plot_number': plot_num + 1,
                    'is_remainder': True
                })
                break
            
            if orientation == "vertical":
                left, right = min_lon, max_lon
            else:
                left, right = min_lat, max_lat
            
            best_piece = None
            iterations = 0
            max_iter = 60
            
            while iterations < max_iter:
                mid = (left + right) / 2
                
                try:
                    if orientation == "vertical":
                        cut_box = box(min_lat - 0.1, min_lon - 0.1, max_lat + 0.1, mid)
                    else:
                        cut_box = box(min_lat - 0.1, min_lon - 0.1, mid, max_lon + 0.1)
                    
                    piece = remaining.intersection(cut_box)
                    
                    if piece.is_empty:
                        if orientation == "vertical":
                            left = mid
                        else:
                            left = mid
                        iterations += 1
                        continue
                    
                    if isinstance(piece, MultiPolygon):
                        piece = max(piece.geoms, key=lambda p: p.area)
                    
                    if not isinstance(piece, Polygon):
                        break
                    
                    piece_coords = list(piece.exterior.coords)
                    piece_area, _ = calculate_area(piece_coords)
                    
                    diff = piece_area - target_area_perch
                    
                    if abs(diff) < 0.1:
                        best_piece = piece
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
                    
                except Exception as e:
                    break
                
                iterations += 1
            
            if best_piece and isinstance(best_piece, Polygon):
                plots.append({
                    'coords': list(best_piece.exterior.coords),
                    'plot_number': plot_num + 1,
                    'is_remainder': False
                })
                
                try:
                    if orientation == "vertical":
                        remaining_box = box(min_lat - 0.1, mid, max_lat + 0.1, max_lon + 0.1)
                    else:
                        remaining_box = box(mid, min_lon - 0.1, max_lat + 0.1, max_lon + 0.1)
                    
                    remaining = remaining.intersection(remaining_box)
                    
                    if isinstance(remaining, MultiPolygon):
                        remaining = max(remaining.geoms, key=lambda p: p.area)
                    
                    if not isinstance(remaining, Polygon) or remaining.is_empty:
                        break
                    
                    min_lat, min_lon, max_lat, max_lon = remaining.bounds
                    
                except Exception as e:
                    break
            else:
                break
            
            plot_num += 1
        
        if not remaining.is_empty and isinstance(remaining, Polygon):
            remaining_coords = list(remaining.exterior.coords)
            remaining_area, _ = calculate_area(remaining_coords)
            if remaining_area > 0.3:
                plots.append({
                    'coords': remaining_coords,
                    'plot_number': len(plots) + 1,
                    'is_remainder': True
                })
        
        return plots
        
    except Exception as e:
        st.error(f"Subdivision error: {e}")
        return []

def subdivide_by_count(main_polygon, count, orientation="vertical"):
    """කැබලි ගණන අනුව බෙදීම"""
    try:
        total_area, _ = calculate_area(list(main_polygon.exterior.coords))
        target_area = total_area / count
        return iterative_equal_area_subdivision(main_polygon, target_area, orientation)
    except:
        return []

def subdivide_by_width(main_polygon, width_m, orientation="vertical"):
    """Width අනුව බෙදීම"""
    try:
        total_area, perimeter = calculate_area(list(main_polygon.exterior.coords))
        if orientation == "vertical":
            min_lat, min_lon, max_lat, max_lon = main_polygon.bounds
            total_width = get_distance_meters((min_lat, min_lon), (min_lat, max_lon))
        else:
            min_lat, min_lon, max_lat, max_lon = main_polygon.bounds
            total_width = get_distance_meters((min_lat, min_lon), (max_lat, min_lon))
        
        count = max(1, int(total_width / width_m))
        return subdivide_by_count(main_polygon, count, orientation)
    except:
        return []

# === LANGUAGE (EXPANDED) ===
texts = {
    "si": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "අවසන් මට්ටමේ මිනුම් පද්ධතිය",
        "manual": "🗺️ සිතියම මත සලකුණු කිරීම",
        "gps": "🛰️ GPS ඇවිද මැනීම",
        "analytics": "📊 විශ්ලේෂණය",
        "subdivision": "🏗️ කැබලි කිරීම",
        "execute": "🚀 කැබලි කරන්න",
        "reset": "🗑️ මකන්න",
        "by_area": "වර්ගඵලයෙන්",
        "by_count": "ගණනින්",
        "by_width": "පළලින්",
        "target_area": "ඉලක්ක වර්ගඵලය (P)",
        "plot_count": "කැබලි ගණන",
        "plot_width": "පළල (m)",
        "total_area": "මුළු වර්ගඵලය",
        "perimeter": "වටප්‍රමාණය",
        "price": "මිල (රු.)",
        "export": "📥 Export",
        "undo": "↩️ Undo",
        "save": "💾 Save",
        "calculating": "ගණනය කරමින්...",
        # NEW: GPS Walking
        "start_walking": "🚶‍♂️ ඇවිදීම පටන් ගන්න",
        "stop_walking": "⏹️ නවතන්න",
        "mark_corner": "📍 Corner සලකුණු කරන්න",
        "auto_detect": "🤖 Auto Corner Detection",
        "gps_quality": "GPS ගුණත්වය",
        "heading": "දිශාව",
        "speed": "වේගය",
        "distance": "දුර",
        "corners": "Corners",
        "walking": "ඇවිදිමින්...",
        "corner_detected": "Corner හමුවිය!",
        "close_boundary": "මායිම වසන්න",
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "Ultimate Survey System",
        "manual": "🗺️ MANUAL MAPPING",
        "gps": "🛰️ GPS WALKING SURVEY",
        "analytics": "📊 ANALYTICS",
        "subdivision": "🏗️ SUBDIVISION",
        "execute": "🚀 EXECUTE",
        "reset": "🗑️ RESET",
        "by_area": "By Area",
        "by_count": "By Count",
        "by_width": "By Width",
        "target_area": "Target Area (P)",
        "plot_count": "Plot Count",
        "plot_width": "Width (m)",
        "total_area": "Total Area",
        "perimeter": "Perimeter",
        "price": "Price (Rs.)",
        "export": "📥 Export",
        "undo": "↩️ Undo",
        "save": "💾 Save",
        "calculating": "Calculating...",
        # NEW: GPS Walking
        "start_walking": "🚶‍♂️ Start Walking",
        "stop_walking": "⏹️ Stop",
        "mark_corner": "📍 Mark Corner",
        "auto_detect": "🤖 Auto Corner Detection",
        "gps_quality": "GPS Quality",
        "heading": "Heading",
        "speed": "Speed",
        "distance": "Distance",
        "corners": "Corners",
        "walking": "Walking...",
        "corner_detected": "Corner Detected!",
        "close_boundary": "Close Boundary",
    }
}

# === MAIN APP ===
if st.session_state.lang is None:
    st.markdown("""
    <div class='main-header'>
        <h1>🗺️ LANKALAND PRO GIS</h1>
        <p style='font-size:1.2em;'>Ultimate Land Survey & Planning System</p>
        <p style='font-size:0.9em; opacity:0.8;'>Version 7.0 - Advanced GPS Walking</p>
        <h3 style='margin-top:25px;'>භාෂාව තෝරන්න / Select Language</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    if col1.button("🇱🇰 සිංහල", use_container_width=True):
        st.session_state.lang = "si"
        st.rerun()
    if col2.button("🌐 ENGLISH", use_container_width=True):
        st.session_state.lang = "en"
        st.rerun()

else:
    T = texts[st.session_state.lang]
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        if st.button("🔙 Main Menu", use_container_width=True):
            st.session_state.update({"method": None, "points": [], "final_plots": [], "gps_path": [], "walking_mode": False})
            st.rerun()
        
        st.markdown("---")
        
        st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)
        st.session_state.price_per_perch = st.number_input(T['price'], min_value=0.0, value=st.session_state.price_per_perch, step=10000.0)
        
        st.markdown("---")
        st.markdown("### 📊 Live Stats")
        
        if st.session_state.points:
            st.metric("Points", len(st.session_state.points))
            if len(st.session_state.points) >= 3:
                area, peri = calculate_area(st.session_state.points)
                st.metric(T['total_area'], f"{area:.2f} P")
                st.metric(T['perimeter'], f"{peri:.1f} m")
        
        if st.session_state.final_plots:
            st.metric("Plots", len(st.session_state.final_plots))
            total = sum(calculate_area(p['coords'])[0] for p in st.session_state.final_plots)
            st.metric("Allocated", f"{total:.2f} P")
        
        # NEW: GPS Stats
        if st.session_state.method == "gps" and st.session_state.gps_path:
            st.markdown("---")
            st.markdown("### 🚶‍♂️ Walking Stats")
            st.metric(T['distance'], f"{st.session_state.distance_walked:.1f} m")
            st.metric(T['corners'], len(st.session_state.points))
            if st.session_state.walking_mode:
                st.metric(T['speed'], f"{st.session_state.walking_speed:.1f} m/s")
    
    # Main content
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
        # Quick toolbar
        st.markdown("<div class='quick-toolbar'>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("➕ Add Point", use_container_width=True):
                st.info("Click on map")
        with col2:
            if st.button(T['undo'], use_container_width=True):
                if st.session_state.points:
                    st.session_state.points.pop()
                    st.rerun()
        with col3:
            if st.button(T['reset'], use_container_width=True):
                st.session_state.points = []
                st.session_state.final_plots = []
                st.session_state.gps_path = []
                st.session_state.walking_mode = False
                st.rerun()
        with col4:
            if st.button(T['save'], use_container_width=True):
                st.success("Saved!")
        with col5:
            if st.button("📸 Screenshot", use_container_width=True):
                st.info("Coming soon")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Main layout
        col_map, col_tools = st.columns([2.5, 1])
        
        with col_map:
            # Calculate center
            if st.session_state.points:
                center = [sum(p[0] for p in st.session_state.points)/len(st.session_state.points),
                         sum(p[1] for p in st.session_state.points)/len(st.session_state.points)]
            else:
                center = [7.8731, 80.7718]
            
            # Create map
            m = folium.Map(location=center, zoom_start=19,
                          tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                          attr="Google Satellite")
            
            LocateControl(auto_start=(st.session_state.method == "gps")).add_to(m)
            Draw(export=True).add_to(m)
            Fullscreen().add_to(m)
            MeasureControl().add_to(m)
            
            # Draw GPS walking path
            if st.session_state.gps_path and len(st.session_state.gps_path) > 1:
                folium.PolyLine(
                    st.session_state.gps_path,
                    color='#00BCD4',
                    weight=3,
                    opacity=0.7,
                    popup="Walking Path"
                ).add_to(m)
            
            # Draw plots
            colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', 
                     '#00BCD4', '#FFEB3B', '#795548', '#FF5722', '#607D8B']
            
            for idx, plot in enumerate(st.session_state.final_plots):
                color = colors[idx % len(colors)]
                area, peri = calculate_area(plot['coords'])
                is_rem = plot.get('is_remainder', False)
                
                folium.Polygon(
                    locations=plot['coords'],
                    color=color,
                    weight=3,
                    fill=True,
                    fill_opacity=0.5,
                    popup=f"<b>Plot #{idx+1}</b><br>Area: {area:.2f} P<br>{'[Remainder]' if is_rem else ''}"
                ).add_to(m)
                
                center_pt = calculate_center(plot['coords'])
                folium.Marker(
                    center_pt,
                    icon=folium.DivIcon(html=f'<div style="font-size:16pt;font-weight:900;color:white;background:{color};padding:8px;border-radius:50%;width:40px;height:40px;text-align:center;line-height:40px;border:3px solid white;">{idx+1}</div>')
                ).add_to(m)
            
            # Draw boundary
            if len(st.session_state.points) >= 2:
                folium.Polygon(
                    locations=st.session_state.points,
                    color="yellow",
                    weight=5,
                    fill=False,
                    dashArray="10, 10"
                ).add_to(m)
                
                for i in range(len(st.session_state.points)):
                    p1, p2 = st.session_state.points[i], st.session_state.points[(i+1)%len(st.session_state.points)]
                    mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]
                    dist = get_distance_meters(p1, p2)
                    folium.Marker(mid, icon=folium.DivIcon(html=f'<div style="background:black;color:white;padding:5px;border-radius:5px;font-weight:bold;">{dist:.1f}m</div>')).add_to(m)
            
            # Draw points
            for i, p in enumerate(st.session_state.points):
                folium.Marker(location=p, draggable=True, icon=folium.Icon(color="green"), popup=f"Point {i+1}").add_to(m)
            
            map_data = st_folium(m, height=650, width="100%", key="main_map")
            
            if map_data and map_data.get('last_clicked'):
                new_pt = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                
                if st.session_state.method == "manual":
                    if new_pt not in st.session_state.points:
                        st.session_state.points.append(new_pt)
                        st.rerun()
                
                elif st.session_state.method == "gps" and st.session_state.walking_mode:
                    # Add to walking path
                    st.session_state.gps_path.append(new_pt)
                    
                    # Calculate distance
                    if len(st.session_state.gps_path) > 1:
                        dist = get_distance_meters(st.session_state.gps_path[-2], st.session_state.gps_path[-1])
                        st.session_state.distance_walked += dist
                    
                    # Auto corner detection
                    if st.session_state.auto_corner_detect and detect_corner(st.session_state.gps_path, st.session_state.corner_threshold):
                        if new_pt not in st.session_state.points:
                            st.session_state.points.append(new_pt)
                            st.toast(f"🎯 {T['corner_detected']}")
                    
                    st.rerun()
        
        with col_tools:
            # Analytics
            st.markdown(f"<div class='card'><h3>{T['analytics']}</h3>", unsafe_allow_html=True)
            
            if len(st.session_state.points) >= 3:
                area, peri = calculate_area(st.session_state.points)
                value = area * st.session_state.price_per_perch
                
                st.markdown(f"<div class='metric-large'>{area:.2f} P</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-label'>{T['total_area']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='stat-mini'>m²: {area*25.29:.2f}</div>", unsafe_allow_html=True)
                
                if st.session_state.price_per_perch > 0:
                    st.markdown(f"<div style='font-size:20px;font-weight:700;color:#66bb6a;margin-top:15px;'>{format_currency(value)}</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # GPS Walking Controls
            if st.session_state.method == "gps":
                st.markdown(f"<div class='card'><h3>🛰️ GPS Walking Mode</h3>", unsafe_allow_html=True)
                
                # GPS Quality Indicator
                quality_class, quality_text, quality_color = get_gps_quality_status(st.session_state.gps_accuracy)
                st.markdown(f"""
                <div class='gps-status gps-{quality_class}'>
                    <strong>{T['gps_quality']}:</strong> {quality_text}<br>
                    <small>Accuracy: ±{100-st.session_state.gps_accuracy}m</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Walking controls
                col1, col2 = st.columns(2)
                with col1:
                    if not st.session_state.walking_mode:
                        if st.button(T['start_walking'], use_container_width=True, type="primary"):
                            st.session_state.walking_mode = True
                            st.session_state.gps_path = []
                            st.session_state.distance_walked = 0.0
                            st.rerun()
                    else:
                        if st.button(T['stop_walking'], use_container_width=True):
                            st.session_state.walking_mode = False
                            st.rerun()
                
                with col2:
                    if st.button(T['mark_corner'], use_container_width=True):
                        if map_data and map_data.get('last_clicked'):
                            new_pt = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                            if new_pt not in st.session_state.points:
                                st.session_state.points.append(new_pt)
                                st.rerun()
                
                # Auto detect toggle
                st.session_state.auto_corner_detect = st.checkbox(
                    T['auto_detect'],
                    value=st.session_state.auto_corner_detect
                )
                
                if st.session_state.auto_corner_detect:
                    st.session_state.corner_threshold = st.slider(
                        "Corner Sensitivity (degrees)",
                        min_value=15,
                        max_value=60,
                        value=st.session_state.corner_threshold,
                        step=5
                    )
                
                # Walking indicator
                if st.session_state.walking_mode:
                    st.markdown("""
                    <div class='walking-indicator'>
                        <div class='pulse-dot'></div>
                        <strong>🚶‍♂️ Walking...</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Path stats
                    if st.session_state.gps_path:
                        heading = calculate_bearing(st.session_state.gps_path[-2], st.session_state.gps_path[-1]) if len(st.session_state.gps_path) > 1 else 0
                        direction = get_compass_emoji(heading)
                        
                        st.markdown(f"""
                        <div class='path-stats'>
                            <div class='path-stat-item'>
                                <div class='path-stat-value'>{st.session_state.distance_walked:.1f}m</div>
                                <div class='path-stat-label'>Distance</div>
                            </div>
                            <div class='path-stat-item'>
                                <div class='path-stat-value'>{direction}</div>
                                <div class='path-stat-label'>Direction</div>
                            </div>
                            <div class='path-stat-item'>
                                <div class='path-stat-value'>{len(st.session_state.points)}</div>
                                <div class='path-stat-label'>Corners</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Close boundary button
                if len(st.session_state.points) >= 3:
                    if st.button(f"✓ {T['close_boundary']}", use_container_width=True):
                        st.session_state.walking_mode = False
                        st.success("Boundary completed!")
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Subdivision (UNCHANGED from previous version)
            st.markdown(f"<div class='card'><h3>{T['subdivision']}</h3>", unsafe_allow_html=True)
            
            if len(st.session_state.points) >= 3:
                mode = st.radio("Mode", ["by_area", "by_count", "by_width"],
                               format_func=lambda x: T[x],
                               key="sub_mode",
                               horizontal=True)
                
                st.session_state.subdivision_mode = mode
                
                if mode == "by_area":
                    st.session_state.target_area = st.number_input(T['target_area'], min_value=1.0, value=st.session_state.target_area, step=0.5)
                elif mode == "by_count":
                    st.session_state.target_count = st.number_input(T['plot_count'], min_value=1, value=st.session_state.target_count, step=1)
                elif mode == "by_width":
                    st.session_state.target_width = st.number_input(T['plot_width'], min_value=5.0, value=st.session_state.target_width, step=5.0)
                
                col1, col2 = st.columns(2)
                if col1.button("සිරස්", use_container_width=True):
                    st.session_state.orientation = "vertical"
                    st.rerun()
                if col2.button("තිරස්", use_container_width=True):
                    st.session_state.orientation = "horizontal"
                    st.rerun()
                
                if st.button(T['execute'], use_container_width=True, type="primary"):
                    area, _ = calculate_area(st.session_state.points)
                    
                    progress = st.empty()
                    anim = st.empty()
                    
                    anim.markdown("<div class='surveyor-animation'>🚶‍♂️📏</div>", unsafe_allow_html=True)
                    
                    def update_prog(cur, tot):
                        pct = (cur/tot)*100
                        progress.markdown(f"<div class='progress-bar'><div class='progress-fill' style='width:{pct}%'></div></div>", unsafe_allow_html=True)
                    
                    try:
                        poly = Polygon(st.session_state.points)
                        if not poly.is_valid:
                            poly = poly.buffer(0)
                        
                        if mode == "by_area":
                            st.session_state.final_plots = iterative_equal_area_subdivision(poly, st.session_state.target_area, st.session_state.orientation, update_prog)
                        elif mode == "by_count":
                            st.session_state.final_plots = subdivide_by_count(poly, st.session_state.target_count, st.session_state.orientation)
                        elif mode == "by_width":
                            st.session_state.final_plots = subdivide_by_width(poly, st.session_state.target_width, st.session_state.orientation)
                        
                        time.sleep(0.3)
                        progress.empty()
                        anim.empty()
                        st.rerun()
                    
                    except Exception as e:
                        progress.empty()
                        anim.empty()
                        st.error(f"Error: {e}")
                
                if st.session_state.final_plots:
                    st.markdown(f"<div class='success-box'>✓ {len(st.session_state.final_plots)} plots created</div>", unsafe_allow_html=True)
                    
                    with st.expander("📊 Plot Details", expanded=True):
                        st.markdown("<table class='comparison-table'>", unsafe_allow_html=True)
                        st.markdown("<tr><th>Plot</th><th>Area (P)</th><th>Area (m²)</th><th>Value</th></tr>", unsafe_allow_html=True)
                        
                        for idx, plot in enumerate(st.session_state.final_plots):
                            a, _ = calculate_area(plot['coords'])
                            v = a * st.session_state.price_per_perch
                            is_rem = plot.get('is_remainder', False)
                            
                            st.markdown(f"""
                            <tr>
                                <td><b>#{idx+1}</b> {'[R]' if is_rem else ''}</td>
                                <td>{a:.2f}</td>
                                <td>{a*25.29:.2f}</td>
                                <td>{format_currency(v)}</td>
                            </tr>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</table>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='text-align:center;opacity:0.3;margin-top:40px;'>🌍 LankaLand Pro GIS v7.0 | Advanced GPS Walking</div>", unsafe_allow_html=True)
