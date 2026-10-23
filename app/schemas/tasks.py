
from typing import List, Optional, Any, Dict, Union
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field as PydanticField
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AgentStep(BaseModel):
    step_id: UUID
    agent_name: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: TaskStatus = TaskStatus.PENDING
    error: Optional[str] = None
    attempts: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TaskContract(BaseModel):
    task_id: UUID
    goal: str
    context: Dict[str, Any]
    steps: List[AgentStep]
    current_step_index: int = 0
    final_result: Optional[Any] = None
    status: TaskStatus = TaskStatus.PENDING
