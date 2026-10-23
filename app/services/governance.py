
from sqlmodel import Session
from ..models.base import ApprovalRequest, AgentTask, ActionType, JobStatus

class GovernanceGuard:
    @staticmethod
    def request_approval(session: Session, task: AgentTask, action_type: ActionType) -> ApprovalRequest:
        # Lock the task
        task.status = JobStatus.WAITING_APPROVAL
        session.add(task)
        
        # Create the approval request
        approval = ApprovalRequest(
            task_id=task.id,
            action_type=action_type,
            payload_json=task.payload,
            status="PENDING"
        )
        session.add(approval)
        session.commit()
        session.refresh(approval)
        return approval

    @staticmethod
    def resolve_approval(session: Session, approval_id: str, decision: str):
        approval = session.get(ApprovalRequest, approval_id)
        if not approval:
            return None
            
        approval.status = decision
        session.add(approval)
        
        task = session.get(AgentTask, approval.task_id)
        if decision == "APPROVED":
            task.status = JobStatus.COMPLETED # In reality, this triggers execution
        else:
            task.status = JobStatus.FAILED
            
        session.add(task)
        session.commit()
        return approval
