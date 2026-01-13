# 📡 Para el Equipo de Backend - Consumo de APIs

## 📋 Estado de Integración

**Estado:** ✅ **TODOS LOS ENDPOINTS INTEGRADOS Y FUNCIONANDO**

---

## 🔗 Endpoints Utilizados por el Frontend

### ✅ Autenticación
```python
# POST /api/auth/login
# Frecuencia: Una vez por sesión
# Usado en: components/auth.py

Request:
{
  "username": "admin",
  "password": "password"
}

Consumo en Frontend:
- Login form al iniciar
- Guarda token en st.session_state
- Token se incluye en headers subsecuentes
```

### ✅ Aeropuertos
```python
# GET /api/airports
# Frecuencia: Una vez al iniciar (cached)
# Usado en: services/api_service.py (init)

Consumo:
- Carga al iniciar el service
- Cachea en memoria (self.airports)
- Usado en dropdowns de ML prediction
- No requiere re-fetch (datos estáticos)

# GET /api/airports/{code}
# Frecuencia: Bajo (solo cuando se necesita detalle)
# Usado en: services/api_service.py
```

### ✅ Maletas (Baggage)
```python
# GET /api/bags
# Frecuencia: Cada 5 segundos (auto-refresh activado)
# Usado en: services/api_service.py -> tick()

Query params usados:
- limit: 100 (default)
- status: Cuando se aplican filtros
- owner_id: Para modo pasajero

Consumo típico:
GET /api/bags?limit=100
GET /api/bags?status=IN_TRANSIT&limit=50
GET /api/bags?owner_id=passenger_1

# GET /api/bags/{id}
# Frecuencia: Al hacer click en maleta
# Usado en: PAE_frontend.py (bag details)

Consumo:
GET /api/bags/286782513
→ Muestra historial completo
→ Muestra detalles de vuelo

# POST /api/bags/scan
# Frecuencia: Muy bajo (admin manual)
# Usado en: (Funcionalidad futura)
```

### ✅ Machine Learning
```python
# POST /api/ml/predict
# Frecuencia: On-demand (cuando usuario usa form)
# Usado en: components/ml_prediction.py

Request típico:
{
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

Esperamos en response:
{
  "probabilidad_perdida": 0.08,
  "prediccion": 0,
  "risk_level": "LOW",
  "factors": ["Lista de strings"]
}

Frontend usa:
- probabilidad_perdida → % display
- risk_level → Color coding (LOW/MEDIUM/HIGH/CRITICAL)
- factors → Lista de warnings
```

### ✅ Analytics
```python
# GET /api/analytics/dashboard
# Frecuencia: Cada 30 seg cuando tab está activo
# Usado en: components/analytics.py

Esperamos:
{
  "status_distribution": {
    "Check In": 15,
    "In Transit": 45,
    ...
  },
  "busiest_airports": [
    {"code": "JFK", "name": "New York", "count": 120},
    ...
  ],
  "session_trends": [
    {
      "timestamp": "2026-01-13T10:00:00",
      "active_bags": 100,
      "lost_bags": 2
    },
    ...
  ]
}

Frontend renderiza:
- Pie chart de status_distribution
- Bar chart de busiest_airports
- Line chart de session_trends

# GET /api/analytics/losses
# Frecuencia: Cada 30 seg en analytics tab

Esperamos:
{
  "total_losses": 45,
  "loss_reasons": {
    "MISSED_TRANSFER": 20,
    "DAMAGED": 10,
    ...
  },
  "loss_status": {
    "RECOVERED": 30,
    "IN_SEARCH": 10,
    "PERMANENT": 5
  },
  "avg_recovery_time_hours": 12.5
}

Frontend usa para:
- KPI cards (Total, Recovered, In Search)
- Bar chart de loss_reasons
- Metric de avg_recovery_time

# GET /api/analytics/top-airports
# Frecuencia: Cada 30 seg

Esperamos:
[
  {"airport_code": "JFK", "loss_count": 15},
  {"airport_code": "LHR", "loss_count": 12},
  ...
]

Frontend renderiza:
- Bar chart horizontal
- Tabla ordenada

# GET /api/analytics/hub-statistics
# Frecuencia: Cada 30 seg

Esperamos:
{
  "total_hubs": 20,
  "data": [
    {
      "airport_code": "JFK",
      "total_bags": 1500,
      "avg_processing_time": 12.3,
      "efficiency_score": 0.87
    },
    ...
  ]
}

Frontend usa:
- Tabla con efficiency_score como progress bar
- Ordenable por columnas
```

### ✅ WebSocket
```python
# WS /ws
# Frecuencia: Conexión persistente
# Usado en: services/websocket_client.py

Mensajes esperados (cada ~5 seg):
{
  "id": "286782513",
  "current_lat": 40.6420,
  "current_lon": -73.7785,
  "status": "IN_TRANSIT",
  "color": [0, 150, 255, 255]
}

Frontend usa para:
- Actualizar posiciones en mapa sin reload
- Actualizar status badges
- Animations suaves de movimiento

Notas:
- Auto-reconecta si se desconecta
- Fallback a polling si WS no disponible
```

### ✅ Utilidades
```python
# GET /health
# Frecuencia: Una vez al iniciar
# Usado en: services/api_service.py (init)

Esperamos:
{
  "status": "healthy",
  "version": "1.0.0"
}

Frontend usa:
- Mostrar mensaje de conexión exitosa
- Validar que backend está up
```

---

## 📊 Patrones de Consumo

### Carga Inicial (Al abrir app)
```
1. GET /health → Verificar backend
2. GET /api/airports → Cargar aeropuertos (cache)
3. (Si API mode) Login flow
4. GET /api/bags?limit=100 → Cargar maletas iniciales
```

### Durante Uso Normal (Admin)
```
Cada 5 segundos:
- GET /api/bags?limit=100

Cada 30 segundos (si tab analytics activo):
- GET /api/analytics/dashboard
- GET /api/analytics/losses
- GET /api/analytics/top-airports
- GET /api/analytics/hub-statistics

On-demand:
- GET /api/bags/{id} → Al click en maleta
- POST /api/ml/predict → Al usar formulario ML
```

### Durante Uso Normal (Pasajero)
```
Cada 5 segundos:
- GET /api/bags?owner_id={passenger_id}

On-demand:
- GET /api/bags/{specific_bag_id} → Detalles
```

---

## 🔧 Configuración Frontend

### Timeouts
```python
# services/api_service.py
API_TIMEOUT = 5  # segundos

Todos los requests tienen timeout=5
Si backend tarda más, frontend muestra error
```

### Retry Policy
```python
# Actualmente: NO hay auto-retry
# Un fallo = muestra error al usuario

Recomendación para backend:
- Responder en < 2 segundos idealmente
- Máximo 5 segundos
```

### Cache
```python
# Aeropuertos: Cached en memoria (no re-fetch)
# Maletas: NO cached (siempre fresh)
# Analytics: NO cached (siempre fresh)
```

---

## 🎨 Formato de Datos Esperados

### Colores
```python
# Esperamos RGBA como lista [R, G, B, A]
Ejemplo: [0, 255, 0, 255]

Frontend usa directamente estos valores para Pydeck
No transformación necesaria
```

### Fechas/Timestamps
```python
# Esperamos ISO 8601 strings
Ejemplo: "2026-01-13T14:30:00Z"

Frontend parsea con datetime.fromisoformat()
```

### Códigos de Aeropuerto
```python
# Esperamos códigos IATA (3 letras)
Ejemplo: "JFK", "LHR", "MAD"

Deben matchear con GET /api/airports
```

---

## ⚠️ Puntos de Atención Backend

### 1. CORS
```python
# Frontend corre en: http://localhost:8501
# Backend debe permitir CORS desde esta URL

Necesario en backend:
- Access-Control-Allow-Origin: http://localhost:8501
- Access-Control-Allow-Methods: GET, POST
- Access-Control-Allow-Headers: Authorization, Content-Type
```

### 2. Tokens JWT
```python
# Frontend envía token en header:
Authorization: Bearer {token}

# Backend debe:
- Validar token en endpoints protegidos
- Return 401 si token inválido/expirado
- Token lifetime razonable (1-24 horas)
```

### 3. Paginación
```python
# Actualmente frontend usa limit=100

Si hay muchas maletas (>1000):
- Considerar implementar offset/page
- Frontend puede adaptar para paginar

Request futuro:
GET /api/bags?limit=100&offset=0
GET /api/bags?limit=100&offset=100
```

### 4. Rate Limiting
```python
# Frontend hace polling cada 5 segundos

Si implementan rate limiting:
- Permitir al menos 1 req/sec por usuario
- O avisar para ajustar polling interval
```

---

## 🐛 Errores Comunes que Frontend Maneja

### Status Codes
```python
200 → Success, procesa data
401 → Token inválido, redirect a login
404 → Recurso no encontrado, muestra error
422 → Validación fallida, muestra mensaje
500 → Server error, muestra error genérico

Frontend espera JSON en todos los casos:
{
  "detail": "Mensaje de error"
}
```

### Timeouts
```python
Si backend no responde en 5 segundos:
→ Frontend muestra: "Error de conexión"
→ No bloquea UI
→ Usuario puede reintentar
```

### Datos Faltantes
```python
# Si falta un campo opcional:
Frontend usa valor default

Ejemplo:
- color no viene → usa [0,255,0,255]
- progress no viene → usa 0.0
- owner no viene → usa "Unknown"
```

---

## 📈 Métricas de Uso (Info para Backend)

### Endpoints Más Usados
```
1. GET /api/bags → Cada 5 seg
2. GET /api/analytics/dashboard → Cada 30 seg
3. GET /api/bags/{id} → Por demanda (alto en uso normal)
4. POST /api/ml/predict → Por demanda (bajo)
5. GET /api/airports → Una vez (inicio)
```

### Carga Esperada
```
10 usuarios simultáneos:
- /api/bags: ~2 req/seg
- /api/analytics/*: ~0.5 req/seg
- /api/ml/predict: ~0.1 req/seg

100 usuarios simultáneos:
- /api/bags: ~20 req/seg
- /api/analytics/*: ~5 req/seg

Optimizaciones recomendadas:
- Cache de analytics (30 seg TTL)
- Índices en DB para filtros
- Connection pooling
```

---

## 🔍 Testing desde Backend

### Test de Integración
```bash
# Correr test suite del frontend
cd Frontend_PAE
python test_integration.py

# Output esperado:
# ✓ Health check
# ✓ Admin login successful
# ✓ Get all airports (20 airports)
# ✓ Get all bags (X bags)
# ... etc ...
# Success Rate: 100.0%
```

### Verificar Endpoints Manualmente
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Bags
curl http://localhost:8000/api/bags?limit=10

# ML Predict
curl -X POST http://localhost:8000/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "origen":"JFK",
    "destino":"LHR",
    "aerolinea":"AA",
    "time_of_day":"morning",
    "retraso_min":15,
    "transfers":1,
    "airport_risk":3,
    "viajero_vip":0,
    "peso_kg":23.5
  }'
```

---

## 📞 Comunicación Frontend-Backend

### Si Cambian un Endpoint
**Avisar a Frontend Team:**
1. Endpoint modificado
2. Campos añadidos/removidos
3. Formato de response cambiado
4. Breaking changes

**Frontend actualizará:**
- `services/api_service.py`
- Componentes afectados
- Documentación

### Si Añaden Nuevo Endpoint
**Compartir con Frontend:**
1. Endpoint URL
2. Method (GET/POST/etc)
3. Request body schema
4. Response schema
5. Casos de uso

**Frontend puede integrar:**
- Nuevo método en api_service.py
- Nuevo componente UI si aplica

### Logs Útiles para Debug
```python
# Backend debería loggear:
- Request method + URL
- Request body (sin passwords)
- Response status code
- Response time
- Errores con traceback

Esto ayuda a debug cuando frontend reporta errores
```

---

## ✅ Checklist de Compatibilidad

**Antes de deploy de cambios en backend:**

- [ ] Todos los tests pasan (`test_integration.py`)
- [ ] CORS configurado para http://localhost:8501
- [ ] Endpoints retornan JSON válido
- [ ] Errores incluyen campo "detail"
- [ ] Timeouts < 5 segundos
- [ ] JWT tokens funcionan correctamente
- [ ] WebSocket acepta conexiones
- [ ] Docs actualizadas en /docs

---

## 🎯 Mejoras Sugeridas para Backend

### Performance
- [ ] Cache de analytics (30s TTL)
- [ ] Índices en DB para queries frecuentes
- [ ] Comprimir responses grandes (gzip)

### Features
- [ ] Paginación real (offset/limit)
- [ ] Filtros adicionales (date ranges, airlines)
- [ ] Webhook para notificaciones
- [ ] Batch operations para bulk updates

### Monitoring
- [ ] Logs estructurados (JSON)
- [ ] Métricas de performance por endpoint
- [ ] Alertas si response time > 3s

---

## 📚 Referencias

- **Frontend API Docs:** `FRONTEND_API_GUIDE.md`
- **API Quick Ref:** `API_QUICK_REFERENCE.md`
- **Backend Swagger:** http://localhost:8000/docs
- **Test Suite:** `test_integration.py`

---

**Contacto Frontend Team:**
- Issues: GitHub Issues
- Docs: Ver archivos *.md en repo

**Última actualización:** Enero 2026
**Frontend Version:** 2.0.0
**Compatible con Backend:** v1.0.0
