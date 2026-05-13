"""Pydantic schemas for database entities."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from backend.db.models import QuestionDifficulty, SessionStatus


class InterviewSessionSchema(BaseModel):
    """Schema for interview sessions."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_name: str
    role: str
    resume_text: str
    skills_extracted: dict[str, Any]
    status: SessionStatus
    created_at: datetime
    completed_at: datetime | None


class InterviewQuestionSchema(BaseModel):
    """Schema for interview questions."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    question_text: str
    context_chunks: list[dict[str, Any]]
    question_number: int
    difficulty: QuestionDifficulty
    topic: str
    created_at: datetime


class InterviewAnswerSchema(BaseModel):
    """Schema for interview answers."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    question_id: str
    session_id: str
    answer_text: str
    score: float | None
    feedback: str | None
    answered_at: datetime
