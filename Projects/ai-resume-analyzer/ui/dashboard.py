"""Executive dashboard composition using reusable presentation components."""

from html import escape
import streamlit as st

from ui.cards import render_action_card, render_executive_insight, render_metric_card
from ui.cards import render_priority_card
from ui.charts import render_ats_breakdown_chart, render_priority_gap_chart
from ui.charts import render_score_comparison_chart, render_skill_coverage_chart


def _top_priority(result: dict) -> str:
    priorities = result.get("priority_focus", [])
    return priorities[0].get("title", "Maintain current strengths") if priorities else "Maintain current strengths"


def render_analytics_dashboard(skill_analysis: dict, ats_analysis: dict, intelligence_result: dict, filename: str = "Resume PDF") -> None:
    """Render the recruiter-ready dashboard in executive reading order."""
    st.markdown("## Dashboard")
    st.caption("Overview of resume alignment, ATS readiness, career gaps, and recommended next actions.")
    gap = intelligence_result.get("career_gap", {})
    top_priority = _top_priority(intelligence_result)
    metrics = (
        ("Career Readiness", f'{intelligence_result.get("readiness_score", 0)}%', "Overall evidence-based readiness"),
        ("Skill Match", f'{skill_analysis.get("match_score", 0):g}%', "Required-job skill alignment"),
        ("ATS Readiness", f'{ats_analysis.get("ats_score", 0)}%', "Rule-based resume readiness"),
        ("Gap Level", gap.get("gap_level", "Not available"), "Current career gap"),
        ("Top Priority", top_priority, "Highest-impact next focus"),
    )
    st.markdown(f'<div class="metric-grid executive-metrics">{"".join(render_metric_card(label, value, subtitle) for label, value, subtitle in metrics)}</div>', unsafe_allow_html=True)
    render_executive_insight(intelligence_result.get("executive_summary", ""), top_priority, gap.get("gap_level"))

    st.markdown("### Visual Analytics")
    chart_columns = st.columns(2, gap="large")
    with chart_columns[0]:
        render_score_comparison_chart(skill_analysis, ats_analysis, intelligence_result)
    with chart_columns[1]:
        render_skill_coverage_chart(skill_analysis)
    render_ats_breakdown_chart(ats_analysis)

    st.markdown("### Top Priorities")
    priority_columns = st.columns(3, gap="large")
    for column, priority in zip(priority_columns, intelligence_result.get("priority_focus", [])[:3]):
        with column:
            st.markdown(render_priority_card(priority), unsafe_allow_html=True)

    st.markdown("### Immediate Actions")
    st.caption("Recommended within 7 days")
    actions = intelligence_result.get("recommended_actions", {}).get("immediate_actions", [])
    st.markdown(f'<div class="action-grid">{"".join(render_action_card(action) for action in actions) or render_action_card("Review the detailed Results page.")}</div>', unsafe_allow_html=True)

    st.markdown("### Analysis Summary")
    required = skill_analysis.get("required_skills", [])
    matched = skill_analysis.get("matched_skills", [])
    metadata = (("Resume analyzed", filename), ("Job description analyzed", "Yes"),
                ("Required skills", len(required)), ("Matched skills", len(matched)),
                ("Missing skills", len(skill_analysis.get("missing_skills", []))),
                ("Analysis mode", "Offline"), ("Personal data stored", "No"))
    st.markdown('<div class="metadata-grid">' + ''.join(f'<div><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>' for label, value in metadata) + '</div>', unsafe_allow_html=True)
    st.info("Use Results for detailed evidence and Learning Roadmap for phase-by-phase development guidance.")


def render_results_visuals(skill_analysis: dict, ats_analysis: dict, intelligence_result: dict) -> None:
    """Render only the decision-focused visuals used on the Results page."""
    st.markdown("### Visual Summary")
    render_score_comparison_chart(skill_analysis, ats_analysis, intelligence_result)
    columns = st.columns(2, gap="large")
    with columns[0]: render_skill_coverage_chart(skill_analysis)
    with columns[1]: render_priority_gap_chart(intelligence_result)
