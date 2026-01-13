# 🔴 Nuevo Endpoint: Report Bag Issue

## Endpoint para Reportar Problemas con Maletas

### **POST** `/api/bags/{bag_id}/report`

Permite a los pasajeros reportar problemas con sus maletas (pérdida, retraso, daño, ubicación incorrecta).

---

## Request

### Headers
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Path Parameters
- `bag_id` (string): ID de la maleta a reportar

### Request Body
```json
{
  "report_type": "LOST",
  "current_location": "Terminal 3, Gate B12",
  "expected_location": "Baggage Claim Area 2",
  "timestamp": "2026-01-13T20:30:00Z",
  "description": "My bag should be at baggage claim but it's not here",
  "passenger_location_lat": 40.6413,
  "passenger_location_lon": -73.7781
}
```

### Campos del Request

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `report_type` | string (enum) | ✅ Sí | Tipo de problema: `LOST`, `DELAYED`, `DAMAGED`, `MISPLACED` |
| `current_location` | string | ✅ Sí | Ubicación actual de la maleta (según pasajero o "Unknown") |
| `expected_location` | string | ✅ Sí | Dónde debería estar la maleta |
| `timestamp` | string (ISO 8601) | ✅ Sí | Hora del reporte |
| `description` | string | ❌ No | Descripción adicional del problema (max 500 chars) |
| `passenger_location_lat` | float | ❌ No | Latitud de la ubicación del pasajero |
| `passenger_location_lon` | float | ❌ No | Longitud de la ubicación del pasajero |

---

## Response

### Success (200 OK)
```json
{
  "report_id": "RPT-12345",
  "bag_id": "286782513",
  "status": "REPORTED",
  "prediction": {
    "loss_probability": 0.45,
    "risk_level": "MEDIUM",
    "estimated_cause": "Transfer delay",
    "recommendations": [
      "Contact airline staff at baggage claim desk",
      "Check delayed baggage area",
      "Your bag may arrive on next flight in 2 hours"
    ]
  },
  "created_at": "2026-01-13T20:30:15Z"
}
```

### Campos del Response

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `report_id` | string | ID único del reporte generado |
| `bag_id` | string | ID de la maleta reportada |
| `status` | string | Estado del reporte (`REPORTED`, `INVESTIGATING`, `RESOLVED`) |
| `prediction` | object | Predicción ML sobre la probabilidad de pérdida |
| `prediction.loss_probability` | float | Probabilidad de pérdida (0.0 - 1.0) |
| `prediction.risk_level` | string | Nivel de riesgo: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `prediction.estimated_cause` | string | Causa probable del problema |
| `prediction.recommendations` | array[string] | Lista de recomendaciones para el pasajero |
| `created_at` | string (ISO 8601) | Timestamp de creación del reporte |

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

#### 404 Not Found
```json
{
  "detail": "Maleta {bag_id} no encontrada"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "report_type"],
      "msg": "Invalid report type",
      "type": "value_error"
    }
  ]
}
```

---

## Implementación Sugerida (FastAPI)

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

router = APIRouter()

class ReportType(str, Enum):
    LOST = "LOST"
    DELAYED = "DELAYED"
    DAMAGED = "DAMAGED"
    MISPLACED = "MISPLACED"

class BagReportRequest(BaseModel):
    report_type: ReportType
    current_location: str
    expected_location: str
    timestamp: str
    description: Optional[str] = None
    passenger_location_lat: Optional[float] = None
    passenger_location_lon: Optional[float] = None

class MLPrediction(BaseModel):
    loss_probability: float
    risk_level: str
    estimated_cause: str
    recommendations: List[str]

class BagReportResponse(BaseModel):
    report_id: str
    bag_id: str
    status: str
    prediction: MLPrediction
    created_at: str

@router.post("/api/bags/{bag_id}/report", response_model=BagReportResponse)
async def report_bag_issue(
    bag_id: str,
    report: BagReportRequest,
    current_user = Depends(get_current_user)
):
    """
    Endpoint para reportar problemas con maletas.

    1. Validar que la maleta existe
    2. Crear registro del reporte en la BD
    3. Llamar al modelo ML para predicción
    4. Retornar reporte con predicción y recomendaciones
    """

    # 1. Verificar que la maleta existe
    bag = get_bag_from_db(bag_id)
    if not bag:
        raise HTTPException(status_code=404, detail=f"Maleta {bag_id} no encontrada")

    # 2. Generar ID de reporte
    report_id = f"RPT-{generate_unique_id()}"

    # 3. Guardar reporte en base de datos
    db_report = {
        "id": report_id,
        "bag_id": bag_id,
        "user_id": current_user.id,
        "report_type": report.report_type,
        "current_location": report.current_location,
        "expected_location": report.expected_location,
        "description": report.description,
        "status": "REPORTED",
        "created_at": datetime.now().isoformat()
    }
    save_report_to_db(db_report)

    # 4. Llamar al modelo ML para predicción
    ml_prediction = predict_bag_loss_risk(
        bag=bag,
        report_type=report.report_type,
        current_location=report.current_location,
        expected_location=report.expected_location
    )

    # 5. Generar recomendaciones basadas en predicción
    recommendations = generate_recommendations(
        bag=bag,
        report_type=report.report_type,
        risk_level=ml_prediction["risk_level"]
    )

    # 6. Retornar respuesta
    return BagReportResponse(
        report_id=report_id,
        bag_id=bag_id,
        status="REPORTED",
        prediction=MLPrediction(
            loss_probability=ml_prediction["loss_probability"],
            risk_level=ml_prediction["risk_level"],
            estimated_cause=ml_prediction.get("cause", "Unknown"),
            recommendations=recommendations
        ),
        created_at=db_report["created_at"]
    )


def generate_recommendations(bag, report_type, risk_level) -> List[str]:
    """
    Genera recomendaciones personalizadas basadas en el tipo de reporte y nivel de riesgo.
    """
    base_recommendations = [
        "Contact airline staff at the baggage claim desk immediately",
        "File an official report with your airline reference number",
        "Keep your baggage claim ticket as proof"
    ]

    if report_type == "LOST":
        base_recommendations.extend([
            "Check the delayed baggage area",
            "Your bag may arrive on the next flight",
            "Request compensation if eligible"
        ])
    elif report_type == "DELAYED":
        base_recommendations.extend([
            "Bags often arrive within 24-48 hours",
            "Check back with airline every 6 hours for updates"
        ])
    elif report_type == "DAMAGED":
        base_recommendations.extend([
            "Take photos of the damage immediately",
            "Do not leave the airport before filing a damage claim",
            "Request repair or compensation"
        ])

    if risk_level in ["HIGH", "CRITICAL"]:
        base_recommendations.insert(0, "⚠️ URGENT: Contact airport supervisor immediately")

    return base_recommendations
```

---

## Flujo de Datos

```
┌─────────────┐
│  Passenger  │
│   Reports   │
│   Issue     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  POST /api/bags/    │
│  {bag_id}/report    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Validate Bag       │
│  Exists & User      │
│  Has Permission     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Save Report to DB  │
│  Status: REPORTED   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Call ML Model      │
│  Predict Loss Risk  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Generate           │
│  Recommendations    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Return Response    │
│  with Prediction    │
└─────────────────────┘
```

---

## Base de Datos

### Tabla: `bag_reports`

```sql
CREATE TABLE bag_reports (
    id VARCHAR(50) PRIMARY KEY,
    bag_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    report_type VARCHAR(20) NOT NULL,
    current_location VARCHAR(255),
    expected_location VARCHAR(255),
    description TEXT,
    status VARCHAR(20) DEFAULT 'REPORTED',
    ml_prediction JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (bag_id) REFERENCES bags(id),
    FOREIGN KEY (user_id) REFERENCES users(id),

    INDEX idx_bag_id (bag_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

---

## Notas de Implementación

1. **Autenticación**: Solo usuarios autenticados (role: PASSENGER) pueden reportar maletas
2. **Validación**: El pasajero solo puede reportar su propia maleta
3. **ML Integration**: Integrar con el modelo ML existente (`/api/ml/predict`)
4. **Notificaciones**: Considerar enviar notificación push/email cuando se crea el reporte
5. **Rate Limiting**: Limitar a 5 reportes por usuario por hora para evitar spam
6. **Logs**: Registrar todos los reportes para análisis y auditoría

---

## Testing

### Ejemplo con cURL

```bash
# Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"passenger_1","password":"password"}' \
  | jq -r '.token')

# Report issue
curl -X POST "http://localhost:8000/api/bags/286782513/report" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "LOST",
    "current_location": "Unknown",
    "expected_location": "JFK Baggage Claim Area 2",
    "timestamp": "2026-01-13T20:30:00Z",
    "description": "My bag did not arrive on flight AA100"
  }'
```

### Respuesta Esperada

```json
{
  "report_id": "RPT-20260113-001",
  "bag_id": "286782513",
  "status": "REPORTED",
  "prediction": {
    "loss_probability": 0.35,
    "risk_level": "MEDIUM",
    "estimated_cause": "Missed connection during transfer",
    "recommendations": [
      "Contact airline staff at the baggage claim desk immediately",
      "Check the delayed baggage area",
      "Your bag may arrive on the next flight in approximately 3 hours",
      "File an official report with your airline reference number",
      "Keep your baggage claim ticket as proof"
    ]
  },
  "created_at": "2026-01-13T20:30:15.123456Z"
}
```
