import streamlit as st
import json
import time
from streamlit_autorefresh import st_autorefresh
import threading
import queue

# Note: WebSocket integration in Streamlit requires careful handling
# This module provides utilities for WebSocket connection

WS_URL = "ws://localhost:8000/ws"

class WebSocketClient:
    """
    WebSocket client for real-time bag updates.

    Note: Streamlit's architecture makes direct WebSocket integration challenging.
    This implementation uses polling as a fallback, but provides the structure
    for WebSocket integration using external libraries.
    """

    def __init__(self):
        self.ws_url = WS_URL
        self.connected = False
        self.message_queue = queue.Queue()

    def connect(self):
        """
        Attempt to connect to WebSocket server.
        In production, this would use websocket-client library.
        """
        try:
            # Import websocket library if available
            import websocket

            def on_message(ws, message):
                """Handle incoming WebSocket messages."""
                try:
                    data = json.loads(message)
                    self.message_queue.put(data)
                except Exception as e:
                    print(f"Error processing message: {e}")

            def on_error(ws, error):
                print(f"WebSocket error: {error}")
                self.connected = False

            def on_close(ws, close_status_code, close_msg):
                print("WebSocket connection closed")
                self.connected = False

            def on_open(ws):
                print("WebSocket connection established")
                self.connected = True

            # Create WebSocket connection
            ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )

            # Run in a separate thread
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()

            return True

        except ImportError:
            st.warning("⚠️ websocket-client no instalado. Ejecuta: pip install websocket-client")
            return False
        except Exception as e:
            st.error(f"Error conectando WebSocket: {e}")
            return False

    def get_updates(self):
        """Get all pending updates from the queue."""
        updates = []
        while not self.message_queue.empty():
            try:
                updates.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return updates

    def is_connected(self):
        """Check if WebSocket is connected."""
        return self.connected


def setup_realtime_updates(interval_ms: int = 5000):
    """
    Setup auto-refresh for real-time updates.

    Args:
        interval_ms: Refresh interval in milliseconds (default: 5000 = 5 seconds)

    Returns:
        Current refresh count
    """
    try:
        from streamlit_autorefresh import st_autorefresh
        # Auto-refresh every interval_ms
        count = st_autorefresh(interval=interval_ms, key="realtime_refresh")
        return count
    except ImportError:
        st.warning("⚠️ streamlit-autorefresh no disponible. Instala con: pip install streamlit-autorefresh")
        return 0


def show_websocket_status():
    """Display WebSocket connection status in sidebar."""
    if 'ws_client' not in st.session_state:
        st.session_state.ws_client = WebSocketClient()

    ws_client = st.session_state.ws_client

    with st.sidebar:
        st.divider()
        st.caption("🔴 Conexión en Tiempo Real")

        if ws_client.is_connected():
            st.success("✅ WebSocket Conectado")

            # Show update count
            updates = ws_client.get_updates()
            if updates:
                st.info(f"📦 {len(updates)} actualizaciones recibidas")
        else:
            st.warning("⚠️ WebSocket Desconectado")

            if st.button("🔄 Reconectar WebSocket"):
                with st.spinner("Conectando..."):
                    if ws_client.connect():
                        st.success("Conectado!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("No se pudo conectar")
