import requests
import pandas as pd
from typing import List, Optional, Dict, Any
from .models import Bag, Airport, BagStatus
from datetime import datetime
import streamlit as st

# Backend API Configuration
API_BASE_URL = "http://localhost:8000"

class RealTimeService:
    """
    Service to interact with the OmniTrack Backend API.
    Provides methods for all available endpoints.
    """
    def __init__(self):
        self.bags: List[Bag] = []
        self.airports: List[Airport] = []
        self.last_update = datetime.now()
        self.token: Optional[str] = None
        self._check_health()
        self._load_airports()
        # Initial fetch of bags
        self._fetch_all_bags()

    def _check_health(self) -> bool:
        """Check if backend is available."""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                return True
        except Exception as e:
            st.warning(f"⚠️ Backend no disponible: {e}")
        return False

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers if token exists."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ==================== AUTHENTICATION ====================

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login to the API and get authentication token.
        Returns: {token, role, user_id, target_bag_id}
        """
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                # Fetch bags after login
                self._fetch_all_bags()
                return data
            else:
                return {"error": "Credenciales inválidas"}
        except Exception as e:
            return {"error": f"Error de conexión: {e}"}

    # ==================== AIRPORTS ====================

    def _load_airports(self):
        """Load all airports from the backend."""
        try:
            response = requests.get(f"{API_BASE_URL}/api/airports", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.airports = [
                    Airport(
                        code=a["code"],
                        name=a["name"],
                        lat=a["lat"],
                        lon=a["lon"]
                    ) for a in data
                ]
        except Exception as e:
            print(f"Error loading airports: {e}")
            # Fallback to some default airports
            self.airports = []

    def get_airports(self) -> List[Airport]:
        """Get all available airports."""
        if not self.airports:
            self._load_airports()
        return self.airports

    def get_airport(self, code: str) -> Optional[Airport]:
        """Get specific airport by code."""
        try:
            response = requests.get(f"{API_BASE_URL}/api/airports/{code}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return Airport(**data)
        except Exception as e:
            print(f"Error fetching airport {code}: {e}")
        return None

    # ==================== BAGGAGE ====================

    def tick(self):
        """
        In API mode, 'tick' fetches the latest data from the backend.
        """
        self._fetch_all_bags()

    def fetch_bags_for_passenger(self, bag_id: str) -> str:
        """
        Fetch a specific bag for a passenger.
        If bag_id doesn't exist, fetch all bags and filter or show first available.
        Returns the actual bag_id that was loaded.
        """
        bag_details = self.get_bag_details(bag_id)
        if bag_details:
            # Convert single bag to list
            self.bags = self._parse_bags_from_api([bag_details])
            return self.bags[0].id if self.bags else None
        else:
            # Bag not found - fallback: fetch all bags and try to find it
            print(f"⚠️ Bag {bag_id} not found via details endpoint, fetching all bags...")
            self._fetch_all_bags()
            # Try to find the bag in the list
            matching_bags = [b for b in self.bags if b.id == bag_id]
            if matching_bags:
                self.bags = matching_bags
                print(f"✅ Found bag {bag_id} in list")
                return matching_bags[0].id
            else:
                # Still not found - use first bag as demo or keep all bags
                if self.bags:
                    print(f"⚠️ Bag {bag_id} not found. Showing first available bag as demo.")
                    actual_bag_id = self.bags[0].id
                    self.bags = [self.bags[0]]
                    return actual_bag_id
                else:
                    print(f"❌ No bags available")
                    self.bags = []
                    return None

    def _fetch_all_bags(self, status: Optional[str] = None, owner_id: Optional[str] = None, limit: int = 100):
        """
        Fetch all bags from the backend with optional filters.
        """
        try:
            params = {"limit": limit}
            if status:
                params["status"] = status
            if owner_id:
                params["owner_id"] = owner_id

            response = requests.get(
                f"{API_BASE_URL}/api/bags",
                params=params,
                headers=self._get_headers(),
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                print(f"🔍 DEBUG: Received {len(data)} bags from API")
                print(f"🔍 DEBUG: Sample data: {data[:2] if data else 'No bags'}")
                self.bags = self._parse_bags_from_api(data)
                print(f"🔍 DEBUG: Parsed {len(self.bags)} bags")
                self.last_update = datetime.now()
            else:
                print(f"❌ Error fetching bags: HTTP {response.status_code}")
                print(f"❌ Response: {response.text}")
                self.bags = []

        except Exception as e:
            print(f"API Connection Error: {e}")
            self.bags = []

    def get_bag_details(self, bag_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific bag including history.
        """
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/bags/{bag_id}",
                headers=self._get_headers(),
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching bag {bag_id}: {e}")
        return None

    def scan_bag(self, bag_id: str, scanner_id: str, status: str, lat: float, lon: float) -> Dict[str, Any]:
        """
        Update bag position (simulate RFID scan).
        """
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/bags/scan",
                json={
                    "bag_id": bag_id,
                    "scanner_id": scanner_id,
                    "status": status,
                    "lat": lat,
                    "lon": lon
                },
                headers=self._get_headers(),
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            return {"error": str(e)}
        return {}

    def report_bag_issue(self, bag_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Report a bag issue (lost, delayed, damaged, misplaced).

        Args:
            bag_id: ID of the bag to report
            report_data: {
                "report_type": "LOST" | "DELAYED" | "DAMAGED" | "MISPLACED",
                "current_location": str,
                "expected_location": str,
                "timestamp": str (ISO format),
                "description": str,
                "passenger_location_lat": float,
                "passenger_location_lon": float
            }

        Returns:
            {
                "report_id": str,
                "bag_id": str,
                "status": str,
                "prediction": {
                    "loss_probability": float,
                    "risk_level": str,
                    "estimated_cause": str,
                    "recommendations": [str]
                },
                "created_at": str
            }
        """
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/bags/{bag_id}/report",
                json=report_data,
                headers=self._get_headers(),
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}

    # ==================== MACHINE LEARNING ====================

    def predict_risk(self, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict bag loss risk using ML model.

        Required fields in prediction_data:
        - origen, destino, aerolinea, time_of_day, retraso_min,
          transfers, airport_risk, viajero_vip, peso_kg
        """
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/ml/predict",
                json=prediction_data,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            return {"error": str(e)}
        return {}

    # ==================== ANALYTICS ====================

    def get_analytics_dashboard(self) -> Dict[str, Any]:
        """
        Get complete analytics dashboard data.
        Returns: {status_distribution, busiest_airports, session_trends}
        """
        try:
            response = requests.get(f"{API_BASE_URL}/api/analytics/dashboard", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching analytics: {e}")
        return {}

    def get_loss_analytics(self) -> Dict[str, Any]:
        """
        Get detailed loss analytics.
        Returns: {total_losses, loss_reasons, loss_status, avg_recovery_time_hours}
        """
        try:
            response = requests.get(f"{API_BASE_URL}/api/analytics/losses", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching loss analytics: {e}")
        return {}

    def get_top_airports(self) -> List[Dict[str, Any]]:
        """
        Get airports with most losses.
        Returns: [{airport_code, loss_count}, ...]
        """
        try:
            response = requests.get(f"{API_BASE_URL}/api/analytics/top-airports", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching top airports: {e}")
        return []

    def get_hub_statistics(self) -> Dict[str, Any]:
        """
        Get hub statistics.
        Returns: {total_hubs, data: [...]}
        """
        try:
            response = requests.get(f"{API_BASE_URL}/api/analytics/hub-statistics", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching hub statistics: {e}")
        return {}

    # ==================== HELPERS ====================

    def _parse_bags_from_api(self, data: List[Dict]) -> List[Bag]:
        """Convert API response to Bag objects."""
        bags = []
        for item in data:
            try:
                # Map API status to BagStatus enum
                status_map = {
                    "CHECK_IN": BagStatus.CHECK_IN,
                    "IN_TRANSIT": BagStatus.IN_TRANSIT,
                    "LANDED": BagStatus.LANDED,
                    "AT_GATE": BagStatus.AT_GATE,
                    "LOST": BagStatus.LOST,
                    "SECURITY": BagStatus.SECURITY,
                    "BAGGAGE_CLAIM": BagStatus.BAGGAGE_CLAIM,
                }

                status = status_map.get(item.get("status", "CHECK_IN"), BagStatus.CHECK_IN)

                # Get or create airports
                # API returns origin_code/destination_code, not origin/destination
                origin_code = item.get("origin_code", item.get("origin", "JFK"))
                destination_code = item.get("destination_code", item.get("destination", "LHR"))

                origin = self._get_or_create_airport(origin_code)
                destination = self._get_or_create_airport(destination_code)

                # API returns owner_name, not owner
                owner = item.get("owner_name", item.get("owner", "Unknown"))

                bag = Bag(
                    id=item["id"],
                    owner=owner,
                    origin=origin,
                    destination=destination,
                    current_lat=item.get("current_lat", item.get("lat", 0.0)),
                    current_lon=item.get("current_lon", item.get("lon", 0.0)),
                    status=status,
                    color=item.get("color", [0, 255, 0, 255]),
                    progress=item.get("progress", 0.0)
                )
                bags.append(bag)
            except Exception as e:
                print(f"❌ Error parsing bag: {e}")
                print(f"   Item data: {item}")
                continue
        return bags

    def _get_or_create_airport(self, code: str) -> Airport:
        """Get airport from cache or create a default one."""
        for airport in self.airports:
            if airport.code == code:
                return airport
        # Default fallback
        return Airport(code=code, name=code, lat=0.0, lon=0.0)

    def get_dataframe(self) -> pd.DataFrame:
        """
        Converts the fetched bag data into a DataFrame compatible with the Map Component.
        """
        if not self.bags:
            return pd.DataFrame(columns=[
                "id", "lat", "lon", "status", "origin", "destination",
                "owner", "color", "size_scale", "dest_lat", "dest_lon"
            ])

        data = []
        for bag in self.bags:
            data.append({
                "id": bag.id,
                "lat": bag.current_lat,
                "lon": bag.current_lon,
                "status": bag.status.value,
                "origin": bag.origin.name,
                "destination": bag.destination.name,
                "owner": bag.owner,
                "color": bag.color,
                "size_scale": 200 if bag.status == BagStatus.LOST else 50,
                "dest_lat": bag.destination.lat,
                "dest_lon": bag.destination.lon,
            })
        return pd.DataFrame(data)
