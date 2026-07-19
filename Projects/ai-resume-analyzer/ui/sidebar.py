"""Sidebar navigation for the Streamlit dashboard."""

import streamlit as st

from config import PLATFORM_NAME, SHORT_PRODUCT_NAME, SHORT_VERSION_LABEL


NEW_ANALYSIS_PAGE = "📄 New Analysis"
DASHBOARD_PAGE = "🏠 Dashboard"
ATS_REVIEW_PAGE = "🎯 ATS Review"
RESULTS_PAGE = "📊 Results"
INTELLIGENCE_PAGE = "🧭 Resume Intelligence"
LEARNING_ROADMAP_PAGE = "📚 Learning Roadmap"
DOWNLOADS_PAGE = "📁 Download Center"
SETTINGS_PAGE = "⚙ Settings"
ABOUT_PAGE = "ℹ About"


def render_sidebar() -> str:
    """Render compact grouped navigation and return the selected page."""
    with st.sidebar:
        st.header(SHORT_PRODUCT_NAME)
        st.caption(PLATFORM_NAME)
        st.caption(SHORT_VERSION_LABEL)
        selected_page = st.radio(
            "Workspace navigation",
            (DASHBOARD_PAGE, NEW_ANALYSIS_PAGE, RESULTS_PAGE, ATS_REVIEW_PAGE,
             INTELLIGENCE_PAGE, LEARNING_ROADMAP_PAGE, DOWNLOADS_PAGE,
             SETTINGS_PAGE, ABOUT_PAGE),
            index=1,
            label_visibility="collapsed",
        )
        st.caption("ANALYSIS · Dashboard, Results, ATS, Intelligence, Roadmap")
        st.divider()
        st.caption("WORKSPACE · Download Center, Settings, About")
        st.caption("● Offline · Local processing · No OpenAI API")
    return selected_page
