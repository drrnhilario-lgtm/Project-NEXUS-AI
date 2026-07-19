"""Unit tests for the offline ATS readiness engine."""

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.ats_engine import analyze_ats_readiness
from core.skill_matcher import analyze_skill_match


COMPLETE_RESUME = """
Jordan Lee
jordan@example.com | +63 917 123 4567 | Manila, Philippines
https://linkedin.com/in/jordanlee

PROFESSIONAL SUMMARY
Data analyst with five years of professional experience supporting operations,
analyzing customer and sales data, building clear dashboards, improving reporting
processes, and communicating practical recommendations to managers and technical
teams across fast-moving service organizations.

SKILLS
Python, SQL, Excel, Power BI, Tableau, Data Analysis, Data Visualization

WORK EXPERIENCE
Data Analyst - Bright Retail Inc. | 2021 - 2025
- Analyzed weekly sales records and built automated dashboards.
- Reduced reporting time by 35% and processed 20 reports per week.
- Improved customer satisfaction to 95% by resolving data quality issues.

EDUCATION
Bachelor of Science in Information Technology
Manila State University | 2020
"""

JOB_DESCRIPTION = """
We require a Data Analyst with strong knowledge of Python and SQL.
Responsibilities include data analysis, Excel reporting, Power BI dashboards,
data visualization, and clear communication with stakeholders.
"""


class ATSReadinessTests(unittest.TestCase):
    def analyze(self, resume: str, job: str = JOB_DESCRIPTION) -> dict:
        skill_result = analyze_skill_match(resume, job)
        return analyze_ats_readiness(resume, job, skill_result)

    def test_complete_resume(self) -> None:
        result = self.analyze(COMPLETE_RESUME)
        self.assertGreaterEqual(result["ats_score"], 70)
        self.assertTrue(result["contact_details"]["email_found"])
        self.assertTrue(result["detected_sections"]["work_experience"])
        self.assertGreater(result["statistics"]["passed_check_count"], 0)

    def test_resume_missing_contact_details(self) -> None:
        resume = "\n".join(COMPLETE_RESUME.splitlines()[5:])
        result = self.analyze(resume)
        self.assertFalse(result["contact_details"]["email_found"])
        self.assertFalse(result["contact_details"]["phone_found"])
        self.assertLess(result["category_scores"]["Contact Information"]["score"], 10)

    def test_resume_without_measurable_achievements(self) -> None:
        resume = """
SUMMARY
Experienced support professional focused on customer service and accurate documentation.
SKILLS
Excel, Communication, Customer Service, Technical Support, Problem Solving
EXPERIENCE
Support Specialist - Service Company
- Assisted customers and documented cases.
EDUCATION
Bachelor Degree, City College
"""
        result = self.analyze(resume)
        self.assertEqual(
            result["category_scores"]["Measurable Achievements"]["score"], 0
        )

    def test_resume_with_no_recognizable_sections(self) -> None:
        result = self.analyze(
            "Jordan supports customers, solves issues, and documents service cases."
        )
        self.assertEqual(sum(result["detected_sections"].values()), 0)
        self.assertIn(
            "Use standard section headings that ATS software can recognize.",
            result["improvement_suggestions"],
        )

    def test_empty_resume(self) -> None:
        result = self.analyze("")
        self.assertEqual(result["ats_score"], 0)
        self.assertEqual(result["statistics"]["word_count"], 0)

    def test_zero_required_job_skills(self) -> None:
        result = self.analyze(
            COMPLETE_RESUME,
            "Join our friendly organization and contribute to a growing team.",
        )
        coverage = result["keyword_coverage"]
        self.assertEqual(coverage["total_required_keyword_count"], 0)
        self.assertEqual(coverage["keyword_coverage_percentage"], 0)
        self.assertEqual(coverage["score"], 0)

    def test_score_remains_between_zero_and_one_hundred(self) -> None:
        for resume in ("", COMPLETE_RESUME, COMPLETE_RESUME * 3):
            with self.subTest(length=len(resume)):
                score = self.analyze(resume)["ats_score"]
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)


if __name__ == "__main__":
    unittest.main()
