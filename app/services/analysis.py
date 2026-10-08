from typing import Dict, Any, Optional

from backend.app.anonymizer import anonymize_text
from backend.app.preprocessing import clean_text, tokenize
from backend.app.scoring.resume_scorer import keyword_score, semantic_score, final_ats_score
from backend.app.models.ranker import ranker
from backend.app.services.genai import suggest_improvements

DEFAULT_SKILLS = {
    "python","django","flask","postgresql","mysql","sql","aws","azure","gcp",
    "rest","api","docker","kubernetes","git","machine learning","nlp",
    "pytorch","tensorflow","react","javascript"
}

def extract_skills(text: str, skills_set=None):
    skills_set = skills_set or DEFAULT_SKILLS
    text_lower = text.lower()
    found = set()

    for s in skills_set:
        if s.lower() in text_lower:
            found.add(s)

    tokens = set(tokenize(text_lower))
    for s in skills_set:
        parts = s.lower().split()
        if all(p in tokens for p in parts):
            found.add(s)

    return sorted(list(found))

def estimate_experience(text: str) -> float:
    import re
    durations = re.findall(r"(\d+)\s+years?", text, flags=re.I)
    if durations:
        return float(sum(int(d) for d in durations))

    years = re.findall(r"\b(19|20)\d{2}\b", text)
    if years:
        years_int = [int(y) for y in years]
        return float(max(years_int) - min(years_int))

    return 0.0

def extract_summary(text: str, max_len: int = 400) -> str:
    cleaned = clean_text(text)
    return cleaned[:max_len] + ("..." if len(cleaned) > max_len else "")

def analyze_resume_from_text(raw_text: str, job_description: Optional[str] = None) -> Dict[str, Any]:
    anonymized = anonymize_text(raw_text)
    summary = extract_summary(raw_text)
    skills = extract_skills(raw_text)
    experience = estimate_experience(raw_text)

    jd_text = job_description if job_description else " ".join(sorted(DEFAULT_SKILLS))

    kw_score = keyword_score(set(s.lower() for s in skills), set(s.lower() for s in DEFAULT_SKILLS))
    sem_score = semantic_score(raw_text, jd_text)

    ats = final_ats_score(kw_score, sem_score)
    ats = round((ats + (experience * 2)), 2)

    features = [[kw_score, sem_score, experience]]
    try:
        rank_score = float(ranker.predict_proba(features)[0])
    except Exception:
        rank_score = round(ats / 100.0, 3)

    try:
        genai_suggestions = suggest_improvements(raw_text)
    except Exception:
        genai_suggestions = ["Add measurable achievements", "Improve formatting", "Highlight JD skills"]

    return {
        "anonymized_text": anonymized,
        "summary": summary,
        "skills_detected": skills,
        "experience_years": experience,
        "keyword_score": round(kw_score, 3),
        "semantic_score": round(sem_score, 3),
        "ats_score": ats,
        "rank_score": round(rank_score, 3),
        "genai_suggestions": genai_suggestions
    }
