"""Pure chart-data preparation and Streamlit chart renderers."""

from typing import Any


ATS_CATEGORY_ORDER = (
    "Contact Information",
    "Professional Summary",
    "Skills Section",
    "Work Experience",
    "Education",
    "Job Keyword Coverage",
    "Measurable Achievements",
    "ATS Readability",
)


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp_score(value: Any) -> float:
    return round(max(0.0, min(100.0, _number(value))), 2)


def prepare_score_comparison_data(
    skill_analysis: dict | None,
    ats_analysis: dict | None,
    intelligence_result: dict | None,
) -> list[dict]:
    """Prepare three bounded scores without implying a shared construct."""
    skill_analysis = skill_analysis or {}
    ats_analysis = ats_analysis or {}
    intelligence_result = intelligence_result or {}
    return [
        {"metric": "Skill Match", "score": _clamp_score(skill_analysis.get("match_score"))},
        {"metric": "ATS Readiness", "score": _clamp_score(ats_analysis.get("ats_score"))},
        {"metric": "Career Readiness", "score": _clamp_score(intelligence_result.get("readiness_score"))},
    ]


def prepare_ats_breakdown_data(ats_analysis: dict | None) -> list[dict]:
    """Prepare normalized ATS category scores with safe zero handling."""
    scores = (ats_analysis or {}).get("category_scores", {})
    rows = []
    for category in ATS_CATEGORY_ORDER:
        values = scores.get(category, {})
        earned = max(0.0, _number(values.get("score")))
        maximum = max(0.0, _number(values.get("max_score")))
        percentage = earned / maximum * 100 if maximum else 0.0
        rows.append(
            {
                "category": category,
                "earned": round(min(earned, maximum) if maximum else 0.0, 2),
                "maximum": round(maximum, 2),
                "percentage": _clamp_score(percentage),
            }
        )
    return rows


def prepare_skill_coverage_data(skill_analysis: dict | None) -> dict:
    """Prepare matched and missing required-skill coverage."""
    analysis = skill_analysis or {}
    matched = len(analysis.get("matched_skills") or [])
    missing = len(analysis.get("missing_skills") or [])
    required = len(analysis.get("required_skills") or [])
    if required == 0 and matched + missing:
        required = matched + missing
    matched = min(matched, required) if required else 0
    missing = max(0, required - matched) if required else 0
    coverage = matched / required * 100 if required else 0.0
    return {
        "matched_count": matched,
        "missing_count": missing,
        "total_required_count": required,
        "coverage_percentage": round(coverage, 2),
        "segments": [
            {"status": "Matched", "count": matched},
            {"status": "Missing", "count": missing},
        ],
    }


def prepare_priority_gap_data(intelligence_result: dict | None) -> list[dict]:
    """Count only explicit High, Medium, and Low improvement priorities."""
    counts = {"High": 0, "Medium": 0, "Low": 0}
    for item in (intelligence_result or {}).get("areas_for_improvement", []) or []:
        priority = item.get("priority")
        if priority in counts:
            counts[priority] += 1
    return [
        {"priority": priority, "count": counts[priority]}
        for priority in ("High", "Medium", "Low")
    ]


def prepare_roadmap_scope_data(roadmap: list[dict] | None) -> list[dict]:
    """Summarize planned phase scope without claiming completion."""
    rows = []
    for index, phase in enumerate(roadmap or [], start=1):
        rows.append(
            {
                "phase": str(phase.get("phase") or f"Phase {index}"),
                "title": str(phase.get("title") or "Untitled Phase"),
                "estimated_duration": str(
                    phase.get("estimated_duration") or "Not specified"
                ),
                "topic_count": len(phase.get("topics") or []),
                "deliverable_count": len(phase.get("deliverables") or []),
            }
        )
    return rows


def _runtime():
    import altair as alt
    import streamlit as st

    return st, alt


def render_score_comparison_chart(
    skill_analysis: dict | None,
    ats_analysis: dict | None,
    intelligence_result: dict | None,
) -> None:
    """Render bounded score comparisons with exact labels."""
    st, alt = _runtime()
    rows = prepare_score_comparison_data(
        skill_analysis, ats_analysis, intelligence_result
    )
    chart = (
        alt.Chart(alt.Data(values=rows), title="Score Comparison")
        .mark_bar(color="#3B82F6", cornerRadiusEnd=4)
        .encode(
            x=alt.X("score:Q", scale=alt.Scale(domain=[0, 100]), title="Score (0–100)"),
            y=alt.Y("metric:N", sort=None, title=None),
            tooltip=["metric:N", alt.Tooltip("score:Q", format=".1f")],
        )
        .properties(height=150)
    )
    labels = chart.mark_text(align="left", baseline="middle", dx=4).encode(
        text=alt.Text("score:Q", format=".1f")
    )
    st.altair_chart((chart + labels).configure_view(strokeOpacity=0), use_container_width=True)
    st.caption(
        "Skill Match measures detected required-skill coverage; ATS Readiness measures "
        "rule-based resume structure; Career Readiness combines both with evidence quality."
    )


def render_ats_breakdown_chart(ats_analysis: dict | None) -> None:
    """Render normalized ATS category attainment against each category maximum."""
    st, alt = _runtime()
    rows = prepare_ats_breakdown_data(ats_analysis)
    if not any(row["maximum"] > 0 for row in rows):
        st.info("ATS category data is unavailable. Complete a New Analysis first.")
        return
    chart = (
        alt.Chart(alt.Data(values=rows), title="ATS Category Attainment")
        .mark_bar(color="#3B82F6", cornerRadiusEnd=4)
        .encode(
            x=alt.X("percentage:Q", scale=alt.Scale(domain=[0, 100]), title="Percent of category maximum"),
            y=alt.Y("category:N", sort=list(ATS_CATEGORY_ORDER), title=None),
            tooltip=[
                "category:N",
                "earned:Q",
                "maximum:Q",
                alt.Tooltip("percentage:Q", format=".1f"),
            ],
        )
        .properties(height=300)
        .configure_view(strokeOpacity=0)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption(
        "Bars show the percentage earned within each category. Category maximums differ, "
        "so percentages are normalized for comparison and do not replace exact points."
    )


def render_skill_coverage_chart(skill_analysis: dict | None) -> None:
    """Render matched versus missing required skills as one stacked bar."""
    st, alt = _runtime()
    coverage = prepare_skill_coverage_data(skill_analysis)
    total = coverage["total_required_count"]
    if total == 0:
        st.info("No required skills were detected, so skill coverage cannot be plotted.")
        return
    columns = st.columns(4)
    columns[0].metric("Matched", coverage["matched_count"])
    columns[1].metric("Missing", coverage["missing_count"])
    columns[2].metric("Required", total)
    columns[3].metric("Coverage", f'{coverage["coverage_percentage"]:g}%')
    chart = (
        alt.Chart(alt.Data(values=coverage["segments"]), title="Required Skill Coverage")
        .mark_bar()
        .encode(
            x=alt.X("count:Q", stack="zero", title="Required skill count"),
            color=alt.Color(
                "status:N",
                scale=alt.Scale(
                    domain=["Matched", "Missing"], range=["#3B82F6", "#94A3B8"]
                ),
                legend=alt.Legend(orient="top"),
            ),
            tooltip=["status:N", "count:Q"],
        )
        .properties(height=90)
        .configure_view(strokeOpacity=0)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption(
        f"{coverage['matched_count']} of {total} detected required skills are supported "
        "by resume evidence. Color is supplemented by direct counts and labels."
    )


def render_priority_gap_chart(intelligence_result: dict | None) -> None:
    """Render counts of explicitly assigned improvement priorities."""
    st, alt = _runtime()
    rows = prepare_priority_gap_data(intelligence_result)
    if not any(row["count"] for row in rows):
        st.info("No prioritized improvement areas are available to plot.")
        return
    chart = (
        alt.Chart(alt.Data(values=rows), title="Priority Gap Counts")
        .mark_bar(color="#D97706", cornerRadiusEnd=4)
        .encode(
            x=alt.X("count:Q", title="Number of improvement areas", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("priority:N", sort=["High", "Medium", "Low"], title=None),
            tooltip=["priority:N", "count:Q"],
        )
        .properties(height=150)
        .configure_view(strokeOpacity=0)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption(
        "Counts reflect only priority levels assigned by the offline intelligence rules; "
        "bar labels communicate priority independently of color."
    )


def render_roadmap_progress_chart(roadmap: list[dict] | None) -> None:
    """Render roadmap scope by topics and deliverables, not completion."""
    st, alt = _runtime()
    rows = prepare_roadmap_scope_data(roadmap)
    if not rows:
        st.info("Roadmap scope is unavailable. Complete a New Analysis first.")
        return
    long_rows = []
    for row in rows:
        long_rows.extend(
            (
                {"phase": row["phase"], "measure": "Topics", "count": row["topic_count"]},
                {"phase": row["phase"], "measure": "Deliverables", "count": row["deliverable_count"]},
            )
        )
    chart = (
        alt.Chart(alt.Data(values=long_rows), title="Roadmap Scope")
        .mark_bar()
        .encode(
            x=alt.X("phase:N", sort=[row["phase"] for row in rows], title=None),
            xOffset="measure:N",
            y=alt.Y("count:Q", title="Planned items", axis=alt.Axis(tickMinStep=1)),
            color=alt.Color(
                "measure:N",
                scale=alt.Scale(
                    domain=["Topics", "Deliverables"], range=["#3B82F6", "#D97706"]
                ),
                legend=alt.Legend(orient="top"),
            ),
            tooltip=["phase:N", "measure:N", "count:Q"],
        )
        .properties(height=230)
        .configure_view(strokeOpacity=0)
    )
    st.altair_chart(chart, use_container_width=True)
    duration_text = " · ".join(
        f"{row['phase']} ({row['title']}): {row['estimated_duration']}" for row in rows
    )
    st.caption(
        "Roadmap Scope shows planned topics and deliverables, not completed progress. "
        + duration_text
    )
