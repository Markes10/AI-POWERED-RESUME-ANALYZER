"""
Attendance Anomaly Detector routes.

Provides endpoints for detecting anomalies in attendance records
(batch + streaming modes) and triggering alerts.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import random
import datetime
from services import anomaly_utils

router = APIRouter(prefix="/attendance", tags=["Attendance Anomaly Detector"])


# -------------------------------
# Request Models
# -------------------------------
class AttendanceRecord(BaseModel):
    employee_id: str
    date: str   # YYYY-MM-DD
    status: str # present/absent/leave/remote


class BatchRequest(BaseModel):
    records: List[AttendanceRecord]


class StreamRequest(BaseModel):
    employee_id: str
    status: str


class AlertRequest(BaseModel):
    employee_id: str
    anomaly_type: str
    details: Dict[str, Any]


# -------------------------------
# Endpoints
# -------------------------------

@router.post("/anomaly/batch")
async def anomaly_batch(req: BatchRequest) -> Dict[str, Any]:
    """
    Detect anomalies in a batch of attendance records.
    Stub: Randomly marks a few records as anomalies.
    Later: Replace with IsolationForest, LSTM Autoencoder, or PyOD models.
    """
    anomalies = []
    for record in req.records:
        # Fake anomaly detection: randomly flag ~10%
        if random.random() < 0.1:
            anomalies.append({
                "employee_id": record.employee_id,
                "date": record.date,
                "reason": "outlier (stub)"
            })

    return {"total_records": len(req.records), "anomalies": anomalies}


@router.post("/anomaly/stream")
async def anomaly_stream(req: StreamRequest) -> Dict[str, Any]:
    """
    Streaming anomaly detection (stub).
    Later: Hook into Kafka/RabbitMQ + River (online ML).
    """
    now = datetime.datetime.utcnow().isoformat()
    return {
        "employee_id": req.employee_id,
        "status": req.status,
        "timestamp": now,
        "anomaly_detected": bool(random.getrandbits(1)),  # stub toggle
    }


@router.post("/alert")
async def send_alert(req: AlertRequest) -> Dict[str, Any]:
    """
    Trigger an alert when anomaly is detected.
    Stub: Just echoes request payload.
    Later: Integrate with email, SMS, or Slack.
    """
    return {
        "alert": "sent",
        "employee_id": req.employee_id,
        "anomaly_type": req.anomaly_type,
        "details": req.details,
        "sent_at": datetime.datetime.utcnow().isoformat()
    }
@router.post("/detect")
def detect_anomalies(payload: Dict[str, Any]):
    anomalies = anomaly_utils.detect(payload.get("series", []))
    return {"anomalies": anomalies} 
