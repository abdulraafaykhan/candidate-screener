"""Resume parsing utilities for extracting structured candidate data."""

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Iterable

import fitz
from pydantic import BaseModel


KNOWN_SKILLS: set[str] = {
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "React",
    "Next.js",
    "FastAPI",
    "Django",
    "Flask",
    "Node.js",
    "TensorFlow",
    "PyTorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "SQL",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "Docker",
    "Kubernetes",
    "AWS",
    "GCP",
    "Azure",
    "Git",
    "LangChain",
    "HuggingFace",
    "OpenCV",
    "Spark",
}


class ResumeData(BaseModel):
    """Structured resume data extracted from a PDF."""

    skills: list[str]
    experience_years: float
    education: list[str]
    job_titles: list[str]
    domains: list[str]
    projects: list[str]
    raw_text: str


@dataclass(frozen=True)
class SectionParseResult:
    """Parsed resume sections."""

    skills_lines: list[str]
    education_lines: list[str]
    experience_lines: list[str]
    projects_lines: list[str]


def parse_resume(pdf_bytes: bytes) -> ResumeData:
    """Parse a PDF resume and return structured data."""

    try:
        raw_text = _extract_text(pdf_bytes)
        sections = _parse_sections(raw_text)
        skills = _extract_skills(raw_text, sections.skills_lines)
        experience_years = _estimate_experience_years(raw_text, sections.experience_lines)
        education = _extract_education(sections.education_lines)
        job_titles = _extract_job_titles(raw_text, sections.experience_lines)
        projects = _extract_projects(sections.projects_lines)
        domains = _categorize_domains(skills)
        return ResumeData(
            skills=skills,
            experience_years=experience_years,
            education=education,
            job_titles=job_titles,
            domains=domains,
            projects=projects,
            raw_text=raw_text,
        )
    except (ValueError, RuntimeError, fitz.FileDataError, fitz.FitzError):
        return ResumeData(
            skills=[],
            experience_years=0.0,
            education=[],
            job_titles=[],
            domains=[],
            projects=[],
            raw_text="",
        )


def _extract_text(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using PyMuPDF."""

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return "\n".join(pages).strip()


def _parse_sections(text: str) -> SectionParseResult:
    """Parse major sections from the resume text."""

    skills_lines: list[str] = []
    education_lines: list[str] = []
    experience_lines: list[str] = []
    projects_lines: list[str] = []

    current_section = ""
    for line in _split_lines(text):
        normalized = line.strip()
        if not normalized:
            continue
        header = normalized.lower()
        if header in {"skills", "technologies", "tech stack", "technical skills"}:
            current_section = "skills"
            continue
        if header in {"experience", "work experience", "professional experience"}:
            current_section = "experience"
            continue
        if header in {"education", "academic background"}:
            current_section = "education"
            continue
        if header in {"projects", "project experience"}:
            current_section = "projects"
            continue

        if current_section == "skills":
            skills_lines.append(normalized)
        elif current_section == "experience":
            experience_lines.append(normalized)
        elif current_section == "education":
            education_lines.append(normalized)
        elif current_section == "projects":
            projects_lines.append(normalized)

    return SectionParseResult(
        skills_lines=skills_lines,
        education_lines=education_lines,
        experience_lines=experience_lines,
        projects_lines=projects_lines,
    )


def _extract_skills(text: str, section_lines: list[str]) -> list[str]:
    """Extract skills from the resume text and skill section."""

    found: list[str] = []
    normalized_text = text.lower()
    for skill in KNOWN_SKILLS:
        if skill.lower() in normalized_text:
            found.append(skill)

    for line in section_lines:
        for entry in re.split(r"[,/]|\s{2,}", line):
            cleaned = entry.strip("-•* \t")
            if not cleaned:
                continue
            for skill in KNOWN_SKILLS:
                if cleaned.lower() == skill.lower() and skill not in found:
                    found.append(skill)
            if cleaned not in found and len(cleaned) <= 40:
                found.append(cleaned)

    return _dedupe_preserve_order(found)


def _estimate_experience_years(text: str, experience_lines: list[str]) -> float:
    """Estimate total years of experience from date ranges."""

    candidates = "\n".join(experience_lines) if experience_lines else text
    range_pattern = re.compile(
        r"(?P<start>(?:19|20)\d{2})\s*[-–]\s*(?P<end>(?:19|20)\d{2}|present|current)",
        re.IGNORECASE,
    )
    current_year = datetime.utcnow().year
    durations: list[int] = []
    for match in range_pattern.finditer(candidates):
        start = int(match.group("start"))
        end_token = match.group("end").lower()
        end = current_year if end_token in {"present", "current"} else int(end_token)
        if end >= start:
            durations.append(end - start)

    if durations:
        return float(max(durations))

    years = [int(year) for year in re.findall(r"(?:19|20)\d{2}", candidates)]
    if len(years) >= 2:
        return float(max(years) - min(years))
    return 0.0


def _extract_education(education_lines: list[str]) -> list[str]:
    """Extract education entries from the education section."""

    entries = [line.strip("-•* \t") for line in education_lines if line.strip()]
    return _dedupe_preserve_order(entries)


def _extract_job_titles(text: str, experience_lines: list[str]) -> list[str]:
    """Extract job titles from the resume text."""

    title_keywords = [
        "engineer",
        "developer",
        "scientist",
        "architect",
        "manager",
        "analyst",
        "lead",
        "researcher",
    ]
    candidates = experience_lines if experience_lines else _split_lines(text)
    titles: list[str] = []
    for line in candidates:
        if any(keyword in line.lower() for keyword in title_keywords):
            cleaned = line.strip("-•* \t")
            if len(cleaned) <= 120:
                titles.append(cleaned)
    return _dedupe_preserve_order(titles)


def _extract_projects(project_lines: list[str]) -> list[str]:
    """Extract project entries from the projects section."""

    entries = [line.strip("-•* \t") for line in project_lines if line.strip()]
    return _dedupe_preserve_order(entries)


def _categorize_domains(skills: Iterable[str]) -> list[str]:
    """Categorize candidate domains based on skills."""

    skill_set = {skill.lower() for skill in skills}
    domains: list[str] = []

    ml_skills = {"tensorflow", "pytorch", "scikit-learn", "huggingface", "opencv"}
    backend_skills = {"fastapi", "django", "flask", "node.js", "postgresql", "redis"}
    data_skills = {"spark", "pandas", "numpy", "sql"}
    cloud_skills = {"aws", "gcp", "azure"}

    if skill_set & ml_skills:
        domains.append("Machine Learning")
    if skill_set & backend_skills:
        domains.append("Backend Development")
    if skill_set & data_skills:
        domains.append("Data Engineering")
    if skill_set & cloud_skills:
        domains.append("Cloud Platforms")

    return domains


def _split_lines(text: str) -> list[str]:
    """Split raw text into normalized lines."""

    return [line.strip() for line in text.splitlines()]


def _dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    """Deduplicate items while preserving order."""

    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered
