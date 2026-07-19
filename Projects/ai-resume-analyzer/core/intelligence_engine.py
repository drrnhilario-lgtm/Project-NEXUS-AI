"""Rule-based career insights built from existing offline analyses."""

from typing import Any


READINESS_STATUSES = (
    (40, "Early Preparation"),
    (60, "Developing Readiness"),
    (75, "Competitive Foundation"),
    (90, "Strong Candidate Readiness"),
    (101, "Highly Competitive"),
)

EVIDENCE_COMPONENTS = {
    "Measurable Achievements": 5,
    "Work Experience": 5,
    "Education": 3,
    "Professional Summary": 3,
    "Skills Section": 2,
    "ATS Readability": 2,
}


def _category_score(ats_analysis: dict, category: str) -> tuple[float, float]:
    values = ats_analysis.get("category_scores", {}).get(category, {})
    return float(values.get("score", 0)), float(values.get("max_score", 0))


def _evidence_quality(ats_analysis: dict) -> float:
    """Return up to 20 points from existing ATS evidence categories."""
    total = 0.0
    for category, weight in EVIDENCE_COMPONENTS.items():
        score, maximum = _category_score(ats_analysis, category)
        total += (score / maximum * weight) if maximum else 0
    return round(max(0.0, min(20.0, total)), 2)


def _readiness_status(score: int) -> str:
    for upper_bound, label in READINESS_STATUSES:
        if score < upper_bound:
            return label
    return "Highly Competitive"


def _unique(items: list[str], limit: int | None = None) -> list[str]:
    unique_items = list(dict.fromkeys(item for item in items if item))
    return unique_items[:limit] if limit is not None else unique_items


def _build_strengths(skill_analysis: dict, ats_analysis: dict) -> list[str]:
    matched = skill_analysis.get("matched_skills", [])
    strengths = []
    if matched:
        strengths.append(
            "Resume evidence supports target-role skills including "
            + ", ".join(matched[:3])
            + "."
        )
    strengths.extend(ats_analysis.get("strengths", []))

    experience_score, experience_max = _category_score(
        ats_analysis, "Work Experience"
    )
    education_score, education_max = _category_score(ats_analysis, "Education")
    skills_score, skills_max = _category_score(ats_analysis, "Skills Section")
    if experience_max and experience_score / experience_max >= 0.75:
        strengths.append("Work experience is supported by recognizable resume evidence.")
    if education_max and education_score / education_max >= 0.75:
        strengths.append("Education and qualification details are clearly identified.")
    if skills_max and skills_score / skills_max >= 0.75:
        strengths.append("The skills section provides useful role-relevant evidence.")
    return _unique(strengths, 6)


def _build_improvements(skill_analysis: dict, ats_analysis: dict) -> list[dict]:
    improvements = []
    priorities = skill_analysis.get("skill_priorities", {})
    for skill in skill_analysis.get("missing_skills", []):
        priority = priorities.get(skill, "Medium")
        improvements.append(
            {
                "title": f"Build {skill} evidence",
                "explanation": (
                    f"{skill} appears in the target role but is not currently "
                    "supported by detected resume evidence."
                ),
                "priority": priority,
                "source": "Skill Match",
            }
        )

    category_messages = {
        "Professional Summary": "Add or strengthen a concise summary using truthful role-relevant evidence.",
        "Skills Section": "Use a dedicated Skills section containing skills you genuinely possess.",
        "Work Experience": "Clarify roles, dates, and action-focused responsibility or achievement bullets.",
        "Education": "Present applicable education and qualification details under a standard heading.",
        "Measurable Achievements": "Add accurate accomplishments supported by numbers, percentages, or outcomes.",
        "ATS Readability": "Use recognizable headings and clear extracted-text structure.",
        "Job Keyword Coverage": "Use relevant target-role wording naturally where it accurately reflects experience.",
    }
    for category, explanation in category_messages.items():
        score, maximum = _category_score(ats_analysis, category)
        ratio = score / maximum if maximum else 0
        if ratio < 0.6:
            improvements.append(
                {
                    "title": f"Improve {category}",
                    "explanation": explanation,
                    "priority": "High" if ratio < 0.35 else "Medium",
                    "source": "ATS" if category != "Measurable Achievements" else "Resume Content",
                }
            )

    if len(improvements) < 3:
        existing_titles = {item["title"] for item in improvements}
        ranked_categories = sorted(
            category_messages,
            key=lambda category: (
                _category_score(ats_analysis, category)[0]
                / max(_category_score(ats_analysis, category)[1], 1)
            ),
        )
        for category in ranked_categories:
            title = f"Review {category}"
            if title in existing_titles or f"Improve {category}" in existing_titles:
                continue
            improvements.append(
                {
                    "title": title,
                    "explanation": (
                        "Review this section for clarity and keep every claim "
                        "specific, accurate, and supported by real evidence."
                    ),
                    "priority": "Low",
                    "source": "Resume Content",
                }
            )
            if len(improvements) >= 3:
                break

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    improvements.sort(key=lambda item: (priority_order[item["priority"]], item["title"]))
    return improvements[:6]


def _build_priority_focus(
    skill_analysis: dict,
    ats_analysis: dict,
    improvements: list[dict],
) -> list[dict]:
    priorities = []
    skill_priorities = skill_analysis.get("skill_priorities", {})
    missing = sorted(
        skill_analysis.get("missing_skills", []),
        key=lambda skill: (
            {"High": 0, "Medium": 1, "Low": 2}.get(
                skill_priorities.get(skill, "Medium"), 1
            ),
            skill,
        ),
    )
    for skill in missing:
        priorities.append(
            {
                "title": skill,
                "reason": (
                    f"{skill} is required by the target role and is currently "
                    "missing from detected resume evidence."
                ),
                "expected_impact": (
                    "High" if skill_priorities.get(skill) == "High" else "Medium"
                ),
                "recommended_evidence": (
                    f"Complete a practical {skill} exercise or portfolio project, "
                    "then document only the work actually completed."
                ),
            }
        )

    for improvement in improvements:
        if len(priorities) >= 3:
            break
        if improvement["source"] == "Skill Match":
            continue
        priorities.append(
            {
                "title": improvement["title"],
                "reason": improvement["explanation"],
                "expected_impact": improvement["priority"],
                "recommended_evidence": (
                    "Update the relevant resume section using accurate examples "
                    "and evidence from completed work."
                ),
            }
        )

    for rank, priority in enumerate(priorities[:3], start=1):
        priority["rank"] = rank
    return priorities[:3]


def _build_actions(
    priority_focus: list[dict],
    improvements: list[dict],
    missing_skills: list[str],
) -> dict:
    immediate = [
        f"Review the evidence for {item['title']} and define one truthful improvement task."
        for item in priority_focus[:2]
    ]
    if not immediate:
        immediate.append("Review the current analysis and verify that extracted resume text is complete.")

    short_term = [
        f"Complete applied practice for {skill} and retain the work as evidence."
        for skill in missing_skills[:3]
    ] or ["Deepen one matched skill through an applied project relevant to the target role."]

    resume_actions = [
        item["explanation"] for item in improvements if item["source"] in {"ATS", "Resume Content"}
    ][:3]
    if not resume_actions:
        resume_actions.append("Keep resume wording specific, accurate, and supported by evidence.")

    portfolio_actions = [
        f"Build a small {skill} project that demonstrates practical application."
        for skill in missing_skills[:2]
    ] or ["Create one end-to-end project that deepens existing target-role strengths."]

    return {
        "immediate_actions": immediate,
        "short_term_actions": short_term,
        "resume_actions": resume_actions,
        "portfolio_actions": portfolio_actions,
    }


def _build_roadmap(skill_analysis: dict) -> list[dict]:
    missing = skill_analysis.get("missing_skills", [])
    matched = skill_analysis.get("matched_skills", [])
    foundation_topics = missing[:2] or matched[:2] or ["Target-role fundamentals"]
    applied_topics = missing[2:4] or foundation_topics
    portfolio_topics = missing[4:6] or applied_topics

    return [
        {
            "phase": "Phase 1",
            "title": "Foundation",
            "objective": "Build accurate foundational knowledge for the highest-priority target-role skills.",
            "estimated_duration": "2–4 weeks, adjusted to available study time",
            "topics": foundation_topics,
            "deliverables": ["Completed practice exercises", "Personal notes or reference guide"],
            "success_criteria": ["Can explain core concepts", "Can complete a small task without copying a solution"],
        },
        {
            "phase": "Phase 2",
            "title": "Applied Practice",
            "objective": "Apply the selected skills to a realistic, bounded problem.",
            "estimated_duration": "3–6 weeks, depending on project scope",
            "topics": applied_topics,
            "deliverables": ["Working applied exercise", "Documented decisions and results"],
            "success_criteria": ["Produces a reproducible output", "Explains the approach and limitations"],
        },
        {
            "phase": "Phase 3",
            "title": "Portfolio and Job Readiness",
            "objective": "Turn completed work into credible portfolio and resume evidence.",
            "estimated_duration": "2–4 weeks after applied practice",
            "topics": portfolio_topics,
            "deliverables": ["End-to-end portfolio project", "Evidence-based resume update"],
            "success_criteria": ["Project is understandable to reviewers", "Resume claims match completed work"],
        },
    ]


def generate_resume_intelligence(
    resume_text: str,
    job_description: str,
    skill_analysis: dict,
    ats_analysis: dict,
) -> dict[str, Any]:
    """Generate deterministic human-readable career insights."""
    del job_description  # Requirements are already represented by skill_analysis.
    skill_score = float(skill_analysis.get("match_score", 0))
    ats_score = float(ats_analysis.get("ats_score", 0))
    evidence_points = _evidence_quality(ats_analysis)
    readiness_score = round(
        max(0.0, min(100.0, skill_score * 0.45 + ats_score * 0.35 + evidence_points))
    )
    status = _readiness_status(readiness_score)
    strengths = _build_strengths(skill_analysis, ats_analysis)
    improvements = _build_improvements(skill_analysis, ats_analysis)
    priority_focus = _build_priority_focus(skill_analysis, ats_analysis, improvements)
    missing = skill_analysis.get("missing_skills", [])
    matched = skill_analysis.get("matched_skills", [])

    strongest_text = (
        "The resume provides evidence for " + ", ".join(matched[:3]) + "."
        if matched
        else "The current resume provides limited evidence for the target role's required skills."
    )
    alignment_text = (
        f"Skill alignment is {skill_score:g}% and rule-based ATS readiness is {ats_score:g}%."
    )
    gap_text = (
        "The most important detected gaps include " + ", ".join(missing[:3]) + "."
        if missing
        else "No required skills are currently missing from the rule-based skill comparison."
    )
    action_text = (
        f"The best next action is to focus on {priority_focus[0]['title']} and add evidence only after completing the work."
        if priority_focus
        else "The best next action is to verify the extracted content and deepen existing evidence."
    )
    executive_summary = " ".join(
        (strongest_text, alignment_text, gap_text, action_text)
    )

    if readiness_score >= 80:
        gap_level = "Minimal"
    elif readiness_score >= 60:
        gap_level = "Moderate"
    elif readiness_score >= 40:
        gap_level = "Significant"
    else:
        gap_level = "Major"
    career_gap = {
        "gap_level": gap_level,
        "gap_summary": (
            f"The {gap_level.lower()} gap level reflects a {readiness_score}% career "
            f"readiness score, {len(matched)} matched required skills, and "
            f"{len(missing)} missing required skills."
        ),
        "major_gaps": missing[:5]
        or [item["title"] for item in improvements[:3]],
        "transferable_strengths": strengths[:4],
    }

    confidence_notes = [
        "Analysis depends on the text successfully extracted from the PDF.",
        "Applicant tracking systems use different parsing and ranking methods.",
        "A detected skill phrase does not prove proficiency.",
        "Missing keywords may be present under wording not covered by the rule set.",
        "Visual resume formatting cannot be fully evaluated from extracted text.",
    ]
    if not resume_text.strip():
        confidence_notes.insert(0, "No resume text was available, so conclusions are highly limited.")

    return {
        "executive_summary": executive_summary,
        "readiness_score": readiness_score,
        "readiness_status": status,
        "strengths": strengths,
        "areas_for_improvement": improvements,
        "career_gap": career_gap,
        "priority_focus": priority_focus,
        "recommended_actions": _build_actions(priority_focus, improvements, missing),
        "learning_roadmap": _build_roadmap(skill_analysis),
        "confidence_notes": confidence_notes,
    }
