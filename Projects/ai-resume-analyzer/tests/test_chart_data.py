"""Tests for pure analytics chart-data preparation."""

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.charts import prepare_ats_breakdown_data
from ui.charts import prepare_priority_gap_data, prepare_roadmap_scope_data
from ui.charts import prepare_score_comparison_data, prepare_skill_coverage_data


class ChartDataTests(unittest.TestCase):
    def test_score_data_is_bounded(self) -> None:
        rows = prepare_score_comparison_data(
            {"match_score": -15},
            {"ats_score": 140},
            {"readiness_score": "72.5"},
        )
        self.assertEqual([row["score"] for row in rows], [0, 100, 72.5])

    def test_missing_scores_default_safely(self) -> None:
        rows = prepare_score_comparison_data(None, {}, None)
        self.assertEqual([row["score"] for row in rows], [0, 0, 0])

    def test_ats_category_percentages(self) -> None:
        rows = prepare_ats_breakdown_data(
            {
                "category_scores": {
                    "Contact Information": {"score": 5, "max_score": 10},
                    "Work Experience": {"score": 15, "max_score": 20},
                }
            }
        )
        by_category = {row["category"]: row for row in rows}
        self.assertEqual(by_category["Contact Information"]["percentage"], 50)
        self.assertEqual(by_category["Work Experience"]["percentage"], 75)

    def test_zero_maximum_does_not_divide(self) -> None:
        rows = prepare_ats_breakdown_data(
            {"category_scores": {"Education": {"score": 5, "max_score": 0}}}
        )
        education = next(row for row in rows if row["category"] == "Education")
        self.assertEqual(education["percentage"], 0)
        self.assertEqual(education["earned"], 0)

    def test_skill_coverage_handles_zero_required(self) -> None:
        coverage = prepare_skill_coverage_data(
            {"required_skills": [], "matched_skills": [], "missing_skills": []}
        )
        self.assertEqual(coverage["total_required_count"], 0)
        self.assertEqual(coverage["coverage_percentage"], 0)

    def test_priority_counts_are_accurate(self) -> None:
        rows = prepare_priority_gap_data(
            {
                "areas_for_improvement": [
                    {"priority": "High"},
                    {"priority": "High"},
                    {"priority": "Medium"},
                    {"priority": "Unknown"},
                ]
            }
        )
        self.assertEqual(
            {row["priority"]: row["count"] for row in rows},
            {"High": 2, "Medium": 1, "Low": 0},
        )

    def test_roadmap_phase_summaries(self) -> None:
        rows = prepare_roadmap_scope_data(
            [
                {
                    "phase": "Phase 1",
                    "title": "Foundation",
                    "estimated_duration": "2 weeks",
                    "topics": ["SQL", "Excel"],
                    "deliverables": ["Exercises"],
                }
            ]
        )
        self.assertEqual(rows[0]["topic_count"], 2)
        self.assertEqual(rows[0]["deliverable_count"], 1)
        self.assertEqual(rows[0]["estimated_duration"], "2 weeks")


if __name__ == "__main__":
    unittest.main()
