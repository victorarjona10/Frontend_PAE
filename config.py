# 🔧 OmniTrack Configuration
# This file contains all configuration settings for the frontend application

# ==================== BACKEND API ====================
# URL of the backend API server
BACKEND_API_URL = "http://localhost:8000"

# WebSocket URL for real-time updates
WEBSOCKET_URL = "ws://localhost:8000/ws"

# API request timeout (seconds)
API_TIMEOUT = 5

# ==================== REAL-TIME UPDATES ====================
# Auto-refresh interval for real-time data (milliseconds)
AUTO_REFRESH_INTERVAL_MS = 5000  # 5 seconds

# Enable WebSocket for real-time updates (if available)
ENABLE_WEBSOCKET = True

# Polling interval when WebSocket is not available (milliseconds)
POLLING_INTERVAL_MS = 5000

# ==================== SIMULATION MODE ====================
# Number of bags to simulate in local mode
SIMULATION_NUM_BAGS = 100

# Simulation tick speed (seconds)
SIMULATION_TICK_SPEED = 0.5

# ==================== UI SETTINGS ====================
# Default map view
DEFAULT_MAP_CENTER = [40.6413, -73.7781]  # JFK Airport
DEFAULT_MAP_ZOOM = 4

# Maximum number of bags to display on map
MAX_BAGS_DISPLAY = 1000

# Show heatmap by default
DEFAULT_SHOW_HEATMAP = False

# ==================== AUTHENTICATION ====================
# Token storage location (session_state, local_storage, etc.)
TOKEN_STORAGE = "session_state"

# Test user credentials (for development only)
TEST_USERS = {
    "admin": {
        "password": "password",
        "role": "admin"
    },
    "passenger_1": {
        "password": "password",
        "role": "passenger",
        "bag_id": "BAG1000000001"
    },
    "passenger_2": {
        "password": "password",
        "role": "passenger",
        "bag_id": "BAG1000000050"
    }
}

# ==================== ANALYTICS ====================
# Maximum number of airports to show in top airports chart
MAX_TOP_AIRPORTS = 10

# Historical data retention (number of ticks)
MAX_HISTORY_LENGTH = 100

# ==================== NOTIFICATIONS ====================
# Enable desktop notifications
ENABLE_DESKTOP_NOTIFICATIONS = False

# Notification check interval (seconds)
NOTIFICATION_CHECK_INTERVAL = 10

# ==================== ML PREDICTION ====================
# Available airports for ML prediction
ML_AIRPORTS = ["JFK", "LHR", "DXB", "HND", "CDG", "AMS", "FRA", "BCN",
               "MAD", "FCO", "MUC", "ZRH", "VIE", "CPH", "ARN", "DUB",
               "BRU", "LIS", "OSL", "AGP"]

# Risk level thresholds
RISK_THRESHOLDS = {
    "LOW": 0.3,      # < 30%
    "MEDIUM": 0.6,   # 30-60%
    "HIGH": 0.8,     # 60-80%
    "CRITICAL": 1.0  # >= 80%
}

# ==================== FEATURE FLAGS ====================
# Enable/disable features
FEATURES = {
    "ml_prediction": True,
    "analytics_dashboard": True,
    "websocket_updates": True,
    "notifications": True,
    "advanced_filters": True,
    "export_data": True
}

# ==================== DEBUGGING ====================
# Enable debug mode
DEBUG = False

# Show API request logs
LOG_API_REQUESTS = False

# Show performance metrics
SHOW_PERFORMANCE_METRICS = False
