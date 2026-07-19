"""Boundary and determinism tests for alias-aware skill matching."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from core.skill_matcher import analyze_skill_match


class SkillMatcherBoundaryTests(unittest.TestCase):
    def test_excel_does_not_match_excellent(self) -> None:
        self.assertNotIn("Excel", analyze_skill_match("excellent service", "excellent service")["required_skills"])

    def test_single_letter_skills_are_not_invented(self) -> None:
        result = analyze_skill_match("career creator", "creative trainer")
        self.assertNotIn("R", result["required_skills"]); self.assertNotIn("C", result["required_skills"]); self.assertNotIn("AI", result["required_skills"])

    def test_sql_does_not_match_partial_string(self) -> None:
        self.assertNotIn("SQL", analyze_skill_match("sequelized", "nosqlish tooling")["required_skills"])

    def test_power_bi_variations_match(self) -> None:
        for phrase in ("Power BI", "powerbi"):
            with self.subTest(phrase=phrase):
                result = analyze_skill_match(phrase, f"Required: {phrase}.")
                self.assertIn("Power BI", result["matched_skills"])

    def test_microsoft_excel_maps_to_excel(self) -> None:
        result = analyze_skill_match("MICROSOFT EXCEL", "Microsoft Excel required")
        self.assertEqual(result["matched_skills"], ["Excel"])

    def test_unsupported_structured_query_language_is_not_invented(self) -> None:
        result = analyze_skill_match("Structured Query Language", "Structured Query Language")
        self.assertNotIn("SQL", result["required_skills"])

    def test_case_and_punctuation_do_not_block_matches(self) -> None:
        result = analyze_skill_match("(PYTHON), [sql].", "python; SQL!")
        self.assertEqual(result["matched_skills"], ["Python", "SQL"])

    def test_duplicate_aliases_count_one_canonical_skill(self) -> None:
        result = analyze_skill_match("Excel spreadsheet", "Excel, Microsoft Excel, spreadsheets")
        self.assertEqual(result["required_skills"].count("Excel"), 1)

    def test_lists_are_deterministic_and_disjoint(self) -> None:
        result = analyze_skill_match("Python SQL", "Tableau, SQL, Python, Excel")
        self.assertEqual(result["required_skills"], sorted(result["required_skills"]))
        self.assertEqual(result["matched_skills"], sorted(result["matched_skills"]))
        self.assertEqual(result["missing_skills"], sorted(result["missing_skills"]))
        self.assertFalse(set(result["matched_skills"]) & set(result["missing_skills"]))
        self.assertEqual(set(result["matched_skills"]) | set(result["missing_skills"]), set(result["required_skills"]))


if __name__ == "__main__": unittest.main()
