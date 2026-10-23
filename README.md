# 🚀 Autonomous Data & Business Analytics Platform

An enterprise-grade, AI-powered analytics platform that automates the data lifecycle from ingestion to executive reporting. Built with a focus on **governance**, **multi-tenant security**, and **autonomous agent orchestration**.

## 🛠 Technical Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + pgvector (Relational & Vector data)
- **Caching/Queue**: Redis + Celery
- **AI Orchestration**: Supervisor-Specialist Agent Architecture
- **LLM Integration**: Ollama (Local) or OpenAI/Anthropic (Cloud)
- **Frontend**: Next.js (B2B SaaS Design System)
- **Infrastructure**: Docker & Docker Compose

---

## 🌟 Core Features

### 1. Human-in-the-Loop (HITL) Governance
The platform implements a `GovernanceGuard` that intercepts all destructive operations.
- **Intercepted Actions**: `DELETE`, `DROP`, `TRUNCATE`, `UPDATE`.
- **Workflow**: AI Agent $ightarrow$ Request Approval $ightarrow$ Admin Sign-off $ightarrow$ Execution.

### 2. Autonomous Agent Fleet
A hierarchical agent system that decomposes complex goals into executable tasks:
- **Supervisor**: Orchestrates and routes intents.
- **Data Engineer**: Handles schema profiling, cleaning, and ingestion.
- **SQL Analyst**: Generates and executes high-performance analytical queries.
- **Business Analyst**: Synthesizes data into executive insights.
- **Viz Agent**: Programmatically builds dashboards and widgets.

### 3. Advanced Analytics Pipeline
- **Profiling**: Automatic data quality reports (Null counts, Cardinality).
- **Cleaning**: AI-suggested transformations based on profiling data.
- **Analytics**: Time-series forecasting, Z-score segmentation, and Anomaly detection.
- **Reporting**: S3-backed PDF/CSV executive reports.

---

## 🚀 Quick Start (Local-First Mode)

### Prerequisites
- Docker & Docker Compose
- Minimum 16GB RAM (recommended for local LLM)

### Setup & Launch
```bash
# 1. Clone and enter the directory
cd analytics_platform

# 2. Configure environment
cp .env.example .env

# 3. Launch the infrastructure
docker-compose -f deployments/docker-compose.yml up --build -d

# 4. Seed the demo data
# Ensure you are in the venv or use docker exec
docker exec -it analytics_api python scripts/seed_demo.py
```

### Accessing the Platform
- **API Documentation**: `http://localhost:8000/docs`
- **Ollama (Local LLM)**: `http://localhost:11434`

---

## 📖 Usage Guide

### Vertical Slice Workflow
1. **Upload**: Use `/datasets/import` to upload a CSV.
2. **Inspect**: Call `/datasets/{id}/metadata` to see the AI-detected schema.
3. **Clean**: Trigger `/datasets/{id}/recommend` and approve the cleaning steps.
4. **Ask**: Use `/chat/stream` to ask a question (e.g., *"What is the revenue trend in APAC?"*).
5. **Visualize**: The AI will automatically create a widget via `/dashboards/{id}/widgets`.
6. **Export**: Trigger `/reports/executive-summary` to get a PDF report.

---

## 🏗 Deployment Modes

### A. Local-First Mode
- **Configuration**: Uses SQLite/Postgres and a local Ollama instance.
- **Use Case**: Development, testing, and privacy-sensitive POCs.
- **Hardware**: GPU recommended for Ollama.

### B. Production Mode
- **Configuration**: Separate containers for API, Workers, and DB.
- **LLM**: Configured to use an external provider (OpenAI/Azure) via `.env`.
- **Storage**: Configured to use AWS S3 or Azure Blob storage for artifacts.
- **Security**: Reverse proxy (Nginx/Traefik) with HTTPS and strictly controlled ports.

---

## 🛠 Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **Job stuck in PENDING** | Worker not running | Check `docker-compose logs worker`. |
| **Approval not appearing** | Permission mismatch | Ensure user has `ADMIN` or `OWNER` role in workspace. |
| **LLM Timeout** | Resource exhaustion | Increase Docker RAM limit or switch to cloud provider. |
| **S3 Upload Failed** | Endpoint unreachable | Verify `S3_ENDPOINT` and network connectivity in `.env`. |

---

## 🧪 Testing & Quality Gates

Run the automated test suite to verify the la lyer:
```bash
pytest tests/
```
- **Unit Tests**: Core logic in `app/services`.
- **Integration Tests**: API endpoints and DB interactions.
- **Safety Tests**: Verification that unapproved destructive queries are blocked.
