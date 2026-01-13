# 📡 API Documentation for Frontend Team

**Backend Version**: 1.0.0
**Base URL**: `http://localhost:8000`
**Date**: January 13, 2026

---

## 🔐 Authentication

### POST `/api/auth/login`

**Descripción**: Autentica un usuario y retorna un token JWT.

**Request**:
```json
{
  "username": "admin",
  "password": "password"
}
```

**Response 200**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "role": "ADMIN",              // "ADMIN" | "PASSENGER"
  "user_id": "USR-001",
  "target_bag_id": null         // ID de maleta si es PASSENGER
}
```

**Response 401**:
```json
{
  "detail": "Credenciales inválidas"
}
```

**Uso**:
- Llamar al iniciar sesión
- Guardar el `token` en localStorage/sessionStorage
- Incluir en header `Authorization: Bearer {token}` en requests protegidos

---

## ✈️ Airports

### GET `/api/airports`

**Descripción**: Lista todos los aeropuertos disponibles (20 aeropuertos).

**Request**: No requiere body ni autenticación.

**Response 200**:
```json
[
  {
    "code": "JFK",
    "name": "New York JFK",
    "lat": 40.6413,
    "lon": -73.7781
  },
  {
    "code": "LHR",
    "name": "London Heathrow",
    "lat": 51.4700,
    "lon": -0.4543
  }
  // ... 18 más
]
```

**Uso**:
- Cargar dropdown de aeropuertos
- Pintar aeropuertos en el mapa
- Validar códigos de aeropuerto

---

### GET `/api/airports/{code}`

**Descripción**: Obtiene un aeropuerto específico por su código IATA.

**URL Params**: `code` (string, ej: "JFK", "LHR", "MAD")

**Request**: No requiere body ni autenticación.

**Response 200**:
```json
{
  "code": "JFK",
  "name": "New York JFK",
  "lat": 40.6413,
  "lon": -73.7781
}
```

**Response 404**:
```json
{
  "detail": "Airport JFK not found"
}
```

**Uso**:
- Obtener detalles de un aeropuerto específico
- Centrar mapa en un aeropuerto

---

## 🎒 Baggage (Maletas)

### GET `/api/bags`

**Descripción**: Lista todas las maletas. Filtrable por estado y propietario.

**Query Params** (opcionales):
- `status` (string): Filtrar por estado ("CHECK_IN", "IN_TRANSIT", "DELAYED", "LOST", "DAMAGED")
- `owner_id` (string): Filtrar por ID de propietario
- `limit` (int, default: 100): Número máximo de resultados

**Request**:
```
GET /api/bags?status=IN_TRANSIT&limit=50
Authorization: Bearer {token}  // OPCIONAL pero recomendado
```

**Response 200**:
```json
[
  {
    "id": "286782513",
    "current_lat": 40.6413,
    "current_lon": -73.7781,
    "status": "CHECK_IN",
    "owner_name": "Passenger 1175",
    "origin_code": "VIE",
    "destination_code": "AGP",
    "color": [0, 255, 0, 255]    // RGBA para pintar en mapa
  }
  // ... más maletas
]
```

**Estados posibles**:
- `CHECK_IN`: Maleta facturada
- `IN_TRANSIT`: En tránsito
- `DELAYED`: Retrasada
- `LOST`: Perdida
- `DAMAGED`: Dañada
- `AT_GATE`: En puerta de embarque
- `LANDED`: Aterrizó

**Uso**:
- Mostrar lista de maletas en tabla
- Pintar maletas en mapa con color por estado
- Filtrar por estado en UI

---

### GET `/api/bags/{id}`

**Descripción**: Obtiene detalles completos de una maleta específica.

**URL Params**: `id` (string, ej: "286782513")

**Request**:
```
GET /api/bags/286782513
Authorization: Bearer {token}  // OPCIONAL
```

**Response 200**:
```json
{
  "id": "286782513",
  "status": "IN_TRANSIT",
  "history": [
    {
      "timestamp": "2026-01-13T10:00:00Z",
      "message": "Check In at VIE"
    },
    {
      "timestamp": "2026-01-13T10:45:00Z",
      "message": "Cleared Security"
    }
  ],
  "flight_details": {
    "flight_number": "AA100",
    "progress": 0.45,              // 0.0 a 1.0 (porcentaje de vuelo)
    "origin_lat": 48.1103,
    "origin_lon": 16.5697,
    "dest_lat": 36.8449,
    "dest_lon": -2.3701
  }
}
```

**Response 404**:
```json
{
  "detail": "Bag not found"
}
```

**Uso**:
- Mostrar detalles al hacer click en maleta
- Timeline de eventos
- Animación de progreso de vuelo

---

### POST `/api/bags/scan`

**Descripción**: Actualiza la posición de una maleta (simulación de escaneo RFID).

**Request**:
```json
{
  "bag_id": "286782513",
  "scanner_id": "GATE-G12-JFK",
  "status": "AT_GATE",           // Nuevo estado
  "lat": 40.6415,
  "lon": -73.7785
}
```

**Response 200**:
```json
{
  "message": "Bag scanned successfully",
  "bag_id": "286782513",
  "new_status": "AT_GATE",
  "timestamp": "2026-01-13T14:30:00Z"
}
```

**Uso**:
- Simular escaneo de maleta
- Actualizar posición manualmente (admin)
- Testing de actualizaciones en tiempo real

---

## 🤖 Machine Learning

### POST `/api/ml/predict`

**Descripción**: Predice el riesgo de pérdida de una maleta usando ML.

**Request**:
```json
{
  "origen": "JFK",               // Código IATA origen
  "destino": "LHR",              // Código IATA destino
  "aerolinea": "AA",             // Código aerolínea
  "time_of_day": "morning",      // "morning" | "afternoon" | "evening" | "night"
  "retraso_min": 15,             // Minutos de retraso (0-999)
  "transfers": 1,                // Número de conexiones (0-2)
  "airport_risk": 3,             // Riesgo del aeropuerto (1-5)
  "viajero_vip": 0,              // Es VIP: 0=no, 1=sí
  "peso_kg": 23.5                // Peso de maleta (kg)
}
```

**Response 200**:
```json
{
  "probabilidad_perdida": 0.0008921810076572001,  // 0.0 a 1.0
  "prediccion": 0,                                 // 0=no se pierde, 1=se pierde
  "risk_level": "LOW",                             // "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  "factors": [                                     // Factores de riesgo detectados
    "Una conexión",
    "Aeropuerto de riesgo medio (nivel 3/5)"
  ]
}
```

**Niveles de riesgo**:
- `LOW`: probabilidad < 0.3 (30%) → 🟢 Verde
- `MEDIUM`: 0.3 ≤ probabilidad < 0.6 → 🟡 Amarillo
- `HIGH`: 0.6 ≤ probabilidad < 0.8 → 🟠 Naranja
- `CRITICAL`: probabilidad ≥ 0.8 → 🔴 Rojo

**Uso**:
- Formulario de predicción de riesgo
- Dashboard de riesgo
- Alertas preventivas
- Mostrar badge de riesgo en cada maleta

---

## 📊 Analytics

### GET `/api/analytics/dashboard`

**Descripción**: Retorna métricas agregadas para el dashboard de analytics.

**Request**: No requiere body ni autenticación.

**Response 200**:
```json
{
  "status_distribution": {
    "Check In": 15,
    "In Transit": 45,
    "Delayed": 8,
    "Lost": 2,
    "Damaged": 1
  },
  "busiest_airports": [
    {
      "code": "LHR",
      "count": 120
    },
    {
      "code": "JFK",
      "count": 98
    }
    // ... top 10
  ],
  "session_trends": [
    {
      "timestamp": "10:00:00",
      "active_bags": 100,
      "lost_bags": 1
    },
    {
      "timestamp": "10:05:00",
      "active_bags": 105,
      "lost_bags": 1
    }
    // ... cada 5 minutos, última hora
  ]
}
```

**Uso**:
- Gráfico de distribución de estados (pie chart)
- Gráfico de aeropuertos más concurridos (bar chart)
- Gráfico de tendencias temporales (line chart)

---

### GET `/api/analytics/losses`

**Descripción**: Análisis detallado de pérdidas de maletas.

**Request**: No requiere body ni autenticación.

**Response 200**:
```json
{
  "total_losses": 45,
  "loss_reasons": {
    "MISSED_TRANSFER": 20,
    "MISHANDLING": 15,
    "THEFT": 5,
    "OTHER": 5
  },
  "loss_status": {
    "RECOVERED": 30,
    "PENDING": 10,
    "PERMANENT": 5
  },
  "avg_recovery_time_hours": 12.5
}
```

**Uso**:
- Dashboard de pérdidas
- Reportes de gestión
- KPIs de recuperación

---

### GET `/api/analytics/top-airports`

**Descripción**: Aeropuertos con más pérdidas de maletas.

**Request**: No requiere body ni autenticación.

**Response 200**:
```json
[
  {
    "airport_code": "JFK",
    "loss_count": 15
  },
  {
    "airport_code": "LHR",
    "loss_count": 12
  }
  // ... top 10
]
```

**Uso**:
- Ranking de aeropuertos problemáticos
- Heatmap de pérdidas

---

### GET `/api/analytics/hub-statistics`

**Descripción**: Estadísticas detalladas de aeropuertos hub.

**Request**: No requiere body ni autenticación.

**Response 200**:
```json
{
  "total_hubs": 20,
  "data": [
    {
      "airport_code": "JFK",
      "total_bags": 1500,
      "avg_handling_time_min": 25,
      "loss_rate": 0.015
      // ... más estadísticas
    }
    // ... más hubs
  ]
}
```

**Uso**:
- Dashboard de eficiencia de hubs
- Comparativas entre aeropuertos

---

## 🔴 WebSocket (Tiempo Real)

### WS `/ws`

**Descripción**: Conexión WebSocket para recibir actualizaciones en tiempo real.

**URL**: `ws://localhost:8000/ws`

**Conexión**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('✅ Conectado al WebSocket');
};

ws.onmessage = (event) => {
  const bagUpdate = JSON.parse(event.data);
  console.log('📦 Update:', bagUpdate);
  // Actualizar mapa/UI con nueva posición
};

ws.onerror = (error) => {
  console.error('❌ Error:', error);
};

ws.onclose = () => {
  console.log('🔌 Desconectado');
  // Reconectar automáticamente
};
```

**Mensajes recibidos**:
```json
{
  "id": "286782513",
  "current_lat": 40.6420,        // Nueva latitud
  "current_lon": -73.7790,       // Nueva longitud
  "status": "IN_TRANSIT",
  "owner_name": "Passenger 1175",
  "origin_code": "VIE",
  "destination_code": "AGP",
  "color": [255, 255, 0, 255]    // Color actualizado (RGBA)
}
```

**Frecuencia**: ~5 segundos por actualización

**Uso**:
- Animar movimiento de maletas en mapa
- Actualizar lista de maletas en tiempo real
- Mostrar notificaciones de cambios de estado

---

## 🛠️ Utility Endpoints

### GET `/`

**Descripción**: Información básica del API.

**Response 200**:
```json
{
  "message": "OmniTrack Baggage API",
  "version": "1.0.0",
  "status": "online",
  "docs": "/docs",
  "redoc": "/redoc",
  "websocket": "/ws/live-updates"
}
```

---

### GET `/health`

**Descripción**: Health check para monitoreo.

**Response 200**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Uso**:
- Verificar que el backend está disponible
- Monitoreo automático

---

## 🔑 Autenticación en Headers

Para endpoints protegidos (opcional pero recomendado):

```javascript
fetch('http://localhost:8000/api/bags', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
```

---

## 📋 Códigos de Estado HTTP

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| 200 | OK | Request exitoso |
| 401 | Unauthorized | Token inválido o expirado |
| 404 | Not Found | Recurso no encontrado (maleta, aeropuerto) |
| 422 | Validation Error | Datos de entrada inválidos |
| 500 | Server Error | Error interno del servidor |

---

## 🎨 Mapeo de Colores por Estado

Para pintar maletas en el mapa:

```javascript
const STATUS_COLORS = {
  "CHECK_IN": [0, 255, 0, 255],      // Verde
  "IN_TRANSIT": [0, 150, 255, 255],  // Azul
  "LANDED": [100, 200, 100, 255],    // Verde claro
  "AT_GATE": [255, 165, 0, 255],     // Naranja
  "DELAYED": [255, 200, 0, 255],     // Amarillo
  "LOST": [255, 0, 0, 255],          // Rojo
  "DAMAGED": [200, 0, 100, 255]      // Rojo oscuro
};
```

El backend ya envía el color correcto en el campo `color` de cada maleta.

---

## 🚀 Flujo de Integración Recomendado

### 1. Al cargar la app:
```javascript
// 1. Verificar salud del backend
await fetch('/health');

// 2. Cargar aeropuertos
const airports = await fetch('/api/airports');

// 3. Si hay login guardado, validar token
const token = localStorage.getItem('token');
// Si no hay token, mostrar pantalla de login
```

### 2. Después del login:
```javascript
// 1. Login
const { token, role, target_bag_id } = await fetch('/api/auth/login', {
  method: 'POST',
  body: JSON.stringify({ username, password })
});

// 2. Guardar token
localStorage.setItem('token', token);

// 3. Si PASSENGER, cargar su maleta específica
if (role === 'PASSENGER') {
  const bag = await fetch(`/api/bags/${target_bag_id}`);
}

// 4. Si ADMIN, cargar todas las maletas
if (role === 'ADMIN') {
  const bags = await fetch('/api/bags');
}

// 5. Conectar WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');
```

### 3. En el dashboard de analytics:
```javascript
// Cargar métricas
const dashboard = await fetch('/api/analytics/dashboard');
const losses = await fetch('/api/analytics/losses');
const topAirports = await fetch('/api/analytics/top-airports');

// Renderizar gráficos con los datos
```

### 4. En formulario de predicción:
```javascript
// Al enviar formulario
const prediction = await fetch('/api/ml/predict', {
  method: 'POST',
  body: JSON.stringify({
    origen: 'JFK',
    destino: 'LHR',
    // ... otros campos
  })
});

// Mostrar resultado con color según risk_level
const riskColor = {
  'LOW': 'green',
  'MEDIUM': 'yellow',
  'HIGH': 'orange',
  'CRITICAL': 'red'
}[prediction.risk_level];
```

---

## ⚠️ Consideraciones Importantes

### CORS
El backend tiene CORS habilitado para:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://localhost:8080` (Vue/otros)

### Rate Limiting
Actualmente no hay rate limiting. En producción se implementará.

### Paginación
`/api/bags` acepta parámetro `limit` (max 1000). Para más de 1000 maletas, implementar paginación con `offset`.

### WebSocket Reconnect
Implementar reconexión automática en caso de desconexión:
```javascript
function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:8000/ws');

  ws.onclose = () => {
    console.log('Reconectando en 3s...');
    setTimeout(connectWebSocket, 3000);
  };

  return ws;
}
```

---

## 📞 Contacto Backend

- **Servidor**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs (Swagger UI)
- **Logs**: `backend/server.log`
- **Tests**: `backend/test_api.sh`

---

## 📝 Ejemplos de Uso Completos

### Ejemplo 1: Login y obtener maletas
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'password'
  })
});
const { token } = await loginResponse.json();

// Obtener maletas
const bagsResponse = await fetch('http://localhost:8000/api/bags', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const bags = await bagsResponse.json();

console.log(`✅ ${bags.length} maletas cargadas`);
```

### Ejemplo 2: Predicción ML
```javascript
const prediction = await fetch('http://localhost:8000/api/ml/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    origen: 'JFK',
    destino: 'LHR',
    aerolinea: 'AA',
    time_of_day: 'morning',
    retraso_min: 15,
    transfers: 1,
    airport_risk: 3,
    viajero_vip: 0,
    peso_kg: 23.5
  })
});

const result = await prediction.json();
console.log(`Riesgo: ${result.risk_level} (${(result.probabilidad_perdida * 100).toFixed(1)}%)`);
```

### Ejemplo 3: WebSocket + Mapa
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
const markers = {}; // Marcadores del mapa

ws.onmessage = (event) => {
  const bag = JSON.parse(event.data);

  // Actualizar o crear marcador
  if (markers[bag.id]) {
    // Animar movimiento suave
    markers[bag.id].setLatLng([bag.current_lat, bag.current_lon]);
    markers[bag.id].setStyle({ color: `rgba(${bag.color.join(',')})` });
  } else {
    // Crear nuevo marcador
    markers[bag.id] = L.marker([bag.current_lat, bag.current_lon])
      .addTo(map);
  }
};
```

---

**Versión**: 1.0.0
**Última actualización**: 2026-01-13
**Base URL**: http://localhost:8000
**WebSocket**: ws://localhost:8000/ws
