# 🏛 Architecture Documentation: Autonomous Analytics Platform

This document provides a deep dive into the architectural decisions, design patterns, and data flows of the platform.

## 1. High-Level System Design
The platform follows a **layered service architecture**, ensuring that the AI agents never have direct, unmediated access to the underlying database.

### Layer Stack:
1.  **API Layer (FastAPI)**: Handles request validation, authentication, and response formatting.
2.  **Orchestration Layer (Supervisor Agent)**: Decomposes natural language goals into structured task contracts.
3.  **Service Layer (Specialists & Tools)**: Implements the business logic and interacts with the database via validated tools.
4.  **Governance Layer (GovernanceGuard)**: An interception middleware that pauses destructive operations for human approval.
5.  **Persistence Layer (PostgreSQL + Redis)**: Stores relational data, vector embeddings, and distributed task states.

---

## 2. The Autonomous Agent Framework

### Supervisor-Specialist Pattern
Instead of a single large LLM prompt, the platform uses a **delegation model**.

- **The Supervisor**: Acts as the "Project Manager." It does not perform the work; it parses intent and routes the request to the correct specialist.
- **The Specialists**: (Data Engineer, SQL Analyst, Biz Analyst, Viz Agent). Each specialist is a constrained agent with a specific toolset. This reduces "hallucinations" by narrowing the agent's focus.

### The Task Lifecycle
To ensure reliability, the platform uses **Typed Task Contracts**:
`Goal` $ightarrow$ `Plan (Steps)` $ightarrow$ `Execution (Worker)` $ightarrow$ `Validation` $ightarrow$ `Final Result`.

Every step is persisted in the `AgentTaskStep` table, allowing the system to resume a failed multi-step analysis from the exact point of failure.

---

## 3. Governance and Safety Model

### The Interception Mechanism
The platform implements a "Default-Deny" posture for destructive operations.

**The Guard Loop:**
1. Any tool call that suggests a `WRITE` or `DELETE` operation is passed to the `GovernanceGuard`.
2. The Guard creates an `ApprovalRequest` and sets the `AgentTask` status to `WAITING_APPROVAL`.
3. The execution thread is paused.
4. An admin receives a notification $ightarrow$ reviews the `suggested_sql` $ightarrow$ Approves/Rejects.
5. Only upon approval does the `TaskExecutor` resume the job.

---

## 4. Data Lifecycle and Flow

### The Ingestion Pipeline
`CSV/JSON` $ightarrow$ `Dataset` $ightarrow$ `DatasetColumn` $ightarrow$ `ColumnProfile` $ightarrow$ `CleaningRecommendation`.

1. **Profiling**: The system calculates mean, null count, and cardinality.
2. **Recommendation**: The `DataEngineerAgent` uses these stats to suggest fixes (e.g., "Fill nulls in Revenue with mean").
3. **Transformation**: Approved transformations are executed as `AnalysisJobs`.

### The Analysis Loop
`Natural Language` $ightarrow$ `SQL Analyst` $ightarrow$ `AnalyticsExecutor` $ightarrow$ `Result Set` $ightarrow$ `Biz Analyst` $ightarrow$ `Insight`.

---

## 5. Deployment Topology

### Local-First Mode
Optimized for privacy and development.
- **LLM**: Ollama runs locally, providing a private API endpoint.
- **DB**: Local PostgreSQL instance.
- **Worker**: Single Celery worker process.

### Production Mode
Optimized for scale and reliability.
- **LLM**: External provider (OpenAI/Azure) for higher reasoning capabilities.
- **Infrastructure**: Distributed containers in a Kubernetes cluster.
- **Storage**: Reports and ML artifacts are streamed to S3-compatible object storage to keep the DB lean.

---

## 6. Security Model
- **Multi-Tenancy**: Every table contains a `workspace_id`. Every query is appended with a `WHERE workspace_id = :current_workspace` filter to prevent cross-tenant data leaks.
- **Identity**: JWT-based authentication with short-lived access tokens.
- **Code Execution**: Python scripts are executed in a restricted global environment, stripping access to `os`, `sys`, and `subprocess` to prevent host-level attacks.
