import argparse
import sys
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.simulator.generator import NexaTechSimulator
import backend.app.models  # load all models into Base.metadata

def seed_database(reset: bool = False, seed: int = 42):
    print("==================================================")
    print("  NexaTech Enterprise Simulator - Database Seed   ")
    print("==================================================")
    
    if reset:
        print("[!] Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("[+] Tables dropped.")

    print("[*] Creating database tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    print("[+] Database schema verified.")

    db = SessionLocal()
    try:
        sim = NexaTechSimulator(seed=seed)
        sim.generate_all(db)

        # Verification counts
        from backend.app.models.service import Service, Deployment
        from backend.app.models.user import User, Team
        from backend.app.models.incident import Incident
        from backend.app.models.security import SecurityFinding, IAMEvent
        from backend.app.models.observability import MetricObservation, LogEntry
        from backend.app.models.knowledge import Document

        srv_count = db.query(Service).count()
        usr_count = db.query(User).count()
        dep_count = db.query(Deployment).count()
        inc_count = db.query(Incident).count()
        sec_count = db.query(SecurityFinding).count()
        iam_count = db.query(IAMEvent).count()
        met_count = db.query(MetricObservation).count()
        log_count = db.query(LogEntry).count()
        doc_count = db.query(Document).count()

        print("\n--- Relational Integrity & Seeding Summary ---")
        print(f" Teams & Users:          {db.query(Team).count()} teams, {usr_count} users")
        print(f" Services:               {srv_count} microservices")
        print(f" Deployments:            {dep_count} recorded releases")
        print(f" Incidents:              {inc_count} active / historical incidents")
        print(f" Security Findings:      {sec_count} CVE vulnerability records")
        print(f" IAM Security Events:    {iam_count} access audit events")
        print(f" Metric Observations:    {met_count} telemetry datapoints")
        print(f" Log Entries:            {log_count} structured application logs")
        print(f" RAG Knowledge Docs:     {doc_count} runbooks & postmortems")
        print("==================================================")
        print("[SUCCESS] NexaTech simulator database ready!")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed NexaTech Simulator Database")
    parser.add_argument("--reset", action="store_true", help="Reset all tables before seeding")
    parser.add_argument("--seed", type=int, default=42, help="Random generator seed (default 42)")
    args = parser.parse_args()
    seed_database(reset=args.reset, seed=args.seed)
