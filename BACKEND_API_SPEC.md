# 🔌 Backend API Specification

This document defines the RESTful API and WebSocket protocols required to support the **OmniTrack** frontend application.

The backend should be implemented using a robust framework (e.g., FastAPI, Django, Node.js) and must support the following features:
1.  **Authentication**: Role-based access (Passenger vs. Admin).
2.  **Baggage Tracking**: CRUD operations and detailed history.
3.  **Real-Time Updates**: WebSocket connections for live map movement and alerts.
4.  **Analytics**: Aggregated data for dashboards.

---

## 1. Authentication & Users

### **POST** `/api/auth/login`
Authenticates a user and returns a session token/role.

*   **Request Body**:
    ```json
    {
      "username": "admin",      // or "passenger_1"
      "password": "password"
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "token": "eyJhbGciOiJIUzI1Ni...",
      "role": "ADMIN",          // Enum: "ADMIN", "PASSENGER"
      "user_id": "USR-001",
      "target_bag_id": null     // If PASSENGER, this is the bag they are tracking
    }
    ```

---

## 2. Baggage Resources

### **GET** `/api/bags`
Retrieves a list of bags. Behavior depends on the user's role.

*   **Query Parameters**:
    *   `status`: (Optional) Filter by status (e.g., `LOST`, `IN_TRANSIT`).
    *   `owner_id`: (Optional) Get bags for a specific passenger.
    *   `limit`: (Default: 100) Pagination limit.
*   **Response Body**:
    ```json
    [
      {
        "id": "BAG-1001",
        "current_lat": 40.6413,
        "current_lon": -73.7781,
        "status": "CHECK_IN",
        "owner_name": "John Doe",
        "origin_code": "JFK",
        "destination_code": "LHR",
        "color": [255, 0, 0, 255] // RGBA for visualization
      },
      ...
    ]
    ```

### **GET** `/api/bags/{id}`
Retrieves detailed information for a single bag.

*   **Response Body**:
    ```json
    {
      "id": "BAG-1001",
      "status": "IN_TRANSIT",
      "history": [
        {"timestamp": "2023-10-27T10:00:00Z", "message": "Check In at JFK"},
        {"timestamp": "2023-10-27T10:45:00Z", "message": "Cleared Security"}
      ],
      "flight_details": {
        "flight_number": "AA100",
        "progress": 0.45,   // 0.0 to 1.0
        "origin_lat": 40.6413,
        "origin_lon": -73.7781,
        "dest_lat": 51.4700,
        "dest_lon": -0.4543
      }
    }
    ```

### **POST** `/api/bags/scan`
Used by physical scanners to update bag status.

*   **Request Body**:
    ```json
    {
      "bag_id": "BAG-1001",
      "scanner_id": "GATE-G12-JFK",
      "status": "AT_GATE",
      "lat": 40.6415,
      "lon": -73.7785
    }
    ```

---

## 3. Analytics & Reporting

### **GET** `/api/analytics/dashboard`
Returns aggregated statistics for the "Analytics" tab.

*   **Response Body**:
    ```json
    {
      "status_distribution": {
        "Check In": 15,
        "In Transit": 45,
        "Landed": 20,
        "Lost": 2
      },
      "busiest_airports": [
        {"code": "LHR", "count": 120},
        {"code": "JFK", "count": 98}
      ],
      "session_trends": [
        {"timestamp": "10:00:00", "active_bags": 100, "lost_bags": 1},
        {"timestamp": "10:05:00", "active_bags": 105, "lost_bags": 1}
      ]
    }
    ```

---

## 4. Airport Resources

### **GET** `/api/airports`
Returns the static list of supported airports.

*   **Response Body**:
    ```json
    [
      {"code": "JFK", "name": "New York JFK", "lat": 40.6413, "lon": -73.7781},
      {"code": "LHR", "name": "London Heathrow", "lat": 51.4700, "lon": -0.4543},
      {"code": "DUB", "name": "Dublin Airport", "lat": 53.4264, "lon": -6.2499},
      {"code": "HND", "name": "Tokyo Haneda", "lat": 35.5494, "lon": 139.7798},
      {"code": "DXB", "name": "Dubai Intl", "lat": 25.2532, "lon": 55.3657},
      // ... include all supported airports
    ]
    ```

---

## 5. Real-Time Updates (WebSocket)

### **WS** `/ws/live-updates`
The server pushes messages for **Map Updates** and **Critical Alerts**.

*   **Event: Bag Update (High Frequency)**
    *   Used to animate bag movement on the frontend map.
    ```json
    {
      "type": "BAG_UPDATE",
      "bag_id": "BAG-1001",
      "new_status": "IN_TRANSIT",
      "lat": 45.123,
      "lon": -30.456,
      "progress": 0.67
    }
    ```

*   **Event: Critical Alert (Low Frequency)**
    *   Used for the **Notification Center** and Toast popups.
    ```json
    {
      "type": "ALERT",
      "severity": "CRITICAL", // "INFO", "WARNING", "CRITICAL"
      "message": "BAG-1001 reported LOST at JFK!",
      "timestamp": "2023-10-27T11:00:00Z"
    }
    ```
