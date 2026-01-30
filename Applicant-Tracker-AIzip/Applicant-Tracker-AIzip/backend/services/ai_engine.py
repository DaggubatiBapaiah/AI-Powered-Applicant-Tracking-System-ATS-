from typing import Set
from backend.utils.text_utils import extract_keywords

def extract_resume_keywords(resume_text: str) -> Set[str]:
    """
    Extracts meaningful keywords from resume text.
    """
    return extract_keywords(resume_text)

def extract_jd_keywords(jd_text: str) -> Set[str]:
    """
    Extracts meaningful keywords from job description text.
    """
    return extract_keywords(jd_text)
