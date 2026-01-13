import streamlit as st
import time
from services.simulation import SimulationEngine, BagStatus
from services.websocket_client import setup_realtime_updates, show_websocket_status
from components.map_view import render_map
from components.metrics import render_metrics
from components.bag_details import render_bag_details
from components.analytics import render_analytics
from components.auth import render_login
from components.ml_prediction import render_ml_prediction
from components.notifications import check_notifications, render_notification_center
from components.passenger_view import render_passenger_bag_details
import pandas as pd

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
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'data_source' not in st.session_state:
    st.session_state.data_source = "Simulation"

if 'is_running' not in st.session_state:
    st.session_state.is_running = False

if 'stats_history' not in st.session_state:
    st.session_state.stats_history = []

def capture_stats():
    """Captures current simulation state for analytics history."""
    df = st.session_state.simulation.get_dataframe()
    tick_time = len(st.session_state.stats_history)

    stats = {
        'timestamp': tick_time,
        'Total Active': len(df),
        'In Transit': len(df[df['status'] == 'In Transit']),
        'Landed': len(df[df['status'].isin(['Landed', 'Baggage Claim'])]),
        'Lost': len(df[df['status'] == 'Lost'])
    }
    st.session_state.stats_history.append(stats)

    # Check for notifications
    check_notifications(st.session_state.simulation.bags)

# --- Auth Check ---
if st.session_state.user_role is None:
    # Pass api_service if in API mode
    if st.session_state.data_source == "Real Backend API" and 'simulation' in st.session_state:
        render_login(st.session_state.simulation)
    else:
        render_login()
    st.stop()

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
                capture_stats()

        # Show current simulation tick/time
        st.metric("Simulation Ticks", len(st.session_state.simulation.bags[0].history) if st.session_state.simulation.bags else 0)

    else:
        st.subheader("API Connection")
        st.warning("📡 Connecting to http://localhost:8000...")
        if st.button("🔄 Fetch Live Data"):
            st.session_state.simulation.tick()
            capture_stats()

        # Auto-refresh toggle for API
        auto_refresh = st.checkbox("Auto-polling (5s)", value=False)
        if auto_refresh:
            st.session_state.is_running = True
        else:
            st.session_state.is_running = False

        # Show WebSocket status
        show_websocket_status()


    st.divider()

    # Map Settings
    st.subheader("Map Settings")
    show_heatmap = st.checkbox("Show Heatmap", value=False)

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
    st.divider()

    # User Profile / Logout
    if st.session_state.user_role == 'passenger':
        st.caption(f"Logged in as Passenger (Tracking {st.session_state.target_bag_id})")
    else:
        st.caption("Logged in as Administrator")

    if st.button("Log Out"):
        st.session_state.user_role = None
        st.session_state.target_bag_id = None
        st.rerun()

    st.divider()
    # Notification Center (Admin Only)
    if st.session_state.user_role == 'admin':
        render_notification_center()

# --- Auto-Run Logic (Only for Admin) ---
if st.session_state.user_role == 'admin' and st.session_state.is_running:
    st.session_state.simulation.tick()
    capture_stats()
    time.sleep(0.5) # Throttle speed
    st.rerun()

# --- Main Layout ---
if st.session_state.user_role == 'passenger':
    st.title(f"🧳 My Luggage Tracker")
else:
    st.title("🌍 Global Luggage Operations")

# Data preparation
# Data preparation
df_bags = st.session_state.simulation.get_dataframe()

# Apply Passenger Constraints
if st.session_state.user_role == 'passenger':
    target_id = st.session_state.get('target_bag_id')
    # Force filter to only this bag
    filtered_df = df_bags[df_bags['id'] == target_id]
    search_id = target_id
    # Hide sidebar filters effectively for passenger (or ignore them)
else:
    filtered_df = df_bags[df_bags['status'].isin(status_filter)]

# 1. Top Level Metrics (Admin Only)
if st.session_state.user_role == 'admin':
    render_metrics(filtered_df)

st.write("") # Spacer

# 2. Main Map
# Highlight selected bag if any
if search_id != "None":
    selected_bag_data = df_bags[df_bags['id'] == search_id]

# --- Tabs Layout ---
# --- Tabs Layout ---
if st.session_state.user_role == 'admin':
    tab_map, tab_analytics, tab_ml, tab_data = st.tabs(["🗺️ Live Map", "📈 Analytics", "🤖 ML Prediction", "📂 Raw Data"])

    with tab_map:
        render_map(filtered_df, show_heatmap=show_heatmap)

        # 3. Drill Down / Details
        if search_id != "None":
            bag = next((b for b in st.session_state.simulation.bags if b.id == search_id), None)
            if bag:
                render_bag_details(bag)
            else:
                st.error("Bag not found!")

    with tab_analytics:
        history_df = pd.DataFrame(st.session_state.stats_history)
        # Pass api_service if in API mode
        if st.session_state.data_source == "Real Backend API":
            render_analytics(filtered_df, history_df, api_service=st.session_state.simulation)
        else:
            render_analytics(filtered_df, history_df)

    with tab_ml:
        # ML Prediction Tab
        if st.session_state.data_source == "Real Backend API":
            render_ml_prediction(st.session_state.simulation)
        else:
            st.warning("🔌 La predicción ML requiere conexión al backend API")
            st.info("Cambia a **'Real Backend API'** en la barra lateral para acceder a esta función")

            # Show a demo of what it would look like
            st.subheader("🤖 Vista Previa de Predicción ML")
            st.markdown("""
            Esta función permite predecir el riesgo de pérdida de equipaje basándose en:
            - **Ruta de vuelo**: Origen y destino
            - **Condiciones del vuelo**: Retrasos, conexiones
            - **Características del aeropuerto**: Nivel de riesgo
            - **Perfil del pasajero**: Estado VIP
            - **Características del equipaje**: Peso

            El modelo ML retorna:
            - 🎯 Probabilidad de pérdida (0-100%)
            - 🚦 Nivel de riesgo (Bajo/Medio/Alto/Crítico)
            - 💡 Recomendaciones personalizadas
            """)

    with tab_data:
        st.dataframe(filtered_df, use_container_width=True)

else:
    # PASSENGER VIEW (Enhanced)
    render_map(filtered_df, show_heatmap=False)

    if search_id:
        bag = next((b for b in st.session_state.simulation.bags if b.id == search_id), None)
        if bag:
            # Use enhanced passenger view
            render_passenger_bag_details(bag, st.session_state.simulation)
        else:
            st.warning("We are currently unable to locate your bag. It might not be in the system yet.")
