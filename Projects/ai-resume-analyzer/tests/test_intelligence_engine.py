"""Unit tests for the offline Resume Intelligence Engine."""

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.ats_engine import analyze_ats_readiness
from core.intelligence_engine import generate_resume_intelligence
from core.skill_matcher import analyze_skill_match


STRONG_RESUME = """
Jordan Lee
jordan@example.com | +63 917 123 4567 | Manila, Philippines
https://linkedin.com/in/jordanlee

PROFESSIONAL SUMMARY
Data analyst with five years of professional experience using Python, SQL, Excel,
Power BI, Tableau, and data visualization to improve reporting, support business
decisions, communicate findings, and deliver accurate analysis across operations.

SKILLS
Python, SQL, Excel, Power BI, Tableau, Data Analysis, Data Visualization, Communication

WORK EXPERIENCE
Data Analyst - Bright Retail Inc. | 2021 - 2025
- Analyzed sales data and created Power BI dashboards.
- Reduced reporting time by 35% and processed 20 reports per week.
- Improved customer satisfaction to 95% through accurate reporting.

EDUCATION
Bachelor of Science in Information Technology
Manila State University | 2020
"""

TARGET_JOB = """
Data Analyst required to use Python, SQL, Excel, Power BI, Tableau, data analysis,
data visualization, and communication to create reports and dashboards.
"""


def build_intelligence(resume: str, job: str) -> tuple[dict, dict, dict]:
    skills = analyze_skill_match(resume, job)
    ats = analyze_ats_readiness(resume, job, skills)
    intelligence = generate_resume_intelligence(resume, job, skills, ats)
    return skills, ats, intelligence


class ResumeIntelligenceTests(unittest.TestCase):
    def test_strong_candidate_profile(self) -> None:
        _, _, result = build_intelligence(STRONG_RESUME, TARGET_JOB)
        self.assertGreaterEqual(result["readiness_score"], 75)
        self.assertTrue(result["strengths"])
        self.assertEqual(len(result["learning_roadmap"]), 3)

    def test_low_skill_match_but_strong_ats(self) -> None:
        job = "Required n8n, Zapier, Make.com, OpenAI, APIs, and Automation experience."
        skills, ats, result = build_intelligence(STRONG_RESUME, job)
        self.assertLess(skills["match_score"], 40)
        self.assertGreater(ats["ats_score"], 40)
        self.assertLess(result["readiness_score"], ats["ats_score"])

    def test_strong_skill_match_but_weak_ats(self) -> None:
        resume = "Python SQL Excel Power BI Tableau data analysis data visualization communication"
        skills, ats, result = build_intelligence(resume, TARGET_JOB)
        self.assertEqual(skills["match_score"], 100)
        self.assertLess(ats["ats_score"], 40)
        self.assertGreater(result["readiness_score"], ats["ats_score"])

    def test_empty_or_minimal_input(self) -> None:
        _, _, result = build_intelligence("", "")
        self.assertGreaterEqual(result["readiness_score"], 0)
        self.assertEqual(result["career_gap"]["gap_level"], "Major")
        self.assertTrue(result["confidence_notes"])

    def test_no_missing_skills(self) -> None:
        skills, _, result = build_intelligence(STRONG_RESUME, TARGET_JOB)
        self.assertEqual(skills["missing_skills"], [])
        self.assertIsInstance(result["priority_focus"], list)
        self.assertEqual(len(result["learning_roadmap"]), 3)

    def test_no_measurable_achievements(self) -> None:
        resume = """
SUMMARY
Experienced Python and SQL analyst supporting business reporting and communication.
SKILLS
Python, SQL, Excel, Communication, Data Analysis
EXPERIENCE
Data Analyst - Example Company
- Prepared reports and supported stakeholders.
EDUCATION
Bachelor Degree, Example University
"""
        _, ats, result = build_intelligence(resume, "Python SQL data analysis role")
        self.assertEqual(
            ats["category_scores"]["Measurable Achievements"]["score"], 0
        )
        titles = [item["title"] for item in result["areas_for_improvement"]]
        self.assertIn("Improve Measurable Achievements", titles)

    def test_readiness_score_stays_between_zero_and_one_hundred(self) -> None:
        for resume, job in (("", ""), ("Python", "Python"), (STRONG_RESUME, TARGET_JOB)):
            with self.subTest(resume_length=len(resume)):
                _, _, result = build_intelligence(resume, job)
                self.assertGreaterEqual(result["readiness_score"], 0)
                self.assertLessEqual(result["readiness_score"], 100)

    def test_output_contains_all_required_keys(self) -> None:
        _, _, result = build_intelligence(STRONG_RESUME, TARGET_JOB)
        expected = {
            "executive_summary",
            "readiness_score",
            "readiness_status",
            "strengths",
            "areas_for_improvement",
            "career_gap",
            "priority_focus",
            "recommended_actions",
            "learning_roadmap",
            "confidence_notes",
        }
        self.assertEqual(set(result), expected)


if __name__ == "__main__":
    unittest.main()
