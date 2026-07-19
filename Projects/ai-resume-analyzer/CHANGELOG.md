# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project intends to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) after the final 1.0.0 release.

## [1.0.0-rc.1] - 2026-07-20

### Added

- Offline PDF resume extraction and alias-aware skill matching.
- Rule-based ATS readiness and resume intelligence engines.
- Career-gap priorities, recommendations, and a three-phase learning roadmap.
- Modular Streamlit dashboard, analytics views, and HTML/text downloads.
- Release validation script and synthetic test fixtures.

### Changed

- Unified official product branding across the application and generated reports.
- Updated all visible version labels to Version 1.0 Release Candidate.
- Refactored processing, reporting, visualization, and UI into modular layers.
- Centralized application metadata, validation limits, and session-state keys.
- Pinned direct runtime dependencies for reproducible release validation.

### Fixed

- Prevented partial-word skill alias matches.
- Added controlled handling for missing, invalid, encrypted, blank, and image-only PDFs.
- Ensured temporary uploads and generated temporary reports are deleted.

### Documentation

- Added architecture, code-quality audit, release checklist, governance, security, and contribution guidance.
- Updated setup, privacy, testing, and offline-workflow documentation.

### Testing

- Expanded the standard-library suite to 59 tests.
- Added PDF, alias-boundary, report-security, text-report, edge-case, and end-to-end offline workflow coverage.
