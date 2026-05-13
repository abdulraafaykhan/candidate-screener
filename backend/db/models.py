"""SQLAlchemy ORM models for interview sessions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class SessionStatus(str, Enum):
    """Interview session status values."""

    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class QuestionDifficulty(str, Enum):
    """Difficulty levels for interview questions."""

    BASIC = "BASIC"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class InterviewSession(Base):
    """Interview session model."""

    __tablename__ = "interview_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    candidate_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    resume_text: Mapped[str] = mapped_column(String, nullable=False)
    skills_extracted: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[SessionStatus] = mapped_column(SqlEnum(SessionStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    questions: Mapped[list[InterviewQuestion]] = relationship(
        "InterviewQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    answers: Mapped[list[InterviewAnswer]] = relationship(
        "InterviewAnswer",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class InterviewQuestion(Base):
    """Interview question model."""

    __tablename__ = "interview_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(String, nullable=False)
    context_chunks: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[QuestionDifficulty] = mapped_column(SqlEnum(QuestionDifficulty), nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    session: Mapped[InterviewSession] = relationship("InterviewSession", back_populates="questions")
    answers: Mapped[list[InterviewAnswer]] = relationship(
        "InterviewAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class InterviewAnswer(Base):
    """Interview answer model."""

    __tablename__ = "interview_answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer_text: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(String, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    session: Mapped[InterviewSession] = relationship("InterviewSession", back_populates="answers")
    question: Mapped[InterviewQuestion] = relationship("InterviewQuestion", back_populates="answers")
