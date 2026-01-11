import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import time

# --- Configuration & Setup ---
st.set_page_config(
    page_title="Suitcase Tracker Live",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for that premium feel
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #f0f2f6;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #1f2937;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #374151;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Mock Data Generation ---
# List of major airports for realistic starting points
AIRPORTS = {
    "JFK": {"lat": 40.6413, "lon": -73.7781, "name": "New York JFK"},
    "LHR": {"lat": 51.4700, "lon": -0.4543, "name": "London Heathrow"},
    "HND": {"lat": 35.5494, "lon": 139.7798, "name": "Tokyo Haneda"},
    "DXB": {"lat": 25.2532, "lon": 55.3657, "name": "Dubai Intl"},
    "CDG": {"lat": 49.0097, "lon": 2.5479, "name": "Paris Charles de Gaulle"},
    "SIN": {"lat": 1.3644, "lon": 103.9915, "name": "Singapore Changi"},
    "SYD": {"lat": -33.9399, "lon": 151.1753, "name": "Sydney Kingsford Smith"},
    "BCN": {"lat": 41.2974, "lon": 2.0833, "name": "Barcelona El Prat"},
}

STATUS_COLORS = {
    "In Transit": [59, 130, 246, 200],  # Blue
    "Landed": [16, 185, 129, 200],      # Green
    "Delayed": [245, 158, 11, 200],     # Orange
    "Lost": [239, 68, 68, 200],         # Red
}

def generate_mock_data(num_suitcases=100):
    """Generates random suitcase data around major airports."""
    data = []
    
    for i in range(num_suitcases):
        # Pick a random airport as a base
        airport_code = np.random.choice(list(AIRPORTS.keys()))
        base = AIRPORTS[airport_code]
        
        # Add some random scatter around the airport to simulate movement/terminals
        lat_offset = np.random.normal(0, 0.05)
        lon_offset = np.random.normal(0, 0.05)
        
        status = np.random.choice(list(STATUS_COLORS.keys()), p=[0.5, 0.3, 0.15, 0.05])
        
        suitcase = {
            "id": f"SC-{1000+i}",
            "lat": base["lat"] + lat_offset,
            "lon": base["lon"] + lon_offset,
            "status": status,
            "origin": base["name"],
            "owner": f"Passenger {i}",
            "color": STATUS_COLORS[status],
            "size": 100 if status == "Lost" else 50 # Make lost bags larger
        }
        data.append(suitcase)
        
    return pd.DataFrame(data)

# --- Sidebar ---
st.sidebar.title("🧳 Tracker Controls")
st.sidebar.markdown("Filter and manage live suitcase tracking.")

if 'data' not in st.session_state:
    st.session_state.data = generate_mock_data(200)

if st.sidebar.button("🔄 Refresh Data"):
    st.session_state.data = generate_mock_data(200)
    st.rerun()

status_filter = st.sidebar.multiselect(
    "Filter by Status",
    options=list(STATUS_COLORS.keys()),
    default=list(STATUS_COLORS.keys())
)

filtered_data = st.session_state.data[st.session_state.data["status"].isin(status_filter)]

# --- Main Dashboard ---
st.markdown("<h1 class='main-header'>✈️ Global Suitcase Tracker Network</h1>", unsafe_allow_html=True)

# Metrics Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-card'><h3>Total Bags</h3><h2>{len(filtered_data)}</h2></div>", unsafe_allow_html=True)
with c2:
    lost_count = len(filtered_data[filtered_data['status'] == 'Lost'])
    st.markdown(f"<div class='metric-card' style='border-color: #ef4444;'><h3>Alerts (Lost)</h3><h2 style='color:#ef4444'>{lost_count}</h2></div>", unsafe_allow_html=True)
with c3:
    transit_count = len(filtered_data[filtered_data['status'] == 'In Transit'])
    st.markdown(f"<div class='metric-card'><h3>In Air</h3><h2>{transit_count}</h2></div>", unsafe_allow_html=True)
with c4:
    landed_count = len(filtered_data[filtered_data['status'] == 'Landed'])
    st.markdown(f"<div class='metric-card' style='border-color: #10b981;'><h3>Arrived</h3><h2 style='color:#10b981'>{landed_count}</h2></div>", unsafe_allow_html=True)

st.write("") # Spacer

# --- Map Visualization ---
# Define the view state
view_state = pdk.ViewState(
    latitude=20.0,
    longitude=0.0,
    zoom=1.5,
    pitch=0,
)

# Tooltip config
tooltip = {
    "html": "<b>Bag ID:</b> {id}<br/>"
            "<b>Status:</b> {status}<br/>"
            "<b>Owner:</b> {owner}<br/>"
            "<b>Origin:</b> {origin}",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}

# Scatterplot Layer
layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_data,
    get_position=["lon", "lat"],
    get_color="color",
    get_radius=20000, # Radius in meters
    radius_scale=1,
    radius_min_pixels=5,
    radius_max_pixels=20,
    pickable=True,
    opacity=0.8,
)

# Animated Arc Layer (Simulating flights)
# Create simple arcs from origin to a fake destination for visual flair
filtered_data['dest_lon'] = filtered_data['lon'] + np.random.normal(0, 10, len(filtered_data))
filtered_data['dest_lat'] = filtered_data['lat'] + np.random.normal(0, 10, len(filtered_data))

arc_layer = pdk.Layer(
    "ArcLayer",
    data=filtered_data[filtered_data['status'] == 'In Transit'].head(20), # Only show a few arcs to avoid clutter
    get_source_position=["lon", "lat"],
    get_target_position=["dest_lon", "dest_lat"],
    get_source_color=[59, 130, 246, 100],
    get_target_color=[255, 255, 255, 100],
    get_width=2,
)

map_chart = pdk.Deck(
    map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', # No API key required for Carto
    initial_view_state=view_state,
    layers=[arc_layer, layer],
    tooltip=tooltip,
)

st.pydeck_chart(map_chart)

# --- Data Table (Optional) ---
with st.expander("📊 View Detailed Data Log"):
    st.dataframe(
        filtered_data[["id", "status", "origin", "lat", "lon"]].sort_values("status"),
        use_container_width=True,
        hide_index=True
    )
