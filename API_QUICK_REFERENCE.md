# 🚀 API Quick Reference for Frontend

**Base URL**: `http://localhost:8000`
**WebSocket**: `ws://localhost:8000/ws`

---

## 📋 Endpoints Summary

| Método | Endpoint | Auth | Descripción | Response |
|--------|----------|------|-------------|----------|
| **POST** | `/api/auth/login` | ❌ | Login usuario | `{token, role, user_id, target_bag_id}` |
| **GET** | `/api/airports` | ❌ | Lista aeropuertos (20) | `[{code, name, lat, lon}, ...]` |
| **GET** | `/api/airports/{code}` | ❌ | Aeropuerto específico | `{code, name, lat, lon}` |
| **GET** | `/api/bags` | ⚠️ | Lista maletas + filtros | `[{id, lat, lon, status, color}, ...]` |
| **GET** | `/api/bags/{id}` | ⚠️ | Detalle de maleta | `{id, status, history, flight_details}` |
| **POST** | `/api/bags/scan` | ⚠️ | Actualizar posición | `{message, bag_id, new_status, timestamp}` |
| **POST** | `/api/ml/predict` | ❌ | Predicción de riesgo | `{probabilidad_perdida, risk_level, factors}` |
| **GET** | `/api/analytics/dashboard` | ❌ | Dashboard completo | `{status_distribution, busiest_airports, trends}` |
| **GET** | `/api/analytics/losses` | ❌ | Análisis pérdidas | `{total_losses, loss_reasons, avg_recovery}` |
| **GET** | `/api/analytics/top-airports` | ❌ | Top aeropuertos pérdidas | `[{airport_code, loss_count}, ...]` |
| **GET** | `/api/analytics/hub-statistics` | ❌ | Stats de hubs | `{total_hubs, data: [{...}]}` |
| **GET** | `/health` | ❌ | Health check | `{status: "healthy", version}` |
| **GET** | `/` | ❌ | Info API | `{message, version, status, docs}` |
| **WS** | `/ws` | ❌ | Actualizaciones tiempo real | Stream de `{id, lat, lon, status, color}` |

**Leyenda Auth**:
- ❌ = No requiere autenticación
- ⚠️ = Opcional (recomendado para filtrar por usuario)

---

## 🔐 Authentication Flow

```javascript
// 1. Login
const { token, role, target_bag_id } = await fetch('/api/auth/login', {
  method: 'POST',
  body: JSON.stringify({ username, password })
}).then(r => r.json());

// 2. Guardar
localStorage.setItem('token', token);

// 3. Usar en requests
fetch('/api/bags', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

**Usuarios de prueba**:
- `admin` / `password` → ADMIN (todas las maletas)
- `passenger_1` / `password` → PASSENGER (maleta BAG1000000001)
- `passenger_2` / `password` → PASSENGER (maleta BAG1000000050)

---

## 🎨 Estados y Colores

| Estado | Color RGBA | Descripción |
|--------|-----------|-------------|
| `CHECK_IN` | `[0, 255, 0, 255]` | 🟢 Maleta facturada |
| `IN_TRANSIT` | `[0, 150, 255, 255]` | 🔵 En tránsito |
| `LANDED` | `[100, 200, 100, 255]` | 🟢 Aterrizó |
| `AT_GATE` | `[255, 165, 0, 255]` | 🟠 En puerta |
| `DELAYED` | `[255, 200, 0, 255]` | 🟡 Retrasada |
| `LOST` | `[255, 0, 0, 255]` | 🔴 Perdida |
| `DAMAGED` | `[200, 0, 100, 255]` | 🔴 Dañada |

El backend envía el color correcto en cada maleta.

---

## 🤖 ML Risk Levels

| Level | Probabilidad | Color | Badge |
|-------|--------------|-------|-------|
| `LOW` | < 0.3 (30%) | 🟢 Verde | Bajo riesgo |
| `MEDIUM` | 0.3 - 0.6 | 🟡 Amarillo | Riesgo moderado |
| `HIGH` | 0.6 - 0.8 | 🟠 Naranja | Alto riesgo |
| `CRITICAL` | ≥ 0.8 (80%) | 🔴 Rojo | Riesgo crítico |

---

## 🌍 Aeropuertos Disponibles

```
JFK (New York), LHR (London), DXB (Dubai), HND (Tokyo)
CDG (Paris), AMS (Amsterdam), FRA (Frankfurt), BCN (Barcelona)
MAD (Madrid), FCO (Rome), MUC (Munich), ZRH (Zurich)
VIE (Vienna), CPH (Copenhagen), ARN (Stockholm), DUB (Dublin)
BRU (Brussels), LIS (Lisbon), OSL (Oslo), AGP (Málaga)
```

---

## 🔴 WebSocket Integration

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// Reconexión automática
ws.onclose = () => {
  console.log('Reconectando...');
  setTimeout(() => connectWS(), 3000);
};

// Recibir updates
ws.onmessage = (event) => {
  const bag = JSON.parse(event.data);
  updateMapMarker(bag.id, bag.current_lat, bag.current_lon);
  updateBagStatus(bag.id, bag.status);
};
```

**Frecuencia**: ~5 segundos por update
**Formato**: Mismo que `/api/bags`

---

## 📊 Analytics Dashboard Data

```javascript
const {
  status_distribution,    // { "Check In": 15, "In Transit": 45, ... }
  busiest_airports,       // [{ code: "LHR", count: 120 }, ...]
  session_trends          // [{ timestamp: "10:00", active_bags: 100, lost_bags: 1 }, ...]
} = await fetch('/api/analytics/dashboard').then(r => r.json());

// Para gráficos:
// - Pie chart: status_distribution
// - Bar chart: busiest_airports
// - Line chart: session_trends
```

---

## 🎯 ML Prediction Input

```javascript
const prediction = await fetch('/api/ml/predict', {
  method: 'POST',
  body: JSON.stringify({
    origen: 'JFK',           // Required: Código IATA
    destino: 'LHR',          // Required: Código IATA
    aerolinea: 'AA',         // Required: Código aerolínea
    time_of_day: 'morning',  // Required: morning|afternoon|evening|night
    retraso_min: 15,         // Required: 0-999
    transfers: 1,            // Required: 0-2
    airport_risk: 3,         // Required: 1-5
    viajero_vip: 0,          // Required: 0|1
    peso_kg: 23.5            // Required: float
  })
}).then(r => r.json());

// Output: { probabilidad_perdida, prediccion, risk_level, factors }
```

---

## ⚡ Performance Tips

### 1. Caching
```javascript
// Cachear aeropuertos (no cambian)
const airports = localStorage.getItem('airports') ||
  await fetch('/api/airports').then(r => r.json());
```

### 2. Polling vs WebSocket
- Usa **WebSocket** para updates de maletas en mapa
- Usa **polling** (cada 30s) para analytics si no hay WS

### 3. Paginación
```javascript
// Limitar resultados
const bags = await fetch('/api/bags?limit=100');
```

---

## ❌ Error Handling

```javascript
try {
  const response = await fetch('/api/bags');

  if (response.status === 401) {
    // Token expirado, re-login
    localStorage.removeItem('token');
    redirectToLogin();
  }

  if (response.status === 404) {
    // Recurso no encontrado
    showNotFound();
  }

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return await response.json();
} catch (error) {
  console.error('Error:', error);
  showErrorMessage('Error de conexión');
}
```

---

## 🔧 CORS

El backend acepta requests desde:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://localhost:8080` (Vue/otros)

Cambiar en producción.

---

## 📝 Ejemplos Completos

### Cargar Dashboard
```javascript
async function loadDashboard() {
  const [dashboard, losses, topAirports] = await Promise.all([
    fetch('/api/analytics/dashboard').then(r => r.json()),
    fetch('/api/analytics/losses').then(r => r.json()),
    fetch('/api/analytics/top-airports').then(r => r.json())
  ]);

  renderCharts({ dashboard, losses, topAirports });
}
```

### Tracking de Maleta Específica
```javascript
async function trackBag(bagId) {
  const bag = await fetch(`/api/bags/${bagId}`).then(r => r.json());

  // Mostrar en mapa
  map.setView([bag.flight_details.origin_lat, bag.flight_details.origin_lon]);

  // Mostrar timeline
  renderTimeline(bag.history);

  // Mostrar progreso
  updateProgress(bag.flight_details.progress);
}
```

### Form de Predicción
```javascript
async function predictRisk(formData) {
  const result = await fetch('/api/ml/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  }).then(r => r.json());

  // Mostrar resultado
  showRiskBadge(result.risk_level);
  showProbability(result.probabilidad_perdida);
  showFactors(result.factors);
}
```

---

## 📞 Support

- **Docs interactivos**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Tests backend**: `cd backend && ./test_api.sh`

---

**Version**: 1.0.0
**Updated**: 2026-01-13
