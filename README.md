# 🧳 OmniTrack: Global Suitcase Tracking System

OmniTrack is a comprehensive real-time baggage tracking and analytics platform that integrates with backend APIs for live data monitoring, ML-powered risk predictions, and advanced analytics. Built with **Streamlit**, **Pydeck**, and a full REST API integration.

## 🚀 Features

### 🎯 Core Functionality
*   **Dual Mode Operation**:
    *   **Simulation Mode**: Local data generation for testing
    *   **API Mode**: Real-time connection to backend (http://localhost:8000)
*   **Real-time Tracking**: Live baggage position updates via REST API and WebSocket
*   **Interactive 3D Map**: Global visualization with Pydeck (Carto Dark theme)
*   **Smart Authentication**: JWT-based login with role-based access (Admin/Passenger)

### 🤖 Advanced Features (NEW!)
*   **ML Risk Prediction**: AI-powered baggage loss probability calculator
    *   Multi-factor analysis (route, delays, connections, airport risk)
    *   Risk levels: LOW/MEDIUM/HIGH/CRITICAL with color coding
    *   Personalized recommendations based on risk assessment
*   **Analytics Dashboard**:
    *   Status distribution charts
    *   Busiest airports rankings
    *   Loss analytics with recovery metrics
    *   Hub efficiency statistics
    *   Real-time operational trends
*   **WebSocket Support**: Live updates without manual refresh
*   **Comprehensive API Integration**: 13+ endpoints fully integrated

### 👥 Role-Based Views
*   **Passenger**: Track individual baggage with flight details
*   **Admin**: Full system monitoring, analytics, and ML predictions

## 🛠️ Technology Stack

*   **Frontend**: Streamlit 1.x
*   **Visualization**: Pydeck (Deck.gl), Altair, Pandas
*   **Backend Integration**: Requests, WebSocket-Client
*   **Real-time Updates**: streamlit-autorefresh
*   **Language**: Python 3.10+

## 📦 Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/victorarjona10/Frontend_PAE.git
    cd Frontend_PAE
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

    **Dependencies include:**
    - streamlit
    - pandas
    - pydeck
    - altair
    - requests
    - websocket-client
    - streamlit-autorefresh

3.  **(Optional) Verify Backend Connection:**
    ```bash
    curl http://localhost:8000/health
    ```
    Expected response: `{"status": "healthy", "version": "1.0.0"}`

## ▶️ Usage

### Quick Start

Run the application:
```bash
streamlit run PAE_frontend.py
```

Open your browser to `http://localhost:8501`.

### 🔐 Login Credentials (API Mode)

**Administrator:**
- Username: `admin`
- Password: `password`
- Access: All features, all baggage

**Passenger Examples:**
- Username: `passenger_1` | Password: `password` | Tracks: `BAG1000000001`
- Username: `passenger_2` | Password: `password` | Tracks: `BAG1000000050`

### Controls

**Sidebar Controls:**
*   **Data Source**: Switch between Simulation/Real Backend API
*   **Start/Pause**: Toggle live updates (Simulation mode)
*   **Step +1**: Manual tick advance (Simulation mode)
*   **Fetch Live Data**: Manual refresh (API mode)
*   **Auto-polling**: Enable automatic 5-second refresh (API mode)
*   **Filters**: Filter by status (Check In, In Transit, Lost, etc.)
*   **Search**: Find specific bag by ID
*   **Map Settings**: Toggle heatmap view

**Admin Tabs:**
1. **🗺️ Live Map**: Real-time global baggage positions
2. **📈 Analytics**: Comprehensive operational dashboards
3. **🤖 ML Prediction**: Risk assessment tool
4. **📂 Raw Data**: Exportable data table

## 📂 Project Structure

```
Frontend_PAE/
├── PAE_frontend.py              # ✅ Main Application Entry Point (UPDATED)
├── config.py                    # 🆕 Configuration settings
├── requirements.txt             # ✅ Dependencies (UPDATED)
├── README.md                    # ✅ Project Documentation (UPDATED)
│
├── components/                  # UI Modules
│   ├── analytics.py             # ✅ Analytics Dashboard (UPDATED - API integration)
│   ├── auth.py                  # ✅ Authentication (UPDATED - Real JWT login)
│   ├── ml_prediction.py         # 🆕 ML Risk Prediction Form (NEW)
│   ├── bag_details.py           # Individual bag tracking view
│   ├── map_view.py              # Pydeck 3D map configuration
│   ├── metrics.py               # Dashboard KPI cards
│   └── notifications.py         # Alert system
│
├── services/                    # Logic & Data Layer
│   ├── api_service.py           # ✅ Full Backend API Client (UPDATED)
│   ├── websocket_client.py      # 🆕 WebSocket Real-time Updates (NEW)
│   ├── models.py                # Data classes (Bag, Airport, BagStatus)
│   └── simulation.py            # Local simulation engine
│
└── docs/                        # Documentation
    ├── FRONTEND_API_GUIDE.md    # Complete API documentation (13 KB)
    ├── API_QUICK_REFERENCE.md   # Quick reference cheatsheet (8 KB)
    ├── INTEGRATION_GUIDE.md     # 🆕 Integration guide (NEW)
    └── BACKEND_API_SPEC.md      # Backend specification
```

## 🆕 What's New in v2.0

### Integrated Backend Endpoints (13+)

✅ **Authentication**
- `POST /api/auth/login` - JWT authentication

✅ **Airports**
- `GET /api/airports` - List all 20 airports
- `GET /api/airports/{code}` - Get specific airport

✅ **Baggage**
- `GET /api/bags` - List with filters (status, owner_id, limit)
- `GET /api/bags/{id}` - Detailed bag info + history
- `POST /api/bags/scan` - Update position (RFID simulation)

✅ **Machine Learning**
- `POST /api/ml/predict` - Predict baggage loss risk

✅ **Analytics**
- `GET /api/analytics/dashboard` - Aggregated metrics
- `GET /api/analytics/losses` - Loss analysis
- `GET /api/analytics/top-airports` - Airports with most losses
- `GET /api/analytics/hub-statistics` - Hub efficiency stats

✅ **Real-time**
- `WS /ws` - WebSocket live updates

### New UI Components

🤖 **ML Prediction Tab**
- Interactive form with 9 risk factors
- Real-time probability calculation
- Color-coded risk levels (🟢 🟡 🟠 🔴)
- Personalized recommendations

📊 **Enhanced Analytics**
- API-powered dashboards
- Loss reason breakdown
- Hub efficiency comparison
- Session trends visualization

🔐 **Real Authentication**
- JWT token management
- Role-based access control
- Test account documentation

⚡ **WebSocket Integration**
- Auto-reconnect on disconnect
- Connection status indicator
- Real-time bag position updates

## 🔧 Configuration

Edit `config.py` to customize:
- Backend URL (default: `http://localhost:8000`)
- WebSocket URL (default: `ws://localhost:8000/ws`)
- Auto-refresh interval
- Risk thresholds
- Feature flags

## 📚 Documentation

- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Complete integration guide
- **[FRONTEND_API_GUIDE.md](FRONTEND_API_GUIDE.md)** - Detailed API documentation
- **[API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)** - Quick reference

## 🐛 Troubleshooting

**Backend Connection Issues:**
```bash
# Check backend health
curl http://localhost:8000/health

# Expected: {"status": "healthy", "version": "1.0.0"}
```

**Missing Dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

**WebSocket Not Connecting:**
- Verify backend WebSocket is enabled
- Check firewall settings
- Use "🔄 Reconectar WebSocket" button in sidebar

## 🚀 Quick Start Example

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start backend (in separate terminal)
cd backend && python main.py

# 3. Start frontend
streamlit run PAE_frontend.py

# 4. Login
# Use: admin / password
```

## 📈 Performance

- Supports **1000+ simultaneous baggage tracking**
- **<5s** refresh rate in API mode
- **Real-time** updates via WebSocket
- Optimized map rendering with Pydeck

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Export analytics to PDF/CSV
- [ ] Multi-language support (i18n)
- [ ] Mobile-responsive UI
- [ ] Historical data playback
- [ ] Custom alert rules

## 📝 License

This project is open-source. Feel free to modify and use it for your own tracking simulations!

## 📞 Support

- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health
- **Issues**: [GitHub Issues](https://github.com/victorarjona10/Frontend_PAE/issues)

---

**Version**: 2.0.0
**Last Updated**: January 2026
**Status**: ✅ Production Ready with Full Backend Integration
