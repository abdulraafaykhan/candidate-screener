"""Prompt templates used across the RAG pipeline."""

from langchain.prompts import PromptTemplate

QUESTION_GENERATION_PROMPT = PromptTemplate(
    input_variables=["role", "resume_summary", "context", "count"],
    template=(
        "You are generating interview questions for the role: {role}.\n"
        "Resume summary:\n{resume_summary}\n\n"
        "Retrieved context:\n{context}\n\n"
        "Generate {count} questions. Questions must be conceptual and applied,"
        " vary in difficulty based on the candidate's experience,"
        " and reference technologies from the resume.\n"
        "Output MUST be a valid JSON array with items:"
        " {\\\"question\\\": string, \\\"topic\\\": string, \\\"difficulty\\\": string,"
        " \\\"expected_keywords\\\": [string]}."
    ),
)

FOLLOW_UP_PROMPT = PromptTemplate(
    input_variables=["question", "answer", "resume_context"],
    template=(
        "You are generating a follow-up interview question.\n"
        "Original question: {question}\n"
        "Candidate answer: {answer}\n"
        "Resume context: {resume_context}\n\n"
        "If the answer is weak, simplify and probe foundational understanding."
        " If the answer is strong, deepen with edge cases or architecture decisions."
        " Provide a concise follow-up question only."
    ),
)

EVALUATION_PROMPT = PromptTemplate(
    input_variables=["question", "expected_keywords", "answer"],
    template=(
        "Evaluate the candidate answer.\n"
        "Question: {question}\n"
        "Expected keywords: {expected_keywords}\n"
        "Answer: {answer}\n\n"
        "Return JSON:"
        " {\\\"score\\\": float, \\\"feedback\\\": string, \\\"strengths\\\": [string],"
        " \\\"gaps\\\": [string]}."
    ),
)

REPORT_GENERATION_PROMPT = PromptTemplate(
    input_variables=["session_data"],
    template=(
        "Generate a structured interview report from the session data below.\n"
        "Session data:\n{session_data}\n\n"
        "Return JSON:"
        " {\\\"overall_score\\\": float, \\\"recommendation\\\": string,"
        " \\\"strengths\\\": [string], \\\"areas_for_improvement\\\": [string],"
        " \\\"topic_scores\\\": {string: float}}."
    ),
)
