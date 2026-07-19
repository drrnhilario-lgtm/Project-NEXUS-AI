"""Streamlit entry point for NEXUS AI Resume Intelligence Platform."""

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from config import ANALYSIS_SESSION_KEYS, APP_TITLE, AUTHOR_NAME, PRODUCT_DESCRIPTION
from config import PRODUCT_NAME, TAGLINE, VERSION_LABEL
from config import MIN_JOB_DESCRIPTION_LENGTH, SESSION_ANALYZED_FILENAME
from config import SESSION_ATS_RESULT, SESSION_COMPACT_HERO
from config import SESSION_INTELLIGENCE_RESULT, SESSION_SKILL_RESULT
from core.ats_engine import analyze_ats_readiness
from core.intelligence_engine import generate_resume_intelligence
from core.pdf_reader import EncryptedPDFError, InvalidPDFError, NoExtractableTextError
from core.pdf_reader import extract_resume_text
from core.skill_matcher import analyze_skill_match
from core.reporting import build_html_report_bytes, build_text_report
from ui.cards import render_download_card, render_empty_state, render_footer
from ui.cards import render_section_card
from ui.dashboard import render_analytics_dashboard, render_results_visuals
from ui.hero import render_hero
from ui.intelligence import render_intelligence_summary, render_learning_roadmap
from ui.intelligence import render_resume_intelligence
from ui.sidebar import ABOUT_PAGE, ATS_REVIEW_PAGE, DASHBOARD_PAGE, DOWNLOADS_PAGE
from ui.sidebar import INTELLIGENCE_PAGE, LEARNING_ROADMAP_PAGE, NEW_ANALYSIS_PAGE
from ui.sidebar import RESULTS_PAGE, SETTINGS_PAGE, render_sidebar
from ui.tabs import render_ats_review, render_dashboard
from ui.theme import apply_theme


LOGGER = logging.getLogger(__name__)

st.set_page_config(page_title=APP_TITLE, page_icon="📄", layout="wide", initial_sidebar_state="expanded")
apply_theme()
selected_page = render_sidebar()
st.session_state.setdefault(SESSION_COMPACT_HERO, True)
render_hero(compact=st.session_state[SESSION_COMPACT_HERO] or selected_page != NEW_ANALYSIS_PAGE)


def analysis_available() -> bool:
    """Return whether one complete, internally consistent analysis is available."""
    return all(st.session_state.get(key) is not None for key in ANALYSIS_SESSION_KEYS)


def show_empty(icon: str) -> None:
    """Render the shared no-analysis state for a workspace page."""
    render_empty_state(
        "Complete a New Analysis first",
        "Complete a New Analysis to unlock resume insights, ATS review, visual analytics, and personalized recommendations.",
        "Go to New Analysis from the sidebar",
        icon,
    )


def finish_page() -> None:
    """Render the shared footer and stop the current Streamlit rerun."""
    render_footer()
    st.stop()


if selected_page == DASHBOARD_PAGE:
    if analysis_available():
        render_analytics_dashboard(st.session_state[SESSION_SKILL_RESULT], st.session_state[SESSION_ATS_RESULT], st.session_state[SESSION_INTELLIGENCE_RESULT], st.session_state.get(SESSION_ANALYZED_FILENAME, "Resume PDF"))
    else:
        show_empty("🏠")
    finish_page()

if selected_page == ATS_REVIEW_PAGE:
    if analysis_available():
        render_ats_review(st.session_state[SESSION_ATS_RESULT])
    else:
        show_empty("🎯")
    finish_page()

if selected_page == INTELLIGENCE_PAGE:
    if analysis_available():
        render_resume_intelligence(st.session_state[SESSION_INTELLIGENCE_RESULT])
    else:
        show_empty("🧭")
    finish_page()

if selected_page == LEARNING_ROADMAP_PAGE:
    if analysis_available():
        render_learning_roadmap(st.session_state[SESSION_INTELLIGENCE_RESULT]["learning_roadmap"])
    else:
        show_empty("📚")
    finish_page()

if selected_page == RESULTS_PAGE:
    if analysis_available():
        render_intelligence_summary(st.session_state[SESSION_INTELLIGENCE_RESULT], st.session_state[SESSION_SKILL_RESULT], st.session_state[SESSION_ATS_RESULT])
        render_results_visuals(st.session_state[SESSION_SKILL_RESULT], st.session_state[SESSION_ATS_RESULT], st.session_state[SESSION_INTELLIGENCE_RESULT])
        render_dashboard(st.session_state[SESSION_SKILL_RESULT], st.session_state[SESSION_ATS_RESULT])
    else:
        show_empty("📊")
    finish_page()

if selected_page == DOWNLOADS_PAGE:
    st.markdown("## Download Center")
    st.caption("Export the current offline analysis without storing the uploaded resume.")
    if not analysis_available():
        show_empty("📁")
    else:
        result = st.session_state[SESSION_SKILL_RESULT]
        columns = st.columns(3, gap="large")
        with columns[0]:
            render_download_card("HTML Analysis Report", "A complete browser-ready report containing scores, skill insights, priorities, and recommendations.", "Available", "Download HTML report", build_html_report_bytes(result), "nexus-resume-analysis.html", "text/html")
        with columns[1]:
            render_download_card("Text Analysis Report", "A lightweight plain-text version for easy copying and archiving.", "Available", "Download text report", build_text_report(result), "nexus-resume-analysis.txt", "text/plain")
        with columns[2]:
            render_download_card("PDF Report", "A print-ready professional report planned for a future sprint.", "Planned")
        st.caption("Reports are generated in memory or through a deleted temporary file. Uploaded resumes are not permanently stored.")
    finish_page()

if selected_page == SETTINGS_PAGE:
    st.markdown("## Settings")
    st.caption("Functional display preferences and offline application information.")
    st.markdown("### Display Preferences")
    st.session_state[SESSION_COMPACT_HERO] = st.toggle("Compact hero", value=st.session_state[SESSION_COMPACT_HERO], help="Reduces hero height across workspace pages.")
    st.markdown("### Analysis Settings")
    st.info("Explanations: Enabled · Limitations: Enabled · Analysis mode: Offline only")
    st.markdown("### Privacy")
    st.write("Uploaded resumes are processed locally during the session. No OpenAI API, database storage, or automatic cloud upload is used.")
    st.markdown("### Application")
    st.write(f"{PRODUCT_NAME} · {VERSION_LABEL} · Python + Streamlit · Offline modular analysis engine")
    finish_page()

if selected_page == ABOUT_PAGE:
    st.markdown("## About")
    render_section_card(
        PRODUCT_NAME,
        f"<p><strong>{TAGLINE}</strong></p><p>{PRODUCT_DESCRIPTION} "
        f"It is privacy-first, open source, and maintained by {AUTHOR_NAME}. "
        f"Current stage: {VERSION_LABEL}.</p>",
        "ℹ",
    )
    finish_page()

st.markdown('<div class="section-label">START A NEW ANALYSIS</div>', unsafe_allow_html=True)
st.markdown('<div class="input-intro">Upload your resume and paste the complete job description. Both inputs stay visible so you can refine and rerun the analysis.</div>', unsafe_allow_html=True)
upload_column, description_column = st.columns(2, gap="large")
with upload_column:
    st.subheader("Upload Resume PDF")
    uploaded_resume = st.file_uploader("Upload a text-based PDF", type=["pdf"], help="Encrypted and image-only PDFs are not supported.")
    if uploaded_resume is not None:
        st.success(f"Selected: {uploaded_resume.name}")
        st.caption(f"File size: {uploaded_resume.size / 1024:.1f} KB")
with description_column:
    st.subheader("Paste Job Description")
    job_description = st.text_area("Paste the complete job description", height=300, placeholder="Include the role summary, responsibilities, required qualifications, preferred skills, tools, and technologies...")

analyze_clicked = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)
if analyze_clicked:
    if uploaded_resume is None:
        st.error("Please upload a PDF resume before starting the analysis.")
    elif not job_description.strip():
        st.error("Please enter a job description before starting the analysis.")
    elif len(job_description.strip()) < MIN_JOB_DESCRIPTION_LENGTH:
        st.error(f"The job description must contain at least {MIN_JOB_DESCRIPTION_LENGTH} characters.")
    else:
        temporary_path = None
        try:
            with st.spinner("Analyzing your resume..."):
                with NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_file:
                    temporary_file.write(uploaded_resume.getvalue())
                    temporary_path = Path(temporary_file.name)
                resume_text = extract_resume_text(temporary_path)
                if not resume_text.strip():
                    raise NoExtractableTextError("The PDF did not contain extractable text.")
                skill_result = analyze_skill_match(resume_text, job_description.strip())
                ats_result = analyze_ats_readiness(resume_text, job_description.strip(), skill_result)
                intelligence_result = generate_resume_intelligence(resume_text, job_description.strip(), skill_result, ats_result)
                st.session_state.update({SESSION_SKILL_RESULT: skill_result, SESSION_ATS_RESULT: ats_result, SESSION_INTELLIGENCE_RESULT: intelligence_result, SESSION_ANALYZED_FILENAME: uploaded_resume.name})
            st.success(f"Analysis complete for {uploaded_resume.name}.")
        except EncryptedPDFError:
            st.error("This PDF is encrypted. Please upload an unencrypted resume.")
        except NoExtractableTextError:
            st.error("No readable text was found. The PDF may be image-only; please upload a text-based PDF.")
        except InvalidPDFError:
            st.error("The uploaded file could not be read as a valid PDF.")
        except (OSError, ValueError) as error:
            st.error(f"The PDF could not be processed: {error}")
        except Exception:
            LOGGER.exception("Unexpected resume-analysis failure")
            st.error("An unexpected processing error occurred. Please verify the PDF and job description, then try again.")
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

if analysis_available():
    st.caption(f'Showing saved results for: {st.session_state.get(SESSION_ANALYZED_FILENAME, "resume")}')
    render_intelligence_summary(st.session_state[SESSION_INTELLIGENCE_RESULT], st.session_state[SESSION_SKILL_RESULT], st.session_state[SESSION_ATS_RESULT])
    render_dashboard(st.session_state[SESSION_SKILL_RESULT], st.session_state[SESSION_ATS_RESULT])
else:
    render_empty_state("Ready to analyze your resume", "Upload a text-based PDF, paste the complete job description, select Analyze Resume, then review your private offline results.", "Four steps · PDF · Job description · Analyze · Review", "📄")
render_footer()
