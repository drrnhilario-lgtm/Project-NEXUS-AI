"""In-memory report builders shared by web workflows and tests."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from core.html_report import generate_html_report
from config import PRODUCT_NAME, TAGLINE, VERSION_LABEL


def build_text_report(result: dict) -> str:
    """Build a deterministic plain-text skill report.

    Args:
        result: Skill-analysis result produced by ``analyze_skill_match``.

    Returns:
        A human-readable report containing no raw dictionary representations.
    """
    priorities = result.get("skill_priorities", {})
    lines = [
        PRODUCT_NAME.upper(),
        TAGLINE,
        VERSION_LABEL,
        "",
        "RESUME SKILL MATCH REPORT",
        "",
        f'Match Score: {float(result.get("match_score", 0)):g}%',
        "",
    ]
    sections = (
        ("Required Skills", result.get("required_skills", [])),
        ("Matched Skills", result.get("matched_skills", [])),
        ("Missing Skills", result.get("missing_skills", [])),
    )
    for heading, skills in sections:
        lines.append(f"{heading}:")
        lines.extend(
            f"- {skill} — {priorities.get(skill, 'Medium')} Priority"
            for skill in skills
        )
        if not skills:
            lines.append("- None")
        lines.append("")

    lines.append("RECOMMENDATIONS")
    missing_skills = result.get("missing_skills", [])
    recommendations = result.get("recommendations", {})
    if not missing_skills:
        lines.append("None")
    for number, skill in enumerate(missing_skills, 1):
        lines.extend(
            (
                f"{number}. {skill}",
                f"   {recommendations.get(skill, 'Review this skill gap.')}",
            )
        )
    return "\n".join(lines)


def build_html_report_bytes(result: dict) -> bytes:
    """Generate the established HTML report and return its bytes.

    The temporary report is always removed, including when generation fails.

    Args:
        result: Skill-analysis result produced by ``analyze_skill_match``.

    Returns:
        UTF-8 HTML report bytes.
    """
    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(suffix=".html", delete=False) as temporary_file:
            temporary_path = Path(temporary_file.name)
        generate_html_report(result, temporary_path)
        return temporary_path.read_bytes()
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
