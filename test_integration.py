#!/usr/bin/env python3
"""
Test script to verify backend API integration.
Run this before starting the frontend to ensure everything is working.
"""

import requests
import json

# Try to import colorama for colored output, fallback to no colors
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORS = True
except ImportError:
    # Fallback: no colors
    class Fore:
        GREEN = RED = YELLOW = CYAN = MAGENTA = ""
    class Style:
        RESET_ALL = ""
    HAS_COLORS = False
    print("Note: Install 'colorama' for colored output: pip install colorama")

API_BASE_URL = "http://localhost:8000"

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text:^60}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

def test_endpoint(method, endpoint, description, data=None, expected_status=200):
    """Test a single API endpoint."""
    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"{Fore.RED}✗ Unsupported method: {method}")
            return False

        if response.status_code == expected_status:
            print(f"{Fore.GREEN}✓ {description}")
            return True
        else:
            print(f"{Fore.RED}✗ {description} (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ {description} - Connection refused")
        print(f"{Fore.YELLOW}  → Make sure backend is running on {API_BASE_URL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}✗ {description} - Error: {e}")
        return False

def main():
    """Run all API tests."""
    print(f"\n{Fore.MAGENTA}🧪 OmniTrack Backend Integration Test Suite")
    print(f"{Fore.MAGENTA}Testing API at: {API_BASE_URL}\n")

    results = []

    # ==================== HEALTH CHECK ====================
    print_header("Health & Info")
    results.append(test_endpoint("GET", "/health", "Health check"))
    results.append(test_endpoint("GET", "/", "API info"))

    # ==================== AUTHENTICATION ====================
    print_header("Authentication")

    # Test admin login
    login_data = {"username": "admin", "password": "password"}
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ Admin login successful")
            token = response.json().get("token")
            print(f"  {Fore.CYAN}→ Token: {token[:30]}...")
            results.append(True)
        else:
            print(f"{Fore.RED}✗ Admin login failed")
            results.append(False)
    except Exception as e:
        print(f"{Fore.RED}✗ Admin login - Error: {e}")
        results.append(False)

    # Test passenger login
    passenger_data = {"username": "passenger_1", "password": "password"}
    results.append(test_endpoint("POST", "/api/auth/login", "Passenger login", passenger_data))

    # ==================== AIRPORTS ====================
    print_header("Airports")

    try:
        response = requests.get(f"{API_BASE_URL}/api/airports", timeout=5)
        if response.status_code == 200:
            airports = response.json()
            print(f"{Fore.GREEN}✓ Get all airports ({len(airports)} airports)")
            results.append(True)
        else:
            print(f"{Fore.RED}✗ Get all airports")
            results.append(False)
    except Exception as e:
        print(f"{Fore.RED}✗ Get all airports - Error: {e}")
        results.append(False)

    results.append(test_endpoint("GET", "/api/airports/JFK", "Get specific airport (JFK)"))

    # ==================== BAGGAGE ====================
    print_header("Baggage")

    try:
        response = requests.get(f"{API_BASE_URL}/api/bags?limit=10", timeout=5)
        if response.status_code == 200:
            bags = response.json()
            print(f"{Fore.GREEN}✓ Get all bags ({len(bags)} bags)")

            # Test getting specific bag
            if len(bags) > 0:
                bag_id = bags[0]["id"]
                results.append(True)

                # Test bag details
                detail_response = requests.get(f"{API_BASE_URL}/api/bags/{bag_id}", timeout=5)
                if detail_response.status_code == 200:
                    print(f"{Fore.GREEN}✓ Get bag details ({bag_id})")
                    results.append(True)
                else:
                    print(f"{Fore.RED}✗ Get bag details")
                    results.append(False)
            else:
                results.append(False)
        else:
            print(f"{Fore.RED}✗ Get all bags")
            results.append(False)
    except Exception as e:
        print(f"{Fore.RED}✗ Get all bags - Error: {e}")
        results.append(False)

    # ==================== MACHINE LEARNING ====================
    print_header("Machine Learning")

    ml_data = {
        "origen": "JFK",
        "destino": "LHR",
        "aerolinea": "AA",
        "time_of_day": "morning",
        "retraso_min": 15,
        "transfers": 1,
        "airport_risk": 3,
        "viajero_vip": 0,
        "peso_kg": 23.5
    }

    try:
        response = requests.post(f"{API_BASE_URL}/api/ml/predict", json=ml_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            prob = result.get("probabilidad_perdida", 0)
            risk = result.get("risk_level", "UNKNOWN")
            print(f"{Fore.GREEN}✓ ML Prediction (Risk: {risk}, Prob: {prob*100:.2f}%)")
            results.append(True)
        else:
            print(f"{Fore.RED}✗ ML Prediction")
            results.append(False)
    except Exception as e:
        print(f"{Fore.RED}✗ ML Prediction - Error: {e}")
        results.append(False)

    # ==================== ANALYTICS ====================
    print_header("Analytics")

    results.append(test_endpoint("GET", "/api/analytics/dashboard", "Analytics dashboard"))
    results.append(test_endpoint("GET", "/api/analytics/losses", "Loss analytics"))
    results.append(test_endpoint("GET", "/api/analytics/top-airports", "Top airports"))
    results.append(test_endpoint("GET", "/api/analytics/hub-statistics", "Hub statistics"))

    # ==================== WEBSOCKET ====================
    print_header("WebSocket")

    print(f"{Fore.YELLOW}ℹ WebSocket test requires websocket-client library")
    print(f"{Fore.YELLOW}  Run: pip install websocket-client")

    try:
        import websocket

        ws_connected = False
        def on_open(ws):
            nonlocal ws_connected
            ws_connected = True
            ws.close()

        def on_error(ws, error):
            pass

        ws = websocket.WebSocketApp(
            "ws://localhost:8000/ws",
            on_open=on_open,
            on_error=on_error
        )

        import threading
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        import time
        time.sleep(2)

        if ws_connected:
            print(f"{Fore.GREEN}✓ WebSocket connection")
            results.append(True)
        else:
            print(f"{Fore.RED}✗ WebSocket connection")
            results.append(False)
    except ImportError:
        print(f"{Fore.YELLOW}⊘ WebSocket test skipped (library not installed)")
    except Exception as e:
        print(f"{Fore.RED}✗ WebSocket connection - Error: {e}")
        results.append(False)

    # ==================== SUMMARY ====================
    print_header("Test Summary")

    total = len(results)
    passed = sum(results)
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n{Fore.CYAN}Total Tests: {total}")
    print(f"{Fore.GREEN}Passed: {passed}")
    print(f"{Fore.RED}Failed: {failed}")
    print(f"{Fore.CYAN}Success Rate: {success_rate:.1f}%\n")

    if success_rate == 100:
        print(f"{Fore.GREEN}{'✓' * 60}")
        print(f"{Fore.GREEN}All tests passed! Backend is ready. 🎉")
        print(f"{Fore.GREEN}{'✓' * 60}\n")
        print(f"{Fore.CYAN}You can now run: streamlit run PAE_frontend.py")
    elif success_rate >= 70:
        print(f"{Fore.YELLOW}{'⚠' * 60}")
        print(f"{Fore.YELLOW}Most tests passed. Some features may be limited.")
        print(f"{Fore.YELLOW}{'⚠' * 60}\n")
    else:
        print(f"{Fore.RED}{'✗' * 60}")
        print(f"{Fore.RED}Many tests failed. Check backend configuration.")
        print(f"{Fore.RED}{'✗' * 60}\n")
        print(f"{Fore.YELLOW}Troubleshooting:")
        print(f"{Fore.YELLOW}1. Ensure backend is running: cd backend && python main.py")
        print(f"{Fore.YELLOW}2. Check backend URL: {API_BASE_URL}")
        print(f"{Fore.YELLOW}3. Verify firewall settings")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user.")
