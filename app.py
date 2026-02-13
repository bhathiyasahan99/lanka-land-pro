import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon

st.set_page_config(page_title="LankaLand Pro", layout="wide")

st.title("🌾 LankaLand Pro - ඉඩම් මැනුම් පද්ධතිය")

if 'points' not in st.session_state:
    st.session_state.points = []

m = folium.Map(location=[7.8731, 80.7718], zoom_start=8, 
               tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")

for p in st.session_state.points:
    folium.Marker(location=[p[0], p[1]], icon=folium.Icon(color='green')).add_to(m)

if len(st.session_state.points) >= 3:
    folium.Polygon(locations=st.session_state.points, color="yellow", fill=True).add_to(m)

m.add_child(folium.LatLngPopup())
output = st_folium(m, height=450, width="100%")

if output['last_clicked']:
    new_p = (output['last_clicked']['lat'], output['last_clicked']['lng'])
    if new_p not in st.session_state.points:
        st.session_state.points.append(new_p)
        st.rerun()

if st.button("Reset (මකන්න)"):
    st.session_state.points = []
    st.rerun()

st.caption("Developed by Bhathiya")
