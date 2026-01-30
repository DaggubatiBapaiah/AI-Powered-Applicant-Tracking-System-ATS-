from typing import Dict, List, Set
from backend.services.ai_engine import extract_resume_keywords, extract_jd_keywords

def match_resume_to_job(resume_text: str, jd_text: str) -> Dict:
    """
    Compares resume text against job description text based on keywords.
    """
    resume_keywords = extract_resume_keywords(resume_text)
    jd_keywords = extract_jd_keywords(jd_text)
    
    if not jd_keywords:
        return {
            "score": 0.0,
            "matched_keywords": [],
            "missing_keywords": []
        }
    
    matched_keywords = resume_keywords.intersection(jd_keywords)
    missing_keywords = jd_keywords - resume_keywords
    
    score = (len(matched_keywords) / len(jd_keywords)) * 100
    
    return {
        "score": round(score, 2),
        "matched_keywords": list(matched_keywords),
        "missing_keywords": list(missing_keywords)
    }
