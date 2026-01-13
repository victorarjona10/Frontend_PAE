# 🧳 OmniTrack Frontend - Guía de Integración Completa

## 🆕 Nuevas Funcionalidades Integradas

### ✅ Implementaciones Completadas

#### 1. **Servicio API Completo** (`services/api_service.py`)
Integración completa con todos los endpoints del backend:

**Autenticación**
- ✅ `POST /api/auth/login` - Login con JWT

**Aeropuertos**
- ✅ `GET /api/airports` - Lista de 20 aeropuertos
- ✅ `GET /api/airports/{code}` - Detalles de aeropuerto

**Maletas (Baggage)**
- ✅ `GET /api/bags` - Lista con filtros (status, owner_id, limit)
- ✅ `GET /api/bags/{id}` - Detalles completos con historial
- ✅ `POST /api/bags/scan` - Actualizar posición (RFID simulation)

**Machine Learning**
- ✅ `POST /api/ml/predict` - Predicción de riesgo de pérdida

**Analytics**
- ✅ `GET /api/analytics/dashboard` - Métricas agregadas
- ✅ `GET /api/analytics/losses` - Análisis de pérdidas
- ✅ `GET /api/analytics/top-airports` - Top aeropuertos con pérdidas
- ✅ `GET /api/analytics/hub-statistics` - Estadísticas de hubs

**Utilidades**
- ✅ Health check automático al iniciar
- ✅ Gestión de tokens JWT
- ✅ Manejo de errores robusto

---

#### 2. **Componente de Predicción ML** (`components/ml_prediction.py`)

Formulario interactivo para predicción de riesgo:

**Inputs del Formulario:**
- Aeropuerto de origen/destino (selección de 20 aeropuertos)
- Código de aerolínea
- Hora del día (mañana/tarde/noche/madrugada)
- Retraso del vuelo (0-999 minutos)
- Número de conexiones (0-2)
- Nivel de riesgo del aeropuerto (1-5 estrellas)
- Estado VIP del pasajero
- Peso del equipaje (kg)

**Visualización de Resultados:**
- 🎯 Nivel de riesgo con código de colores (LOW/MEDIUM/HIGH/CRITICAL)
- 📊 Probabilidad de pérdida (%)
- ✅/❌ Predicción binaria
- ⚠️ Factores de riesgo detectados
- 💡 Recomendaciones personalizadas por nivel de riesgo

---

#### 3. **Analytics Mejorado** (`components/analytics.py`)

Ahora con dos modos de operación:

**Modo API (Backend conectado):**
- 📦 Distribución por estado (pie chart)
- ✈️ Aeropuertos más concurridos (bar chart)
- 📈 Tendencias de operación en tiempo real (line chart)
- 🔴 Análisis de pérdidas con métricas:
  - Total perdidas
  - Recuperadas
  - En búsqueda
  - Tiempo medio de recuperación
- 🔍 Razones de pérdida (MISSED_TRANSFER, DAMAGED, etc.)
- 🌍 Top 10 aeropuertos con más pérdidas
- 🏢 Estadísticas de eficiencia de hubs

**Modo Simulación (Fallback):**
- Gráficos básicos con datos de simulación local

---

#### 4. **WebSocket Client** (`services/websocket_client.py`)

Soporte para actualizaciones en tiempo real:

**Características:**
- Conexión WebSocket a `ws://localhost:8000/ws`
- Auto-reconexión en caso de desconexión
- Cola de mensajes para procesamiento asíncrono
- Indicador de estado de conexión en sidebar
- Auto-refresh con `streamlit-autorefresh`

**Nota:** Requiere la librería `websocket-client` instalada.

---

#### 5. **Autenticación Real** (`components/auth.py`)

Login mejorado con dos modos:

**Modo API:**
- Formulario de login con usuario/contraseña
- Integración con `POST /api/auth/login`
- Gestión automática de roles (ADMIN/PASSENGER)
- Almacenamiento de token JWT
- Cuentas de prueba documentadas

**Modo Simulación:**
- Login simplificado (modo anterior)

**Usuarios de Prueba:**
```
Admin:
- Usuario: admin
- Contraseña: password
- Acceso: Todas las maletas

Pasajeros:
- Usuario: passenger_1 | Contraseña: password | Maleta: BAG1000000001
- Usuario: passenger_2 | Contraseña: password | Maleta: BAG1000000050
```

---

#### 6. **Frontend Principal Actualizado** (`PAE_frontend.py`)

**Nuevos Features:**
- ✅ Pestaña "🤖 ML Prediction" (solo para admins)
- ✅ Analytics con datos reales del backend
- ✅ Indicador de estado WebSocket en sidebar
- ✅ Login con API en modo backend
- ✅ Auto-refresh para actualizaciones en tiempo real

---

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Nuevas dependencias añadidas:**
- `requests` - Llamadas HTTP al backend
- `websocket-client` - Cliente WebSocket
- `streamlit-autorefresh` - Auto-refresh para tiempo real
- `altair` - Gráficos interactivos

### 2. Verificar Backend

Asegúrate de que el backend esté corriendo:

```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{"status": "healthy", "version": "1.0.0"}
```

### 3. Ejecutar Frontend

```bash
streamlit run PAE_frontend.py
```

---

## 📖 Guía de Uso

### Modo Simulación
1. En sidebar, selecciona **"Simulation"**
2. Login con modo simplificado
3. Datos generados localmente

### Modo API (Backend Real)
1. En sidebar, selecciona **"Real Backend API"**
2. Login con credenciales:
   - Admin: `admin` / `password`
   - Pasajero: `passenger_1` / `password`
3. Datos en tiempo real desde http://localhost:8000

---

## 🎯 Funcionalidades por Rol

### Pasajero (Passenger)
- ✅ Ver posición de su maleta en el mapa
- ✅ Historial de movimientos
- ✅ Detalles del vuelo
- ✅ Estado actual
- ❌ No acceso a analytics ni ML

### Administrador (Admin)
- ✅ Vista global de todas las maletas
- ✅ Dashboard de analytics completo
- ✅ Predicción ML de riesgo
- ✅ Filtros avanzados
- ✅ Datos crudos exportables
- ✅ Notificaciones de alertas

---

## 🔧 Configuración Avanzada

### Cambiar URL del Backend

En `services/api_service.py`:
```python
API_BASE_URL = "http://localhost:8000"  # Cambiar aquí
```

### Ajustar Intervalo de Auto-Refresh

En `PAE_frontend.py`:
```python
setup_realtime_updates(interval_ms=5000)  # 5 segundos
```

### Habilitar WebSocket

El WebSocket se conecta automáticamente en modo API. Para reconectar manualmente:
- Ir a sidebar → "🔴 Conexión en Tiempo Real" → "🔄 Reconectar WebSocket"

---

## 📊 Endpoints Disponibles

Ver documentación completa en:
- `FRONTEND_API_GUIDE.md` - Guía completa
- `API_QUICK_REFERENCE.md` - Referencia rápida

**Resumen de endpoints integrados:**
```
✅ POST   /api/auth/login
✅ GET    /api/airports
✅ GET    /api/airports/{code}
✅ GET    /api/bags
✅ GET    /api/bags/{id}
✅ POST   /api/bags/scan
✅ POST   /api/ml/predict
✅ GET    /api/analytics/dashboard
✅ GET    /api/analytics/losses
✅ GET    /api/analytics/top-airports
✅ GET    /api/analytics/hub-statistics
✅ GET    /health
✅ WS     /ws
```

---

## 🎨 Estructura de Archivos Actualizada

```
Frontend_PAE/
├── PAE_frontend.py                 # ✅ ACTUALIZADO - Main app
├── requirements.txt                # ✅ ACTUALIZADO - Nuevas deps
│
├── components/
│   ├── analytics.py                # ✅ ACTUALIZADO - API integration
│   ├── auth.py                     # ✅ ACTUALIZADO - Real login
│   ├── ml_prediction.py            # 🆕 NUEVO - ML prediction form
│   ├── map_view.py
│   ├── metrics.py
│   ├── bag_details.py
│   └── notifications.py
│
├── services/
│   ├── api_service.py              # ✅ ACTUALIZADO - Full API client
│   ├── websocket_client.py         # 🆕 NUEVO - WebSocket support
│   ├── simulation.py
│   └── models.py
│
└── docs/
    ├── FRONTEND_API_GUIDE.md       # Backend API documentation
    ├── API_QUICK_REFERENCE.md      # Quick reference
    └── INTEGRATION_GUIDE.md        # 🆕 ESTE ARCHIVO
```

---

## 🐛 Troubleshooting

### Error: "Backend no disponible"
**Solución:** Verifica que el backend esté corriendo en http://localhost:8000
```bash
curl http://localhost:8000/health
```

### Error: "websocket-client no instalado"
**Solución:**
```bash
pip install websocket-client
```

### Error: "streamlit-autorefresh no disponible"
**Solución:**
```bash
pip install streamlit-autorefresh
```

### Login falla con "Credenciales inválidas"
**Solución:** Verifica que estés usando las credenciales correctas:
- Admin: `admin` / `password`
- Passenger: `passenger_1` / `password`

### Analytics muestra "No hay datos disponibles"
**Solución:** 
1. Verifica conexión al backend
2. Asegúrate de que hay datos en la base de datos
3. Intenta hacer un "Fetch Live Data" desde el sidebar

### WebSocket no conecta
**Solución:**
1. Verifica que el backend WebSocket esté activo
2. Usa el botón "🔄 Reconectar WebSocket" en sidebar
3. Verifica que no haya firewall bloqueando el puerto

---

## 📈 Próximas Mejoras Sugeridas

- [ ] Exportar datos de analytics a CSV/PDF
- [ ] Notificaciones push para pasajeros
- [ ] Historial de predicciones ML
- [ ] Comparativa de eficiencia entre aeropuertos
- [ ] Dashboard personalizable
- [ ] Modo oscuro/claro
- [ ] Multi-idioma (i18n)

---

## 📞 Contacto y Soporte

**Backend API:**
- URL: http://localhost:8000
- Docs: http://localhost:8000/docs (Swagger UI)
- WebSocket: ws://localhost:8000/ws

**Documentación:**
- Guía completa: `FRONTEND_API_GUIDE.md`
- Referencia rápida: `API_QUICK_REFERENCE.md`

---

**Versión:** 2.0.0  
**Última actualización:** Enero 2026  
**Estado:** ✅ Completamente integrado con backend
