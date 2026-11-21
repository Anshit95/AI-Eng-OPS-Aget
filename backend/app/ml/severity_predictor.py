from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "severity_predictor.joblib"

SEVERITY_CLASSES = ["P0", "P1", "P2", "P3"]

TIER_MAP = {
    "Tier-1": 3,
    "Tier-2": 2,
    "Tier-3": 1
}

FEATURES = [
    "tier_level",
    "error_rate",
    "impacted_users_pct",
    "has_security_flag",
    "recent_deploy_minutes"
]

class SeverityPredictor:
    def __init__(self):
        self.model = None
        self.load()

    def train(self, df: pd.DataFrame):
        X = df[FEATURES].fillna(0)
        y = df["severity"]
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
        self.model.fit(X, y)
        joblib.dump(self.model, MODEL_PATH)
        print(f"[+] Severity predictor trained on {len(X)} samples and saved to {MODEL_PATH}")

    def load(self):
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"[!] Warning: Could not load severity predictor: {e}")

    def predict(self, sample: dict) -> dict:
        tier_str = sample.get("service_tier", "Tier-2")
        tier_num = TIER_MAP.get(tier_str, 2)
        
        feature_vals = {
            "tier_level": float(tier_num),
            "error_rate": float(sample.get("error_rate", 0.0)),
            "impacted_users_pct": float(sample.get("impacted_users_pct", 0.0)),
            "has_security_flag": 1.0 if sample.get("has_security_flag") else 0.0,
            "recent_deploy_minutes": float(sample.get("recent_deploy_minutes", 120.0))
        }

        # Model inference if available, else heuristic fallback
        if self.model is not None:
            X_sample = pd.DataFrame([feature_vals])
            pred_class = self.model.predict(X_sample)[0]
            probs = self.model.predict_proba(X_sample)[0]
            prob_dict = {cls: round(float(p), 3) for cls, p in zip(self.model.classes_, probs)}
            confidence = float(max(probs))
        else:
            # Deterministic heuristic based on operational criticality
            err = feature_vals["error_rate"]
            imp = feature_vals["impacted_users_pct"]
            if tier_num == 3 and (err > 10.0 or imp > 20.0):
                pred_class = "P0"
                confidence = 0.92
            elif (tier_num >= 2 and err > 5.0) or feature_vals["has_security_flag"]:
                pred_class = "P1"
                confidence = 0.85
            elif err > 1.0 or imp > 5.0:
                pred_class = "P2"
                confidence = 0.78
            else:
                pred_class = "P3"
                confidence = 0.88
            prob_dict = {c: 0.1 for c in SEVERITY_CLASSES}
            prob_dict[pred_class] = confidence

        top_factors = []
        if feature_vals["error_rate"] > 5.0:
            top_factors.append(f"Elevated error rate: {feature_vals['error_rate']}%")
        if tier_num == 3:
            top_factors.append("Critical Tier-1 Service with external traffic")
        if feature_vals["has_security_flag"]:
            top_factors.append("Active high/critical security vulnerability or IAM alert")
        if feature_vals["recent_deploy_minutes"] < 60:
            top_factors.append(f"Recent deployment within {int(feature_vals['recent_deploy_minutes'])} mins")

        return {
            "predicted_severity": pred_class,
            "confidence": round(confidence, 3),
            "probabilities": prob_dict,
            "top_factors": top_factors or ["Nominal operational baseline"]
        }

severity_predictor = SeverityPredictor()
