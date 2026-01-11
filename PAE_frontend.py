import streamlit as st
import time
from services.simulation import SimulationEngine, BagStatus
from components.map_view import render_map
from components.metrics import render_metrics
from components.bag_details import render_bag_details

# --- Page Config ---
st.set_page_config(
    page_title="Suitcase Tracker Pro",
    page_icon="✈️",
    layout="wide",
)

# --- CSS Styling ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; }
    .stButton>button { width: 100%; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'data_source' not in st.session_state:
    st.session_state.data_source = "Simulation"

if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# --- Sidebar Controls ---
with st.sidebar:
    st.title("🧳 OmniTrack")
    
    # Mode Selection
    source_option = st.radio(
        "Data Source", 
        ["Simulation", "Real Backend API"],
        index=0 if st.session_state.data_source == "Simulation" else 1
    )
    
    # Handle Mode Switching
    if source_option != st.session_state.data_source:
        st.session_state.data_source = source_option
        st.session_state.is_running = False # Stop running on switch
        
        # Re-initialize the correct service
        if source_option == "Simulation":
            st.session_state.simulation = SimulationEngine(num_bags=100)
        else:
            # Lazy import to avoid circular defaults
            from services.api_service import RealTimeService 
            st.session_state.simulation = RealTimeService()
        st.rerun()

    # Initialize generic 'service' wrapper if not present (handled by re-init above generally, but for first load):
    if 'simulation' not in st.session_state:
        st.session_state.simulation = SimulationEngine(num_bags=100)

    # Dynamic Controls based on Mode
    if st.session_state.data_source == "Simulation":
        st.subheader("Simulation Controls")
        st.caption("Press Start to begin real-time tracking updates.")
        
        col_play, col_tick = st.columns(2)
        
        with col_play:
            run_label = "⏸ Pause" if st.session_state.is_running else "▶ Start Live"
            if st.button(run_label):
                st.session_state.is_running = not st.session_state.is_running
        
        with col_tick:
            if st.button("Step +1"):
                st.session_state.simulation.tick()
                
        # Show current simulation tick/time
        st.metric("Simulation Ticks", len(st.session_state.simulation.bags[0].history) if st.session_state.simulation.bags else 0)

    else:
        st.subheader("API Connection")
        st.warning("📡 Connecting to http://localhost:8000...")
        if st.button("🔄 Fetch Live Data"):
            st.session_state.simulation.tick()
        
        # Auto-refresh toggle for API
        auto_refresh = st.checkbox("Auto-polling (5s)", value=False)
        if auto_refresh:
            st.session_state.is_running = True
        else:
            st.session_state.is_running = False

    
    st.divider()
    
    # Filters
    st.subheader("Filters")
    status_filter = st.multiselect(
        "Status",
        options=[s.value for s in BagStatus],
        default=[s.value for s in BagStatus]
    )
    
    # Search
    st.subheader("Find Bag")
    all_bag_ids = [b.id for b in st.session_state.simulation.bags]
    search_id = st.selectbox("Select Bag ID", ["None"] + all_bag_ids)

# --- Auto-Run Logic ---
if st.session_state.is_running:
    st.session_state.simulation.tick()
    time.sleep(0.5) # Throttle speed
    st.rerun()

# --- Main Layout ---
st.title("🌍 Global Luggage Operations")

# Data preparation
df_bags = st.session_state.simulation.get_dataframe()
filtered_df = df_bags[df_bags['status'].isin(status_filter)]

# 1. Top Level Metrics
render_metrics(filtered_df)

st.write("") # Spacer

# 2. Main Map
# Highlight selected bag if any
if search_id != "None":
    selected_bag_data = df_bags[df_bags['id'] == search_id]
    # We could zoom to it, but for now let's just show it filter-wise or highlight
    # Let's filter the map to show only relevant or all? 
    # Better to show all but highlight. For now, let's keep showing all but use the search below.

render_map(filtered_df)

# 3. Drill Down / Details
if search_id != "None":
    # Find the bag object
    bag = next((b for b in st.session_state.simulation.bags if b.id == search_id), None)
    if bag:
        render_bag_details(bag)
    else:
        st.error("Bag not found!")
elif len(filtered_df) > 0 and len(filtered_df) < 5:
    # If filtered to a few, show details for first one
    st.info("Select a bag from the sidebar to view full history.")

# 4. Raw Data Expander
with st.expander("📂 Raw Data Log"):
    st.dataframe(filtered_df, use_container_width=True)
