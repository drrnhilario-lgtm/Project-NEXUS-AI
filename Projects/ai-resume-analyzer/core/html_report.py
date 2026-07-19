"""Generate a self-contained HTML skill-match report."""

from html import escape
from pathlib import Path

from config import COPYRIGHT_YEAR, PRODUCT_NAME, TAGLINE


def generate_html_report(analysis_result: dict, output_path: str | Path) -> None:
    """Render an escaped, responsive HTML report and save it locally."""
    output_file = Path(output_path)
    priorities = analysis_result["skill_priorities"]
    required_skills = analysis_result["required_skills"]
    matched_skills = analysis_result["matched_skills"]
    missing_skills = analysis_result["missing_skills"]
    evidence = analysis_result["match_evidence"]
    recommendations = analysis_result["recommendations"]
    score = max(0, min(100, float(analysis_result["match_score"])))

    def safe(value: object) -> str:
        return escape(str(value), quote=True)

    def priority_badge(skill: str) -> str:
        priority = priorities[skill]
        css_class = {
            "High": "priority-high",
            "Medium": "priority-medium",
            "Low": "priority-low",
        }.get(priority, "priority-medium")
        return f'<span class="priority-badge {css_class}">{safe(priority)} Priority</span>'

    required_items = "".join(
        f'<li><span class="skill-name">{safe(skill)}</span>{priority_badge(skill)}</li>'
        for skill in required_skills
    ) or '<li class="empty-state">None</li>'

    matched_items = "".join(
        "<li>"
        f'<span class="skill-name">{safe(skill)}</span>'
        f'<p class="evidence"><strong>Evidence:</strong> {safe(evidence[skill])}</p>'
        "</li>"
        for skill in matched_skills
    ) or '<li class="empty-state">None</li>'

    missing_items = "".join(
        f'<li><span class="skill-name">{safe(skill)}</span>{priority_badge(skill)}</li>'
        for skill in missing_skills
    ) or '<li class="empty-state">None</li>'

    recommendation_items = "".join(
        "<li>"
        f"<strong>{safe(skill)}</strong>"
        f"<p>{safe(recommendations[skill])}</p>"
        "</li>"
        for skill in missing_skills
    ) or '<li class="empty-state">No recommendations needed.</li>'

    priority_groups = (
        ("Learn First", "High"),
        ("Learn Next", "Medium"),
        ("Optional Development", "Low"),
    )
    action_plan = "".join(
        '<article class="action-card">'
        f"<h3>{safe(heading)}</h3>"
        "<ul>"
        + (
            "".join(
                f"<li>{safe(skill)}</li>"
                for skill in missing_skills
                if priorities[skill] == priority
            )
            or '<li class="empty-state">None</li>'
        )
        + "</ul></article>"
        for heading, priority in priority_groups
    )

    high_priority_missing = sum(
        priorities[skill] == "High" for skill in missing_skills
    )
    display_score = f"{score:g}%"

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{safe(PRODUCT_NAME)} - Skill Match Report</title>
  <style>
    :root {{
      --background: #f3f6fb;
      --surface: #ffffff;
      --text: #172033;
      --muted: #637087;
      --border: #dfe5ef;
      --primary: #2855d9;
      --primary-dark: #173ca8;
      --high-bg: #fee2e2;
      --high-text: #991b1b;
      --medium-bg: #fef3c7;
      --medium-text: #92400e;
      --low-bg: #dcfce7;
      --low-text: #166534;
      --shadow: 0 12px 30px rgba(23, 32, 51, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--background);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}
    .container {{ width: min(1120px, calc(100% - 32px)); margin: 40px auto; }}
    .hero {{
      padding: clamp(28px, 5vw, 52px);
      border-radius: 22px;
      background: linear-gradient(135deg, #172b66, var(--primary));
      color: white;
      box-shadow: var(--shadow);
    }}
    .eyebrow {{ margin: 0 0 6px; opacity: 0.75; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }}
    h1 {{ margin: 0; font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1.1; }}
    .score-row {{ display: flex; align-items: end; justify-content: space-between; gap: 24px; margin-top: 32px; }}
    .score {{ font-size: clamp(2.5rem, 8vw, 5rem); font-weight: 800; line-height: 1; }}
    .score-label {{ margin-top: 8px; opacity: 0.8; }}
    .progress {{ flex: 1; max-width: 560px; height: 16px; overflow: hidden; border-radius: 999px; background: rgba(255,255,255,0.22); }}
    .progress-bar {{ width: {score}%; height: 100%; border-radius: inherit; background: #78e8b4; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
    .summary-card, .panel, .action-card {{ background: var(--surface); border: 1px solid var(--border); box-shadow: var(--shadow); }}
    .summary-card {{ padding: 22px; border-radius: 16px; }}
    .summary-card strong {{ display: block; font-size: 2rem; color: var(--primary-dark); }}
    .summary-card span {{ color: var(--muted); font-size: 0.9rem; }}
    .panel {{ margin-top: 20px; padding: clamp(22px, 4vw, 34px); border-radius: 18px; }}
    h2 {{ margin: 0 0 20px; font-size: 1.35rem; }}
    h3 {{ margin: 0 0 12px; font-size: 1.05rem; }}
    ul, ol {{ margin: 0; padding-left: 22px; }}
    .skill-list {{ list-style: none; padding: 0; }}
    .skill-list > li {{ padding: 14px 0; border-bottom: 1px solid var(--border); }}
    .skill-list > li:last-child {{ border-bottom: 0; }}
    .skill-name {{ margin-right: 10px; font-weight: 700; }}
    .priority-badge {{ display: inline-block; padding: 3px 9px; border-radius: 999px; font-size: 0.75rem; font-weight: 800; }}
    .priority-high {{ background: var(--high-bg); color: var(--high-text); }}
    .priority-medium {{ background: var(--medium-bg); color: var(--medium-text); }}
    .priority-low {{ background: var(--low-bg); color: var(--low-text); }}
    .evidence {{ margin: 7px 0 0; color: var(--muted); }}
    .recommendations li {{ margin-bottom: 18px; padding-left: 6px; }}
    .recommendations p {{ margin: 4px 0 0; color: var(--muted); }}
    .action-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
    .action-card {{ padding: 20px; border-radius: 14px; box-shadow: none; }}
    .action-card li {{ margin: 6px 0; }}
    .empty-state {{ color: var(--muted); font-style: italic; }}
    footer {{ padding: 28px 0 8px; color: var(--muted); text-align: center; font-size: 0.85rem; }}
    @media (max-width: 800px) {{
      .summary-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .action-grid {{ grid-template-columns: 1fr; }}
      .score-row {{ align-items: start; flex-direction: column; }}
      .progress {{ width: 100%; }}
    }}
    @media (max-width: 480px) {{
      .container {{ width: min(100% - 20px, 1120px); margin: 10px auto 24px; }}
      .hero, .panel {{ border-radius: 14px; }}
      .summary-grid {{ grid-template-columns: 1fr 1fr; gap: 10px; }}
      .summary-card {{ padding: 16px; }}
      .summary-card strong {{ font-size: 1.6rem; }}
    }}
  </style>
</head>
<body>
  <main class="container">
    <header class="hero">
      <p class="eyebrow">Offline Skill Match Report</p>
      <h1>{safe(PRODUCT_NAME)}</h1>
      <p>{safe(TAGLINE)}</p>
      <div class="score-row">
        <div><div class="score">{safe(display_score)}</div><div class="score-label">Overall match score</div></div>
        <div class="progress" role="progressbar" aria-label="Match score" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{safe(score)}">
          <div class="progress-bar"></div>
        </div>
      </div>
    </header>

    <section class="summary-grid" aria-label="Analysis summary">
      <div class="summary-card"><strong>{len(required_skills)}</strong><span>Required Skills</span></div>
      <div class="summary-card"><strong>{len(matched_skills)}</strong><span>Matched Skills</span></div>
      <div class="summary-card"><strong>{len(missing_skills)}</strong><span>Missing Skills</span></div>
      <div class="summary-card"><strong>{high_priority_missing}</strong><span>High-Priority Skills Missing</span></div>
    </section>

    <section class="panel"><h2>Required Skills</h2><ul class="skill-list">{required_items}</ul></section>
    <section class="panel"><h2>Matched Skills and Evidence</h2><ul class="skill-list">{matched_items}</ul></section>
    <section class="panel"><h2>Missing Skills</h2><ul class="skill-list">{missing_items}</ul></section>
    <section class="panel recommendations"><h2>Recommendations</h2><ol>{recommendation_items}</ol></section>
    <section class="panel"><h2>Priority Action Plan</h2><div class="action-grid">{action_plan}</div></section>
    <footer>Generated locally by {safe(PRODUCT_NAME)} · © {safe(COPYRIGHT_YEAR)}. No data was sent to an external service.</footer>
  </main>
</body>
</html>
"""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(document, encoding="utf-8")
