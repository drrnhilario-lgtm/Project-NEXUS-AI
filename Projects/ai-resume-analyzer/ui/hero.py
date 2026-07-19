"""Official NEXUS AI hero component."""

import streamlit as st

from config import PLATFORM_NAME, SHORT_PRODUCT_NAME, TAGLINE


def render_hero(compact: bool = False) -> None:
    """Render the responsive product hero, optionally at dashboard density."""
    css_class = "nexus-hero compact" if compact else "nexus-hero"
    st.markdown(
        f"""
        <header class="{css_class}">
          <div class="brand">{SHORT_PRODUCT_NAME}</div>
          <h1>{PLATFORM_NAME}</h1>
          <p class="subtitle">{TAGLINE}</p>
          <div class="hero-badges">
            <span class="hero-badge">🔒 Privacy First</span>
            <span class="hero-badge">⚡ Offline</span>
            <span class="hero-badge">🚀 Fast Analysis</span>
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )
