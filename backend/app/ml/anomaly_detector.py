import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "anomaly_detector.joblib"

FEATURES = [
    "error_rate",
    "latency_p95",
    "latency_p99",
    "cpu_usage",
    "memory_usage",
    "db_latency"
]

# Baseline expected values for NexaTech microservices
BASELINES = {
    "error_rate": {"mean": 0.15, "std": 0.10, "threshold": 2.0},
    "latency_p95": {"mean": 110.0, "std": 30.0, "threshold": 500.0},
    "latency_p99": {"mean": 210.0, "std": 50.0, "threshold": 1000.0},
    "cpu_usage": {"mean": 30.0, "std": 10.0, "threshold": 80.0},
    "memory_usage": {"mean": 45.0, "std": 8.0, "threshold": 85.0},
    "db_latency": {"mean": 14.0, "std": 5.0, "threshold": 150.0}
}

class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.load()

    def train(self, df: pd.DataFrame):
        X = df[FEATURES].fillna(0)
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.08,
            random_state=42
        )
        self.model.fit(X)
        joblib.dump(self.model, MODEL_PATH)
        print(f"[+] Anomaly detector trained on {len(X)} samples and saved to {MODEL_PATH}")

    def load(self):
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"[!] Warning: Could not load anomaly detector: {e}")

    def detect(self, sample: dict) -> dict:
        features_dict = {f: float(sample.get(f, 0.0)) for f in FEATURES}
        
        # 1. Isolation Forest inference
        if self.model is not None:
            X_sample = pd.DataFrame([features_dict])
            raw_score = -float(self.model.score_samples(X_sample)[0])  # higher = more anomalous
            iso_pred = int(self.model.predict(X_sample)[0])  # -1 is anomaly, 1 is normal
            is_iso_anomaly = (iso_pred == -1)
        else:
            raw_score = 0.5
            is_iso_anomaly = False

        # 2. Statistical baseline deviation check (Z-scores)
        z_scores = {}
        contributing = {}
        flagged_reasons = []

        for f, val in features_dict.items():
            base = BASELINES[f]
            z = (val - base["mean"]) / max(1e-4, base["std"])
            z_scores[f] = round(z, 2)
            if val > base["threshold"] or z > 3.0:
                contributing[f] = round(val, 2)
                flagged_reasons.append(f"{f}={val} exceeded baseline ({base['mean']} ± {base['std']})")

        is_stat_anomaly = len(contributing) > 0
        is_anomaly = is_iso_anomaly or is_stat_anomaly
        normalized_score = min(1.0, max(0.0, raw_score + (0.2 * len(contributing))))

        explanation = (
            f"Flagged as ANOMALY: {'; '.join(flagged_reasons)}"
            if is_anomaly and flagged_reasons
            else "Operational telemetry is within normal nominal bounds."
        )

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(normalized_score, 3),
            "contributing_features": contributing,
            "baseline_comparison": {
                "z_scores": z_scores,
                "deviations_count": len(contributing)
            },
            "explanation": explanation
        }

anomaly_detector = AnomalyDetector()
