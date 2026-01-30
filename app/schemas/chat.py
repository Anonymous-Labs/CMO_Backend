from typing import List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    autonomous_mode: bool = False


class ChatResponse(BaseModel):
    message: str
    role: str = "assistant"
    autonomous_followup: Optional[str] = None  # Follow-up message for autonomous mode

