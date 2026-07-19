# NEXUS AI Resume Intelligence Platform Architecture

## Folder structure

```text
ai-resume-analyzer/
├── config.py               # Application metadata and session-state keys
├── app.py                  # Command-line entry point
├── streamlit_app.py        # Streamlit orchestration entry point
├── core/                   # Framework-independent processing
│   ├── pdf_reader.py       # PDF validation and text extraction
│   ├── skill_matcher.py    # Offline skill matching and priorities
│   ├── ats_engine.py       # Rule-based ATS readiness scoring
│   ├── intelligence_engine.py # Career-readiness insights and roadmap
│   └── html_report.py      # Standalone HTML report generation
├── ui/                     # Reusable Streamlit presentation layer
│   ├── hero.py             # Branded hero
│   ├── sidebar.py          # Workspace navigation
│   ├── cards.py            # Cards, badges, lists, and footer
│   ├── tabs.py             # Analysis dashboard and tabs
│   └── theme.py            # Shared theme-aware CSS
├── assets/                 # Reserved local visual assets
├── docs/                   # Architecture and product documentation
├── sample-data/            # Local example inputs
├── prompts/                # Prompt templates retained for future work
└── outputs/                # Generated local reports
```

## Responsibilities

- `core/` contains reusable processing logic with no Streamlit dependency.
- `config.py` centralizes product metadata, validation thresholds, and Streamlit session-state key names to prevent repeated magic strings.
- `core/ats_engine.py` evaluates ATS readiness using transparent text rules and weighted categories. It receives extracted resume text, the job description, and optional existing skill-analysis data; it returns the ATS score and status, category scores, checks, strengths, suggestions, keyword coverage, detected-section flags, redacted contact booleans, and text statistics.
- `core/intelligence_engine.py` converts resume text plus existing skill and ATS results into an executive summary, career-readiness score, evidence-based strengths, prioritized improvements, career-gap analysis, recommended actions, and a three-phase learning roadmap.
- `ui/` owns Streamlit rendering, navigation, layout, and styling.
- The reusable UI component layer in `ui/hero.py`, `ui/cards.py`, `ui/sidebar.py`, and `ui/theme.py` centralizes compact heroes, executive metrics, insight cards, priorities, actions, downloads, empty states, navigation, and design tokens.
- `ui/dashboard.py` composes the Dashboard in executive reading order: metrics, insight, analytics, priorities, actions, and privacy-safe analysis metadata. Core engines remain the sole source of analysis results.
- `ui/charts.py` separates deterministic chart-data preparation from Streamlit/Altair rendering. Its pure preparation helpers normalize scores, category percentages, skill coverage, priority gaps, and roadmap scope so edge cases can be unit tested without starting Streamlit.
- `ui/dashboard.py` composes the executive Dashboard and Results visual summaries from existing session-state analysis dictionaries. Charts visualize existing outputs only; they do not recalculate or alter analysis scores.
- `streamlit_app.py` validates web inputs, coordinates temporary-file processing, stores session results, and delegates rendering.
- `app.py` preserves the command-line workflow and delegates processing and report generation to `core/`.
- `assets/`, `sample-data/`, `prompts/`, and `outputs/` contain supporting project files rather than application logic.

## Data flow

### Streamlit application

1. The user uploads a PDF and enters a job description.
2. `streamlit_app.py` validates both inputs and writes the upload to a secure temporary PDF.
3. `core.pdf_reader.extract_resume_text()` validates and extracts resume text.
4. `core.skill_matcher.analyze_skill_match()` compares resume evidence with required job skills.
5. `core.ats_engine.analyze_ats_readiness()` reuses the skill result and evaluates eight weighted categories.
6. `core.intelligence_engine.generate_resume_intelligence()` combines the skill and ATS evidence into career insights.
7. The temporary PDF is deleted in a `finally` block.
8. Skill, ATS, and intelligence results are stored together in Streamlit session state.
9. The Dashboard, Results, ATS Review, Resume Intelligence, and Learning Roadmap views read those persisted dictionaries and render the appropriate cards, charts, and detailed evidence.

### Visualization flow

1. Skill, ATS, and intelligence engines remain the source of truth for every score and recommendation.
2. `streamlit_app.py` passes persisted session-state results to page renderers.
3. Pure helpers in `ui/charts.py` convert those dictionaries into bounded, display-ready records without changing the underlying formulas.
4. Chart renderers use Streamlit and Altair to present score comparisons, normalized ATS categories, skill coverage, priority gaps, readiness, and roadmap scope.
5. Empty or zero-valued inputs produce safe empty states instead of division errors or misleading graphics.

The presentation layer deliberately keeps analysis and visualization separate: `core/` calculates results, while `ui/` only prepares and displays them.

### Download Center and preferences

The Download Center reads the current skill-analysis dictionary from session state. Text content is generated in memory; the established HTML generator uses a temporary file that is deleted immediately after reading. PDF export remains informational and unavailable. Uploaded resume files are never retained for report downloads.

The functional `compact_hero` display preference is stored only in Streamlit session state. It does not affect scores or persist to a database.

### ATS scoring categories

- Contact Information: 10 points
- Professional Summary: 10 points
- Skills Section: 15 points
- Work Experience: 20 points
- Education: 10 points
- Job Keyword Coverage: 20 points
- Measurable Achievements: 10 points
- ATS Readability: 5 points

The engine works only with extracted text. It does not claim to inspect visual formatting, does not expose contact values, and does not represent the behavior of any specific applicant tracking system.

### Career-readiness scoring

The Resume Intelligence Engine uses this deterministic formula:

```text
Career Readiness = (Skill Match × 0.45) + (ATS Readiness × 0.35) + Evidence Quality
```

Evidence Quality contributes up to 20 points. It is calculated proportionally from existing ATS category scores:

- Measurable Achievements: 5 points
- Work Experience: 5 points
- Education: 3 points
- Professional Summary: 3 points
- Skills Section: 2 points
- ATS Readability: 2 points

The result is rounded and clamped between 0 and 100. Neither the skill-match nor ATS formulas are changed.

### Intelligence limitations

- Conclusions depend on successfully extracted PDF text.
- Skill phrase detection does not prove proficiency.
- Missing evidence may use wording outside the configured rule set.
- Visual formatting cannot be fully evaluated from extracted text.
- Results are guidance and do not guarantee employment or match a specific ATS product.

### Command-line application

1. `app.py` reads the existing extracted resume and sample job description.
2. `core.skill_matcher.analyze_skill_match()` creates the analysis result.
3. `app.py` writes the text report.
4. `core.html_report.generate_html_report()` writes the HTML report.

All current analysis is local and offline.

## Testing strategy

The standard-library `unittest` suite separates focused engine tests from an offline workflow smoke test. PDF tests generate lightweight temporary PDFs. Skill tests protect alias boundaries and determinism. Report tests verify HTML escaping, stable text headings, Unicode handling, and privacy-safe output. Chart tests exercise pure data preparation rather than Streamlit rendering.

All files under `tests/fixtures/` are synthetic and contain no real resume or contact data. Binary resume fixtures are generated temporarily instead of committed.

`tests/test_offline_workflow.py` validates the in-process path from synthetic resume and job-description text through skill matching, ATS readiness, resume intelligence, chart preparation, and HTML/text report generation. Active pipeline modules contain no network client.

The read-only `scripts/validate_release.py` checks required files, compiles Python sources, runs the full suite, verifies exact dependency pins, checks tracked secret filenames, confirms documentation, and verifies Streamlit startup does not depend on generated output files. Any failed gate produces a nonzero exit code.
