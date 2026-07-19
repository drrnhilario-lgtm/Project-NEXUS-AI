"""End-to-end and edge-case tests for the complete offline workflow."""

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))
FIXTURES = Path(__file__).resolve().parent / "fixtures"

from core.ats_engine import analyze_ats_readiness
from core.intelligence_engine import generate_resume_intelligence
from core.reporting import build_html_report_bytes, build_text_report
from core.skill_matcher import analyze_skill_match
from ui.charts import prepare_ats_breakdown_data, prepare_score_comparison_data
from ui.charts import prepare_skill_coverage_data


def run_pipeline(resume: str, job: str) -> tuple[dict, dict, dict]:
    """Run the same deterministic engines used by the Streamlit entry point."""
    skills = analyze_skill_match(resume, job)
    ats = analyze_ats_readiness(resume, job, skills)
    intelligence = generate_resume_intelligence(resume, job, skills, ats)
    return skills, ats, intelligence


class OfflineWorkflowTests(unittest.TestCase):
    def test_complete_pipeline_is_consistent_and_private(self) -> None:
        resume = (FIXTURES / "sample_resume_data_analyst.txt").read_text(encoding="utf-8")
        job = (FIXTURES / "sample_job_description_data_analyst.txt").read_text(encoding="utf-8")
        skills, ats, intelligence = run_pipeline(resume, job)
        self.assertIsInstance(skills, dict); self.assertIsInstance(ats, dict); self.assertIsInstance(intelligence, dict)
        self.assertEqual(set(skills["matched_skills"]) | set(skills["missing_skills"]), set(skills["required_skills"]))
        self.assertFalse(set(skills["matched_skills"]) & set(skills["missing_skills"]))
        for score in (skills["match_score"], ats["ats_score"], intelligence["readiness_score"]):
            self.assertGreaterEqual(score, 0); self.assertLessEqual(score, 100)
        self.assertEqual(len(prepare_score_comparison_data(skills, ats, intelligence)), 3)
        self.assertEqual(len(prepare_ats_breakdown_data(ats)), 8)
        self.assertEqual(prepare_skill_coverage_data(skills)["total_required_count"], len(skills["required_skills"]))
        self.assertTrue(build_html_report_bytes(skills)); self.assertTrue(build_text_report(skills))
        persisted = json.dumps((skills, ats, intelligence))
        self.assertNotIn("alex@example.test", persisted); self.assertNotIn("+63 900 000 0000", persisted)
        if skills["missing_skills"]:
            self.assertTrue(intelligence["priority_focus"])

    def test_empty_inputs_fail_safely(self) -> None:
        skills, ats, intelligence = run_pipeline("", "")
        self.assertEqual(skills["required_skills"], []); self.assertEqual(ats["ats_score"], 0)
        self.assertGreaterEqual(intelligence["readiness_score"], 0)

    def test_each_empty_input_is_controlled(self) -> None:
        for resume, job in (("Python experience", ""), ("", "Python required")):
            with self.subTest(resume=bool(resume), job=bool(job)):
                skills, ats, intelligence = run_pipeline(resume, job)
                self.assertIsInstance(skills, dict); self.assertIsInstance(ats, dict); self.assertIsInstance(intelligence, dict)

    def test_no_sections_no_skills_and_no_required_skills(self) -> None:
        skills, ats, _ = run_pipeline("Friendly graduate seeking a first role.", "Join our collaborative team.")
        self.assertEqual(skills["required_skills"], []); self.assertEqual(sum(ats["detected_sections"].values()), 0)

    def test_fresh_graduate_and_extensive_experience(self) -> None:
        fresh = "EDUCATION\nBachelor Degree, Example University 2026\nSKILLS\nExcel Communication"
        extensive = ("WORK EXPERIENCE\nData Analyst - Example Corp | 2000 - 2025\n- Analyzed data and improved KPI by 20%.\n" * 80) + "SKILLS\nPython SQL Excel"
        for resume in (fresh, extensive):
            with self.subTest(length=len(resume)):
                _, ats, intelligence = run_pipeline(resume, "Python SQL Excel data analysis required")
                self.assertLessEqual(ats["ats_score"], 100); self.assertLessEqual(intelligence["readiness_score"], 100)

    def test_very_long_inputs_repeated_keywords_and_spacing(self) -> None:
        resume = ("  Python\n\n SQL\tExcel data analysis ₱50,000  \n" * 1000)
        job = ("Required Python, SQL, Excel, data analysis.\n" * 1000)
        skills, ats, intelligence = run_pipeline(resume, job)
        self.assertEqual(skills["match_score"], 100); self.assertLessEqual(ats["ats_score"], 100); self.assertLessEqual(intelligence["readiness_score"], 100)

    def test_customer_service_fixture_is_synthetic_and_usable(self) -> None:
        resume = (FIXTURES / "sample_resume_customer_service.txt").read_text(encoding="utf-8")
        job = (FIXTURES / "sample_job_description_fraud_analyst.txt").read_text(encoding="utf-8")
        skills, _, _ = run_pipeline(resume, job)
        self.assertIn("Communication", skills["matched_skills"]); self.assertIn("Fraud Detection", skills["missing_skills"])


if __name__ == "__main__": unittest.main()
