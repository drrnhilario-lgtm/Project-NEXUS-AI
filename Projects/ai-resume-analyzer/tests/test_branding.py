"""Consistency tests for centralized NEXUS AI release branding."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config


class BrandingConsistencyTests(unittest.TestCase):
    def test_official_brand_metadata_is_centralized(self) -> None:
        self.assertEqual(config.PRODUCT_NAME, "NEXUS AI Resume Intelligence Platform")
        self.assertEqual(config.SHORT_PRODUCT_NAME, "NEXUS AI")
        self.assertEqual(
            config.TAGLINE,
            "AI-Powered Resume Intelligence for Smarter Career Decisions",
        )
        self.assertEqual(config.VERSION, "1.0.0")
        self.assertEqual(config.RELEASE_STAGE, "Release Candidate")
        self.assertEqual(config.AUTHOR_NAME, "Darren Hilario")
        self.assertEqual(config.COPYRIGHT_YEAR, "2026")

    def test_old_beta_labels_are_absent_from_project_text(self) -> None:
        checked_extensions = {".py", ".md", ".txt", ".html"}
        for path in PROJECT_ROOT.rglob("*"):
            if (
                not path.is_file()
                or path.resolve() == Path(__file__).resolve()
                or path.suffix.lower() not in checked_extensions
            ):
                continue
            with self.subTest(path=path.relative_to(PROJECT_ROOT)):
                content = path.read_text(encoding="utf-8", errors="ignore").lower()
                self.assertNotIn("v1.0 beta", content)
                self.assertNotIn("version 1.0 beta", content)

    def test_primary_brand_surfaces_use_config_constants(self) -> None:
        expected_imports = {
            "ui/hero.py": ("SHORT_PRODUCT_NAME", "TAGLINE"),
            "ui/sidebar.py": ("SHORT_PRODUCT_NAME", "SHORT_VERSION_LABEL"),
            "ui/cards.py": ("PRODUCT_NAME", "VERSION_LABEL"),
            "core/html_report.py": ("PRODUCT_NAME", "TAGLINE"),
            "core/reporting.py": ("PRODUCT_NAME", "TAGLINE"),
        }
        for relative_path, names in expected_imports.items():
            source = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(path=relative_path):
                for name in names:
                    self.assertIn(name, source)


if __name__ == "__main__":
    unittest.main()
