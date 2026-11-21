# Google Cloud Run Deployment & Production Guide

This guide details the procedure for deploying the **AI Engineering Operations Agent** to **Google Cloud Run** with **Cloud SQL (PostgreSQL with pgvector)** and **Google Secret Manager**.

---

## 1. Prerequisites

- Google Cloud SDK (`gcloud`) authenticated: `gcloud auth login`
- Google Cloud Project with billing enabled: `gcloud config set project [PROJECT_ID]`
- Enabled APIs:
  ```bash
  gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com
  ```

---

## 2. Cloud SQL (PostgreSQL with pgvector) Setup

1. Create a Cloud SQL instance:
   ```bash
   gcloud sql instances create nexatech-ops-db \
     --database-version=POSTGRES_17 \
     --tier=db-custom-2-7680 \
     --region=us-central1 \
     --storage-auto-increase \
     --backup-start-time=02:00
   ```

2. Create database and application user:
   ```bash
   gcloud sql databases create ops_agent --instance=nexatech-ops-db
   gcloud sql users create ops_app --instance=nexatech-ops-db --password=[STRONG_DB_PASSWORD]
   ```

3. Enable `pgvector` extension:
   Connect via Cloud Shell or `psql` and execute:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

## 3. Secret Manager Configuration

Store sensitive credentials securely in Google Secret Manager:

```bash
# Database URL
echo -n "postgresql+psycopg://ops_app:[STRONG_DB_PASSWORD]@/ops_agent?host=/cloudsql/[PROJECT_ID]:us-central1:nexatech-ops-db" | \
  gcloud secrets create OPS_DATABASE_URL --data-file=-

# JWT Secret Key
echo -n "$(openssl rand -hex 32)" | \
  gcloud secrets create OPS_SECRET_KEY --data-file=-

# Google Gemini API Key
echo -n "[YOUR_GEMINI_API_KEY]" | \
  gcloud secrets create GEMINI_API_KEY --data-file=-
```

---

## 4. Build and Deploy Container to Cloud Run

1. Create an Artifact Registry repository:
   ```bash
   gcloud artifacts repositories create ops-agent-repo \
     --repository-format=docker \
     --location=us-central1
   ```

2. Build and submit image via Cloud Build:
   ```bash
   gcloud builds submit \
     --tag us-central1-docker.pkg.dev/[PROJECT_ID]/ops-agent-repo/ai-eng-ops-agent:latest
   ```

3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy ai-eng-ops-agent \
     --image us-central1-docker.pkg.dev/[PROJECT_ID]/ops-agent-repo/ai-eng-ops-agent:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --add-cloudsql-instances=[PROJECT_ID]:us-central1:nexatech-ops-db \
     --set-secrets="DATABASE_URL=OPS_DATABASE_URL:latest,SECRET_KEY=OPS_SECRET_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest" \
     --set-env-vars="ENVIRONMENT=production,DEBUG=False,GEMINI_MODEL=gemini-2.5-flash" \
     --memory=2Gi \
     --cpu=2 \
     --min-instances=1 \
     --max-instances=10
   ```

---

## 5. Seed Enterprise Database & ML Models on Cloud Run

Execute a single-run Cloud Run Job or run seed command through Cloud Shell:
```bash
gcloud run jobs create seed-nexatech-db \
  --image us-central1-docker.pkg.dev/[PROJECT_ID]/ops-agent-repo/ai-eng-ops-agent:latest \
  --command="python" \
  --args="-m,backend.app.simulator.seed,--seed,42" \
  --set-secrets="DATABASE_URL=OPS_DATABASE_URL:latest" \
  --region us-central1

gcloud run jobs execute seed-nexatech-db --region us-central1
```

---

## 6. Continuous Integration (GitHub Actions)

Create `.github/workflows/ci.yml`:
```yaml
name: CI Test & Evaluation Suite

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Backend Dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Seed Test Database
        run: |
          python -m backend.app.simulator.seed --reset --seed 42

      - name: Run ML Training & Evaluation
        run: |
          python -m backend.app.ml.pipeline

      - name: Run Pytest Suite
        run: |
          python -m pytest backend/tests/ -v

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Build Frontend Assets
        run: |
          cd frontend
          npm ci
          npm run build
```
