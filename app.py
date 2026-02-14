import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MeasureControl
from shapely.geometry import Polygon
import math
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration ---
st.set_page_config(page_title="LankaLand Pro GIS", layout="wide")

# CSS Styling (ඔබේ Dark Theme එක ආරක්ෂා කරමින්)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .main-header { 
        background: linear-gradient(90deg, #1b5e20, #4caf50); 
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    .card { background: #1d2129; padding: 15px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if 'points' not in st.session_state: st.session_state.points = []
if 'final_plots' not in st.session_state: st.session_state.final_plots = []

# --- ප්‍රස්ථාරය ඇඳීමේ ශ්‍රිතය (පැහැදිලි Grid Lines සහිතව) ---
def render_price_graph():
    x = np.arange(1, 11)
    y = [102, 105, 104, 108, 112, 110, 115, 118, 117, 120]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#1d2129')
    ax.set_facecolor('#ffffff')
    
    # දත්ත රේඛාව
    ax.plot(x, y, color='#1b5e20', marker='o', linewidth=2.5)
    
    # ඔබ විශේෂයෙන්ම ඉල්ලූ "කට්ටි" (Grid Lines)
    ax.minorticks_on()
    # Major Grids (තද කොළ)
    ax.grid(which='major', color='#2ecc71', linestyle='-', linewidth=1.2, alpha=0.8)
    # Minor Grids (ලා කොළ)
    ax.grid(which='minor', color='#d5f5e3', linestyle=':', linewidth=0.8, alpha=0.6)
    
    ax.tick_params(colors='white', which='both', labelsize=8)
    ax.set_title("මිල දර්ශකය (Price Index)", color='white', fontsize=10)
    return fig

# --- App Layout ---
st.markdown("<div class='main-header'><h1>🌍 LANKALAND PRO GIS</h1></div>", unsafe_allow_html=True)

col1, col2 = st.columns([2.5, 1])

with col1:
    # සිතියම
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
    
    # ඉඩම් කට්ටි වෙන් කරන රේඛා (Lines) පෙන්වීම
    for plot in st.session_state.final_plots:
        folium.Polygon(
            locations=plot['coords'], 
            color="#00e676", # පැහැදිලි කොළ පාට ඉරි
            weight=4, 
            fill=True, 
            fill_opacity=0.3
        ).add_to(m)
        
    map_res = st_folium(m, height=550, width="100%")
    
    if map_res['last_clicked']:
        st.session_state.points.append((map_res['last_clicked']['lat'], map_res['last_clicked']['lng']))
        st.rerun()

with col2:
    st.markdown("<div class='card'><h3>📊 දත්ත වාර්තාව</h3>", unsafe_allow_html=True)
    st.write(f"සලකුණු කළ ලක්ෂ්‍ය ගණන: {len(st.session_state.points)}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ප්‍රස්ථාරය පෙන්වීම
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.pyplot(render_price_graph())
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 කට්ටි කර පෙන්වන්න"):
        if len(st.session_state.points) >= 3:
            # කට්ටි කිරීමේ උදාහරණයක් (මෙය ඔබේ logic එකට අනුව වෙනස් විය හැක)
            st.session_state.final_plots.append({'coords': st.session_state.points})
            st.rerun()

    if st.button("🗑️ සියල්ල මකන්න"):
        st.session_state.points = []
        st.session_state.final_plots = []
        st.rerun()
