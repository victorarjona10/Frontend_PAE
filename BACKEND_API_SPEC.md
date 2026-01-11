# 🔌 Backend API Specification (Draft)

To transition **OmniTrack** from a simulation to a real-world application, you will need a backend API (e.g., FastAPI, Django, or Node.js) to manage the data.

Here are the core RESTful endpoints required to support the current frontend features.

## 1. Baggage Resources

### **GET** `/api/bags`
Retrieves a list of all suitcases. Used for the **Main Map** and **Metrics**.

*   **Query Parameters (Filters):**
    *   `status`: (Optional) Filter by status (e.g., `?status=LOST`).
    *   `flight_id`: (Optional) Get all bags on a specific flight.
*   **Response Body:**
    ```json
    [
      {
        "id": "BAG-1001",
        "current_lat": 40.6413,
        "current_lon": -73.7781,
        "status": "CHECK_IN",
        "owner_name": "John Doe",
        "origin_code": "JFK",
        "destination_code": "LHR"
      },
      ...
    ]
    ```

### **GET** `/api/bags/{id}`
Retrieves detailed information for a single bag. Used for the **Bag Detail View**.

*   **Response Body:**
    ```json
    {
      "id": "BAG-1001",
      "status": "IN_TRANSIT",
      "history": [
        {"timestamp": "2023-10-27T10:00:00Z", "event": "Check In at JFK"},
        {"timestamp": "2023-10-27T10:45:00Z", "event": "Cleared Security"}
      ],
      "flight_details": {
        "flight_number": "AA100",
        "progress": 0.45
      }
    }
    ```

### **POST** `/api/bags/scan`
Your physical IoT scanners would hit this endpoint to update a bag's location/status.

*   **Request Body:**
    ```json
    {
      "bag_id": "BAG-1001",
      "scanner_id": "GATE-G12-JFK",
      "status": "AT_GATE",
      "lat": 40.6415,
      "lon": -73.7785
    }
    ```

## 2. Airport Resources

### **GET** `/api/airports`
Returns the static list of supported airports to populate frontend dropdowns/maps.

*   **Response Body:**
    ```json
    [
      {"code": "JFK", "name": "New York JFK", "lat": 40.64, "lon": -73.77},
      {"code": "LHR", "name": "London Heathrow", "lat": 51.47, "lon": -0.45}
    ]
    ```

## 3. Real-Time Updates (WebSocket)

For a truly "Live" map, instead of polling `GET /api/bags` every few seconds, you should implement a WebSocket.

### **WS** `/ws/live-updates`
*   **Behavior**: The server pushes a message whenever a bag's status changes.
*   **Message Format:**
    ```json
    {
      "type": "BAG_UPDATE",
      "bag_id": "BAG-1001",
      "new_status": "LANDED",
      "lat": ...,
      "lon": ...
    }
    ```
