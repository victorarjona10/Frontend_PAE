import random
import math
import pandas as pd
from typing import List, Dict
from .models import Bag, Airport, BagStatus

# Configuration
AIRPORTS = {
    "JFK": Airport("JFK", "New York JFK", 40.6413, -73.7781),
    "LHR": Airport("LHR", "London Heathrow", 51.4700, -0.4543),
    "HND": Airport("HND", "Tokyo Haneda", 35.5494, 139.7798),
    "DXB": Airport("DXB", "Dubai Intl", 25.2532, 55.3657),
    "CDG": Airport("CDG", "Paris Charles de Gaulle", 49.0097, 2.5479),
    "SIN": Airport("SIN", "Singapore Changi", 1.3644, 103.9915),
    "SYD": Airport("SYD", "Sydney Kingsford Smith", -33.9399, 151.1753),
    "BCN": Airport("BCN", "Barcelona El Prat", 41.2974, 2.0833),
    "LAX": Airport("LAX", "Los Angeles Intl", 33.9416, -118.4085),
    "GRU": Airport("GRU", "São Paulo Guarulhos", -23.4356, -46.4731),
}

STATUS_COLORS = {
    BagStatus.CHECK_IN: [169, 169, 169, 200],      # Grey
    BagStatus.SECURITY: [255, 255, 0, 200],        # Yellow
    BagStatus.AT_GATE: [100, 149, 237, 200],       # Cornflower Blue
    BagStatus.IN_TRANSIT: [30, 144, 255, 255],     # Dodger Blue (Bright)
    BagStatus.LANDED: [50, 205, 50, 200],          # Lime Green
    BagStatus.BAGGAGE_CLAIM: [255, 165, 0, 200],   # Orange
    BagStatus.CLAIMED: [0, 128, 0, 150],           # Dark Green
    BagStatus.LOST: [255, 0, 0, 255],              # Red
}

class SimulationEngine:
    def __init__(self, num_bags=50):
        self.bags: List[Bag] = []
        self._initialize_bags(num_bags)

    def _initialize_bags(self, count):
        codes = list(AIRPORTS.keys())
        for i in range(count):
            origin_code = random.choice(codes)
            dest_code = random.choice([c for c in codes if c != origin_code])
            
            origin = AIRPORTS[origin_code]
            dest = AIRPORTS[dest_code]
            
            # Randomize initial state logic
            state_val = random.random()
            if state_val < 0.2:
                status = BagStatus.CHECK_IN
                lat, lon = self._jitter(origin.lat, origin.lon)
            elif state_val < 0.3:
                status = BagStatus.SECURITY
                lat, lon = self._jitter(origin.lat, origin.lon)
            elif state_val < 0.4:
                status = BagStatus.AT_GATE
                lat, lon = self._jitter(origin.lat, origin.lon)
            elif state_val < 0.7:
                status = BagStatus.IN_TRANSIT
                # Start somewhere on the path
                progress = random.random()
                lat, lon = self._interpolate_pos(origin, dest, progress)
            elif state_val < 0.8:
                status = BagStatus.LANDED
                lat, lon = dest.lat, dest.lon
            elif state_val < 0.95:
                status = BagStatus.BAGGAGE_CLAIM
                lat, lon = self._jitter(dest.lat, dest.lon)
            else:
                status = BagStatus.LOST
                lat, lon = self._jitter(origin.lat, origin.lon) # Stuck at origin?

            bag = Bag(
                id=f"BAG-{1000+i}",
                owner=f"Passenger {i}",
                origin=origin,
                destination=dest,
                current_lat=lat,
                current_lon=lon,
                status=status,
                color=STATUS_COLORS[status]
            )
            
            if status == BagStatus.IN_TRANSIT:
                bag.progress = random.random()
                
            bag.update_history(f"Bag created at {origin.name}")
            self.bags.append(bag)

    def _jitter(self, lat, lon, scale=0.02):
        return lat + random.normalvariate(0, scale), lon + random.normalvariate(0, scale)

    def _interpolate_pos(self, origin, dest, t):
        # Simple linear interpolation for now (could be Great Circle)
        lat = origin.lat + (dest.lat - origin.lat) * t
        lon = origin.lon + (dest.lon - origin.lon) * t
        return lat, lon

    def _great_circle_pos(self, origin, dest, t):
        # Placeholder for more complex visualization logic if needed
        return self._interpolate_pos(origin, dest, t)

    def tick(self):
        """Advances the state of the simulation."""
        for bag in self.bags:
            if bag.status == BagStatus.CHECK_IN:
                if random.random() < 0.1:
                    bag.status = BagStatus.SECURITY
                    bag.update_history("Cleared Check-in")
            
            elif bag.status == BagStatus.SECURITY:
                if random.random() < 0.1:
                    bag.status = BagStatus.AT_GATE
                    bag.update_history("Cleared Security")

            elif bag.status == BagStatus.AT_GATE:
                if random.random() < 0.05:
                    bag.status = BagStatus.IN_TRANSIT
                    bag.progress = 0.0
                    bag.update_history("Boarded Flight")

            elif bag.status == BagStatus.IN_TRANSIT:
                bag.progress += 0.02 # Move 2% per tick
                if bag.progress >= 1.0:
                    bag.status = BagStatus.LANDED
                    bag.current_lat, bag.current_lon = bag.destination.lat, bag.destination.lon
                    bag.update_history(f"Landed at {bag.destination.name}")
                else:
                    lat, lon = self._interpolate_pos(bag.origin, bag.destination, bag.progress)
                    bag.current_lat = lat
                    bag.current_lon = lon

            elif bag.status == BagStatus.LANDED:
                if random.random() < 0.1:
                    bag.status = BagStatus.BAGGAGE_CLAIM
                    bag.update_history("Unloaded to Baggage Claim")

            elif bag.status == BagStatus.BAGGAGE_CLAIM:
                if random.random() < 0.05:
                    bag.status = BagStatus.CLAIMED
                    bag.update_history("Picked up by owner")
                    
            # Lost bags stay lost... until found? (Not implemented)

    def get_dataframe(self):
        """Returns a Pandas DataFrame for Pydeck."""
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
                # For arcs
                "dest_lat": bag.destination.lat,
                "dest_lon": bag.destination.lon,
            })
        return pd.DataFrame(data)
