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
import base64
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="LankaLand Pro GIS | Professional Survey System", 
    layout="wide", 
    page_icon="🗺️",
    initial_sidebar_state="expanded"
)

# --- Professional Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&family=Roboto+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
    }
    
    .stApp { 
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        color: #e0e0e0;
    }
    
    /* Main Header - Ultra Professional */
    .main-header { 
        background: linear-gradient(135deg, #1565c0 0%, #2e7d32 50%, #0d47a1 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        color: white;
        box-shadow: 0 8px 32px rgba(21, 101, 192, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .main-header h1 {
        position: relative;
        z-index: 1;
        font-weight: 900;
        font-size: 2.5em;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        margin: 0;
    }
    
    .main-header p {
        position: relative;
        z-index: 1;
        font-size: 1.1em;
        opacity: 0.95;
        margin-top: 10px;
    }
    
    /* Professional Cards */
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
        box-shadow: 0 6px 25px rgba(21, 101, 192, 0.3);
        border-color: rgba(33, 150, 243, 0.3);
    }
    
    .card h3 {
        color: #4fc3f7;
        font-weight: 700;
        margin-bottom: 15px;
        font-size: 1.3em;
    }
    
    /* Metrics Display */
    .metric-val { 
        font-size: 28px;
        font-weight: 900;
        color: #4caf50;
        text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        font-family: 'Roboto Mono', monospace;
    }
    
    .metric-label {
        font-size: 13px;
        color: #90a4ae;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Plot Cards */
    .plot-card { 
        background: linear-gradient(135deg, #2a2f45, #1e2337);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #4caf50;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .plot-card:hover { 
        background: linear-gradient(135deg, #2d3348, #232844);
        transform: translateX(8px);
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    /* Buttons - Premium Design */
    .stButton>button { 
        width: 100%;
        border-radius: 14px;
        height: 3.8em;
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important;
        font-weight: 800;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 0.95em;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #1b5e20 0%, #0d3d16 100%) !important;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.6);
    }
    
    /* Status Boxes */
    .warning-box { 
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 12px 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
        border-left: 5px solid #f57c00;
    }
    
    .success-box { 
        background: linear-gradient(135deg, #4caf50, #2e7d32);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 12px 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        border-left: 5px solid #2e7d32;
    }
    
    .error-box {
        background: linear-gradient(135deg, #f44336, #c62828);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 12px 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
        border-left: 5px solid #c62828;
    }
    
    .info-box {
        background: linear-gradient(135deg, #2196f3, #1565c0);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 12px 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
        border-left: 5px solid #1565c0;
    }
    
    /* Surveyor Animation - Professional */
    .surveyor-animation {
        text-align: center;
        font-size: 50px;
        margin: 25px 0;
        animation: survey-walk 2.5s ease-in-out infinite;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));
    }
    
    @keyframes survey-walk {
        0%, 100% { transform: translateX(-15px) rotate(-5deg); }
        50% { transform: translateX(15px) rotate(5deg); }
    }
    
    /* Progress Bar - Modern */
    .progress-container {
        background: rgba(0,0,0,0.3);
        border-radius: 12px;
        padding: 15px;
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .progress-bar {
        height: 12px;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        overflow: hidden;
        margin: 10px 0;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.3);
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4caf50, #8bc34a, #4caf50);
        background-size: 200% 100%;
        animation: progress-shine 2s linear infinite;
        border-radius: 8px;
        transition: width 0.5s ease;
        box-shadow: 0 0 15px rgba(76, 175, 80, 0.6);
    }
    
    @keyframes progress-shine {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    /* Accuracy Badges - Professional */
    .accuracy-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 16px;
        font-size: 11px;
        font-weight: 800;
        margin-left: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .badge-perfect { 
        background: linear-gradient(135deg, #4caf50, #66bb6a);
        color: white;
        animation: pulse-perfect 2s ease-in-out infinite;
    }
    
    @keyframes pulse-perfect {
        0%, 100% { box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3); }
        50% { box-shadow: 0 2px 15px rgba(76, 175, 80, 0.6); }
    }
    
    .badge-good { 
        background: linear-gradient(135deg, #8bc34a, #9ccc65);
        color: white;
    }
    
    .badge-fair { 
        background: linear-gradient(135deg, #ffc107, #ffb300);
        color: #000;
    }
    
    .badge-poor { 
        background: linear-gradient(135deg, #ff5722, #f4511e);
        color: white;
    }
    
    /* Professional Table */
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
        font-size: 11px;
        color: white;
    }
    
    .comparison-table td {
        background: rgba(30, 36, 57, 0.8);
        padding: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        transition: background 0.3s ease;
    }
    
    .comparison-table tr:hover td {
        background: rgba(33, 150, 243, 0.1);
    }
    
    /* Statistics Mini Cards */
    .stat-mini {
        display: inline-block;
        background: linear-gradient(135deg, #2a2f45, #1e2337);
        padding: 8px 14px;
        border-radius: 8px;
        margin: 5px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .stat-mini strong {
        color: #4fc3f7;
    }
    
    /* Coordinate Display - Monospace Professional */
    .coord-display { 
        background: rgba(0,0,0,0.4);
        padding: 12px;
        border-radius: 8px;
        font-family: 'Roboto Mono', monospace;
        font-size: 11px;
        margin-top: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        max-height: 200px;
        overflow-y: auto;
    }
    
    .coord-display::-webkit-scrollbar {
        width: 6px;
    }
    
    .coord-display::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.2);
        border-radius: 4px;
    }
    
    .coord-display::-webkit-scrollbar-thumb {
        background: #2196f3;
        border-radius: 4px;
    }
    
    /* Feature Highlights */
    .feature-card {
        background: linear-gradient(145deg, #1e2439, #252a42);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3);
        border-color: rgba(33, 150, 243, 0.4);
    }
    
    .feature-card h2 {
        font-size: 3em;
        margin: 0;
    }
    
    .feature-card h4 {
        color: #4fc3f7;
        margin: 15px 0 10px 0;
    }
    
    .feature-card p {
        font-size: 13px;
        color: #b0bec5;
        line-height: 1.6;
    }
    
    /* Confidence Meter */
    .confidence-meter {
        background: rgba(0,0,0,0.3);
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .confidence-bar {
        height: 20px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        overflow: hidden;
        position: relative;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 700;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    }
    
    .confidence-high {
        background: linear-gradient(90deg, #4caf50, #66bb6a);
    }
    
    .confidence-medium {
        background: linear-gradient(90deg, #ff9800, #ffa726);
    }
    
    .confidence-low {
        background: linear-gradient(90deg, #f44336, #ef5350);
    }
    
    /* Compass Rose */
    .compass {
        text-align: center;
        font-size: 60px;
        animation: rotate-compass 10s linear infinite;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));
    }
    
    @keyframes rotate-compass {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Export Section */
    .export-card {
        background: linear-gradient(135deg, #1565c0, #0d47a1);
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 20px rgba(21, 101, 192, 0.4);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Measurement Tools */
    .tool-icon {
        font-size: 2em;
        margin: 10px;
        transition: transform 0.3s ease;
        cursor: pointer;
    }
    
    .tool-icon:hover {
        transform: scale(1.2) rotate(10deg);
    }
    
    /* Language Selector */
    .lang-button {
        background: linear-gradient(135deg, #2e7d32, #1b5e20);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .lang-button:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(46, 125, 50, 0.5);
        border-color: rgba(76, 175, 80, 0.5);
    }
    
    /* Professional Footer */
    .footer {
        text-align: center;
        opacity: 0.5;
        margin-top: 40px;
        padding: 20px;
        font-size: 12px;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        color: #4fc3f7;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.2);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2196f3, #1565c0);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1976d2, #0d47a1);
    }
    
    /* Loading Animation */
    .loading-spinner {
        text-align: center;
        font-size: 40px;
        animation: spin 2s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Elevation Badge */
    .elevation-badge {
        background: rgba(33, 150, 243, 0.2);
        border: 1px solid #2196f3;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 10px;
        display: inline-block;
        margin-left: 8px;
        color: #4fc3f7;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
default_states = {
    'lang': None,
    'method': None,
    'points': [],
    'final_plots': [],
    'orientation': 'vertical',
    'history': [],
    'price_per_perch': 0.0,
    'project_name': f"Project_{datetime.now().strftime('%Y%m%d_%H%M')}",
    'subdivision_method': 'equal_area',
    'show_cutting_lines': True,
    'confidence_level': 100,
    'last_calculation_time': 0,
    'measurement_notes': '',
    'surveyor_name': '',
    'survey_date': datetime.now().strftime('%Y-%m-%d')
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Advanced Calculations ---
def get_distance_meters(p1, p2):
    """Haversine formula - Professional surveyor-grade accuracy"""
    try:
        R = 6371000  # Earth radius in meters
        lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    except Exception as e:
        st.error(f"Distance calculation error: {e}")
        return 0.0

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

def calculate_detailed_area(coords):
    """වර්ගඵලය සහ වටප්‍රමාණය - Surveyor-grade precision"""
    if len(coords) < 3: 
        return 0.0, 0.0
    try:
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
        
        # More accurate area calculation using average latitude
        avg_lat = math.radians(sum(c[0] for c in coords) / len(coords))
        lat_factor = abs(math.cos(avg_lat))
        
        area_m2 = poly.area * (111319.9 ** 2) * lat_factor
        perimeter = sum(get_distance_meters(coords[i], coords[(i+1)%len(coords)]) 
                       for i in range(len(coords)))
        
        # Convert to perches (1 perch = 25.29 m²)
        area_perch = area_m2 / 25.29
        
        return area_perch, perimeter
    except Exception as e:
        st.error(f"Area calculation error: {e}")
        return 0.0, 0.0

def calculate_plot_center(coords):
    """කට්ටියේ මධ්‍ය ලක්ෂ්‍යය - Centroid calculation"""
    try:
        poly = Polygon(coords)
        centroid = poly.centroid
        return (centroid.y, centroid.x)
    except:
        if coords:
            return (coords[0][0], coords[0][1])
        return (0, 0)

def format_currency(amount):
    """මුදල් format කරනවා - Sri Lankan style"""
    if amount >= 10000000:
        return f"රු. {amount/10000000:.2f} කෝටි"
    elif amount >= 100000:
        return f"රු. {amount/100000:.2f} ලක්ෂ"
    else:
        return f"රු. {amount:,.2f}"

def get_accuracy_badge(actual, target):
    """නිවැරදිතා මට්ටම - Professional grading"""
    if target == 0:
        return ""
    diff_percent = abs(actual - target) / target * 100
    if diff_percent < 0.5:
        return "<span class='accuracy-badge badge-perfect'>✓ PERFECT</span>"
    elif diff_percent < 2:
        return "<span class='accuracy-badge badge-good'>✓ GOOD</span>"
    elif diff_percent < 5:
        return "<span class='accuracy-badge badge-fair'>! FAIR</span>"
    else:
        return "<span class='accuracy-badge badge-poor'>✗ POOR</span>"

def calculate_confidence_level(points, plots):
    """Measurement confidence calculator"""
    confidence = 100
    
    # Reduce confidence for few points
    if len(points) < 4:
        confidence -= 20
    
    # Reduce if plots have high variance
    if plots:
        areas = [calculate_detailed_area(p['coords'])[0] for p in plots if not p.get('is_remainder')]
        if areas and len(areas) > 1:
            variance = np.var(areas)
            if variance > 1.0:
                confidence -= min(30, int(variance * 10))
    
    return max(0, min(100, confidence))

# --- ACCURATE SUBDIVISION ALGORITHM ---
def accurate_subdivision(main_polygon, target_area_perch, orientation="vertical", progress_callback=None):
    """
    Professional subdivision algorithm with binary search
    Surveyor-grade accuracy: ±0.05 perch tolerance
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
            
            # Binary search for accurate cutting position
            if orientation == "vertical":
                left, right = min_lon, max_lon
            else:
                left, right = min_lat, max_lat
            
            best_cut = None
            tolerance = 0.000001
            max_iterations = 50
            
            for iteration in range(max_iterations):
                mid = (left + right) / 2
                
                # Create cutting line
                if orientation == "vertical":
                    cut_line = LineString([(mid, min_lat - 1), (mid, max_lat + 1)])
                else:
                    cut_line = LineString([(min_lon - 1, mid), (max_lon + 1, mid)])
                
                try:
                    # Cut the plot
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
                    
                    if isinstance(piece, (Polygon, MultiPolygon)):
                        if isinstance(piece, MultiPolygon):
                            piece = max(piece.geoms, key=lambda p: p.area)
                        
                        piece_coords = list(piece.exterior.coords)
                        piece_area, _ = calculate_detailed_area(piece_coords)
                        
                        diff = piece_area - target_area_perch
                        
                        if abs(diff) < 0.05:  # High precision tolerance
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
            
            # Save best cut
            if best_cut and isinstance(best_cut, Polygon):
                plots.append({
                    'coords': list(best_cut.exterior.coords),
                    'plot_number': plot_num + 1
                })
                
                # Update remaining area
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
        
        # Add remaining area
        if not remaining.is_empty and isinstance(remaining, Polygon):
            remaining_coords = list(remaining.exterior.coords)
            remaining_area, _ = calculate_detailed_area(remaining_coords)
            if remaining_area > 0.5:
                plots.append({
                    'coords': remaining_coords,
                    'plot_number': len(plots) + 1,
                    'is_remainder': True
                })
        
        return plots
        
    except Exception as e:
        st.error(f"Subdivision error: {e}")
        return []

def generate_survey_report():
    """Generate professional survey report data"""
    if not st.session_state.points:
        return None
    
    total_area, total_perimeter = calculate_detailed_area(st.session_state.points)
    
    report = {
        "project_info": {
            "name": st.session_state.project_name,
            "date": st.session_state.survey_date,
            "surveyor": st.session_state.surveyor_name or "Not specified",
            "method": "GPS Survey" if st.session_state.method == "gps" else "Manual Survey"
        },
        "measurements": {
            "total_area_perch": round(total_area, 2),
            "total_area_sqm": round(total_area * 25.29, 2),
            "total_perimeter_m": round(total_perimeter, 2),
            "boundary_points": len(st.session_state.points),
            "coordinates": st.session_state.points
        },
        "subdivision": {
            "method": st.session_state.subdivision_method,
            "orientation": st.session_state.orientation,
            "total_plots": len(st.session_state.final_plots),
            "plots": []
        },
        "valuation": {
            "price_per_perch": st.session_state.price_per_perch,
            "total_value": total_area * st.session_state.price_per_perch
        },
        "confidence": calculate_confidence_level(st.session_state.points, st.session_state.final_plots),
        "notes": st.session_state.measurement_notes
    }
    
    # Add plot details
    for plot in st.session_state.final_plots:
        area, perimeter = calculate_detailed_area(plot['coords'])
        report["subdivision"]["plots"].append({
            "number": plot.get('plot_number', 0),
            "area_perch": round(area, 2),
            "area_sqm": round(area * 25.29, 2),
            "perimeter_m": round(perimeter, 2),
            "value": round(area * st.session_state.price_per_perch, 2),
            "is_remainder": plot.get('is_remainder', False)
        })
    
    return report

def export_project_data():
    """Export comprehensive project data"""
    report = generate_survey_report()
    if report:
        report["export_timestamp"] = datetime.now().isoformat()
        return json.dumps(report, indent=2)
    return "{}"

# --- Language Dictionary ---
texts = {
    "si": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "වෘත්තීය මිනුම් සහ ඉඩම් සැලසුම්කරණ පද්ධතිය",
        "enterprise": "Enterprise Edition",
        "manual": "🗺️ සිතියම මත සලකුණු කිරීම",
        "gps": "🛰️ GPS මැනුම් සමීක්ෂණය",
        "analytics": "📊 මැනුම් වාර්තාව",
        "subdivision": "🏗️ වෘත්තීය කට්ටි කිරීම",
        "execute": "🚀 නිවැරදිව කට්ටි කරන්න",
        "reset": "🗑️ සියල්ල මකන්න",
        "val_p": "පර්චසයක මිල (රු.)",
        "mark_gps": "📍 ස්ථානය සලකුණු කරන්න",
        "undo": "↩️ අවසන් ලක්ෂ්‍යය මකන්න",
        "total_area": "මුළු වර්ගඵලය",
        "perimeter": "වටප්‍රමාණය",
        "remainder": "ඉතිරිය",
        "plot": "කට්ටිය",
        "total_value": "මුළු වටිනාකම",
        "export": "📥 වාර්තාව Export කරන්න",
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
        "method": "ක්‍රමය",
        "confidence": "විශ්වාසනීයත්වය",
        "surveyor": "මිනුම්කරු නම",
        "notes": "සටහන්",
        "bearing": "දිශාව",
        "report": "වාර්තාව"
    },
    "en": {
        "title": "🌍 LANKALAND PRO GIS",
        "subtitle": "Professional Survey & Land Planning System",
        "enterprise": "Enterprise Edition",
        "manual": "🗺️ MANUAL MAPPING",
        "gps": "🛰️ GPS SURVEY",
        "analytics": "📊 ANALYTICS",
        "subdivision": "🏗️ PROFESSIONAL SUBDIVISION",
        "execute": "🚀 EXECUTE ACCURATE SPLIT",
        "reset": "🗑️ RESET ALL",
        "val_p": "Value per Perch (Rs.)",
        "mark_gps": "📍 MARK LOCATION",
        "undo": "↩️ UNDO LAST",
        "total_area": "Total Area",
        "perimeter": "Perimeter",
        "remainder": "Remainder",
        "plot": "Plot",
        "total_value": "Total Value",
        "export": "📥 EXPORT REPORT",
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
        "method": "Method",
        "confidence": "Confidence",
        "surveyor": "Surveyor Name",
        "notes": "Notes",
        "bearing": "Bearing",
        "report": "Report"
    }
}

# --- Main Application Logic ---
if st.session_state.lang is None:
    # Language Selection Screen
    st.markdown("""
    <div class='main-header'>
        <h1>🗺️ LANKALAND PRO GIS</h1>
        <p style='font-size:1.3em; margin-top:15px;'>Professional Survey & Land Planning System</p>
        <p style='font-size:0.9em; opacity:0.8; margin-top:10px;'>Enterprise Edition v5.0</p>
        <div style='margin-top:25px;'>
            <h3>භාෂාව තෝරන්න / Select Language</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇱🇰 සිංහල\n\nසම්පූර්ණ සිංහල අතුරුමුහුණත", use_container_width=True, help="Sinhala Interface"):
            st.session_state.lang = "si"
            st.rerun()
    with col2:
        if st.button("🌐 ENGLISH\n\nComplete English Interface", use_container_width=True, help="English Interface"):
            st.session_state.lang = "en"
            st.rerun()
    
    # Feature Preview
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <div class='tool-icon'>🎯</div>
            <h4>Accurate Subdivision</h4>
            <p>Binary search algorithm for precise equal-area plot division</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <div class='tool-icon'>📊</div>
            <h4>Real-time Analytics</h4>
            <p>Professional surveyor-grade measurements with confidence metrics</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <div class='tool-icon'>🗺️</div>
            <h4>GPS Integration</h4>
            <p>Walk-and-mark with satellite imagery and live tracking</p>
        </div>
        """, unsafe_allow_html=True)

else:
    T = texts[st.session_state.lang]
    
    # Professional Sidebar
    with st.sidebar:
        st.markdown(f"### ⚙️ {T['method']}")
        
        if st.button("🔙 Main Menu", use_container_width=True, help="Return to main menu"):
            st.session_state.update({"method": None, "points": [], "final_plots": [], "history": []})
            st.rerun()
        
        st.markdown("---")
        
        # Project Information
        st.markdown("#### 📋 Project Info")
        st.session_state.project_name = st.text_input(
            T['project_name'], 
            st.session_state.project_name,
            help="Enter project identifier"
        )
        st.session_state.surveyor_name = st.text_input(
            T['surveyor'],
            st.session_state.surveyor_name,
            help="Surveyor or company name"
        )
        st.session_state.survey_date = st.date_input(
            "Survey Date",
            value=datetime.strptime(st.session_state.survey_date, '%Y-%m-%d') if st.session_state.survey_date else datetime.now()
        ).strftime('%Y-%m-%d')
        
        st.markdown("---")
        
        # Pricing
        st.markdown("#### 💰 Valuation")
        st.session_state.price_per_perch = st.number_input(
            T['val_p'], 
            min_value=0.0, 
            value=st.session_state.price_per_perch, 
            step=10000.0,
            help="Price per perch in LKR"
        )
        
        st.markdown("---")
        
        # Subdivision Settings
        st.markdown("#### 🏗️ Subdivision")
        st.session_state.subdivision_method = st.radio(
            "",
            ["equal_area", "simple"],
            format_func=lambda x: "🎯 Accurate (Binary Search)" if x == "equal_area" else "⚡ Simple (Fast)",
            index=0 if st.session_state.subdivision_method == "equal_area" else 1,
            help="Choose subdivision algorithm"
        )
        
        st.session_state.show_cutting_lines = st.checkbox(
            "Show Cutting Lines", 
            value=st.session_state.show_cutting_lines,
            help="Display subdivision lines on map"
        )
        
        st.markdown("---")
        
        # Live Statistics
        if st.session_state.points:
            st.markdown("#### 📈 Live Stats")
            st.metric(T['points_marked'], len(st.session_state.points))
            
            if len(st.session_state.points) >= 3:
                area, peri = calculate_detailed_area(st.session_state.points)
                st.metric(T['total_area'], f"{area:.2f} P")
                st.metric(T['perimeter'], f"{peri:.1f} m")
        
        if st.session_state.final_plots:
            st.metric(T['plot_details'], f"{len(st.session_state.final_plots)} plots")
            total_allocated = sum(calculate_detailed_area(p['coords'])[0] for p in st.session_state.final_plots)
            st.metric("Allocated", f"{total_allocated:.2f} P")
            
            # Confidence Level
            confidence = calculate_confidence_level(st.session_state.points, st.session_state.final_plots)
            st.session_state.confidence_level = confidence
            
            st.markdown(f"#### {T['confidence']}")
            conf_color = "confidence-high" if confidence >= 80 else "confidence-medium" if confidence >= 60 else "confidence-low"
            st.markdown(f"""
            <div class='confidence-meter'>
                <div class='confidence-bar'>
                    <div class='confidence-fill {conf_color}' style='width: {confidence}%'>
                        {confidence}%
                    </div>
                </div>
                <small style='color: #b0bec5; display: block; margin-top: 5px;'>
                    {'Excellent' if confidence >= 80 else 'Good' if confidence >= 60 else 'Fair'}
                </small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Notes
        st.session_state.measurement_notes = st.text_area(
            T['notes'],
            st.session_state.measurement_notes,
            height=100,
            help="Add survey notes or observations"
        )

    # Main Content Area
    if st.session_state.method is None:
        # Mode Selection Screen
        st.markdown(f"""
        <div class='main-header'>
            <h1>{T['title']}</h1>
            <p>{T['subtitle']}</p>
            <span style='font-size:0.85em; opacity:0.8;'>{T['enterprise']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class='feature-card'>
                <h2>🎯</h2>
                <h4>Binary Search</h4>
                <p>±0.05P accuracy</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='feature-card'>
                <h2>📊</h2>
                <h4>Live Analytics</h4>
                <p>Real-time metrics</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class='feature-card'>
                <h2>🗺️</h2>
                <h4>GPS Survey</h4>
                <p>Walk & mark</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div class='feature-card'>
                <h2>📥</h2>
                <h4>Export</h4>
                <p>Professional reports</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mode selection buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button(T['manual'], use_container_width=True, help="Click on map to mark boundary points"):
                st.session_state.method = "manual"
                st.rerun()
        with col2:
            if st.button(T['gps'], use_container_width=True, help="Use live GPS to mark boundary"):
                st.session_state.method = "gps"
                st.rerun()
    
    else:
        # Main Survey Interface
        col_map, col_tools = st.columns([2.5, 1])
        
        with col_map:
            try:
                # Calculate map center
                if st.session_state.points:
                    center_lat = sum(p[0] for p in st.session_state.points) / len(st.session_state.points)
                    center_lon = sum(p[1] for p in st.session_state.points) / len(st.session_state.points)
                    map_center = [center_lat, center_lon]
                else:
                    map_center = [7.8731, 80.7718]  # Default: Sri Lanka
                
                # Create professional map
                m = folium.Map(
                    location=map_center,
                    zoom_start=19,
                    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                    attr="Google Satellite"
                )
                
                # Add controls
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
                
                # Draw subdivided plots
                colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', 
                         '#00BCD4', '#FFEB3B', '#795548', '#FF5722', '#607D8B']
                
                for idx, item in enumerate(st.session_state.final_plots):
                    color = colors[idx % len(colors)]
                    area_p, peri = calculate_detailed_area(item['coords'])
                    value = area_p * st.session_state.price_per_perch
                    is_remainder = item.get('is_remainder', False)
                    
                    # Draw plot polygon
                    folium.Polygon(
                        locations=item['coords'],
                        color=color,
                        weight=3,
                        fill=True,
                        fill_opacity=0.5,
                        popup=f"""
                        <b>{'Remainder' if is_remainder else f'Plot #{idx+1}'}</b><br>
                        Area: {area_p:.2f} P ({area_p*25.29:.1f} m²)<br>
                        Perimeter: {peri:.1f} m<br>
                        Value: {format_currency(value)}
                        """
                    ).add_to(m)
                    
                    # Add plot label
                    center = calculate_plot_center(item['coords'])
                    label = "R" if is_remainder else str(idx+1)
                    folium.Marker(
                        center,
                        icon=folium.DivIcon(
                            html=f'''
                            <div style="
                                font-size:16pt;
                                font-weight:900;
                                color:white;
                                background:{color};
                                padding:8px;
                                border-radius:50%;
                                width:40px;
                                height:40px;
                                text-align:center;
                                line-height:40px;
                                box-shadow: 0 4px 8px rgba(0,0,0,0.4);
                                border: 3px solid white;
                            ">{label}</div>
                            '''
                        )
                    ).add_to(m)
                
                # Draw main boundary
                if len(st.session_state.points) >= 2:
                    folium.Polygon(
                        locations=st.session_state.points,
                        color="yellow",
                        weight=5,
                        fill=False,
                        dashArray="10, 10"
                    ).add_to(m)
                    
                    # Add distance and bearing labels
                    for i in range(len(st.session_state.points)):
                        p1, p2 = st.session_state.points[i], st.session_state.points[(i+1)%len(st.session_state.points)]
                        mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]
                        dist = get_distance_meters(p1, p2)
                        bearing = calculate_bearing(p1, p2)
                        
                        folium.Marker(
                            mid,
                            icon=folium.DivIcon(
                                html=f'''
                                <div style="
                                    font-size:10pt;
                                    color:white;
                                    background:rgba(0,0,0,0.85);
                                    padding:6px 10px;
                                    border-radius:6px;
                                    font-weight:bold;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
                                    border: 1px solid rgba(255,255,255,0.3);
                                    white-space: nowrap;
                                ">
                                    📏 {dist:.1f}m<br>
                                    🧭 {bearing:.0f}°
                                </div>
                                '''
                            )
                        ).add_to(m)
                
                # Draw boundary points
                for i, p in enumerate(st.session_state.points):
                    folium.Marker(
                        location=p,
                        draggable=True,
                        icon=folium.Icon(color="green", icon="map-pin", prefix='fa'),
                        popup=f"""
                        <b>Point {i+1}</b><br>
                        Lat: {p[0]:.6f}<br>
                        Lon: {p[1]:.6f}
                        """
                    ).add_to(m)
                
                # Render map
                map_data = st_folium(m, height=650, width="100%", key="main_map")
                
                # Handle map clicks
                if map_data and map_data.get('last_clicked') and st.session_state.method == "manual":
                    new_point = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                    if new_point not in st.session_state.points:
                        st.session_state.points.append(new_point)
                        st.session_state.history.append(("add_point", new_point))
                        st.rerun()
            
            except Exception as e:
                st.error(f"Map error: {e}")
        
        with col_tools:
            # Analytics Card
            st.markdown(f"<div class='card'><h3>{T['analytics']}</h3>", unsafe_allow_html=True)
            
            if len(st.session_state.points) >= 3:
                area_p, peri_m = calculate_detailed_area(st.session_state.points)
                total_value = area_p * st.session_state.price_per_perch
                
                st.markdown(f"<div class='metric-label'>{T['total_area']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-val'>{area_p:.2f} P</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='stat-mini'><strong>m²:</strong> {area_p * 25.29:.2f}</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='metric-label' style='margin-top:15px;'>{T['perimeter']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-val' style='color:#ffa726'>{peri_m:.1f} m</div>", unsafe_allow_html=True)
                
                if st.session_state.price_per_perch > 0:
                    st.markdown(f"<div class='metric-label' style='margin-top:15px;'>{T['total_value']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-val' style='color:#66bb6a'>{format_currency(total_value)}</div>", unsafe_allow_html=True)
            else:
                st.info("අවම වශයෙන් ලක්ෂ්‍ය 3ක් සලකුණු කරන්න" if st.session_state.lang == "si" else "Mark at least 3 points")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # GPS Controls
            if st.session_state.method == "gps":
                st.markdown(f"<div class='card'><h3>🛰️ GPS CONTROL</h3>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(T['mark_gps'], use_container_width=True):
                        if map_data and map_data.get('last_clicked'):
                            new_point = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
                            st.session_state.points.append(new_point)
                            st.session_state.history.append(("add_point", new_point))
                            st.rerun()
                        else:
                            st.warning("Click on map first")
                
                with col2:
                    if st.button(T['undo'], use_container_width=True):
                        if st.session_state.points:
                            removed = st.session_state.points.pop()
                            st.session_state.history.append(("remove_point", removed))
                            st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Subdivision Engine
            st.markdown(f"<div class='card'><h3>{T['subdivision']}</h3>", unsafe_allow_html=True)
            
            if len(st.session_state.points) >= 3:
                target = st.number_input(
                    "Target Area (P)",
                    min_value=1.0,
                    value=10.0,
                    step=0.5,
                    key="target_input",
                    help="Desired plot size in perches"
                )
                
                # Orientation buttons
                col1, col2 = st.columns(2)
                vert_style = "🟢 " if st.session_state.orientation == "vertical" else ""
                horz_style = "🟢 " if st.session_state.orientation == "horizontal" else ""
                
                with col1:
                    if st.button(f"{vert_style}සිරස්\nVertical", use_container_width=True):
                        st.session_state.orientation = "vertical"
                        st.rerun()
                with col2:
                    if st.button(f"{horz_style}තිරස්\nHorizontal", use_container_width=True):
                        st.session_state.orientation = "horizontal"
                        st.rerun()
                
                # Execute button
                if st.button(T['execute'], use_container_width=True, type="primary"):
                    area_p, _ = calculate_detailed_area(st.session_state.points)
                    
                    if area_p < target:
                        st.error(f"Total area ({area_p:.2f} P) is less than target!")
                    else:
                        # Show surveyor animation
                        progress_placeholder = st.empty()
                        surveyor_placeholder = st.empty()
                        
                        surveyor_placeholder.markdown(
                            "<div class='surveyor-animation'>🚶‍♂️📏🗺️</div>",
                            unsafe_allow_html=True
                        )
                        
                        def update_progress(current, total):
                            progress = (current / total) * 100
                            progress_placeholder.markdown(f"""
                            <div class='progress-container'>
                                <small style='color: #4fc3f7; font-weight: 600;'>
                                    {T['calculating']} Plot {current+1}/{total}
                                </small>
                                <div class='progress-bar'>
                                    <div class='progress-fill' style='width: {progress}%'></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        try:
                            start_time = time.time()
                            
                            main_poly = Polygon(st.session_state.points)
                            if not main_poly.is_valid:
                                main_poly = main_poly.buffer(0)
                            
                            if st.session_state.subdivision_method == "equal_area":
                                st.session_state.final_plots = accurate_subdivision(
                                    main_poly,
                                    target,
                                    st.session_state.orientation,
                                    update_progress
                                )
                            else:
                                # Simple method (kept for comparison)
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
                                                st.session_state.final_plots.append({
                                                    'coords': list(intersect.exterior.coords),
                                                    'plot_number': i+1
                                                })
                                            elif isinstance(intersect, MultiPolygon):
                                                for part in intersect.geoms:
                                                    st.session_state.final_plots.append({
                                                        'coords': list(part.exterior.coords),
                                                        'plot_number': i+1
                                                    })
                                else:
                                    cuts = np.linspace(min_lat, max_lat, num + 1)
                                    for i in range(len(cuts)-1):
                                        update_progress(i, num)
                                        blade = box(cuts[i], min_lon-0.01, cuts[i+1], max_lon+0.01)
                                        intersect = main_poly.intersection(blade)
                                        if not intersect.is_empty:
                                            if isinstance(intersect, Polygon):
                                                st.session_state.final_plots.append({
                                                    'coords': list(intersect.exterior.coords),
                                                    'plot_number': i+1
                                                })
                                            elif isinstance(intersect, MultiPolygon):
                                                for part in intersect.geoms:
                                                    st.session_state.final_plots.append({
                                                        'coords': list(part.exterior.coords),
                                                        'plot_number': i+1
                                                    })
                            
                            calc_time = time.time() - start_time
                            st.session_state.last_calculation_time = calc_time
                            
                            time.sleep(0.3)
                            progress_placeholder.empty()
                            surveyor_placeholder.empty()
                            
                            st.success(f"✓ Completed in {calc_time:.2f}s")
                            st.rerun()
                        
                        except Exception as e:
                            progress_placeholder.empty()
                            surveyor_placeholder.empty()
                            st.error(f"Error: {e}")
                
                # Results Display
                if st.session_state.final_plots:
                    area_p, _ = calculate_detailed_area(st.session_state.points)
                    total_allocated = sum(calculate_detailed_area(p['coords'])[0] 
                                        for p in st.session_state.final_plots)
                    
                    st.markdown(f"""
                    <div class='success-box'>
                        ✓ {len(st.session_state.final_plots)} plots created
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Accuracy Report
                    with st.expander("📊 Detailed Accuracy Report", expanded=True):
                        st.markdown("<table class='comparison-table'>", unsafe_allow_html=True)
                        st.markdown("""
                        <tr>
                            <th>Plot</th>
                            <th>Target</th>
                            <th>Actual</th>
                            <th>Diff</th>
                            <th>Status</th>
                        </tr>
                        """, unsafe_allow_html=True)
                        
                        for idx, plot in enumerate(st.session_state.final_plots):
                            plot_area, _ = calculate_detailed_area(plot['coords'])
                            is_remainder = plot.get('is_remainder', False)
                            
                            if not is_remainder:
                                diff = plot_area - target
                                diff_percent = (diff / target * 100) if target > 0 else 0
                                badge = get_accuracy_badge(plot_area, target)
                                
                                st.markdown(f"""
                                <tr>
                                    <td><b>#{idx+1}</b></td>
                                    <td>{target:.2f} P</td>
                                    <td>{plot_area:.2f} P</td>
                                    <td style='color: {"#4caf50" if abs(diff) < 0.5 else "#ffa726"}'>
                                        {diff:+.2f} P<br>
                                        <small>({diff_percent:+.1f}%)</small>
                                    </td>
                                    <td>{badge}</td>
                                </tr>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <tr style='background: rgba(255, 152, 0, 0.1);'>
                                    <td><b>Remainder</b></td>
                                    <td>-</td>
                                    <td>{plot_area:.2f} P</td>
                                    <td>-</td>
                                    <td><span class='elevation-badge'>REMAINDER</span></td>
                                </tr>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("</table>", unsafe_allow_html=True)
                        
                        # Summary statistics
                        st.markdown(f"""
                        <div style='margin-top: 20px; padding: 15px; background: rgba(33, 150, 243, 0.1); border-radius: 10px; border: 1px solid rgba(33, 150, 243, 0.3);'>
                            <div class='stat-mini'><strong>Original:</strong> {area_p:.2f} P</div>
                            <div class='stat-mini'><strong>Allocated:</strong> {total_allocated:.2f} P</div>
                            <div class='stat-mini'><strong>Difference:</strong> {abs(area_p - total_allocated):.3f} P</div>
                            <div class='stat-mini'><strong>Accuracy:</strong> {(1 - abs(area_p - total_allocated)/area_p)*100:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Mark boundary first" if st.session_state.lang == "en" else "ප්‍රථමයෙන් මායිම සලකුණු කරන්න")
            
            if st.button(T['reset'], use_container_width=True):
                st.session_state.update({"points": [], "final_plots": [], "history": []})
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Export Section
            if st.session_state.points or st.session_state.final_plots:
                st.markdown(f"<div class='export-card'><h3 style='color:white;'>{T['export']}</h3>", unsafe_allow_html=True)
                
                if st.button("📥 Download JSON Report", use_container_width=True):
                    json_data = export_project_data()
                    st.download_button(
                        label="💾 Save Report",
                        data=json_data,
                        file_name=f"{st.session_state.project_name}_report.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # GPS Coordinates
            if st.session_state.points:
                with st.expander("🗺️ GPS Coordinates"):
                    st.markdown("<div class='coord-display'>", unsafe_allow_html=True)
                    for i, p in enumerate(st.session_state.points):
                        st.text(f"Point {i+1}: {p[0]:.6f}, {p[1]:.6f}")
                    st.markdown("</div>", unsafe_allow_html=True)
    
    # Professional Footer
    st.markdown("""
    <div class='footer'>
        <strong>🌍 LankaLand Pro GIS Enterprise v5.0</strong><br>
        Professional Survey & Land Planning System<br>
        Binary Search Subdivision | Surveyor-Grade Accuracy | Real-time Analytics<br>
        <small style='opacity: 0.6;'>© 2024 - Built with precision. Designed for excellence.</small>
    </div>
    """, unsafe_allow_html=True)
