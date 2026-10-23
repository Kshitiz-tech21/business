
from .base import BaseAgent
from .specialists import DataEngineerAgent, SQLAnalystAgent, BusinessAnalystAgent, VizAgent
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlmodel import Session

class SupervisorAgent(BaseAgent):
    def __init__(self, session: Session, chat_session_id: UUID):
        super().__init__(
            name="Supervisor", 
            role="Orchestrator", 
            session=session, 
            chat_session_id=chat_session_id
        )
        self.agents = {
            "data_eng": DataEngineerAgent("DataEng", "Data Engineer", session, chat_session_id),
            "sql_analyst": SQLAnalystAgent("SQLAnalyst", "SQL Analyst", session, chat_session_id),
            "biz_analyst": BusinessAnalystAgent("BizAnalyst", "Business Analyst", session, chat_session_id),
            "viz": VizAgent("VizAgent", "Visualization Expert", session, chat_session_id)
        }

    async def process(self, message: str, context: Dict[str, Any]) -> str:
        # 1. Intent Parsing (Simulation of LLM Router)
        # In production, this would be: response = llm.chat(prompt + message)
        route = self._route_intent(message)
        
        if route == "data_eng":
            result = await self.agents["data_eng"].process(message, context)
        elif route == "sql_analyst":
            result = await self.agents["sql_analyst"].process(message, context)
        elif route == "biz_analyst":
            result = await self.agents["biz_analyst"].process(message, context)
        elif route == "viz":
            result = await self.agents["viz"].process(message, context)
        else:
            result = "I'm not sure which specialist to route this to. Could you clarify?"
            
        return result
    async def process_complex_task(self, message: str, context: Dict[str, Any]):
        # 1. Create a Task and plan the steps (Simulation)
        task = AgentTask(
            workspace_id=context.get('workspace_id'),
            goal=message,
            payload=message
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        
        # 2. Hand off to the TaskExecutor
        from ..services.executor import TaskExecutor
        executor = TaskExecutor(self.session)
        result = await executor.run_task(task.id, self.agents, context)
        
        return result


    def _route_intent(self, message: str) -> str:
        m = message.lower()
        if any(w in m for w in ["import", "clean", "null", "schema", "dataset"]): return "data_eng"
        if any(w in m for w in ["query", "sum", "count", "average", "sql"]): return "sql_analyst"
        if any(w in m for w in ["trend", "why", "insight", "growth", "analyze"]): return "biz_analyst"
        if any(w in m for w in ["chart", "graph", "dashboard", "visualize"]): return "viz"
        return "unknown"
