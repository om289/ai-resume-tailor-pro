"""Prompt templates and builder functions for resume tailoring."""

from src.scoring import ROLE_PRESETS

PROMPT_VERSION = "resume-tailor-v2"

SYSTEM_PROMPT = """You are a production-grade resume tailoring assistant.
Improve relevance, clarity, and keyword alignment without inventing experience.
Never claim the candidate has a skill, project, result, company, degree, or tool unless it appears in the resume or is explicitly marked as a conditional suggestion.

Return these sections:
1. Match Summary
2. ATS Keyword Improvements
3. Best Matching Skills
4. Resume Bullet Rewrites
5. Missing Keywords To Add Only If True
6. Short Cover Letter
7. Interview Talking Points
"""


def build_prompt(
    resume_text: str,
    job_text: str,
    role_key: str,
    tone: str,
    match_report: dict,
) -> str:
    """Build the user message for the LLM, including local ATS analysis context."""
    preset = ROLE_PRESETS.get(role_key, ROLE_PRESETS["backend"])
    return f"""Prompt version: {PROMPT_VERSION}
Target role preset: {preset["label"]}
Tone: {tone}

Local ATS analysis:
- Match score: {match_report["score"]}%
- Matched keywords: {", ".join(match_report["matched_keywords"]) or "None"}
- Missing keywords: {", ".join(match_report["missing_keywords"]) or "None"}

Candidate resume:
{resume_text}

Target job description:
{job_text}

Create a truthful, polished application package. Keep the output concise enough for a student or junior candidate to use."""


def build_local_output(match_report: dict, role_key: str) -> str:
    """Build a local (no-LLM) tailoring summary from keyword analysis."""
    preset = ROLE_PRESETS.get(role_key, ROLE_PRESETS["backend"])
    matched = ", ".join(match_report["matched_keywords"]) or "No direct keyword matches yet"
    missing = ", ".join(match_report["missing_keywords"]) or "No major keyword gaps found"
    return f"""1. Match Summary
The candidate has a {match_report["score"]}% keyword match for the {preset["label"]} preset.

2. ATS Keyword Improvements
Matched keywords: {matched}
Missing keywords to consider only if true: {missing}

3. Resume Bullet Rewrites
- Rewrite each experience bullet to start with an action verb.
- Add tools, measurable results, or project impact where the resume already supports it.
- Keep every claim truthful and directly connected to the original resume.

4. Missing Keywords To Add Only If True
{missing}

5. Short Cover Letter
Use the matched skills above to write a direct cover letter focused on the target role and the candidate's existing experience.

Note: This local output is generated without the LLM API. Add AI_API_KEY to produce a full tailored draft."""
