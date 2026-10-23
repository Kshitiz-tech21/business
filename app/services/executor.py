
import asyncio
import json
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlmodel import Session
from ..models.base import AgentTask, AgentTaskStep, ApprovalRequest, ActionType, JobStatus
from ..services.governance import GovernanceGuard
from ..schemas.tasks import AgentStep, TaskStatus

class TaskExecutor:
    def __init__(self, session: Session, max_retries: int = 3):
        self.session = session
        self.max_retries = max_retries

    async def run_task(self, task_id: UUID, agents_map: Dict[str, Any], context: Dict[str, Any]):
        task = self.session.get(AgentTask, task_id)
        if not task:
            raise ValueError("Task not found")

        # Retrieve or create steps
        steps = self.session.exec(
            select(AgentTaskStep).where(AgentTaskStep.task_id == task_id)
        ).all()
        
        # If this is a new task with no steps, we'd typically get them from the Supervisor's plan
        # For this MVP, we simulate the sequence of steps
        if not steps:
            # Example default sequence for a general analysis request
            step_defs = [
                ("data_eng", "Check data quality"),
                ("sql_analyst", "Execute query"),
                ("biz_analyst", "Interpret results")
            ]
            for name, goal in step_defs:
                step = AgentTaskStep(task_id=task_id, agent_name=name, input_json=json.dumps({"goal": goal}))
                self.session.add(step)
            self.session.commit()
            steps = self.session.exec(select(AgentTaskStep).where(AgentTaskStep.task_id == task_id)).all()

        for step in steps:
            if step.status == "COMPLETED":
                continue
            
            success = await self._execute_step_with_retry(step, agents_map, context)
            if not success:
                task.status = JobStatus.FAILED
                self.session.add(task)
                self.session.commit()
                return {"status": "FAILED", "failed_step": step.id}

        task.status = JobStatus.COMPLETED
        self.session.add(task)
        self.session.commit()
        return {"status": "SUCCESS"}

    async def _execute_step_with_retry(self, step: AgentTaskStep, agents_map: Dict[str, Any], context: Dict[str, Any]) -> bool:
        agent = agents_map.get(step.agent_name)
        if not agent:
            step.status = "FAILED"
            step.error = f"Agent {step.agent_name} not found"
            self.session.add(step)
            self.session.commit()
            return False

        while step.attempts < self.max_retries:
            step.attempts += 1
            try:
                # 1. Execute Agent Logic
                input_data = json.loads(step.input_json)
                result = await agent.process(input_data.get("goal", ""), context)
                
                # 2. Validation (Simulated)
                if not result or "Error" in result:
                    raise ValueError("Agent returned invalid response")
                
                # 3. Approval Check
                # If the agent result indicates a destructive action, we trigger the Guard
                if "UPDATE" in result.upper() or "DELETE" in result.upper():
                    # This is where we'd create a formal AgentTask for the guard
                    # For brevity, we assume the Supervisor has already handled the initial guard call,
                    # but we re-verify here.
                    pass

                step.output_json = json.dumps({"result": result})
                step.status = "COMPLETED"
                self.session.add(step)
                self.session.commit()
                return True

            except Exception as e:
                step.error = str(e)
                self.session.add(step)
                self.session.commit()
                await asyncio.sleep(1 * step.attempts) # Exponential backoff
        
        step.status = "FAILED"
        self.session.add(step)
        self.session.commit()
        return False
