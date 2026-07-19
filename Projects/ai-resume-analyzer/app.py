"""Generate a resume-analysis prompt locally, with optional OpenAI support."""

import os
import sys
from pathlib import Path

from core.html_report import generate_html_report
from core.skill_matcher import analyze_skill_match
from config import PRODUCT_NAME, TAGLINE, VERSION_LABEL

PROJECT_DIR = Path(__file__).resolve().parent
RESUME_FILE = PROJECT_DIR / "sample-data" / "sample-resume.txt"
RESUME_PDF_FILE = PROJECT_DIR / "sample-data" / "sample-resume.pdf"
JOB_DESCRIPTION_FILE = PROJECT_DIR / "sample-data" / "sample-job-description.txt"
PROMPT_TEMPLATE_FILE = PROJECT_DIR / "prompts" / "analysis-prompt.txt"
OUTPUT_FILE = PROJECT_DIR / "outputs" / "generated-analysis-prompt.txt"
EXTRACTED_RESUME_FILE = PROJECT_DIR / "outputs" / "extracted_resume.txt"
SKILL_MATCH_REPORT_FILE = PROJECT_DIR / "outputs" / "skill-match-report.txt"
SKILL_MATCH_HTML_FILE = PROJECT_DIR / "outputs" / "skill-match-report.html"


class InputFileError(Exception):
    """Report a missing or empty input file."""


def read_required_file(path: Path, description: str) -> str:
    """Read a required UTF-8 file and reject missing or empty content."""
    if not path.is_file():
        raise InputFileError(f"Missing {description}: {path}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise InputFileError(f"The {description} is empty: {path}")

    return content


def analyze_with_openai(prompt: str) -> str | None:
    """Send a generated prompt to OpenAI when live analysis is enabled later."""
    from dotenv import load_dotenv
    from openai import APIConnectionError, AuthenticationError, OpenAI

    load_dotenv(PROJECT_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY is missing from the .env file.", file=sys.stderr)
        return None

    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        return response.output_text
    except AuthenticationError:
        print("Error: The OpenAI API key is invalid.", file=sys.stderr)
    except APIConnectionError:
        print("Error: Could not connect to the OpenAI API.", file=sys.stderr)

    return None


def main() -> None:
    """Generate an offline resume-to-job skill match report."""
    try:
        resume_text = read_required_file(
            EXTRACTED_RESUME_FILE,
            "extracted resume file",
        )
        job_description = read_required_file(
            JOB_DESCRIPTION_FILE,
            "job-description file",
        )
    except InputFileError as error:
        print(f"Error: {error}", file=sys.stderr)
        return

    result = analyze_skill_match(resume_text, job_description)
    required_skills = "\n".join(
        f'- {skill} — {result["skill_priorities"][skill]} Priority'
        for skill in result["required_skills"]
    ) or "- None"
    matched_skills = "\n".join(
        f'- {skill}\n  Evidence: {result["match_evidence"][skill]}'
        for skill in result["matched_skills"]
    ) or "- None"
    missing_skills = "\n".join(
        f'- {skill} — {result["skill_priorities"][skill]} Priority'
        for skill in result["missing_skills"]
    ) or "- None"
    match_score = f'{result["match_score"]:g}'
    matched_count = len(result["matched_skills"])
    required_count = len(result["required_skills"])
    high_priority_missing = [
        skill
        for skill in result["missing_skills"]
        if result["skill_priorities"][skill] == "High"
    ]
    recommendations = "\n\n".join(
        f'{number}. {skill}\n   {result["recommendations"][skill]}'
        for number, skill in enumerate(result["missing_skills"], start=1)
    ) or "None"
    priority_groups = {
        "Learn First": high_priority_missing,
        "Learn Next": [
            skill
            for skill in result["missing_skills"]
            if result["skill_priorities"][skill] == "Medium"
        ],
        "Optional Development": [
            skill
            for skill in result["missing_skills"]
            if result["skill_priorities"][skill] == "Low"
        ],
    }
    priority_action_plan = "\n\n".join(
        f"{number}. {heading}\n"
        + ("\n".join(f"   - {skill}" for skill in skills) if skills else "   - None")
        for number, (heading, skills) in enumerate(priority_groups.items(), start=1)
    )

    report = (
        f"{PRODUCT_NAME.upper()}\n{TAGLINE}\n{VERSION_LABEL}\n\n"
        "RESUME SKILL MATCH REPORT\n\n"
        f"Match Score: {match_score}%\n"
        f"Matched Required Skills: {matched_count} of {required_count}\n"
        f"High-Priority Skills Missing: {len(high_priority_missing)}\n\n"
        "Required Skills Found in Job Description:\n"
        f"{required_skills}\n\n"
        f"Matched Skills:\n{matched_skills}\n\n"
        f"Missing Skills:\n{missing_skills}\n\n"
        f"RECOMMENDATIONS\n\n{recommendations}\n\n"
        f"PRIORITY ACTION PLAN\n\n{priority_action_plan}\n"
    )

    SKILL_MATCH_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SKILL_MATCH_REPORT_FILE.write_text(report, encoding="utf-8")
    generate_html_report(result, SKILL_MATCH_HTML_FILE)
    print(f"Text report saved to: {SKILL_MATCH_REPORT_FILE}")
    print(f"HTML report saved to: {SKILL_MATCH_HTML_FILE}")


if __name__ == "__main__":
    main()
