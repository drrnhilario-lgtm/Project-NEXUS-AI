"""Analysis dashboard and tab content."""

from html import escape

import streamlit as st

from ui.charts import render_ats_breakdown_chart
from ui.cards import render_priority_badge, render_section_card
from ui.cards import render_skill_list, render_status_badge
from ui.cards import render_summary_metric_cards


def get_score_status(score: float) -> str:
    """Return the dashboard status label for a match score."""
    if score < 40:
        return "Needs Improvement"
    if score < 60:
        return "Developing Match"
    if score < 80:
        return "Good Match"
    if score < 90:
        return "Strong Match"
    return "Excellent Match"


def render_ats_review(ats_result: dict) -> None:
    """Render the transparent ATS readiness result."""
    score = ats_result["ats_score"]
    st.markdown(
        '<section class="ats-heading"><div>'
        '<div class="section-kicker">ATS READINESS</div>'
        f'<div class="score-display">{score}%</div>'
        f'<div class="status-label">{render_status_badge(ats_result["ats_status"])}</div>'
        "</div></section>",
        unsafe_allow_html=True,
    )
    st.progress(score / 100, text=ats_result["ats_status"])
    render_ats_breakdown_chart(ats_result)

    coverage = ats_result["keyword_coverage"]
    coverage_columns = st.columns(3)
    coverage_columns[0].metric("Matched Keywords", coverage["matched_keyword_count"])
    coverage_columns[1].metric(
        "Required Keywords", coverage["total_required_keyword_count"]
    )
    coverage_columns[2].metric(
        "Keyword Coverage", f'{coverage["keyword_coverage_percentage"]:g}%'
    )

    st.subheader("Category Breakdown")
    category_html = "".join(
        '<div class="ats-category"><span>'
        f"{escape(category)}</span><strong>{values['score']} / "
        f"{values['max_score']}</strong></div>"
        for category, values in ats_result["category_scores"].items()
    )
    st.markdown(category_html, unsafe_allow_html=True)

    passed_checks = [check for check in ats_result["checks"] if check["passed"]]
    failed_checks = [check for check in ats_result["checks"] if not check["passed"]]
    check_columns = st.columns(2)
    with check_columns[0]:
        st.markdown("#### Passed Checks")
        for check in passed_checks:
            st.markdown(f"- ✅ **{check['name']}** — {check['feedback']}")
    with check_columns[1]:
        st.markdown("#### Checks to Improve")
        for check in failed_checks:
            st.markdown(f"- ⚠️ **{check['name']}** — {check['feedback']}")

    insight_columns = st.columns(2)
    with insight_columns[0]:
        st.markdown("#### Strengths")
        if ats_result["strengths"]:
            for strength in ats_result["strengths"]:
                st.markdown(f"- {strength}")
        else:
            st.caption("No strong ATS signals were detected yet.")
    with insight_columns[1]:
        st.markdown("#### Improvement Suggestions")
        for suggestion in ats_result["improvement_suggestions"]:
            st.markdown(f"- {suggestion}")
    st.caption(
        "The ATS Readiness Score is a rule-based estimate for guidance only. "
        "Actual applicant tracking systems use different parsing and ranking methods."
    )


def render_dashboard(analysis_result: dict, ats_result: dict | None = None) -> None:
    """Render the persisted analysis dashboard and its five tabs."""
    score = float(analysis_result["match_score"])
    status = get_score_status(score)
    required = analysis_result["required_skills"]
    matched = analysis_result["matched_skills"]
    missing = analysis_result["missing_skills"]
    priorities = analysis_result["skill_priorities"]
    evidence = analysis_result["match_evidence"]

    st.markdown(
        '<section class="dashboard-heading"><div>'
        '<div class="section-kicker">ANALYSIS COMPLETE</div>'
        f'<div class="score-display">{score:g}%</div>'
        f'<div class="status-label">{render_status_badge(status)}</div></div>'
        '<div class="score-summary">'
        f"<strong>{len(matched)} of {len(required)}</strong> required skills matched"
        "</div></section>",
        unsafe_allow_html=True,
    )
    st.progress(
        max(0.0, min(1.0, score / 100)),
        text=f"{status} — {score:g}% match",
    )
    render_summary_metric_cards(analysis_result, ats_result)

    overview, skills, ats_tab, recommendations, roadmap, downloads = st.tabs(
        [
            "Overview",
            "Skill Analysis",
            "ATS Review",
            "Recommendations",
            "Learning Roadmap",
            "Downloads",
        ]
    )

    with overview:
        st.subheader("Result Summary")
        st.write(
            f"Your resume matches {len(matched)} of {len(required)} skills "
            f"detected in the job description. The result is **{status}**."
        )
        columns = st.columns(3)
        with columns[0]:
            st.markdown("#### Required Skills")
            render_skill_list(required)
        with columns[1]:
            st.markdown("#### Matched Skills")
            render_skill_list(matched, evidence=evidence, card_type="matched")
        with columns[2]:
            st.markdown("#### Missing Skills")
            render_skill_list(missing, card_type="missing")

    with skills:
        columns = st.columns(3)
        with columns[0]:
            st.markdown("#### Required Skills")
            render_skill_list(required, priorities=priorities)
        with columns[1]:
            st.markdown("#### Matched Skills")
            render_skill_list(
                matched,
                priorities=priorities,
                evidence=evidence,
                card_type="matched",
            )
        with columns[2]:
            st.markdown("#### Missing Skills")
            render_skill_list(missing, priorities=priorities, card_type="missing")

    with ats_tab:
        if ats_result is None:
            render_section_card(
                "Complete a New Analysis first",
                "<p>ATS readiness results will appear here after a resume and job description are analyzed.</p>",
                "🎯",
            )
        else:
            render_ats_review(ats_result)

    with recommendations:
        st.subheader("Recommended Next Steps")
        if not missing:
            st.success("No missing required skills were detected.")
        for number, skill in enumerate(sorted(missing), start=1):
            st.markdown(
                '<div class="recommendation-card">'
                f'<span class="recommendation-number">{number}</span><div>'
                f'<div class="recommendation-title">{escape(skill)} '
                f"{render_priority_badge(priorities[skill])}</div>"
                f'<p>{escape(analysis_result["recommendations"][skill])}</p>'
                "</div></div>",
                unsafe_allow_html=True,
            )

    with roadmap:
        columns = st.columns(3)
        groups = (
            ("Learn First", "High", "Start with these critical gaps."),
            ("Learn Next", "Medium", "Build these skills next."),
            ("Optional Development", "Low", "Develop these when time allows."),
        )
        for column, (heading, priority, description) in zip(columns, groups):
            roadmap_skills = [
                skill for skill in missing if priorities[skill] == priority
            ]
            with column:
                st.markdown(
                    '<div class="roadmap-card">'
                    f"<h3>{escape(heading)}</h3>{render_priority_badge(priority)}"
                    f"<p>{escape(description)}</p></div>",
                    unsafe_allow_html=True,
                )
                render_skill_list(roadmap_skills)

    with downloads:
        render_section_card(
            "Reports are available in the Download Center",
            "<p>Open Downloads from the sidebar to export HTML or text reports. PDF remains planned.</p>",
            "↗",
        )
