
import pytest
from ..services.agents.supervisor import SupervisorAgent
from ..services.executor import TaskExecutor
from sqlmodel import Session

def test_vertical_slice_flow(session, test_user, test_workspace):
    # 1. User asks a question
    supervisor = SupervisorAgent(session, "00000000-0000-0000-0000-000000000000")
    context = {"workspace_id": test_workspace.id, "user_id": test_user.id}
    
    # 2. Supervisor routes to specialist
    # We simulate a 'query' intent
    result = supervisor._route_intent("What is the total revenue?")
    assert result == "sql_analyst"
    
    # 3. Specialist uses Tool to submit Job
    # (Logic tested in test_governance and test_analytics)
    pass
