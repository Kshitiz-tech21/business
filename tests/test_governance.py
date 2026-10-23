
import pytest
from ..services.governance import GovernanceGuard
from ..models.base import AgentTask, ActionType, JobStatus
from sqlmodel import Session

def test_governance_guard_intercepts(session):
    task = AgentTask(workspace_id="00000000-0000-0000-0000-000000000000", goal="test", payload="DROP TABLE")
    session.add(task)
    session.commit()
    
    approval = GovernanceGuard.request_approval(session, task, ActionType.DELETE)
    
    assert task.status == JobStatus.WAITING_APPROVAL
    assert approval.status == "PENDING"
