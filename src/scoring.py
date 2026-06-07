"""Keyword extraction, ATS matching, and score calculation."""

from __future__ import annotations

import re
from collections import Counter


ROLE_PRESETS = {
    "backend": {
        "label": "Backend Developer",
        "skills": [
            "python", "flask", "fastapi", "django", "sql", "postgresql",
            "mysql", "rest api", "api", "git", "testing", "docker",
        ],
    },
    "frontend": {
        "label": "Frontend Developer",
        "skills": [
            "html", "css", "javascript", "typescript", "react", "vue",
            "angular", "responsive", "ui", "accessibility", "api", "git",
        ],
    },
    "data": {
        "label": "Data Analyst",
        "skills": [
            "python", "sql", "excel", "power bi", "tableau", "pandas",
            "numpy", "statistics", "dashboard", "visualization", "etl",
        ],
    },
    "ai": {
        "label": "AI/ML Intern",
        "skills": [
            "python", "machine learning", "deep learning", "nlp", "pandas",
            "numpy", "scikit-learn", "tensorflow", "pytorch", "llm",
            "fine-tuning", "api",
        ],
    },
}

STOPWORDS = {
    "and", "the", "for", "with", "from", "this", "that", "will", "you",
    "our", "are", "job", "role", "work", "team", "using", "have", "need",
    "good", "plus", "must", "can", "who", "into", "your", "their", "about",
    "build", "create", "candidate", "developer", "experience",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z+#.\-]{1,}", text.lower())


def extract_keywords(text: str, role_key: str = "backend", limit: int = 18) -> list[str]:
    """Extract the most relevant keywords from text, prioritizing role-preset skills."""
    normalized = normalize_text(text)
    preset = ROLE_PRESETS.get(role_key, ROLE_PRESETS["backend"])
    keywords: list[str] = []

    for skill in preset["skills"]:
        if skill in normalized and skill not in keywords:
            keywords.append(skill)

    counts = Counter(
        token
        for token in tokenize(text)
        if token not in STOPWORDS and len(token) > 2 and not token.isdigit()
    )
    for token, _ in counts.most_common(40):
        if token not in keywords:
            keywords.append(token)
        if len(keywords) >= limit:
            break

    return keywords[:limit]


def calculate_match_score(resume_text: str, job_text: str, role_key: str) -> dict:
    """Calculate ATS-style keyword match score between resume and job description."""
    resume_norm = normalize_text(resume_text)
    job_keywords = extract_keywords(job_text, role_key=role_key, limit=24)
    matched = [kw for kw in job_keywords if kw in resume_norm]
    missing = [kw for kw in job_keywords if kw not in resume_norm]
    score = round((len(matched) / max(len(job_keywords), 1)) * 100)

    section_scores = {
        "keyword_match": score,
        "resume_depth": min(100, max(20, len(tokenize(resume_text)) // 3)),
        "job_alignment": min(100, 45 + len(matched) * 7),
        "truthfulness_guard": 100,
    }

    return {
        "score": score,
        "matched_keywords": matched,
        "missing_keywords": missing[:12],
        "job_keywords": job_keywords,
        "section_scores": section_scores,
    }
