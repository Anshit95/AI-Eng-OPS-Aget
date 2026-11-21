import json
from pathlib import Path
import random
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score, accuracy_score

from backend.app.ml.anomaly_detector import anomaly_detector
from backend.app.ml.severity_predictor import severity_predictor
from backend.app.ml.deployment_risk import deployment_risk_estimator
from backend.app.core.database import SessionLocal
from backend.app.models.evaluation import EvaluationRun

REPORT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "models" / "eval_report.json"

def generate_synthetic_ml_data(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    n_samples = 1200

    # 1. Telemetry dataset for Anomaly Detection
    telemetry_data = []
    for _ in range(n_samples):
        is_anomaly = random.random() < 0.10
        if is_anomaly:
            telemetry_data.append({
                "error_rate": np.random.uniform(5.0, 25.0),
                "latency_p95": np.random.uniform(800.0, 3500.0),
                "latency_p99": np.random.uniform(1500.0, 5000.0),
                "cpu_usage": np.random.uniform(70.0, 98.0),
                "memory_usage": np.random.uniform(75.0, 95.0),
                "db_latency": np.random.uniform(200.0, 1500.0),
                "label": 1
            })
        else:
            telemetry_data.append({
                "error_rate": np.random.uniform(0.01, 0.40),
                "latency_p95": np.random.uniform(40.0, 160.0),
                "latency_p99": np.random.uniform(80.0, 280.0),
                "cpu_usage": np.random.uniform(15.0, 50.0),
                "memory_usage": np.random.uniform(30.0, 60.0),
                "db_latency": np.random.uniform(5.0, 25.0),
                "label": 0
            })
    df_telemetry = pd.DataFrame(telemetry_data)

    # 2. Incident Severity dataset
    severity_data = []
    for _ in range(n_samples):
        tier = random.choice([1, 2, 3])
        err = np.random.exponential(scale=3.0)
        impact = np.random.uniform(0.1, 40.0)
        sec_flag = 1 if random.random() < 0.15 else 0
        deploy_mins = random.randint(5, 720)

        # Ground truth rule assignment
        if tier == 3 and (err > 12.0 or impact > 25.0):
            sev = "P0"
        elif (tier >= 2 and err > 4.0) or (sec_flag == 1 and impact > 10.0):
            sev = "P1"
        elif err > 1.0 or impact > 3.0:
            sev = "P2"
        else:
            sev = "P3"

        severity_data.append({
            "tier_level": tier,
            "error_rate": err,
            "impacted_users_pct": impact,
            "has_security_flag": sec_flag,
            "recent_deploy_minutes": deploy_mins,
            "severity": sev
        })
    df_severity = pd.DataFrame(severity_data)

    # 3. Pre-deployment Risk dataset (Strictly pre-deployment features)
    deploy_data = []
    for _ in range(n_samples):
        tier = random.choice([1, 2, 3])
        added = int(np.random.exponential(scale=80.0))
        deleted = int(np.random.exponential(scale=30.0))
        files = max(1, int(added / 25.0) + random.randint(1, 4))
        migrations = 1 if (random.random() < 0.20 or added > 200) else 0
        prior_deploys = random.randint(2, 60)
        is_weekend = 1 if random.random() < 0.25 else 0

        # Regression probability
        prob = 0.05
        if migrations == 1:
            prob += 0.35
        if added > 180 or files > 7:
            prob += 0.25
        if is_weekend == 1:
            prob += 0.15
        if tier == 3:
            prob += 0.10
        if prior_deploys < 5:
            prob += 0.10

        caused_regression = 1 if (random.random() < min(0.92, prob)) else 0

        deploy_data.append({
            "tier_level": tier,
            "lines_added": added,
            "lines_deleted": deleted,
            "files_changed": files,
            "has_migrations": migrations,
            "author_prior_deployments": prior_deploys,
            "is_friday_or_weekend": is_weekend,
            "caused_regression": caused_regression
        })
    df_deploy = pd.DataFrame(deploy_data)

    return df_telemetry, df_severity, df_deploy

def run_ml_training_and_evaluation():
    print("==================================================")
    print("      Machine Learning Training & Evaluation      ")
    print("==================================================")
    
    df_telemetry, df_severity, df_deploy = generate_synthetic_ml_data(seed=42)
    db = SessionLocal()
    metrics_summary = {}

    try:
        # A. Train Anomaly Detector
        print("[1/3] Training Isolation Forest Anomaly Detector...")
        anomaly_detector.train(df_telemetry)
        
        # Evaluate anomaly detector against synthetic ground truth
        preds = []
        for _, row in df_telemetry.iterrows():
            res = anomaly_detector.detect(row.to_dict())
            preds.append(1 if res["is_anomaly"] else 0)
        
        y_true_anom = df_telemetry["label"].values
        prec_anom = precision_score(y_true_anom, preds, zero_division=0)
        rec_anom = recall_score(y_true_anom, preds, zero_division=0)
        f1_anom = f1_score(y_true_anom, preds, zero_division=0)
        acc_anom = accuracy_score(y_true_anom, preds)

        metrics_summary["anomaly_detection"] = {
            "algorithm": "Isolation Forest + Statistical Deviation Thresholds",
            "samples": len(df_telemetry),
            "precision": round(prec_anom, 4),
            "recall": round(rec_anom, 4),
            "f1": round(f1_anom, 4),
            "accuracy": round(acc_anom, 4)
        }
        db.add(EvaluationRun(
            suite_name="ML_ANOMALY",
            ground_truth_scenario="SYNTHETIC_EVAL_SPLIT",
            passed=(f1_anom > 0.70),
            precision=prec_anom,
            recall=rec_anom,
            f1=f1_anom,
            accuracy=acc_anom,
            details_json=json.dumps(metrics_summary["anomaly_detection"])
        ))

        # B. Train Severity Predictor
        print("[2/3] Training Random Forest Incident Severity Classifier...")
        X_sev = df_severity[["tier_level", "error_rate", "impacted_users_pct", "has_security_flag", "recent_deploy_minutes"]]
        y_sev = df_severity["severity"]
        X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X_sev, y_sev, test_size=0.25, random_state=42, stratify=y_sev)
        
        severity_predictor.train(pd.concat([X_train_s, y_train_s], axis=1))
        y_pred_sev = severity_predictor.model.predict(X_test_s)
        
        prec_sev = precision_score(y_test_s, y_pred_sev, average="weighted", zero_division=0)
        rec_sev = recall_score(y_test_s, y_pred_sev, average="weighted", zero_division=0)
        f1_sev = f1_score(y_test_s, y_pred_sev, average="weighted", zero_division=0)
        acc_sev = accuracy_score(y_test_s, y_pred_sev)
        cm_sev = confusion_matrix(y_test_s, y_pred_sev, labels=["P0", "P1", "P2", "P3"]).tolist()

        metrics_summary["severity_prediction"] = {
            "algorithm": "Random Forest Multi-Class Classifier (P0-P3)",
            "test_samples": len(y_test_s),
            "precision": round(prec_sev, 4),
            "recall": round(rec_sev, 4),
            "f1": round(f1_sev, 4),
            "accuracy": round(acc_sev, 4),
            "confusion_matrix": cm_sev,
            "labels": ["P0", "P1", "P2", "P3"]
        }
        db.add(EvaluationRun(
            suite_name="ML_SEVERITY",
            ground_truth_scenario="SYNTHETIC_EVAL_SPLIT",
            passed=(acc_sev > 0.75),
            precision=prec_sev,
            recall=rec_sev,
            f1=f1_sev,
            accuracy=acc_sev,
            details_json=json.dumps(metrics_summary["severity_prediction"])
        ))

        # C. Train Deployment Risk Estimator
        print("[3/3] Training Gradient Boosting Deployment Risk Estimator...")
        X_dep = df_deploy[["tier_level", "lines_added", "lines_deleted", "files_changed", "has_migrations", "author_prior_deployments", "is_friday_or_weekend"]]
        y_dep = df_deploy["caused_regression"]
        X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X_dep, y_dep, test_size=0.25, random_state=42, stratify=y_dep)
        
        deployment_risk_estimator.train(pd.concat([X_train_d, y_train_d], axis=1))
        y_pred_dep = deployment_risk_estimator.model.predict(X_test_d)

        prec_dep = precision_score(y_test_d, y_pred_dep, zero_division=0)
        rec_dep = recall_score(y_test_d, y_pred_dep, zero_division=0)
        f1_dep = f1_score(y_test_d, y_pred_dep, zero_division=0)
        acc_dep = accuracy_score(y_test_d, y_pred_dep)
        cm_dep = confusion_matrix(y_test_d, y_pred_dep).tolist()

        metrics_summary["deployment_risk"] = {
            "algorithm": "Gradient Boosting Binary Classifier (No Temporal Leakage)",
            "test_samples": len(y_test_d),
            "precision": round(prec_dep, 4),
            "recall": round(rec_dep, 4),
            "f1": round(f1_dep, 4),
            "accuracy": round(acc_dep, 4),
            "confusion_matrix": cm_dep
        }
        db.add(EvaluationRun(
            suite_name="ML_DEPLOY_RISK",
            ground_truth_scenario="SYNTHETIC_EVAL_SPLIT",
            passed=(f1_dep > 0.70),
            precision=prec_dep,
            recall=rec_dep,
            f1=f1_dep,
            accuracy=acc_dep,
            details_json=json.dumps(metrics_summary["deployment_risk"])
        ))

        db.commit()

        # Save metrics report to file
        with open(REPORT_PATH, "w") as f:
            json.dump(metrics_summary, f, indent=2)

        print("\n--- ML Training & Evaluation Results ---")
        for model_name, m in metrics_summary.items():
            print(f"[{model_name.upper()}] Acc: {m['accuracy']:.4f} | Prec: {m['precision']:.4f} | Rec: {m['recall']:.4f} | F1: {m['f1']:.4f}")
        print(f"[+] Evaluation report persisted to {REPORT_PATH}")
        print("==================================================")

    finally:
        db.close()

if __name__ == "__main__":
    run_ml_training_and_evaluation()
