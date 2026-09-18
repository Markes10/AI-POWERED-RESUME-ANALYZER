"""
Anomaly detection utilities for Attendance Anomaly Detector.

- Batch anomaly detection (PyOD: IsolationForest, AutoEncoder, etc.)
- Streaming anomaly detection (stub, later with River)
"""

import numpy as np
from typing import List, Dict, Any

try:
    from pyod.models.iforest import IForest
    _pyod_available = True
except ImportError:
    _pyod_available = False


# -------------------------------
# Batch Anomaly Detection
# -------------------------------
class BatchAnomalyDetector:
    """
    Wrapper for PyOD Isolation Forest anomaly detection.
    """

    def __init__(self, contamination: float = 0.1):
        if not _pyod_available:
            raise ImportError("PyOD not installed. Install with `pip install pyod`.")
        self.model = IForest(contamination=contamination, random_state=42)

    def fit_predict(self, features: List[List[float]]) -> List[int]:
        """
        Fit anomaly model and return predictions.
        0 = normal, 1 = anomaly
        """
        X = np.array(features)
        preds = self.model.fit_predict(X)
        return preds.tolist()

    def anomaly_scores(self, features: List[List[float]]) -> List[float]:
        """
        Return anomaly scores (higher = more anomalous).
        """
        X = np.array(features)
        scores = self.model.decision_function(X)
        return scores.tolist()


# -------------------------------
# Streaming Anomaly Detection (Stub)
# -------------------------------
class StreamAnomalyDetector:
    """
    Stub for streaming anomaly detection.
    Later: integrate with River for online learning.
    """

    def __init__(self):
        self.count = 0

    def update(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a new record (stub).
        Returns anomaly flag randomly for now.
        """
        import random
        self.count += 1
        return {
            "record": record,
            "anomaly_detected": bool(random.getrandbits(1)),
            "processed_count": self.count
        }


# -------------------------------
# Factory helpers
# -------------------------------
def get_batch_detector() -> BatchAnomalyDetector:
    """
    Get a batch anomaly detector (IsolationForest).
    """
    return BatchAnomalyDetector()


def get_stream_detector() -> StreamAnomalyDetector:
    """
    Get a streaming anomaly detector (stub).
    """
    return StreamAnomalyDetector()
