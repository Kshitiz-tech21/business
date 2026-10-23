# 🛡 Security & Limitations Documentation

This document outlines the security posture of the Autonomous Analytics Platform, the safeguards implemented to prevent data loss and unauthorized access, and the known technical limitations of the current version.

## 1. Security Architecture

### 🔐 Identity & Access Management (IAM)
- **Authentication**: Implements OAuth2 with JWT (JSON Web Tokens). Tokens are short-lived and signed with a secure `SECRET_KEY`.
- **Authorization**: Uses a **Workspace-based Access Control** model. Every user must be a member of a `Workspace` to access any associated `Project`, `Dataset`, or `Dashboard`.
- **Role-Based Access (RBAC)**: Implements roles (`OWNER`, `ADMIN`, `EDITOR`, `VIEWER`) to control who can create projects or approve destructive actions.

### 🏢 Multi-Tenant Isolation
- **Row-Level Isolation**: Every core table includes a `workspace_id`. 
- **Query Enforcement**: The API layer enforces a mandatory filter on all database reads, ensuring that a user from Workspace A can never access data from Workspace B, even if they have the exact UUID of a dataset.

### 🛡️ The Governance Guard (HITL)
The platform treats AI agents as "untrusted actors."
- **Destructive Action Interception**: All `UPDATE`, `DELETE`, `DROP`, and `TRUNCATE` operations are intercepted by the `GovernanceGuard`.
- **Approval Workflow**: Such actions are paused and converted into an `ApprovalRequest`. They cannot be executed until a human with `ADMIN` or `OWNER` privileges signs off.
- **Audit Trail**: Every approved or rejected action is logged in the `AuditEvent` table with a timestamp and reviewer ID.

### ☣️ Execution Sandboxing
- **Python Isolation**: Python scripts are executed using a restricted `exec()` environment. We strip the `__builtins__` to prevent access to dangerous modules like `os`, `sys`, and `subprocess`.
- **SQL Validation**: The system scans generated SQL for high-risk keywords before submission.

---

## 2. Known Limitations

### ⚠️ AI Reasoning & Hallucinations
- **SQL Accuracy**: While the `SQLAnalystAgent` is highly capable, it may occasionally generate syntactically correct but logically incorrect SQL. Users must verify results via the provided "Result Summary."
- **Determinism**: LLM responses can vary slightly between runs unless `temperature` is set to `0.0`.

### ⚠️ Sandbox Constraints
- **Execution Environment**: The current Python sandbox is a "software-level" restriction. For high-security production environments, this should be replaced with **OS-level isolation** (e.g., gVisor, Firecracker, or ephemeral Docker containers).
- **Library Access**: Only pre-approved libraries (numpy, pandas, scikit-learn) are available to the Python executor.

### ⚠️ Performance Bottlenecks
- **Sequential Execution**: Multi-agent tasks are currently executed sequentially. For very large datasets, this may introduce latency.
- **Memory Limits**: Large datasets loaded into the Python executor's memory may trigger OOM (Out-of-Memory) errors if not handled via chunking.

---

## 3. Hardening Guide (Production Recommendations)

For teams moving from the demo/local mode to a full production deployment, the following upgrades are recommended:

1.  **Infrastructure**: Move from SQLite to a managed **PostgreSQL (RDS/Cloud SQL)** instance.
2.  **Security**: Replace the local `SECRET_KEY` with a key managed by **AWS Secrets Manager** or **HashiCorp Vault**.
3.  **Network**: Deploy the API behind a **Reverse Proxy (Nginx/Traefik)** with forced HTTPS and a Web Application Firewall (WAF).
4.  **Compute**: Transition the `TaskExecutor` to run in **Isolated Kubernetes Pods** with strict resource quotas and no network access.
5.  **Monitoring**: Integrate **Prometheus and Grafana** to monitor job failure rates and LLM latency.
