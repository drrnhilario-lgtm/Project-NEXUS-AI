"""Streamlit views for Resume Intelligence results."""

from html import escape

import streamlit as st

from ui.cards import render_metric_card, render_priority_badge, render_section_card
from ui.charts import render_priority_gap_chart
from ui.charts import render_roadmap_progress_chart


LIMITATIONS_NOTICE = (
    "This rule-based intelligence depends on extracted PDF text and offline matching. "
    "Skill presence does not prove proficiency, wording can vary, visual formatting "
    "is not fully evaluated, and results do not guarantee hiring outcomes."
)


def render_intelligence_summary(
    intelligence: dict,
    skill_analysis: dict,
    ats_analysis: dict,
) -> None:
    """Render a compact executive insight and five summary cards."""
    top_priority = (
        intelligence["priority_focus"][0]["title"]
        if intelligence["priority_focus"]
        else "Maintain evidence"
    )
    metrics = (
        ("Career Readiness", f'{intelligence["readiness_score"]}%'),
        ("Skill Match", f'{skill_analysis["match_score"]:g}%'),
        ("ATS Readiness", f'{ats_analysis["ats_score"]}%'),
        ("Gap Level", intelligence["career_gap"]["gap_level"]),
        ("Top Priority", top_priority),
    )
    cards = "".join(render_metric_card(label, value) for label, value in metrics)
    st.markdown("### Executive Insight")
    st.markdown(
        f'<div class="executive-summary">{escape(intelligence["executive_summary"])}</div>'
        f'<div class="metric-grid intelligence-metrics">{cards}</div>',
        unsafe_allow_html=True,
    )


def render_learning_roadmap(roadmap: list[dict]) -> None:
    """Render the three personalized learning phases."""
    st.subheader("Personalized Learning Roadmap")
    st.caption("This roadmap represents recommended scope, not tracked completion.")
    render_roadmap_progress_chart(roadmap)
    columns = st.columns(3)
    for column, phase in zip(columns, roadmap):
        topics = "".join(f"<li>{escape(topic)}</li>" for topic in phase["topics"])
        deliverables = "".join(
            f"<li>{escape(item)}</li>" for item in phase["deliverables"]
        )
        success = "".join(
            f"<li>{escape(item)}</li>" for item in phase["success_criteria"]
        )
        with column:
            st.markdown(
                '<article class="intelligence-card roadmap-phase">'
                f'<div class="phase-label">{escape(phase["phase"])}</div>'
                f'<h3>{escape(phase["title"])}</h3>'
                f'<p>{escape(phase["objective"])}</p>'
                f'<div class="duration">{escape(phase["estimated_duration"])}</div>'
                f"<strong>Topics</strong><ul>{topics}</ul>"
                f"<strong>Deliverables</strong><ul>{deliverables}</ul>"
                f"<strong>Success criteria</strong><ul>{success}</ul>"
                "</article>",
                unsafe_allow_html=True,
            )


def render_resume_intelligence(intelligence: dict) -> None:
    """Render the dedicated Resume Intelligence page."""
    st.markdown("## Resume Intelligence")
    st.markdown(
        '<section class="intelligence-hero">'
        f'<div><div class="section-kicker">CAREER READINESS</div>'
        f'<div class="score-display">{intelligence["readiness_score"]}%</div>'
        f'<div class="status-badge">{escape(intelligence["readiness_status"])}</div></div>'
        f'<p>{escape(intelligence["executive_summary"])}</p></section>',
        unsafe_allow_html=True,
    )
    st.progress(
        intelligence["readiness_score"] / 100,
        text=f'{intelligence["readiness_status"]} — {intelligence["readiness_score"]}%',
    )
    strength_column, gap_column = st.columns(2)
    with strength_column:
        st.markdown("### Evidence-Based Strengths")
        if intelligence["strengths"]:
            for strength in intelligence["strengths"]:
                st.markdown(f"- ✅ {strength}")
        else:
            st.caption("Limited strength evidence was detected in the extracted text.")
    with gap_column:
        gap = intelligence["career_gap"]
        st.markdown("### Career Gap")
        st.metric("Gap Level", gap["gap_level"])
        st.write(gap["gap_summary"])
        if gap["major_gaps"]:
            st.markdown("**Major gaps:** " + ", ".join(gap["major_gaps"]))

    st.markdown("### Prioritized Areas for Improvement")
    render_priority_gap_chart(intelligence)
    for item in intelligence["areas_for_improvement"]:
        st.markdown(
            '<div class="intelligence-card improvement-card">'
            f'<div><strong>{escape(item["title"])}</strong> '
            f'{render_priority_badge(item["priority"])}</div>'
            f'<span class="source-label">{escape(item["source"])}</span>'
            f'<p>{escape(item["explanation"])}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Top 3 Priorities")
    priority_columns = st.columns(3)
    for column, item in zip(priority_columns, intelligence["priority_focus"]):
        with column:
            st.markdown(
                '<article class="intelligence-card priority-card">'
                f'<div class="priority-rank">{item["rank"]}</div>'
                f'<h3>{escape(item["title"])}</h3>'
                f'<p>{escape(item["reason"])}</p>'
                f'<strong>Expected impact: {escape(item["expected_impact"])}</strong>'
                f'<p>{escape(item["recommended_evidence"])}</p></article>',
                unsafe_allow_html=True,
            )

    st.markdown("### Recommended Actions")
    action_labels = (
        ("Within 7 Days", "immediate_actions"),
        ("Within 30–60 Days", "short_term_actions"),
        ("Resume Actions", "resume_actions"),
        ("Portfolio Actions", "portfolio_actions"),
    )
    action_columns = st.columns(2)
    for index, (label, key) in enumerate(action_labels):
        with action_columns[index % 2]:
            body = "".join(
                f"<li>{escape(action)}</li>"
                for action in intelligence["recommended_actions"][key]
            )
            render_section_card(label, f"<ul>{body}</ul>")

    render_learning_roadmap(intelligence["learning_roadmap"])

    st.markdown("### Confidence and Limitations")
    st.info(LIMITATIONS_NOTICE)
    for note in intelligence["confidence_notes"]:
        st.markdown(f"- {note}")
