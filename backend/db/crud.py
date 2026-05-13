"""CRUD helpers for interview sessions."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.models import InterviewAnswer, InterviewQuestion, InterviewSession, QuestionDifficulty, SessionStatus


async def create_session(
    db: AsyncSession,
    role: str,
    candidate_name: str,
    resume_text: str,
) -> InterviewSession:
    """Create a new interview session."""

    session = InterviewSession(
        role=role,
        candidate_name=candidate_name,
        resume_text=resume_text,
        skills_extracted={},
        status=SessionStatus.CREATED,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def update_session_skills(
    db: AsyncSession,
    session_id: str,
    skills: dict[str, Any],
) -> InterviewSession:
    """Update extracted skills for a session."""

    session = await get_session(db, session_id)
    if session is None:
        raise ValueError("Session not found")
    session.skills_extracted = skills
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, session_id: str) -> InterviewSession | None:
    """Retrieve a session by id."""

    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(selectinload(InterviewSession.questions), selectinload(InterviewSession.answers)),
    )
    return result.scalar_one_or_none()


async def complete_session(db: AsyncSession, session_id: str) -> InterviewSession:
    """Mark a session as completed."""

    session = await get_session(db, session_id)
    if session is None:
        raise ValueError("Session not found")
    session.status = SessionStatus.COMPLETED
    await db.commit()
    await db.refresh(session)
    return session


async def create_question(
    db: AsyncSession,
    session_id: str,
    question_text: str,
    context: list[dict[str, Any]],
    topic: str,
    difficulty: QuestionDifficulty,
) -> InterviewQuestion:
    """Create an interview question for a session."""

    question = InterviewQuestion(
        session_id=session_id,
        question_text=question_text,
        context_chunks=context,
        question_number=await _next_question_number(db, session_id),
        topic=topic,
        difficulty=difficulty,
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def get_session_questions(db: AsyncSession, session_id: str) -> list[InterviewQuestion]:
    """List all questions for a session."""

    result = await db.execute(
        select(InterviewQuestion)
        .where(InterviewQuestion.session_id == session_id)
        .order_by(InterviewQuestion.question_number)
    )
    return list(result.scalars().all())


async def create_answer(
    db: AsyncSession,
    question_id: str,
    session_id: str,
    answer_text: str,
) -> InterviewAnswer:
    """Create an answer for a question."""

    answer = InterviewAnswer(
        question_id=question_id,
        session_id=session_id,
        answer_text=answer_text,
    )
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    return answer


async def update_answer_score(
    db: AsyncSession,
    answer_id: str,
    score: float,
    feedback: str,
) -> InterviewAnswer:
    """Update evaluation details for an answer."""

    result = await db.execute(select(InterviewAnswer).where(InterviewAnswer.id == answer_id))
    answer = result.scalar_one_or_none()
    if answer is None:
        raise ValueError("Answer not found")
    answer.score = score
    answer.feedback = feedback
    await db.commit()
    await db.refresh(answer)
    return answer


async def get_session_report(db: AsyncSession, session_id: str) -> dict[str, Any]:
    """Return the complete session report payload."""

    session = await get_session(db, session_id)
    if session is None:
        raise ValueError("Session not found")
    return {
        "session": session,
        "questions": session.questions,
        "answers": session.answers,
    }


async def _next_question_number(db: AsyncSession, session_id: str) -> int:
    """Compute the next question number for a session."""

    result = await db.execute(
        select(InterviewQuestion)
        .where(InterviewQuestion.session_id == session_id)
        .order_by(InterviewQuestion.question_number.desc())
        .limit(1)
    )
    last_question = result.scalar_one_or_none()
    if last_question is None:
        return 1
    return last_question.question_number + 1
