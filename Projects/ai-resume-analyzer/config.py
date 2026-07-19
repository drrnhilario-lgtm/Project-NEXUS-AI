"""Central product identity, release metadata, and application configuration."""

PRODUCT_NAME = "NEXUS AI Resume Intelligence Platform"
SHORT_PRODUCT_NAME = "NEXUS AI"
PLATFORM_NAME = "Resume Intelligence Platform"
TAGLINE = "AI-Powered Resume Intelligence for Smarter Career Decisions"
PRODUCT_DESCRIPTION = (
    "An offline-first platform for transparent resume, ATS-readiness, "
    "skill-gap, and career-development guidance."
)
VERSION = "1.0.0"
RELEASE_STAGE = "Release Candidate"
AUTHOR_NAME = "Darren Hilario"
COPYRIGHT_YEAR = "2026"
VERSION_SHORT = ".".join(VERSION.split(".")[:2])
VERSION_LABEL = f"Version {VERSION_SHORT} {RELEASE_STAGE}"
SHORT_VERSION_LABEL = f"v{VERSION_SHORT} {RELEASE_STAGE}"
APP_TITLE = f"{PRODUCT_NAME} — {RELEASE_STAGE}"

BRAND_PRINCIPLES = (
    "Privacy First",
    "Offline First",
    "Open Source",
    "Data Driven",
    "Career Focused",
)

SESSION_SKILL_RESULT = "analysis_result"
SESSION_ATS_RESULT = "ats_result"
SESSION_INTELLIGENCE_RESULT = "intelligence_result"
SESSION_ANALYZED_FILENAME = "analyzed_filename"
SESSION_COMPACT_HERO = "compact_hero"

ANALYSIS_SESSION_KEYS = (
    SESSION_SKILL_RESULT,
    SESSION_ATS_RESULT,
    SESSION_INTELLIGENCE_RESULT,
)

MIN_JOB_DESCRIPTION_LENGTH = 50
