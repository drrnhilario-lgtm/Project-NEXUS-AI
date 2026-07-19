"""Offline skill matching for resumes and job descriptions."""

import re


SKILL_ALIASES = {
    "Python": ["python"],
    "SQL": ["sql", "mysql", "postgresql", "database querying"],
    "Excel": ["excel", "microsoft excel", "spreadsheets", "spreadsheet"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Data Analysis": [
        "data analysis",
        "data analytics",
        "analyzing data",
        "data reporting",
        "reporting and analysis",
    ],
    "Data Visualization": [
        "data visualization",
        "dashboard",
        "dashboards",
        "charts",
        "graphs",
    ],
    "Communication": [
        "communication",
        "communication skills",
        "excellent communication skills",
        "strong communication skills",
        "verbal communication",
        "written communication",
        "verbal and written communication",
        "excellent verbal and written communication",
        "communicated with customers",
        "handled customer concerns",
        "customer inquiries",
        "assisted customers",
        "customer interaction",
        "client interaction",
        "client communication",
        "customer-facing",
        "inbound calls",
        "outbound calls",
    ],
    "Customer Service": [
        "customer service",
        "customer support",
        "customer assistance",
        "client support",
    ],
    "Technical Support": [
        "technical support",
        "technical troubleshooting",
        "troubleshooting",
        "tech support",
    ],
    "CRM": ["crm", "customer relationship management", "case management system"],
    "Problem Solving": [
        "problem solving",
        "problem-solving",
        "issue resolution",
        "resolving customer concerns",
        "root cause analysis",
    ],
    "Fraud Detection": [
        "fraud detection",
        "fraud prevention",
        "fraud investigation",
        "fraud analysis",
    ],
    "Claims Processing": [
        "claims processing",
        "claim processing",
        "insurance claims",
    ],
    "APIs": ["api", "apis", "application programming interface"],
    "Automation": [
        "automation",
        "automated workflow",
        "workflow automation",
        "process automation",
    ],
    "OpenAI": ["openai", "chatgpt", "large language model", "llm"],
    "n8n": ["n8n"],
    "Zapier": ["zapier"],
    "Make": ["make.com", "integromat"],
}

SKILL_RECOMMENDATIONS = {
    "Python": "Learn Python fundamentals and build a small data-cleaning project using pandas.",
    "SQL": "Learn SELECT, WHERE, JOIN, GROUP BY, subqueries, and window functions.",
    "Excel": "Practice PivotTables, XLOOKUP, data cleaning, charts, and basic dashboards.",
    "Power BI": "Build an interactive dashboard using Power Query, data modeling, and DAX.",
    "Tableau": "Create a portfolio dashboard using a public dataset.",
    "Data Analysis": "Complete a project involving data cleaning, analysis, interpretation, and business recommendations.",
    "Data Visualization": "Create charts and dashboards that clearly communicate insights.",
    "Communication": "Add measurable examples of explaining issues, assisting clients, documenting cases, or presenting findings.",
    "Customer Service": "Add measurable examples of resolving customer needs and improving customer outcomes.",
    "Technical Support": "Practice structured troubleshooting and document a technical issue-resolution example.",
    "CRM": "Gain hands-on experience tracking customer interactions in a CRM platform.",
    "Problem Solving": "Add an example showing how you identified a root cause and implemented a solution.",
    "Fraud Detection": "Study common fraud indicators and complete a small fraud-analysis case study.",
    "Claims Processing": "Learn the claims lifecycle and document an example of accurate case processing.",
    "APIs": "Build a small project that retrieves and processes data from a public API.",
    "Automation": "Automate a repetitive workflow and document the time or effort saved.",
    "OpenAI": "Build a small project that uses an OpenAI model responsibly and evaluates its output.",
    "n8n": "Create and document a multi-step n8n workflow using triggers and integrations.",
    "Zapier": "Build a Zapier automation that connects two applications and handles errors.",
    "Make": "Create a Make scenario with multiple modules, filters, and error handling.",
}

HIGH_PRIORITY_CUES = (
    "required",
    "must have",
    "essential",
    "strong knowledge",
    "proficient",
    "proficiency",
    "advanced",
    "minimum requirement",
)

LOW_PRIORITY_CUES = (
    "preferred",
    "advantage",
    "bonus",
    "nice to have",
    "plus",
    "optional",
)


def _find_alias_matches(text: str, aliases: list[str]) -> list[tuple[int, int, str]]:
    """Find non-overlapping aliases, preferring longer phrases at each location."""
    candidates = []
    for alias in aliases:
        pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"
        candidates.extend(
            (match.start(), match.end(), match.group(0))
            for match in re.finditer(pattern, text, flags=re.IGNORECASE)
        )

    matches = []
    for candidate in sorted(candidates, key=lambda item: (item[0], -(item[1] - item[0]))):
        start, end, _ = candidate
        if not any(start < saved_end and end > saved_start for saved_start, saved_end, _ in matches):
            matches.append(candidate)

    return matches


def _find_alias(text: str, aliases: list[str]) -> str | None:
    """Return the exact text matching the most descriptive complete alias."""
    for alias in sorted(aliases, key=len, reverse=True):
        match = re.search(
            rf"(?<!\w){re.escape(alias)}(?!\w)",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(0)

    return None


def _skill_priority(job_description: str, aliases: list[str]) -> str:
    """Classify a required skill from occurrence count and nearby cue words."""
    matches = _find_alias_matches(job_description, aliases)
    normalized_description = job_description.lower()
    nearby_contexts = []
    for start, end, _ in matches:
        preceding_boundaries = [
            normalized_description.rfind(delimiter, 0, start)
            for delimiter in ("\n", ".", "!", "?")
        ]
        following_boundaries = [
            position
            for delimiter in ("\n", ".", "!", "?")
            if (position := normalized_description.find(delimiter, end)) != -1
        ]
        context_start = max(preceding_boundaries) + 1
        context_end = min(following_boundaries) if following_boundaries else len(job_description)
        nearby_contexts.append(normalized_description[context_start:context_end])

    if len(matches) > 1 or any(
        cue in context
        for context in nearby_contexts
        for cue in HIGH_PRIORITY_CUES
    ):
        return "High"

    if any(
        cue in context
        for context in nearby_contexts
        for cue in LOW_PRIORITY_CUES
    ):
        return "Low"

    return "Medium"


def analyze_skill_match(resume_text: str, job_description: str) -> dict:
    """Compare resume skills with aliased skills required by a job description."""
    required_skills = sorted(
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if _find_alias(job_description, aliases)
    )
    match_evidence = {
        skill: evidence
        for skill in required_skills
        if (evidence := _find_alias(resume_text, SKILL_ALIASES[skill]))
    }
    matched_skills = sorted(match_evidence)
    missing_skills = sorted(
        skill for skill in required_skills if skill not in matched_skills
    )
    recommendations = {
        skill: SKILL_RECOMMENDATIONS[skill] for skill in missing_skills
    }
    skill_priorities = {
        skill: _skill_priority(job_description, SKILL_ALIASES[skill])
        for skill in required_skills
    }

    match_score = (
        len(matched_skills) / len(required_skills) * 100
        if required_skills
        else 0
    )

    return {
        "match_score": round(match_score, 2),
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_evidence": match_evidence,
        "recommendations": recommendations,
        "skill_priorities": skill_priorities,
    }
