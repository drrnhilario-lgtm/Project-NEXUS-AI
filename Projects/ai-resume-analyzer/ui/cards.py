"""Reusable, theme-aware UI cards and pure display helpers."""

from html import escape

import streamlit as st

from config import AUTHOR_NAME, COPYRIGHT_YEAR, PRODUCT_NAME, VERSION_LABEL


def clamp_percentage(value: object) -> float:
    """Return a safe percentage in the inclusive 0–100 range."""
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def safe_metric_value(value: object, fallback: str = "—") -> str:
    """Format missing metric values without leaking Python sentinel text."""
    return fallback if value is None or str(value).strip() == "" else str(value)


def safe_priority_title(value: object, limit: int = 72) -> str:
    """Compact an unusually long priority title for responsive cards."""
    title = safe_metric_value(value, "Maintain current strengths").strip()
    return title if len(title) <= limit else f"{title[: limit - 1].rstrip()}…"


def normalize_actions(actions: object) -> list[str]:
    """Return clean action strings, with a useful empty-list fallback."""
    if not isinstance(actions, (list, tuple)):
        return []
    return [str(action).strip() for action in actions if str(action).strip()]


def normalize_download_metadata(metadata: dict | None) -> dict:
    """Return safe, predictable metadata for a download card."""
    source = metadata or {}
    return {
        "title": safe_metric_value(source.get("title"), "Analysis report"),
        "description": safe_metric_value(source.get("description"), "Report details."),
        "status": safe_metric_value(source.get("status"), "Planned"),
        "file_name": source.get("file_name") or None,
        "mime": source.get("mime") or "application/octet-stream",
    }


def empty_state_content(title: object = None, message: object = None) -> tuple[str, str]:
    """Provide accessible fallbacks for empty-state copy."""
    return (
        safe_metric_value(title, "Analysis not available"),
        safe_metric_value(
            message,
            "Complete a New Analysis to unlock resume insights, ATS review, "
            "visual analytics, and personalized recommendations.",
        ),
    )


def render_metric_card(
    label: str,
    value: object,
    subtitle: str | None = None,
    status: str | None = None,
    help_text: str | None = None,
) -> str:
    """Return one escaped executive metric card."""
    supporting = subtitle or help_text
    status_html = render_status_badge(status) if status else ""
    support_html = (
        f'<span class="metric-subtitle">{escape(supporting)}</span>'
        if supporting else ""
    )
    return (
        '<article class="metric-card">'
        f'<span class="metric-label">{escape(label)}</span>'
        f'<span class="metric-value">{escape(safe_metric_value(value))}</span>'
        f"{status_html}{support_html}</article>"
    )


def render_status_badge(status: str) -> str:
    """Return an escaped status badge as HTML."""
    return f'<span class="status-badge">{escape(safe_metric_value(status, "Status unavailable"))}</span>'


def render_priority_badge(priority: str) -> str:
    """Return a normalized, escaped priority badge as HTML."""
    normalized = priority if priority in {"High", "Medium", "Low"} else "Medium"
    return (
        f'<span class="priority-badge priority-{normalized.lower()}">'
        f"{escape(normalized)} Priority</span>"
    )


def render_executive_insight(summary: str, top_priority: str | None = None, gap_level: str | None = None) -> None:
    """Render a compact executive summary with optional context chips."""
    chips = "".join(
        f'<span class="insight-chip">{escape(label)}: {escape(safe_metric_value(value))}</span>'
        for label, value in (("Gap", gap_level), ("Top priority", top_priority)) if value
    )
    st.markdown(
        '<section class="executive-insight"><div class="section-kicker">EXECUTIVE INSIGHT</div>'
        f'<p>{escape(safe_metric_value(summary, "No executive summary is available."))}</p>'
        f'<div class="insight-chips">{chips}</div></section>', unsafe_allow_html=True,
    )


def render_priority_card(priority: dict) -> str:
    """Return a safe priority card from an intelligence priority mapping."""
    level = priority.get("priority", "High" if priority.get("rank") == 1 else "Medium")
    return (
        '<article class="priority-card polished-card">'
        f'<div class="priority-card-head"><span class="priority-rank">{escape(str(priority.get("rank", "—")))}</span>'
        f'{render_priority_badge(level)}</div><h3>{escape(safe_priority_title(priority.get("title")))}</h3>'
        f'<p>{escape(safe_metric_value(priority.get("reason"), "No reason supplied."))}</p>'
        f'<div class="support-line"><strong>Expected impact:</strong> {escape(safe_metric_value(priority.get("expected_impact")))}</div>'
        f'<div class="support-line"><strong>Recommended evidence:</strong> {escape(safe_metric_value(priority.get("recommended_evidence")))}</div>'
        '</article>'
    )


def render_action_card(action: str, timeframe: str = "Recommended within 7 days") -> str:
    """Return a compact action card with its recommended timeframe."""
    return (
        '<div class="action-card"><span class="action-check">✓</span><div>'
        f'<strong>{escape(safe_metric_value(action))}</strong><span>{escape(timeframe)}</span>'
        '</div></div>'
    )


def render_download_card(title: str, description: str, status: str, button_label: str | None = None, data: str | bytes | None = None, file_name: str | None = None, mime: str | None = None) -> None:
    """Render report metadata and a download button only when data exists."""
    st.markdown(
        '<article class="download-card polished-card">'
        f'<div><span class="download-status">{escape(status)}</span><h3>{escape(title)}</h3><p>{escape(description)}</p></div></article>',
        unsafe_allow_html=True,
    )
    if data is not None and button_label and file_name:
        st.download_button(button_label, data=data, file_name=file_name, mime=mime, use_container_width=True)
    else:
        st.caption("This format is not available in the current version.")


def render_empty_state(title: str | None = None, message: str | None = None, action_label: str | None = None, icon: str | None = None) -> None:
    """Render a reusable empty state with safe fallback content."""
    safe_title, safe_message = empty_state_content(title, message)
    action = f'<div class="empty-action">{escape(action_label)}</div>' if action_label else ""
    st.markdown(
        '<section class="empty-state-card">'
        f'<div class="empty-icon">{escape(icon or "○")}</div><div><h3>{escape(safe_title)}</h3>'
        f'<p>{escape(safe_message)}</p>{action}</div></section>', unsafe_allow_html=True,
    )


def render_section_card(title: str, body_html: str, icon: str = "") -> None:
    """Render a general section card whose body is trusted application HTML."""
    icon_html = f'<div class="section-card-icon">{escape(icon)}</div>' if icon else ""
    st.markdown(f'<section class="section-card">{icon_html}<div><h3>{escape(title)}</h3>{body_html}</div></section>', unsafe_allow_html=True)


def render_footer() -> None:
    """Render centralized application and version metadata."""
    st.markdown(f'<footer class="nexus-footer"><strong>{escape(PRODUCT_NAME)}</strong><br>{escape(VERSION_LABEL)}<br>Built with Python and Streamlit<br>Offline processing • © {escape(COPYRIGHT_YEAR)} {escape(AUTHOR_NAME)}</footer>', unsafe_allow_html=True)


def render_summary_metric_cards(analysis_result: dict, ats_result: dict | None = None) -> None:
    """Render skill-analysis summary cards with an optional ATS score."""
    missing = analysis_result.get("missing_skills", [])
    priorities = analysis_result.get("skill_priorities", {})
    metrics = [("Skill Match Score", f'{clamp_percentage(analysis_result.get("match_score")):g}%'), ("Required Skills", len(analysis_result.get("required_skills", []))), ("Matched Skills", len(analysis_result.get("matched_skills", []))), ("Missing Skills", len(missing)), ("High-Priority Gaps", sum(priorities.get(skill) == "High" for skill in missing))]
    if ats_result is not None:
        metrics.insert(1, ("ATS Readiness Score", f'{clamp_percentage(ats_result.get("ats_score")):g}%'))
    st.markdown(f'<div class="metric-grid">{"".join(render_metric_card(*item) for item in metrics)}</div>', unsafe_allow_html=True)


def render_skill_list(skills: list[str], priorities: dict[str, str] | None = None, evidence: dict[str, str] | None = None, card_type: str = "neutral") -> None:
    """Render sorted skills with optional priorities and detected evidence."""
    if not skills:
        st.markdown('<div class="empty-inline">None</div>', unsafe_allow_html=True)
        return
    items = []
    for skill in sorted(skills):
        badge = render_priority_badge(priorities.get(skill, "Medium")) if priorities else ""
        evidence_html = f'<div class="evidence-line"><strong>Detected evidence:</strong> {escape(evidence[skill])}</div>' if evidence and skill in evidence else ""
        items.append(f'<div class="skill-item skill-{escape(card_type)}"><div class="skill-heading"><strong>{escape(skill)}</strong>{badge}</div>{evidence_html}</div>')
    st.markdown("".join(items), unsafe_allow_html=True)
