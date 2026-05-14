"""Tests for the resume parser."""

from backend.core.resume_parser import parse_resume


def test_parse_resume_from_pdf_bytes() -> None:
    """Parse a synthetic resume PDF and validate extracted fields."""

    sample_text = """
    Jane Doe
    Skills
    Python, FastAPI, React, AWS
    Experience
    Machine Learning Engineer — 2018 - Present
    Education
    B.S. Computer Science, University of Example
    Projects
    Resume Analyzer
    """
    try:
        import fitz
    except ImportError as exc:
        raise AssertionError("PyMuPDF is required for this test") from exc

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), sample_text)
    pdf_bytes = doc.tobytes()
    doc.close()

    result = parse_resume(pdf_bytes)

    assert "Python" in result.skills
    assert result.experience_years >= 0.0
    assert any("Computer Science" in entry for entry in result.education)
