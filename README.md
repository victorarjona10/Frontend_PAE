# 🧳 OmniTrack: Global Suitcase Tracking System

OmniTrack is a real-time simulation and visualization dashboard for tracking luggage across a global airport network. Built with **Streamlit** and **Pydeck**, it simulates status updates, flight paths, and baggage handling events in an interactive dark-mode interface.

## 🚀 Features

*   **Real-time Simulation**: Bags autonomously transition states (Check-in -> Security -> Gate -> In Transit -> Landed -> Baggage Claim).
*   **Live Map Visualization**: 
    *   View global bag positions on an interactive 3D map (Carto Dark theme).
    *   See active flight paths with animated arcs for bags in transit.
*   **Detailed Tracking**: customizable "Deep Dive" view to inspect individual bag history and timestamps.
*   **Modular Architecture**: Clean separation of concerns with a dedicated simulation engine (`services/`) and UI components (`components/`).

## 🛠️ Technology Stack

*   **Frontend**: Streamlit
*   **Visualization**: Pydeck (Deck.gl), Pandas
*   **Language**: Python 3.10+

## 📦 Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/victorarjona10/Frontend_PAE.git
    cd Frontend_PAE
    ```

2.  Install dependencies:
    ```bash
    pip install streamlit pandas pydeck numpy
    ```

## ▶️ Usage

Run the application using Streamlit:

```bash
streamlit run PAE_frontend.py
```

Open your browser to `http://localhost:8501`.

### Controls
*   **Sidebar**:
    *   **Start/Pause**: Toggle the simulation clock.
    *   **Step +1**: Manually advance time by one tick.
    *   **Filters**: View only lost bags, bags in flight, etc.
    *   **Search**: Find a specific bag by ID.

## 📂 Project Structure

```
├── PAE_frontend.py       # Main Application Entry Point
├── components/           # UI Modules
│   ├── bag_details.py    # Individual bag tracking view
│   ├── map_view.py       # Pydeck map configuration
│   └── metrics.py        # Dashboard key metrics cards
├── services/             # Logic Layer
│   ├── models.py         # Data classes (Bag, Airport)
│   └── simulation.py     # State machine and Data generation
└── README.md             # Project Documentation
```

## 📝 License

This project is open-source. Feel free to modify and use it for your own tracking simulations!
