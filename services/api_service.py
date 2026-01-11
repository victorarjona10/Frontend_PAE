import requests
import pandas as pd
from typing import List, Optional
from .models import Bag, Airport, BagStatus
from datetime import datetime

# Placeholder URL - User would change this in the future
API_BASE_URL = "http://localhost:8000/api"

class RealTimeService:
    def __init__(self):
        self.bags: List[Bag] = []
        self.last_update = datetime.now()
        
    def tick(self):
        """
        In API mode, 'tick' fetches the latest data from the backend.
        It does not simulate movement locally.
        """
        self._fetch_all_bags()

    def _fetch_all_bags(self):
        try:
            # Mocking the call since we don't assume the backend exists yet.
            # In a real scenario, this would be:
            # response = requests.get(f"{API_BASE_URL}/bags")
            # data = response.json()
            
            # For now, we print to console so the user sees it's trying to connect
            print(f"[{datetime.now()}] Attempting to fetch live data from {API_BASE_URL}/bags...")
            
            # Since there is no backend, we keep the list empty or raise a warning
            # self.bags = [parse_json_to_bag(b) for b in data]
            self.bags = [] 
            
        except Exception as e:
            print(f"API Connection Error: {e}")

    def get_dataframe(self) -> pd.DataFrame:
        """
        Converts the fetched bag data into a DataFrame compatible with the Map Component.
        """
        if not self.bags:
            # Return empty structure if no data
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
