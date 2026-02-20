"""
=================================================================================
LANKALAND PRO GIS - ENHANCEMENT MODULE
=================================================================================
These functions will be ADDED to the existing app.py without removing anything.

New Features:
1. Irregular Shape Measurement (කුඹුරු Mode)
2. 3D Visualization
3. Enhanced Animations
4. AR-Ready Export
5. Advanced Analytics
"""

import plotly.graph_objects as go
from scipy.interpolate import splprep, splev
import plotly.express as px

# ═══════════════════════════════════════════════════════════════
# FEATURE 1: IRREGULAR SHAPE TOOLS (කුඹුරු Mode)
# ═══════════════════════════════════════════════════════════════

def smooth_boundary_curve(points, density=10):
    """
    Create smooth curve through GPS points for irregular shapes
    Essential for කුඹුරු (paddy fields) with curved boundaries
    
    Args:
        points: List of (lat, lon) tuples
        density: Points per segment (higher = smoother)
    
    Returns:
        List of smoothed points
    """
    if len(points) < 3:
        return points
    
    try:
        points_array = np.array(points)
        
        # Create parametric spline
        tck, u = splprep(points_array.T, s=0, per=True)
        
        # Generate smooth curve
        u_new = np.linspace(0, 1, len(points) * density)
        smooth_curve = splev(u_new, tck)
        
        return list(zip(smooth_curve[0], smooth_curve[1]))
    except:
        return points

def calculate_point_density_quality(points):
    """
    Analyze GPS point density to detect areas needing more points
    Returns quality score and suggestions
    """
    if len(points) < 3:
        return 0, []
    
    suggestions = []
    segment_qualities = []
    
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        
        # Calculate distance between consecutive points
        from math import radians, sin, cos, sqrt, atan2
        lat1, lon1 = radians(p1[0]), radians(p1[1])
        lat2, lon2 = radians(p2[0]), radians(p2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        distance = 2 * 6371000 * atan2(sqrt(a), sqrt(1-a))
        
        # Quality based on distance
        # Ideal: 2-5 meters between points for irregular shapes
        if distance > 10:
            quality = 30  # Poor
            suggestions.append(f"Segment {i+1}: තව points අවශ්‍යයි (distance: {distance:.1f}m)")
        elif distance > 5:
            quality = 70  # Fair
        else:
            quality = 100  # Good
        
        segment_qualities.append(quality)
    
    overall_quality = sum(segment_qualities) / len(segment_qualities)
    
    return overall_quality, suggestions

def estimate_irregular_area_confidence(points, plots):
    """
    Calculate confidence score for irregular shape measurement
    Higher score = more reliable measurement
    """
    base_confidence = 100
    
    # Point count factor
    if len(points) < 6:
        base_confidence -= 30
    elif len(points) < 10:
        base_confidence -= 15
    elif len(points) < 15:
        base_confidence -= 5
    
    # Point density check
    quality, _ = calculate_point_density_quality(points)
    if quality < 50:
        base_confidence -= 20
    elif quality < 70:
        base_confidence -= 10
    
    # Polygon complexity
    if len(points) > 20:
        base_confidence += 10  # Bonus for detailed measurement
    
    return max(0, min(100, base_confidence))

# ═══════════════════════════════════════════════════════════════
# FEATURE 2: 3D VISUALIZATION
# ═══════════════════════════════════════════════════════════════

def create_3d_plot_visualization(plots, price_per_perch):
    """
    Create interactive 3D visualization where plot height = value
    Beautiful visual representation of land value distribution
    """
    if not plots:
        return None
    
    fig = go.Figure()
    
    for idx, plot in enumerate(plots):
        coords = plot['coords']
        
        # Calculate area and value
        area = 0
        try:
            from shapely.geometry import Polygon
            poly = Polygon(coords)
            area_m2 = poly.area * (111319.9 ** 2) * abs(np.cos(np.radians(coords[0][0])))
            area = area_m2 / 25.29
        except:
            pass
        
        value = area * price_per_perch
        height = value / 100000  # Scale for visualization
        
        # Separate lat/lon
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        
        # Create 3D mesh (walls)
        for i in range(len(coords)):
            next_i = (i + 1) % len(coords)
            
            # Bottom vertices
            x_bottom = [lons[i], lons[next_i], lons[next_i], lons[i]]
            y_bottom = [lats[i], lats[next_i], lats[next_i], lats[i]]
            z_bottom = [0, 0, 0, 0]
            
            # Top vertices
            x_top = [lons[i], lons[next_i], lons[next_i], lons[i]]
            y_top = [lats[i], lats[next_i], lats[next_i], lats[i]]
            z_top = [height, height, height, height]
            
            # Wall
            x_wall = [lons[i], lons[next_i], lons[next_i], lons[i]]
            y_wall = [lats[i], lats[next_i], lats[next_i], lats[i]]
            z_wall = [0, 0, height, height]
            
            color = px.colors.qualitative.Set3[idx % len(px.colors.qualitative.Set3)]
            
            fig.add_trace(go.Mesh3d(
                x=x_wall + x_top,
                y=y_wall + y_top,
                z=z_wall + z_top,
                color=color,
                opacity=0.7,
                name=f"Plot {idx+1}",
                showlegend=(i==0),
                hovertemplate=f"<b>Plot {idx+1}</b><br>" +
                             f"Area: {area:.2f} P<br>" +
                             f"Value: Rs. {value:,.0f}<br>" +
                             "<extra></extra>"
            ))
    
    # Update layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Longitude', showbackground=False),
            yaxis=dict(title='Latitude', showbackground=False),
            zaxis=dict(title='Value (Lakhs)', showbackground=False),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': '3D Plot Value Visualization',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#4fc3f7'}
        },
        showlegend=True,
        legend=dict(
            bgcolor='rgba(30, 36, 57, 0.8)',
            font=dict(color='white')
        ),
        height=600
    )
    
    return fig

def create_value_comparison_chart(plots, price_per_perch):
    """
    Create bar chart comparing plot values
    """
    if not plots:
        return None
    
    plot_numbers = []
    plot_values = []
    plot_areas = []
    
    for idx, plot in enumerate(plots):
        coords = plot['coords']
        
        # Calculate area
        area = 0
        try:
            from shapely.geometry import Polygon
            poly = Polygon(coords)
            area_m2 = poly.area * (111319.9 ** 2) * abs(np.cos(np.radians(coords[0][0])))
            area = area_m2 / 25.29
        except:
            pass
        
        value = area * price_per_perch
        
        plot_numbers.append(f"Plot {idx+1}")
        plot_values.append(value / 100000)  # Convert to lakhs
        plot_areas.append(area)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=plot_numbers,
        y=plot_values,
        text=[f"{v:.2f}L<br>{a:.1f}P" for v, a in zip(plot_values, plot_areas)],
        textposition='outside',
        marker=dict(
            color=plot_values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Value (Lakhs)")
        ),
        hovertemplate="<b>%{x}</b><br>" +
                     "Value: Rs. %{y:.2f} Lakhs<br>" +
                     "<extra></extra>"
    ))
    
    fig.update_layout(
        title='Plot Value Comparison',
        xaxis_title='Plot',
        yaxis_title='Value (Lakhs)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    return fig

# ═══════════════════════════════════════════════════════════════
# FEATURE 3: AR-READY EXPORT
# ═══════════════════════════════════════════════════════════════

def export_ar_ready_format(points, plots, project_info):
    """
    Export data in AR-ready format (JSON with 3D coordinates)
    Can be used with AR apps/viewers
    """
    ar_data = {
        "version": "1.0",
        "type": "LankaLand_AR_Scene",
        "project": project_info,
        "coordinate_system": "WGS84",
        "units": "meters",
        "created": datetime.now().isoformat(),
        
        "boundary": {
            "type": "polygon",
            "coordinates": points,
            "marker_color": "#FFFF00",
            "marker_size": 0.3
        },
        
        "plots": []
    }
    
    for idx, plot in enumerate(plots):
        coords = plot['coords']
        
        # Calculate center and area
        center_lat = sum(c[0] for c in coords) / len(coords)
        center_lon = sum(c[1] for c in coords) / len(coords)
        
        area = 0
        try:
            from shapely.geometry import Polygon
            poly = Polygon(coords)
            area_m2 = poly.area * (111319.9 ** 2) * abs(np.cos(np.radians(coords[0][0])))
            area = area_m2 / 25.29
        except:
            pass
        
        plot_data = {
            "id": idx + 1,
            "type": "polygon",
            "coordinates": coords,
            "center": [center_lat, center_lon],
            "area_perch": round(area, 2),
            "area_sqm": round(area * 25.29, 2),
            "color": f"#{hex(hash(f'plot_{idx}') % 0xFFFFFF)[2:].zfill(6)}",
            "height": 2.0,  # Height in meters for 3D visualization
            "label": {
                "text": f"Plot {idx + 1}",
                "position": [center_lat, center_lon, 1.5],  # Elevated for visibility
                "size": 0.5
            }
        }
        
        ar_data["plots"].append(plot_data)
    
    return json.dumps(ar_data, indent=2)

# ═══════════════════════════════════════════════════════════════
# FEATURE 4: ENHANCED ANALYTICS
# ═══════════════════════════════════════════════════════════════

def generate_comprehensive_report(points, plots, price_per_perch, project_name):
    """
    Generate comprehensive analytics report
    """
    report = {
        "project": project_name,
        "timestamp": datetime.now().isoformat(),
        "summary": {},
        "quality_metrics": {},
        "plots_analysis": [],
        "recommendations": []
    }
    
    # Calculate totals
    total_area = 0
    total_perimeter = 0
    plot_areas = []
    
    for coords in [p['coords'] for p in plots]:
        try:
            from shapely.geometry import Polygon
            poly = Polygon(coords)
            area_m2 = poly.area * (111319.9 ** 2) * abs(np.cos(np.radians(coords[0][0])))
            area = area_m2 / 25.29
            
            perimeter = 0
            for i in range(len(coords)):
                c1, c2 = coords[i], coords[(i+1) % len(coords)]
                # Distance calculation
                lat1, lon1 = np.radians(c1[0]), np.radians(c1[1])
                lat2, lon2 = np.radians(c2[0]), np.radians(c2[1])
                dlat, dlon = lat2 - lat1, lon2 - lon1
                a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
                dist = 2 * 6371000 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
                perimeter += dist
            
            total_area += area
            total_perimeter += perimeter
            plot_areas.append(area)
        except:
            pass
    
    # Summary
    report["summary"] = {
        "total_area_perch": round(total_area, 2),
        "total_area_sqm": round(total_area * 25.29, 2),
        "total_area_acres": round(total_area / 160, 3),
        "total_value": round(total_area * price_per_perch, 2),
        "number_of_plots": len(plots),
        "average_plot_size": round(total_area / len(plots), 2) if plots else 0
    }
    
    # Quality metrics
    quality, suggestions = calculate_point_density_quality(points)
    confidence = estimate_irregular_area_confidence(points, plots)
    
    report["quality_metrics"] = {
        "boundary_points": len(points),
        "point_density_score": round(quality, 1),
        "measurement_confidence": round(confidence, 1),
        "data_quality": "Excellent" if confidence > 85 else "Good" if confidence > 70 else "Fair"
    }
    
    # Plot variance
    if plot_areas:
        variance = np.var(plot_areas)
        std_dev = np.std(plot_areas)
        report["quality_metrics"]["plot_variance"] = round(variance, 3)
        report["quality_metrics"]["plot_std_dev"] = round(std_dev, 3)
    
    # Recommendations
    if quality < 70:
        report["recommendations"].append("තව GPS points එකතු කිරීම නිර්දේශ කරනු ලැබේ")
    if confidence < 80:
        report["recommendations"].append("Verify measurements with additional survey")
    if len(points) < 10 and total_area > 100:
        report["recommendations"].append("Large area - consider adding more boundary points")
    
    return report

# End of Enhancement Module
