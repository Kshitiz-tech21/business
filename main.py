import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
from uuid import UUID, uuid4
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Field, Session, SQLModel, create_engine, select
from passlib.context import CryptContext
from jose import JWTError, jwt

# --- CONFIGURATION ---
PROJECT_ROOT = os.path.expanduser("~/analytics_platform")
os.makedirs(PROJECT_ROOT, exist_ok=True)
DATABASE_URL = f"sqlite:///{PROJECT_ROOT}/analytics.db"
SECRET_KEY = "SUPER_SECRET_B2B_SAAS_KEY_CHANGE_IN_PROD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
engine = create_engine(DATABASE_URL)

# --- MODELS ---
class ActionType(str, Enum):
    DB_WRITE = "DB_WRITE"
    DATA_TRANSFER = "DATA_TRANSFER"
    DELETE = "DELETE"
    READ = "READ"


class ImportStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    is_active: bool = True

class Workspace(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    slug: str




class DatasetColumn(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    dataset_id: UUID = Field(foreign_key="dataset.id", index=True)
    name: str
    data_type: str # e.g., 'INTEGER', 'VARCHAR', 'FLOAT'
    is_nullable: bool = True


class RecommendationType(str, Enum):
    FILL_NULLS = "FILL_NULLS"
    REMOVE_DUPLICATES = "REMOVE_DUPLICATES"
    TYPE_CONVERSION = "TYPE_CONVERSION"
    OUTLIER_REMOVAL = "OUTLIER_REMOVAL"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ChatRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"

class ChatSession(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    user_id: UUID = Field(foreign_key="user.id")
    title: str = "New Analysis Session"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="chatsession.id", index=True)
    role: ChatRole
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobType(str, Enum):
    SQL = "SQL"
    PYTHON = "PYTHON"

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING_APPROVAL = "WAITING_APPROVAL"

class AnalysisJob(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    user_id: UUID = Field(foreign_key="user.id")
    job_type: JobType
    code: str # The SQL query or Python script
    status: JobStatus = Field(default=JobStatus.PENDING)
    result_summary: Optional[str] = None
    execution_time_ms: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class CleaningRecommendation(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    dataset_id: UUID = Field(foreign_key="dataset.id", index=True)
    column_id: Optional[UUID] = Field(foreign_key="datasetcolumn.id")
    rec_type: RecommendationType
    description: str
    suggested_sql: str
    priority: str = "MEDIUM" # LOW, MEDIUM, HIGH
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ColumnProfile(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    column_id: UUID = Field(foreign_key="datasetcolumn.id", index=True)
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    mean_value: Optional[float] = None
    null_count: int = 0
    distinct_count: int = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Dataset(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    name: str
    source_type: str # e.g., 'CSV', 'JSON', 'SQL'
    status: ImportStatus = Field(default=ImportStatus.PENDING)
    row_count: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Dashboard(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    name: str
    layout_json: str = "{}" # Stores grid layout
    created_by: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Widget(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    dashboard_id: UUID = Field(foreign_key="dashboard.id", index=True)
    widget_type: str # e.g., 'BAR_CHART', 'KPI_CARD', 'TABLE'
    config_json: str = "{}" # Stores query, metric_id, formatting
    position_json: str = "{}" # Stores x, y, w, h

class Project(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkspaceMember(SQLModel, table=True):
    workspace_id: UUID = Field(foreign_key="workspace.id", primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    role: str = "VIEWER" # OWNER, ADMIN, EDITOR, VIEWER

class AgentTask(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id")
    goal: str
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    payload: str

class ApprovalRequest(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="agenttask.id")
    action_type: ActionType
    payload_json: str
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_by: Optional[str] = None

# --- AUTH UTILS ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # passlib bcrypt has a 72-byte limit; truncate and use a standard hashing method if needed
    # For this MVP, we truncate to 72 bytes to satisfy the bcrypt backend
    return pwd_context.hash(password[:72])

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- DEPENDENCIES ---
def get_session():
    with Session(engine) as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.get(User, UUID(user_id))
    if user is None:
        raise credentials_exception
    return user

# --- GOVERNANCE GUARD ---
class GovernanceGuard:
    @staticmethod
    def request_action(session: Session, task: AgentTask, action_type: ActionType):
        task.status = TaskStatus.WAITING_APPROVAL
        session.add(task)
        approval = ApprovalRequest(task_id=task.id, action_type=action_type, payload_json=task.payload)
        session.add(approval)
        session.commit()
        session.refresh(approval)
        return approval

# --- API ---
app = FastAPI(title="Autonomous Analytics Platform")

@app.post("/auth/register", status_code=201)
def register(email: str, password: str, full_name: str, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, hashed_password=get_password_hash(password), full_name=full_name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "full_name": current_user.full_name}

@app.post("/tasks/execute")
def execute_task(
    workspace_id: UUID, goal: str, action_type: ActionType, payload: str, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    member = session.get(WorkspaceMember, (workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    task = AgentTask(workspace_id=workspace_id, goal=goal, payload=payload)
    session.add(task)
    session.commit()
    session.refresh(task)
    
    if action_type in [ActionType.DB_WRITE, ActionType.DELETE, ActionType.DATA_TRANSFER]:
        approval = GovernanceGuard.request_action(session, task, action_type)
        return {"status": "WAITING_APPROVAL", "approval_id": approval.id}
    
    task.status = TaskStatus.COMPLETED
    session.add(task)
    session.commit()
    return {"status": "COMPLETED"}

@app.post("/approvals/{approval_id}/resolve")
def resolve_approval(
    approval_id: UUID, decision: ApprovalStatus, reviewer: str, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    approval = session.get(ApprovalRequest, approval_id)
    if not approval: raise HTTPException(status_code=404)
    
    approval.status = decision
    approval.reviewed_by = f"{current_user.full_name} ({reviewer})"
    session.add(approval)
    
    task = session.get(AgentTask, approval.task_id)
    task.status = TaskStatus.COMPLETED if decision == ApprovalStatus.APPROVED else TaskStatus.FAILED
    session.add(task)
    session.commit()
    return {"status": "RESOLVED", "decision": decision}


@app.post("/projects", status_code=201)
def create_project(
    workspace_id: UUID, name: str, description: Optional[str] = None, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    member = session.get(WorkspaceMember, (workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    project = Project(workspace_id=workspace_id, name=name, description=description)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@app.get("/projects")
def list_projects(
    workspace_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    member = session.get(WorkspaceMember, (workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    return session.exec(select(Project).where(Project.workspace_id == workspace_id)).all()

@app.get("/projects/{project_id}")
def get_project(
    project_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    member = session.get(WorkspaceMember, (project.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    return project

@app.patch("/projects/{project_id}")
def update_project(
    project_id: UUID, name: Optional[str] = None, description: Optional[str] = None, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    member = session.get(WorkspaceMember, (project.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    if name: project.name = name
    if description: project.description = description
    project.updated_at = datetime.now(timezone.utc)
    
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@app.delete("/projects/{project_id}")
def delete_project(
    project_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    member = session.get(WorkspaceMember, (project.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    # Route deletion through Governance Guard as it is a destructive action
    # We simulate an agent task for the deletion
    task = AgentTask(
        workspace_id=project.workspace_id, 
        goal=f"Delete project {project.name}", 
        payload=f"DELETE FROM project WHERE id='{project.id}'"
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    approval = GovernanceGuard.request_action(session, task, ActionType.DELETE)
    return {"status": "WAITING_APPROVAL", "approval_id": approval.id, "message": "Project deletion requires admin approval."}



@app.post("/datasets/import", status_code=202)
def import_dataset(
    workspace_id: UUID, project_id: UUID, name: str, source_type: str, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    # Authorization check
    member = session.get(WorkspaceMember, (workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    # Verify project exists and belongs to workspace
    project = session.get(Project, project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Project not found in this workspace")
    
    # Create dataset record with PENDING status
    dataset = Dataset(
        workspace_id=workspace_id, 
        project_id=project_id, 
        name=name, 
        source_type=source_type, 
        status=ImportStatus.PENDING
    )
    session.add(dataset)
    session.commit()
    session.refresh(dataset)
    
    # In a real system, we would dispatch a Celery/RabbitMQ task here.
    # For this MVP, we return the ID and simulate the status in a separate endpoint.
    return {"dataset_id": dataset.id, "status": dataset.status, "message": "Import queued successfully."}

@app.get("/datasets/{dataset_id}/status")
def get_dataset_status(
    dataset_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Authorization check
    member = session.get(WorkspaceMember, (dataset.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    return {
        "dataset_id": dataset.id,
        "name": dataset.name,
        "status": dataset.status,
        "row_count": dataset.row_count,
        "created_at": dataset.created_at
    }



@app.get("/datasets/{dataset_id}/metadata")
def get_dataset_metadata(
    dataset_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    member = session.get(WorkspaceMember, (dataset.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    columns = session.exec(select(DatasetColumn).where(DatasetColumn.dataset_id == dataset_id)).all()
    return {
        "dataset_name": dataset.name,
        "columns": columns
    }

@app.post("/datasets/{dataset_id}/profile", status_code=202)
def trigger_dataset_profiling(
    dataset_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    member = session.get(WorkspaceMember, (dataset.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    # Simulate profiling trigger. In production, this sends a message to a worker.
    return {"status": "PROCESSING", "message": "Profiling job started. You can poll the results at /datasets/{id}/profile."}

@app.get("/datasets/{dataset_id}/profile")
def get_dataset_profile(
    dataset_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    member = session.get(WorkspaceMember, (dataset.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    columns = session.exec(select(DatasetColumn).where(DatasetColumn.dataset_id == dataset_id)).all()
    profiles = []
    for col in columns:
        profile = session.exec(select(ColumnProfile).where(ColumnProfile.column_id == col.id)).first()
        profiles.append({
            "column": col.name,
            "profile": profile if profile else "No profile available. Trigger profiling first."
        })
    
    return {"dataset_id": dataset_id, "profiling_results": profiles}



@app.post("/datasets/{dataset_id}/recommend", status_code=200)
def generate_cleaning_recommendations(
    dataset_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    member = session.get(WorkspaceMember, (dataset.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    # Rule-based recommendation engine based on profiling data
    columns = session.exec(select(DatasetColumn).where(DatasetColumn.dataset_id == dataset_id)).all()
    recs = []
    
    for col in columns:
        profile = session.exec(select(ColumnProfile).where(ColumnProfile.column_id == col.id)).first()
        if profile:
            # Rule 1: High null count -> Suggest filling nulls
            if profile.null_count > 0:
                recs.append(CleaningRecommendation(
                    dataset_id=dataset_id,
                    column_id=col.id,
                    rec_type=RecommendationType.FILL_NULLS,
                    description=f"Column {col.name} has {profile.null_count} nulls. Suggest filling with mean.",
                    suggested_sql=f"UPDATE dataset_{dataset_id} SET {col.name} = {profile.mean_value or 0} WHERE {col.name} IS NULL"
                ))
            # Rule 2: Low distinct count relative to total -> Suggest type conversion to categorical
            if profile.distinct_count and profile.distinct_count < 10:
                recs.append(CleaningRecommendation(
                    dataset_id=dataset_id,
                    column_id=col.id,
                    rec_type=RecommendationType.TYPE_CONVERSION,
                    description=f"Column {col.name} has very low cardinality. Suggest converting to categorical.",
                    suggested_sql=f"ALTER TABLE dataset_{dataset_id} ALTER COLUMN {col.name} TYPE CATEGORICAL"
                ))
    
    session.add_all(recs)
    session.commit()
    return {"recommendations_generated": len(recs)}

@app.get("/datasets/{dataset_id}/recommendations")
def list_recommendations(
    dataset_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    member = session.get(WorkspaceMember, (dataset.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    return session.exec(select(CleaningRecommendation).where(CleaningRecommendation.dataset_id == dataset_id)).all()

@app.post("/datasets/{dataset_id}/transform/{rec_id}")
def execute_transformation(
    dataset_id: UUID, rec_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    rec = session.get(CleaningRecommendation, rec_id)
    if not rec or rec.dataset_id != dataset_id:
        raise HTTPException(status_code=404, detail="Recommendation not found for this dataset")
    
    dataset = session.get(Dataset, dataset_id)
    
    # Transformations are destructive writes -> Must go through Governance Guard
    task = AgentTask(
        workspace_id=dataset.workspace_id,
        goal=f"Execute cleaning: {rec.description}",
        payload=rec.suggested_sql
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    approval = GovernanceGuard.request_action(session, task, ActionType.DB_WRITE)
    return {
        "status": "WAITING_APPROVAL", 
        "approval_id": approval.id, 
        "message": "Data transformation requires admin approval to prevent data loss."
    }



@app.post("/analysis/run", status_code=202)
def create_analysis_run(
    project_id: UUID, query: str, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    # Project authorization
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    member = session.get(WorkspaceMember, (project.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    run = AnalysisJob(
        project_id=project_id, 
        user_id=current_user.id, 
        query=query, 
        status=JobStatus.PENDING
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    
    # Simulation: In a real system, we'd dispatch to an async executor (Triton, Spark, etc.)
    return {"run_id": run.id, "status": run.status, "message": "Analysis run queued successfully."}

@app.get("/analysis/run/{run_id}")
def get_run_status(
    run_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    run = session.get(AnalysisJob, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    
    # Project authorization
    project = session.get(Project, run.project_id)
    member = session.get(WorkspaceMember, (project.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    return {
        "run_id": run.id,
        "status": run.status,
        "query": run.query,
        "result_summary": run.result_summary,
        "execution_time_ms": run.execution_time_ms,
        "created_at": run.created_at,
        "completed_at": run.completed_at
    }

@app.get("/analysis/runs")
def list_project_runs(
    project_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    member = session.get(WorkspaceMember, (project.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    return session.exec(select(AnalysisJob).where(AnalysisJob.project_id == project_id)).all()



async def ai_response_generator(session_id: UUID, user_message: str, session: Session):
    # Simulate the AI thinking and acting process
    thoughts = [
        "Analyzing the request...",
        "Checking available datasets in the workspace...",
        "Formulating a SQL query to extract the metrics...",
        "Executing query and summarizing results..."
    ]
    
    for thought in thoughts:
        yield f'data: {{"type": "thought", "content": "{thought}"}}\\n\\n'
        await asyncio.sleep(0.8)
    
    full_response = f"Based on the data, I found that the trend for '{user_message}' is positive. Would you like me to generate a visualization?"
    tokens = full_response.split(" ")
    
    for token in tokens:
        yield f'data: {{"type": "token", "content": "{token} "}}\\n\\n'
        await asyncio.sleep(0.1)
    
    yield 'data: {"type": "done"}\\n\\n'
    
    # Save final response to DB
    msg = ChatMessage(session_id=session_id, role=ChatRole.ASSISTANT, content=full_response)
    session.add(msg)
    session.commit()

@app.post("/chat/sessions", status_code=201)
def create_chat_session(
    workspace_id: UUID, title: str = "New Analysis Session", 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    member = session.get(WorkspaceMember, (workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    chat_session = ChatSession(workspace_id=workspace_id, user_id=current_user.id, title=title)
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session

@app.post("/chat/stream")
async def chat_stream(
    session_id: UUID, message: str, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    chat_session = session.get(ChatSession, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    member = session.get(WorkspaceMember, (chat_session.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    # Save user message
    user_msg = ChatMessage(session_id=session_id, role=ChatRole.USER, content=message)
    session.add(user_msg)
    session.commit()
    
    return StreamingResponse(
        ai_response_generator(session_id, message, session), 
        media_type="text/event-stream"
    )

@app.get("/chat/sessions/{session_id}/messages")
def get_chat_history(
    session_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    chat_session = session.get(ChatSession, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    member = session.get(WorkspaceMember, (chat_session.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    return session.exec(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)).all()



@app.post("/jobs/submit", status_code=202)
def submit_job(
    project_id: UUID, job_type: JobType, code: str, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    # Project authorization
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    member = session.get(WorkspaceMember, (project.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    # Create the job record
    job = AnalysisJob(
        project_id=project_id, 
        user_id=current_user.id, 
        job_type=job_type, 
        code=code, 
        status=JobStatus.PENDING
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    
    # GOVERNANCE CHECK
    # If it's SQL with writes or Python with potential destructive patterns, route to Guard
    is_destructive = False
    if job_type == JobType.SQL:
        destructive_keywords = ["UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER"]
        if any(kw in code.upper() for kw in destructive_keywords):
            is_destructive = True
    elif job_type == JobType.PYTHON:
        # Simple pattern match for destructive python calls
        destructive_patterns = ["os.remove", "shutil.rmtree", "cursor.execute", "drop_table"]
        if any(pat in code for pat in destructive_patterns):
            is_destructive = True
            
    if is_destructive:
        # We reuse the AgentTask logic to route through the GovernanceGuard
        task = AgentTask(
            workspace_id=project.workspace_id,
            goal=f"Execute {job_type} job",
            payload=code
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        approval = GovernanceGuard.request_action(session, task, ActionType.DB_WRITE)
        job.status = JobStatus.WAITING_APPROVAL
        session.add(job)
        session.commit()
        
        return {
            "job_id": job.id, 
            "status": "WAITING_APPROVAL", 
            "approval_id": approval.id,
            "message": "Job contains potentially destructive operations and requires admin approval."
        }
    
    return {"job_id": job.id, "status": job.status, "message": "Job submitted successfully."}

@app.get("/jobs/{job_id}")
def get_job_status(
    job_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    job = session.get(AnalysisJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    project = session.get(Project, job.project_id)
    member = session.get(WorkspaceMember, (project.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    return job



@app.post("/dashboards", status_code=201)
def create_dashboard(
    workspace_id: UUID, name: str, layout_json: Optional[str] = "{}", 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    member = session.get(WorkspaceMember, (workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    dashboard = Dashboard(
        workspace_id=workspace_id, 
        name=name, 
        layout_json=layout_json, 
        created_by=current_user.id
    )
    session.add(dashboard)
    session.commit()
    session.refresh(dashboard)
    return dashboard

@app.get("/dashboards")
def list_dashboards(
    workspace_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    member = session.get(WorkspaceMember, (workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    return session.exec(select(Dashboard).where(Dashboard.workspace_id == workspace_id)).all()

@app.get("/dashboards/{dashboard_id}")
def get_dashboard(
    dashboard_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dashboard = session.get(Dashboard, dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    member = session.get(WorkspaceMember, (dashboard.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    widgets = session.exec(select(Widget).where(Widget.dashboard_id == dashboard_id)).all()
    return {"dashboard": dashboard, "widgets": widgets}

@app.patch("/dashboards/{dashboard_id}")
def update_dashboard(
    dashboard_id: UUID, name: Optional[str] = None, layout_json: Optional[str] = None, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dashboard = session.get(Dashboard, dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    member = session.get(WorkspaceMember, (dashboard.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    if name: dashboard.name = name
    if layout_json: dashboard.layout_json = layout_json
    dashboard.updated_at = datetime.now(timezone.utc)
    
    session.add(dashboard)
    session.commit()
    session.refresh(dashboard)
    return dashboard

@app.delete("/dashboards/{dashboard_id}")
def delete_dashboard(
    dashboard_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dashboard = session.get(Dashboard, dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    member = session.get(WorkspaceMember, (dashboard.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    # Route to Governance Guard
    task = AgentTask(
        workspace_id=dashboard.workspace_id, 
        goal=f"Delete dashboard {dashboard.name}", 
        payload=f"DELETE FROM dashboard WHERE id='{dashboard.id}'"
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    approval = GovernanceGuard.request_action(session, task, ActionType.DELETE)
    return {"status": "WAITING_APPROVAL", "approval_id": approval.id, "message": "Dashboard deletion requires admin approval."}

@app.post("/dashboards/{dashboard_id}/widgets", status_code=201)
def add_widget(
    dashboard_id: UUID, widget_type: str, config_json: str = "{}", position_json: str = "{}",
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    dashboard = session.get(Dashboard, dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    member = session.get(WorkspaceMember, (dashboard.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    widget = Widget(
        dashboard_id=dashboard_id, 
        widget_type=widget_type, 
        config_json=config_json, 
        position_json=position_json
    )
    session.add(widget)
    session.commit()
    session.refresh(widget)
    return widget



@app.post("/widgets/{widget_id}/execute", status_code=202)
def execute_widget_query(
    widget_id: UUID, 
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    # 1. Retrieve the widget and its dashboard context
    widget = session.get(Widget, widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    dashboard = session.get(Dashboard, widget.dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Associated dashboard not found")
    
    # 2. Authorization: Verify user belongs to the workspace
    member = session.get(WorkspaceMember, (dashboard.workspace_id, current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    # 3. Extract the query from config_json (simulating JSON parsing)
    import json
    try:
        config = json.loads(widget.config_json)
        query = config.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Widget configuration is missing a query")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in widget configuration")

    # 4. Route through the AnalysisJob system for auditing and execution
    # Chart queries are typically SQL reads.
    job = AnalysisJob(
        project_id=dashboard.workspace_id, # Reusing workspace_id for context in this MVP
        user_id=current_user.id,
        job_type=JobType.SQL,
        code=query,
        status=JobStatus.PENDING
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    
    # Security Check: Even though it's a "Chart", we check for destructive keywords
    destructive_keywords = ["UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER"]
    if any(kw in query.upper() for kw in destructive_keywords):
        task = AgentTask(
            workspace_id=dashboard.workspace_id,
            goal=f"Execute chart query for widget {widget_id}",
            payload=query
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        approval = GovernanceGuard.request_action(session, task, ActionType.DB_WRITE)
        job.status = JobStatus.WAITING_APPROVAL
        session.add(job)
        session.commit()
        
        return {
            "job_id": job.id, 
            "status": "WAITING_APPROVAL", 
            "approval_id": approval.id, 
            "message": "Chart query contains destructive operations and requires approval."
        }
    
    return {
        "job_id": job.id, 
        "status": job.status, 
        "message": "Chart query submitted successfully."
    }


SQLModel.metadata.create_all(engine)
