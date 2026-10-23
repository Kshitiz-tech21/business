
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlmodel import Session
from ..models.base import ChatSession, ChatMessage

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, session: Session, chat_session_id: UUID):
        self.name = name
        self.role = role
        self.session = session
        self.chat_session_id = chat_session_id

    @abstractmethod
    async def process(self, message: str, context: Dict[str, Any]) -> str:
        pass

    def log_message(self, role: str, content: str):
        msg = ChatMessage(session_id=self.chat_session_id, role=role, content=content)
        self.session.add(msg)
        self.session.commit()
