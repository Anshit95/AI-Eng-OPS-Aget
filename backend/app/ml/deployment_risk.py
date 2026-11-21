from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
import joblib

MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "deployment_risk.joblib"

TIER_MAP = {
    "Tier-1": 3,
    "Tier-2": 2,
    "Tier-3": 1
}

FEATURES = [
    "tier_level",
    "lines_added",
    "lines_deleted",
    "files_changed",
    "has_migrations",
    "author_prior_deployments",
    "is_friday_or_weekend"
]

class DeploymentRiskEstimator:
    def __init__(self):
        self.model = None
        self.load()

    def train(self, df: pd.DataFrame):
        X = df[FEATURES].fillna(0)
        y = df["caused_regression"]  # 0 or 1
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=4,
            random_state=42
        )
        self.model.fit(X, y)
        joblib.dump(self.model, MODEL_PATH)
        print(f"[+] Deployment risk model trained on {len(X)} samples and saved to {MODEL_PATH}")

    def load(self):
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"[!] Warning: Could not load deployment risk estimator: {e}")

    def estimate(self, sample: dict) -> dict:
        tier_str = sample.get("service_tier", "Tier-2")
        tier_num = TIER_MAP.get(tier_str, 2)

        feature_vals = {
            "tier_level": float(tier_num),
            "lines_added": float(sample.get("lines_added", 50)),
            "lines_deleted": float(sample.get("lines_deleted", 10)),
            "files_changed": float(sample.get("files_changed", 3)),
            "has_migrations": 1.0 if sample.get("has_migrations") else 0.0,
            "author_prior_deployments": float(sample.get("author_prior_deployments", 20)),
            "is_friday_or_weekend": 1.0 if sample.get("is_friday_or_weekend") else 0.0
        }

        if self.model is not None:
            X_sample = pd.DataFrame([feature_vals])
            risk_prob = float(self.model.predict_proba(X_sample)[0][1])
        else:
            # Baseline deterministic pre-deployment heuristic
            base_risk = 0.10
            if feature_vals["has_migrations"] == 1.0:
                base_risk += 0.35
            if feature_vals["lines_added"] > 150 or feature_vals["files_changed"] > 6:
                base_risk += 0.25
            if feature_vals["is_friday_or_weekend"] == 1.0:
                base_risk += 0.15
            if tier_num == 3:
                base_risk += 0.10
            risk_prob = min(0.95, base_risk)

        # Risk level determination
        if risk_prob > 0.70:
            level = "CRITICAL"
            strategy = "MANUAL_APPROVAL_REQUIRED"
        elif risk_prob > 0.45:
            level = "HIGH"
            strategy = "CANARY"
        elif risk_prob > 0.25:
            level = "MODERATE"
            strategy = "CANARY"
        else:
            level = "LOW"
            strategy = "DIRECT"

        risk_factors = []
        if feature_vals["has_migrations"]:
            risk_factors.append("Includes database schema migrations with potential lock contention")
        if feature_vals["lines_added"] > 100:
            risk_factors.append(f"Large diff payload ({int(feature_vals['lines_added'])} lines added across {int(feature_vals['files_changed'])} files)")
        if feature_vals["is_friday_or_weekend"]:
            risk_factors.append("Off-peak / weekend deployment window")
        if tier_num == 3:
            risk_factors.append("Tier-1 core revenue pipeline service")

        return {
            "risk_score": round(risk_prob, 3),
            "risk_level": level,
            "recommended_strategy": strategy,
            "top_risk_factors": risk_factors or ["Standard low-risk change diff"]
        }

deployment_risk_estimator = DeploymentRiskEstimator()
