"""Tests for deterministic, privacy-safe text report generation."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from core.reporting import build_text_report


class TextReportTests(unittest.TestCase):
    def test_complete_report_has_stable_headings(self) -> None:
        result = {"match_score": 50, "required_skills": ["Excel", "Python"], "matched_skills": ["Excel"], "missing_skills": ["Python"], "skill_priorities": {"Excel": "Medium", "Python": "High"}, "recommendations": {"Python": "Build a project."}}
        report = build_text_report(result)
        for heading in ("RESUME SKILL MATCH REPORT", "Required Skills:", "Matched Skills:", "Missing Skills:", "RECOMMENDATIONS"):
            self.assertIn(heading, report)
        self.assertNotIn("{'", report)

    def test_missing_optional_sections_and_empty_recommendations(self) -> None:
        report = build_text_report({"match_score": 0})
        self.assertGreaterEqual(report.count("- None"), 3); self.assertTrue(report.endswith("None"))

    def test_unicode_is_preserved_and_contact_data_not_added(self) -> None:
        result = {"match_score": 0, "required_skills": ["Analýsis ₱"], "matched_skills": [], "missing_skills": ["Analýsis ₱"], "skill_priorities": {}, "recommendations": {}}
        report = build_text_report(result)
        self.assertIn("Analýsis ₱", report); self.assertNotIn("someone@example.com", report); self.assertNotIn("+63 917", report)


if __name__ == "__main__": unittest.main()
