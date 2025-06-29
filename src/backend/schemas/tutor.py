"""
Schemas for Tutor Antonina mode.
Definiuje modele żądań i odpowiedzi dla trybu edukacyjnego.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    """Chat message model for tutor mode."""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")


class TutorRequest(BaseModel):
    """Tutor mode request model."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    model: Optional[str] = Field(None, description="Model to use for completion")
    provider: Optional[str] = Field(None, description="Specific provider to use")
    tutor_mode: bool = Field(False, description="Włącz tryb Tutor Antoniny")


class TutorResponse(BaseModel):
    """Tutor mode response model."""
    reply: str = Field(..., description="Standard AI response")
    tutor_question: Optional[str] = Field(None, description="Pytanie doprecyzowujące od tutora")
    tutor_feedback: Optional[str] = Field(None, description="Sugestia i ulepszony prompt od tutora")
    model: str = Field(..., description="Model used for response")
    provider: str = Field(..., description="Provider used for response")
    usage: dict = Field(..., description="Token usage information")
    cost: dict = Field(..., description="Cost information")
    finish_reason: str = Field(..., description="Reason for completion")
    response_time: float = Field(..., description="Response time in seconds") 