"""Security regression tests for generated HTML reports."""

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from core.html_report import generate_html_report


class HTMLReportSecurityTests(unittest.TestCase):
    def test_dynamic_content_is_escaped_and_markup_remains(self) -> None:
        malicious = '<script>alert("x")</script> & <b>skill</b>\'s “Unicode” ₱ ' + "X" * 300
        result = {
            "match_score": 50,
            "required_skills": [malicious],
            "matched_skills": [malicious],
            "missing_skills": [],
            "skill_priorities": {malicious: "High"},
            "match_evidence": {malicious: malicious},
            "recommendations": {},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.html"
            generate_html_report(result, path)
            html = path.read_text(encoding="utf-8")
        self.assertNotIn('<script>alert("x")</script>', html)
        self.assertNotIn("<b>skill</b>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&amp;", html)
        self.assertIn("&#x27;", html)
        self.assertIn("₱", html)
        self.assertIn('<section class="panel">', html)
        self.assertTrue(html.startswith("<!DOCTYPE html>")); self.assertIn("</html>", html)

    def test_malicious_recommendation_is_escaped(self) -> None:
        payload = '<img src=x onerror="alert(1)">'
        result = {"match_score": 0, "required_skills": ["Python"], "matched_skills": [], "missing_skills": ["Python"], "skill_priorities": {"Python": "High"}, "match_evidence": {}, "recommendations": {"Python": payload}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.html"; generate_html_report(result, path); html = path.read_text(encoding="utf-8")
        self.assertNotIn(payload, html); self.assertIn("&lt;img", html)


if __name__ == "__main__": unittest.main()
