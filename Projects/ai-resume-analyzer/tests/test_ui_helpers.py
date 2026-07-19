"""Unit tests for pure executive-dashboard formatting helpers."""

import sys
import unittest
from types import SimpleNamespace

sys.modules.setdefault("streamlit", SimpleNamespace())

from ui.cards import clamp_percentage, empty_state_content, normalize_actions
from ui.cards import normalize_download_metadata, safe_metric_value, safe_priority_title


class UIHelperTests(unittest.TestCase):
    def test_percentage_is_clamped(self):
        self.assertEqual(clamp_percentage(-8), 0)
        self.assertEqual(clamp_percentage(108), 100)
        self.assertEqual(clamp_percentage(72.5), 72.5)

    def test_missing_metric_value_is_safe(self):
        self.assertEqual(safe_metric_value(None), "—")
        self.assertEqual(safe_metric_value(""), "—")

    def test_long_priority_title_is_compacted(self):
        result = safe_priority_title("A" * 100, limit=30)
        self.assertEqual(len(result), 30)
        self.assertTrue(result.endswith("…"))

    def test_empty_actions_return_safe_default(self):
        self.assertEqual(normalize_actions(None), [])
        self.assertEqual(normalize_actions(["", " Review results "]), ["Review results"])

    def test_download_metadata_is_valid(self):
        metadata = normalize_download_metadata({"title": "HTML", "status": "Available"})
        self.assertEqual(metadata["status"], "Available")
        self.assertEqual(metadata["mime"], "application/octet-stream")

    def test_status_label_is_preserved(self):
        metadata = normalize_download_metadata({"status": "Planned"})
        self.assertEqual(metadata["status"], "Planned")

    def test_empty_state_has_fallback_text(self):
        title, message = empty_state_content()
        self.assertTrue(title)
        self.assertIn("New Analysis", message)


if __name__ == "__main__":
    unittest.main()
