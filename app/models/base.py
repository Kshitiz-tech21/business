
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship

# --- ENUMS ---
class ActionType(str, Enum):
    DB_WRITE = "DB_WRITE"
    DATA_TRANSFER = "DATA_TRANSFER"
    DELETE = "DELETE"
    READ = "READ"

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING_APPROVAL = "WAITING_APPROVAL"

class ImportStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# --- MODELS ---

class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Workspace(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    slug: str
    settings_json: str = "{}"

class WorkspaceMember(SQLModel, table=True):
    workspace_id: UUID = Field(foreign_key="workspace.id", primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    role: str = "VIEWER" # OWNER, ADMIN, EDITOR, VIEWER

class Project(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Dataset(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    name: str
    source_type: str
    status: ImportStatus = Field(default=ImportStatus.PENDING)
    row_count: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DatasetColumn(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    dataset_id: UUID = Field(foreign_key="dataset.id", index=True)
    name: str
    data_type: str
    is_nullable: bool = True

class ColumnProfile(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    column_id: UUID = Field(foreign_key="datasetcolumn.id", index=True)
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    mean_value: Optional[float] = None
    null_count: int = 0
    distinct_count: int = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CleaningRecommendation(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    dataset_id: UUID = Field(foreign_key="dataset.id", index=True)
    column_id: Optional[UUID] = Field(foreign_key="datasetcolumn.id")
    rec_type: str
    description: str
    suggested_sql: str
    priority: str = "MEDIUM"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AnalysisJob(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    user_id: UUID = Field(foreign_key="user.id")
    job_type: str # SQL or PYTHON
    code: str
    status: JobStatus = Field(default=JobStatus.PENDING)
    result_summary: Optional[str] = None
    execution_time_ms: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class ChatSession(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    user_id: UUID = Field(foreign_key="user.id")
    title: str = "New Analysis Session"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="chatsession.id", index=True)
    role: str # USER, ASSISTANT, SYSTEM
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Dashboard(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    name: str
    layout_json: str = "{}"
    created_by: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Widget(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    dashboard_id: UUID = Field(foreign_key="dashboard.id", index=True)
    widget_type: str
    config_json: str = "{}"
    position_json: str = "{}"

class Metric(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    name: str
    formula_sql: str
    aggregation_type: str
    unit: str
    description: Optional[str] = None

class Pipeline(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    name: str
    config_json: str = "{}"
    schedule_cron: Optional[str] = None
    is_active: bool = True

class PipelineRun(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    pipeline_id: UUID = Field(foreign_key="pipeline.id", index=True)
    status: JobStatus = Field(default=JobStatus.PENDING)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    logs: Optional[str] = None

class Report(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    name: str
    artifact_path: str # Path to S3/Object Storage
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MLExperiment(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    name: str
    model_config_json: str = "{}"
    metric_results_json: str = "{}"
    artifact_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AuditEvent(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    user_id: UUID = Field(foreign_key="user.id")
    action: str
    entity_type: str
    entity_id: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AgentTask(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID
    goal: str
    status: JobStatus = Field(default=JobStatus.PENDING)
    payload: str


class AgentTaskStep(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="agenttask.id", index=True)
    agent_name: str
    input_json: str
    output_json: Optional[str] = None
    status: str = "PENDING" # PENDING, COMPLETED, FAILED
    error: Optional[str] = None
    attempts: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ApprovalRequest(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="agenttask.id")
    action_type: str
    payload_json: str
    status: str = "PENDING"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_by: Optional[str] = None
