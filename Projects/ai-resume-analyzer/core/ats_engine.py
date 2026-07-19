"""Transparent, rule-based ATS readiness analysis."""

import re
from typing import Iterable

from core.skill_matcher import analyze_skill_match


CATEGORY_WEIGHTS = {
    "Contact Information": 10,
    "Professional Summary": 10,
    "Skills Section": 15,
    "Work Experience": 20,
    "Education": 10,
    "Job Keyword Coverage": 20,
    "Measurable Achievements": 10,
    "ATS Readability": 5,
}

SECTION_HEADINGS = {
    "professional_summary": (
        "professional summary",
        "summary",
        "profile",
        "career profile",
        "objective",
        "about me",
    ),
    "skills": (
        "skills",
        "core competencies",
        "technical skills",
        "competencies",
        "areas of expertise",
    ),
    "work_experience": (
        "work experience",
        "professional experience",
        "employment history",
        "career history",
        "experience",
    ),
    "education": (
        "education",
        "academic background",
        "qualifications",
    ),
}

ACTION_VERBS = (
    "achieved",
    "analyzed",
    "built",
    "created",
    "delivered",
    "developed",
    "improved",
    "increased",
    "led",
    "managed",
    "reduced",
    "resolved",
    "supported",
    "implemented",
)

PROFESSIONAL_TERMS = (
    "experience",
    "professional",
    "specialist",
    "analyst",
    "manager",
    "support",
    "customer",
    "data",
    "operations",
    "technical",
)


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()]


def _heading_key(line: str) -> str | None:
    normalized = re.sub(r"[^a-z ]", "", line.lower()).strip()
    for key, headings in SECTION_HEADINGS.items():
        if normalized in headings:
            return key
    return None


def _extract_section(text: str, section_key: str) -> str:
    """Extract text following a recognized heading until the next heading."""
    lines = _lines(text)
    start = None
    collected = []
    for index, line in enumerate(lines):
        heading = _heading_key(line)
        if start is None and heading == section_key:
            start = index + 1
            continue
        if start is not None:
            if heading is not None:
                break
            if line:
                collected.append(line)
    return "\n".join(collected)


def _has_any(text: str, terms: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", lowered) for term in terms)


def _phone_found(text: str) -> bool:
    for match in re.finditer(r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)", text):
        digits = re.sub(r"\D", "", match.group(0))
        if 10 <= len(digits) <= 15:
            return True
    return False


def _contact_analysis(text: str) -> tuple[dict, int, list[dict]]:
    email_found = bool(
        re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.IGNORECASE)
    )
    phone_found = _phone_found(text)
    location_found = bool(
        re.search(
            r"(?:\b(?:address|location)\s*:|\b[A-Za-z .'-]+,\s*(?:Philippines|USA|United States|Canada|UK|United Kingdom)\b|\b\d{1,5}\s+[A-Za-z .'-]+\s+(?:Street|St|Road|Rd|Avenue|Ave)\b)",
            text,
            re.IGNORECASE,
        )
    )
    professional_link_found = bool(
        re.search(
            r"(?:linkedin\.com|github\.com|portfolio\s*:|https?://\S+)",
            text,
            re.IGNORECASE,
        )
    )
    details = {
        "email_found": email_found,
        "phone_found": phone_found,
        "location_found": location_found,
        "professional_link_found": professional_link_found,
    }
    points = {
        "email_found": 3,
        "phone_found": 3,
        "location_found": 2,
        "professional_link_found": 2,
    }
    checks = [
        {
            "category": "Contact Information",
            "name": name.replace("_found", "").replace("_", " ").title(),
            "passed": found,
            "feedback": "Detected without exposing the underlying value." if found else "Not detected.",
        }
        for name, found in details.items()
    ]
    return details, sum(points[name] for name, found in details.items() if found), checks


def _summary_analysis(text: str) -> tuple[dict, list[dict]]:
    section = _extract_section(text, "professional_summary")
    found = bool(section)
    word_count = len(re.findall(r"\b[\w'-]+\b", section))
    relevant_terms = sum(term in section.lower() for term in PROFESSIONAL_TERMS)
    generic_phrases = sum(
        phrase in section.lower()
        for phrase in (
            "hard working",
            "team player",
            "go getter",
            "results driven",
            "think outside the box",
        )
    )
    score = 0
    if found:
        score += 3
        score += 4 if word_count >= 30 else 0
        score += 2 if relevant_terms >= 2 else 0
        score += 1 if generic_phrases <= 1 else 0
    feedback = (
        "Summary is clearly labeled and sufficiently detailed."
        if score >= 8
        else "Add or strengthen a concise professional summary of at least 30 words."
    )
    result = {
        "section_found": found,
        "approximate_word_count": word_count,
        "score": score,
        "feedback": feedback,
    }
    checks = [
        {"category": "Professional Summary", "name": "Summary section", "passed": found, "feedback": feedback},
        {"category": "Professional Summary", "name": "Summary length", "passed": word_count >= 30, "feedback": f"Approximately {word_count} words detected."},
        {"category": "Professional Summary", "name": "Professional relevance", "passed": relevant_terms >= 2, "feedback": "Relevant professional terms detected." if relevant_terms >= 2 else "Use specific professional terms supported by your experience."},
    ]
    return result, checks


def _skills_analysis(text: str, skill_analysis: dict) -> tuple[dict, list[dict]]:
    section = _extract_section(text, "skills")
    found = bool(section)
    tokens = [
        token.strip(" -•\t")
        for token in re.split(r"[,;|\n]", section)
        if token.strip(" -•\t")
    ]
    identifiable_count = len(tokens)
    relevant_count = len(skill_analysis.get("matched_skills", []))
    score = (5 if found else 0) + (5 if identifiable_count >= 5 else 0) + (5 if relevant_count else 0)
    result = {
        "section_found": found,
        "identifiable_skill_count": identifiable_count,
        "matched_required_skill_count": relevant_count,
        "score": score,
        "feedback": "Dedicated skills section is present." if found else "Add a dedicated Skills section.",
    }
    checks = [
        {"category": "Skills Section", "name": "Skills heading", "passed": found, "feedback": result["feedback"]},
        {"category": "Skills Section", "name": "At least five listed skills", "passed": identifiable_count >= 5, "feedback": f"Approximately {identifiable_count} skill entries detected."},
        {"category": "Skills Section", "name": "Target-job skill relevance", "passed": relevant_count > 0, "feedback": f"{relevant_count} required skills matched."},
    ]
    return result, checks


def _experience_analysis(text: str) -> tuple[dict, list[dict]]:
    section = _extract_section(text, "work_experience")
    found = bool(section)
    title_or_company = bool(
        re.search(r"\b(?:analyst|specialist|manager|associate|representative|engineer|developer|assistant|coordinator|consultant|officer|intern|inc\.?|corp\.?|company|ltd\.?)\b", section, re.IGNORECASE)
    )
    dates = bool(
        re.search(r"\b(?:19|20)\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(?:19|20)\d{2}\b", section, re.IGNORECASE)
    )
    bullets = any(line.lstrip().startswith(("-", "•", "*")) for line in section.splitlines())
    action_verbs = _has_any(section, ACTION_VERBS)
    score = sum((5 if found else 0, 4 if title_or_company else 0, 4 if dates else 0, 4 if bullets else 0, 3 if action_verbs else 0))
    result = {
        "section_found": found,
        "job_or_company_found": title_or_company,
        "dates_found": dates,
        "bullet_content_found": bullets,
        "action_verbs_found": action_verbs,
        "score": score,
        "feedback": "Work experience is clearly structured." if score >= 15 else "Use a standard Experience heading with roles, dates, and action-focused bullets.",
    }
    checks = [
        {"category": "Work Experience", "name": "Experience section", "passed": found, "feedback": result["feedback"]},
        {"category": "Work Experience", "name": "Role or company indicators", "passed": title_or_company, "feedback": "Role or company wording detected."},
        {"category": "Work Experience", "name": "Employment dates", "passed": dates, "feedback": "Dates or date ranges detected."},
        {"category": "Work Experience", "name": "Bullet-style content", "passed": bullets, "feedback": "Bullet-style responsibilities detected."},
        {"category": "Work Experience", "name": "Action verbs", "passed": action_verbs, "feedback": "Action-oriented wording detected."},
    ]
    return result, checks


def _education_analysis(text: str) -> tuple[dict, list[dict]]:
    section = _extract_section(text, "education")
    lowered = section.lower()
    found = bool(section) or bool(re.search(r"(?im)^\s*(?:education|academic background|qualifications)\s*:?[\s]*$", text))
    degree = bool(re.search(r"\b(?:bachelor|master|doctorate|phd|degree|diploma|certificate|bs|ba|ms|mba)\b", lowered))
    institution = bool(re.search(r"\b(?:university|college|institute|academy|school)\b", lowered))
    date = bool(re.search(r"\b(?:19|20)\d{2}\b", section))
    score = sum((3 if found else 0, 3 if degree else 0, 2 if institution else 0, 2 if date else 0))
    result = {
        "section_found": found,
        "qualification_found": degree,
        "institution_found": institution,
        "date_found": date,
        "score": score,
        "feedback": "Education details are clearly identifiable." if score >= 8 else "Add a clear Education section with qualification and institution details.",
    }
    checks = [
        {"category": "Education", "name": "Education section", "passed": found, "feedback": result["feedback"]},
        {"category": "Education", "name": "Degree or qualification", "passed": degree, "feedback": "Qualification wording detected."},
        {"category": "Education", "name": "Institution", "passed": institution, "feedback": "Institution wording detected."},
        {"category": "Education", "name": "Education date", "passed": date, "feedback": "A year was detected when available."},
    ]
    return result, checks


def _achievement_analysis(text: str) -> tuple[dict, list[dict]]:
    evidence_patterns = (
        r"\b\d+(?:\.\d+)?\s*%",
        r"(?:₱|\$|PHP\s*|USD\s*)\d[\d,]*(?:\.\d+)?",
        r"\b\d+\s+(?:cases|customers|tickets|calls|projects|reports|records|sales|tasks|transactions)\b",
        r"\b(?:reduced|decreased|cut|saved|improved|increased)\b[^\n.!?]{0,80}\b\d+(?:\.\d+)?\s*(?:%|minutes?|hours?|days?|cases?|customers?|tickets?)",
        r"\b(?:exceeded|surpassed)\s+(?:a\s+)?KPI\b",
        r"\b(?:increased sales|improved productivity|customer satisfaction)\b",
    )
    phrases = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line and any(re.search(pattern, line, re.IGNORECASE) for pattern in evidence_patterns):
            phrases.append(line)
    unique_phrases = list(dict.fromkeys(phrases))
    count = len(unique_phrases)
    score = 10 if count >= 3 else 7 if count == 2 else 4 if count == 1 else 0
    result = {
        "achievement_count": count,
        "sample_achievement_phrases": unique_phrases[:3],
        "score": score,
        "feedback": "Measurable achievement evidence is present." if count else "Include measurable accomplishments using numbers, percentages, or business outcomes.",
    }
    checks = [
        {"category": "Measurable Achievements", "name": "Quantified achievements", "passed": count > 0, "feedback": result["feedback"]}
    ]
    return result, checks


def _readability_analysis(text: str, detected_sections: dict) -> tuple[dict, list[dict]]:
    words = re.findall(r"\b[\w'-]+\b", text)
    nonempty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    word_count = len(words)
    average_line_words = word_count / len(nonempty_lines) if nonempty_lines else 0
    symbols = re.findall(r"[^\w\s.,;:!?%+()/#&'@-]", text)
    unusual_symbol_ratio = len(symbols) / max(len(text), 1)
    text_present = bool(text.strip())
    checks_map = {
        "Text extracted": text_present,
        "Reasonable word count": 100 <= word_count <= 1500,
        "Reasonable average line length": 2 <= average_line_words <= 30,
        "Limited unusual symbols": text_present and unusual_symbol_ratio <= 0.03,
        "Recognizable section headings": sum(detected_sections.values()) >= 2,
    }
    score = sum(checks_map.values())
    result = {
        "score": score,
        "word_count": word_count,
        "line_count": len(nonempty_lines),
        "average_line_word_count": round(average_line_words, 2),
        "unusual_symbol_ratio": round(unusual_symbol_ratio, 4),
        "feedback": "Extracted text is reasonably ATS-readable." if score >= 4 else "Use standard headings and clear text structure; visual formatting was not evaluated.",
    }
    checks = [
        {"category": "ATS Readability", "name": name, "passed": passed, "feedback": result["feedback"]}
        for name, passed in checks_map.items()
    ]
    return result, checks


def _status(score: int) -> str:
    if score < 40:
        return "Needs Major Improvement"
    if score < 60:
        return "Developing"
    if score < 75:
        return "ATS Ready"
    if score < 90:
        return "Strong ATS Readiness"
    return "Excellent ATS Readiness"


def analyze_ats_readiness(
    resume_text: str,
    job_description: str,
    skill_analysis: dict | None = None,
) -> dict:
    """Score ATS readiness with explainable offline rules."""
    resume_text = resume_text or ""
    job_description = job_description or ""
    if skill_analysis is None:
        skill_analysis = analyze_skill_match(resume_text, job_description)

    contact_details, contact_score, contact_checks = _contact_analysis(resume_text)
    summary, summary_checks = _summary_analysis(resume_text)
    skills, skills_checks = _skills_analysis(resume_text, skill_analysis)
    experience, experience_checks = _experience_analysis(resume_text)
    education, education_checks = _education_analysis(resume_text)
    achievements, achievement_checks = _achievement_analysis(resume_text)

    required_count = len(skill_analysis.get("required_skills", []))
    matched_count = len(skill_analysis.get("matched_skills", []))
    coverage = matched_count / required_count * 100 if required_count else 0.0
    keyword_score = round(coverage / 100 * CATEGORY_WEIGHTS["Job Keyword Coverage"])
    keyword_coverage = {
        "matched_keyword_count": matched_count,
        "total_required_keyword_count": required_count,
        "keyword_coverage_percentage": round(coverage, 2),
        "score": keyword_score,
    }
    keyword_checks = [
        {
            "category": "Job Keyword Coverage",
            "name": "Required keyword coverage",
            "passed": coverage >= 60 if required_count else False,
            "feedback": (
                f"{matched_count} of {required_count} required skills matched."
                if required_count
                else "No required skills were identified in the job description."
            ),
        }
    ]

    detected_sections = {
        "professional_summary": summary["section_found"],
        "skills": skills["section_found"],
        "work_experience": experience["section_found"],
        "education": education["section_found"],
    }
    readability, readability_checks = _readability_analysis(
        resume_text, detected_sections
    )

    category_scores = {
        "Contact Information": {"score": contact_score, "max_score": 10},
        "Professional Summary": {"score": summary["score"], "max_score": 10},
        "Skills Section": {"score": skills["score"], "max_score": 15},
        "Work Experience": {"score": experience["score"], "max_score": 20},
        "Education": {"score": education["score"], "max_score": 10},
        "Job Keyword Coverage": {"score": keyword_score, "max_score": 20},
        "Measurable Achievements": {"score": achievements["score"], "max_score": 10},
        "ATS Readability": {"score": readability["score"], "max_score": 5},
    }
    ats_score = max(0, min(100, sum(item["score"] for item in category_scores.values())))
    checks = (
        contact_checks
        + summary_checks
        + skills_checks
        + experience_checks
        + education_checks
        + keyword_checks
        + achievement_checks
        + readability_checks
    )

    strengths = []
    if contact_score >= 8:
        strengths.append("Contact information is complete.")
    if experience["score"] >= 15:
        strengths.append("Work experience is clearly identified.")
    if education["score"] >= 8:
        strengths.append("Education details are present.")
    if achievements["achievement_count"]:
        strengths.append("Resume includes measurable achievements.")
    if coverage >= 60 and required_count:
        strengths.append("Good coverage of target-job keywords.")
    if readability["score"] >= 4:
        strengths.append("Extracted text uses recognizable ATS-friendly structure.")

    suggestions = []
    if not summary["section_found"]:
        suggestions.append("Add a clear Professional Summary section.")
    elif summary["score"] < 8:
        suggestions.append("Strengthen the Professional Summary with specific, truthful professional terms and at least 30 words.")
    if not skills["section_found"]:
        suggestions.append("Add a dedicated Skills section using skills you genuinely possess.")
    if experience["score"] < 15:
        suggestions.append("Use a standard Experience heading with roles, dates, and action-focused responsibility bullets.")
    if education["score"] < 8:
        suggestions.append("Add clear education, qualification, and institution details where applicable.")
    if not achievements["achievement_count"]:
        suggestions.append("Include measurable accomplishments using numbers or percentages when they are accurate.")
    if required_count and coverage < 60:
        suggestions.append("Add relevant target-job keywords naturally only where they truthfully describe your experience.")
    if not contact_details["professional_link_found"]:
        suggestions.append("Add a LinkedIn or portfolio link if you maintain one.")
    if sum(detected_sections.values()) < 2:
        suggestions.append("Use standard section headings that ATS software can recognize.")

    statistics = {
        "word_count": readability["word_count"],
        "line_count": readability["line_count"],
        "average_line_word_count": readability["average_line_word_count"],
        "recognizable_section_count": sum(detected_sections.values()),
        "passed_check_count": sum(check["passed"] for check in checks),
        "failed_check_count": sum(not check["passed"] for check in checks),
    }

    return {
        "ats_score": ats_score,
        "ats_status": _status(ats_score),
        "category_scores": category_scores,
        "checks": checks,
        "strengths": strengths,
        "improvement_suggestions": suggestions,
        "keyword_coverage": keyword_coverage,
        "detected_sections": detected_sections,
        "contact_details": contact_details,
        "statistics": statistics,
    }
