# 📘 Guía Rápida de Uso - OmniTrack Frontend

## 🚀 Inicio Rápido (3 Pasos)

### Paso 1: Instalación
```bash
cd Frontend_PAE
pip install -r requirements.txt
```

### Paso 2: Verificar Backend (Opcional)
```bash
python test_integration.py
```

### Paso 3: Iniciar Aplicación
```bash

# O usar: ./start.sh
```

---

## 👤 Guía de Usuario por Rol

### 🔐 Como Administrador

#### 1. Login
```
URL: http://localhost:8501
Username: admin
Password: password
```

#### 2. Vista de Mapa
- **Filtrar maletas:** Sidebar → Filters → Seleccionar estados
- **Buscar maleta:** Sidebar → Find Bag → Seleccionar ID
- **Ver detalles:** Click en punto del mapa o buscar por ID

#### 3. Analytics Dashboard
**Pestaña: 📈 Analytics**

Ver en tiempo real:
- Distribución de estados (pie chart)
- Aeropuertos más concurridos
- Tendencias de operación
- Análisis de pérdidas con métricas
- Top aeropuertos problemáticos
- Estadísticas de eficiencia de hubs

**Ejemplo de uso:**
1. Ir a pestaña "Analytics"
2. Ver distribución de estados → Identificar problemas
3. Revisar "Análisis de Pérdidas" → Ver razones
4. Consultar "Top Aeropuertos" → Identificar puntos críticos

#### 4. Predicción ML
**Pestaña: 🤖 ML Prediction**

**Caso de uso:** Predecir riesgo antes de facturar

1. Seleccionar ruta:
   - Origen: JFK
   - Destino: LHR
   - Aerolínea: AA

2. Configurar condiciones:
   - Hora: Morning
   - Retraso: 30 minutos
   - Conexiones: 1
   - Riesgo aeropuerto: 3/5
   - VIP: No
   - Peso: 23 kg

3. Click "Predecir Riesgo"

4. Interpretar resultado:
   - 🟢 LOW → OK para facturar
   - 🟡 MEDIUM → Precaución, seguir recomendaciones
   - 🟠 HIGH → Considerar alternativas
   - 🔴 CRITICAL → Evitar facturar si es posible

**Ejemplo de respuesta:**
```
Nivel de Riesgo: 🟡 Riesgo Moderado
Probabilidad: 35.2%
Predicción: ✅ No se perderá

Factores de Riesgo:
• Una conexión
• Aeropuerto de riesgo medio

Recomendaciones:
⏰ Llega al aeropuerto con tiempo
📸 Toma fotos del equipaje
🏷️ Etiquetas con contacto
📱 Activa notificaciones
```

#### 5. Datos Crudos
**Pestaña: 📂 Raw Data**

Exportar datos para análisis:
1. Ver tabla completa de maletas
2. Filtrar según necesidad
3. Copiar/pegar en Excel o herramienta de análisis

---

### 👜 Como Pasajero

#### 1. Login
```
Username: passenger_1
Password: password
```

**Resultado:** Automáticamente te muestra tu maleta (BAG1000000001)

#### 2. Ver Estado Actual
La vista principal muestra:
- 🗺️ Posición actual en el mapa
- 📍 Aeropuerto actual
- 🎯 Destino
- ⏱️ Estado (Check In, In Transit, Landed, etc.)

#### 3. Ver Historial
En la sección de detalles:
- Timeline de eventos
- Hora de cada escaneo
- Ubicaciones visitadas

**Ejemplo de timeline:**
```
✅ 10:30 - Check In at JFK
✅ 11:15 - Security Cleared
✅ 11:45 - At Gate G12
🔵 12:30 - In Transit to LHR
⏳ Esperando llegada...
```

---

## 🔄 Modos de Operación

### Modo Simulación (Local)
**Cuándo usar:** Testing, demos, sin backend disponible

**Activar:**
1. Sidebar → Data Source → "Simulation"
2. Click "▶ Start Live"

**Características:**
- Datos generados localmente
- Control manual de tiempo (Step +1)
- No requiere backend
- Ideal para pruebas

### Modo API (Backend Real)
**Cuándo usar:** Producción, datos reales, ML predictions

**Activar:**
1. Sidebar → Data Source → "Real Backend API"
2. Login con credenciales reales
3. Enable "Auto-polling (5s)" para actualizaciones automáticas

**Características:**
- Datos en tiempo real
- ML predictions disponibles
- Analytics completos
- WebSocket updates

---

## 🎯 Casos de Uso Prácticos

### Caso 1: Monitoreo de Operaciones (Admin)
**Objetivo:** Supervisar operación diaria

```
1. Login como admin
2. Vista de mapa → Ver todas las maletas
3. Sidebar → Filters → "In Transit" → Ver maletas en vuelo
4. Analytics → Ver tendencias del día
5. Identificar anomalías (muchas perdidas, retrasos)
6. Tomar acciones correctivas
```

### Caso 2: Investigación de Pérdida (Admin)
**Objetivo:** Analizar por qué se pierden maletas

```
1. Analytics → "Análisis de Pérdidas"
2. Ver "Total Perdidas": 45
3. Ver "Razones de Pérdida":
   - MISSED_TRANSFER: 20 (mayoría)
   - DAMAGED: 10
   - MISDIRECTED: 10
4. Ver "Top Aeropuertos": JFK (15 pérdidas)
5. Conclusión: Problemas con conexiones en JFK
6. Acción: Revisar proceso de transferencia en JFK
```

### Caso 3: Evaluación Pre-Viaje (Admin/Consultor)
**Objetivo:** Aconsejar a pasajero sobre riesgo

```
1. Pasajero consulta: "Vuelo JFK→LHR→MAD, ¿riesgo?"
2. ML Prediction → Ingresar datos:
   - Origen: JFK
   - Destino: MAD
   - Conexión: LHR (1 transfer)
   - Retraso esperado: 45 min
3. Resultado: 🟠 HIGH (72% probabilidad)
4. Recomendación: "Considere equipaje de mano o seguro"
```

### Caso 4: Tracking Personal (Pasajero)
**Objetivo:** Seguir mi maleta durante el viaje

```
Hora 10:00 - Check-in JFK
→ Login: passenger_1
→ Ver: "Check In at JFK"
→ Mapa: Punto verde en JFK

Hora 12:00 - Durante vuelo
→ Refresh página
→ Ver: "In Transit"
→ Mapa: Punto azul entre JFK y LHR

Hora 18:00 - Llegada
→ Refresh página
→ Ver: "Landed at LHR - Baggage Claim"
→ Mapa: Punto verde en LHR
→ Ir a recoger maleta ✓
```

---

## 🛠️ Consejos de Uso

### Para Administradores

**1. Configurar Auto-refresh**
```
Sidebar → Auto-polling (5s) ✓
```
Mantiene datos siempre actualizados sin clicks manuales.

**2. Usar Filtros Inteligentemente**
```
Ejemplo: Ver solo problemas
→ Filters → Lost, Delayed
→ Mapa muestra solo maletas problemáticas
```

**3. Revisar Analytics Regularmente**
```
Frecuencia recomendada: Cada 30 minutos
→ Identificar tendencias
→ Prevenir problemas
```

**4. Combinar Herramientas**
```
Workflow completo:
1. Mapa → Ver situación general
2. Analytics → Identificar patrones
3. ML → Predecir riesgos futuros
4. Raw Data → Exportar para reportes
```

### Para Pasajeros

**1. Bookmark la URL**
```
http://localhost:8501
Acceso rápido desde móvil
```

**2. Refresh Periódico**
```
Durante conexiones: Cada 15 minutos
En espera de llegada: Cada 5 minutos
```

**3. Capturar Info Importante**
```
Screenshot cuando:
- Maleta facturada (prueba)
- Estado cambia a "Lost"
- Llega a destino (confirmación)
```

---

## ⚡ Shortcuts y Tips

### Navegación Rápida
```
Tab Map → Ver posiciones
Tab Analytics → Ver estadísticas
Tab ML → Hacer predicción
Tab Data → Exportar datos
```

### Búsqueda Rápida
```
Sidebar → Find Bag → Type BAG ID
Enter → Ver en mapa automáticamente
```

### Filtros Rápidos
```
Ver solo perdidas: Filter → Lost
Ver solo en vuelo: Filter → In Transit
Ver todo: Filter → Select All
```

---

## 🔍 Troubleshooting Común

### "No data available"
**Causa:** Backend no conectado
**Solución:**
```bash
# Verificar backend
curl http://localhost:8000/health

# Si falla, iniciar backend
cd backend && python main.py
```

### "Login failed"
**Causa:** Credenciales incorrectas
**Solución:** Usar credenciales exactas:
```
admin / password (case-sensitive)
```

### "Bag not found"
**Causa:** ID incorrecto o maleta no existe
**Solución:**
```
1. Ver lista completa en Raw Data tab
2. Copiar ID exacto
3. Pegar en búsqueda
```

### Mapa no se actualiza
**Causa:** Auto-refresh desactivado
**Solución:**
```
Sidebar → Auto-polling (5s) → Activar
O
Click manual en "🔄 Fetch Live Data"
```

---

## 📊 Interpretación de Métricas

### Analytics Dashboard

**Status Distribution (Pie Chart)**
```
Verde predominante → Operación normal
Rojo aumentando → Problema con pérdidas
Amarillo alto → Muchos retrasos
```

**Busiest Airports (Bar Chart)**
```
Barra más alta → Más tráfico
Útil para: Planificar recursos
```

**Loss Analytics**
```
Total Losses: Número absoluto
Avg Recovery Time: Eficiencia del sistema
  < 6h → Excelente
  6-12h → Bueno
  12-24h → Mejorable
  > 24h → Problema
```

---

## 🎓 Ejemplos Paso a Paso

### Ejemplo 1: Primera Vez como Admin

```bash
# 1. Iniciar sistema
streamlit run PAE_frontend.py

# 2. Esperar a que abra navegador (http://localhost:8501)

# 3. Cambiar a modo API
Sidebar → Data Source → "Real Backend API"

# 4. Login
Username: admin
Password: password
[Click] "🔓 Iniciar Sesión"

# 5. Ver mapa
→ Puntos de colores = maletas
→ Verde = OK
→ Rojo = Problemas

# 6. Ver analytics
[Click] Tab "📈 Analytics"
→ Revisar distribución
→ Ver tendencias

# 7. Probar ML
[Click] Tab "🤖 ML Prediction"
→ Llenar formulario
→ Ver predicción
```

### Ejemplo 2: Primera Vez como Pasajero

```bash
# 1. Abrir app
http://localhost:8501

# 2. Modo API
Sidebar → "Real Backend API"

# 3. Login
Username: passenger_1
Password: password

# 4. Ver tu maleta automáticamente
→ Mapa centrado en tu maleta
→ Info completa visible

# 5. Verificar estado
→ Color del punto:
  Verde = Todo bien
  Azul = En vuelo
  Rojo = Problema

# 6. Ver detalles
Scroll down → Timeline
→ Ver historial completo
```

---

## 📞 Ayuda Adicional

**Documentación Completa:**
- [README.md](README.md) - Visión general
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Guía técnica
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Resumen

**Backend API:**
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

**Soporte:**
- Issues: GitHub Issues
- Logs: Terminal donde corre Streamlit

---

**Versión:** 2.0.0
**Última actualización:** Enero 2026
