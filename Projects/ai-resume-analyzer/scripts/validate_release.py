"""Validate the NEXUS AI release candidate without modifying it."""

from __future__ import annotations

import compileall
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parents[1]
REQUIRED_FILES = (
    "README.md", "requirements.txt", "requirements-dev.txt", "config.py",
    "app.py", "streamlit_app.py", "core/pdf_reader.py", "core/skill_matcher.py",
    "core/ats_engine.py", "core/intelligence_engine.py", "core/html_report.py",
    "core/reporting.py", "docs/architecture.md", "docs/roadmap.md",
    "docs/release-checklist.md", "docs/code-quality-audit.md",
)
SECRET_NAMES = {".env", "secrets.toml", "credentials.json", "service-account.json"}
PINNED_REQUIREMENT = re.compile(r"^[A-Za-z0-9_.-]+==[^=\s]+$")


def check_required_files() -> list[str]:
    """Return messages for required release files that are missing."""
    return [f"Missing required file: {name}" for name in REQUIRED_FILES if not (PROJECT_ROOT / name).is_file()]


def check_pinned_requirements() -> list[str]:
    """Return messages for unpinned direct runtime dependencies."""
    lines = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    dependencies = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if not dependencies:
        return ["requirements.txt contains no runtime dependencies."]
    return [f"Runtime dependency is not exactly pinned: {line}" for line in dependencies if not PINNED_REQUIREMENT.fullmatch(line)]


def check_tracked_secrets() -> list[str]:
    """Return messages for obvious secret files tracked beneath the project."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(REPOSITORY_ROOT), "ls-files", "--", str(PROJECT_ROOT.relative_to(REPOSITORY_ROOT))],
            check=True, capture_output=True, text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        return [f"Unable to inspect tracked files for secrets: {error}"]
    return [f"Obvious secret file is tracked: {name}" for name in completed.stdout.splitlines() if Path(name).name.lower() in SECRET_NAMES]


def check_startup_independence() -> list[str]:
    """Ensure the web entry point does not require generated output artifacts."""
    source = (PROJECT_ROOT / "streamlit_app.py").read_text(encoding="utf-8").lower()
    return ["Streamlit startup references the generated outputs directory."] if "outputs/" in source or '"outputs"' in source else []


def run_tests() -> tuple[bool, str]:
    """Run the complete unittest suite and return success plus combined output."""
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(PROJECT_ROOT / "tests"), "-v"],
        cwd=PROJECT_ROOT, capture_output=True, text=True,
    )
    return completed.returncode == 0, completed.stdout + completed.stderr


def main() -> int:
    """Run every release gate and return a shell-compatible status code."""
    failures = check_required_files()
    if not failures:
        failures.extend(check_pinned_requirements())
    failures.extend(check_tracked_secrets())
    failures.extend(check_startup_independence())

    compiled = compileall.compile_dir(PROJECT_ROOT, quiet=1, force=True)
    if not compiled:
        failures.append("One or more Python files failed compilation.")

    tests_passed, test_output = run_tests()
    if not tests_passed:
        failures.append("The unittest suite failed.\n" + test_output)

    print("NEXUS AI — RELEASE VALIDATION")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Compilation: {'PASS' if compiled else 'FAIL'}")
    print(f"Unit tests: {'PASS' if tests_passed else 'FAIL'}")
    print(f"Required files: {'PASS' if not check_required_files() else 'FAIL'}")
    print(f"Pinned dependencies: {'PASS' if not check_pinned_requirements() else 'FAIL'}")
    print(f"Tracked-secret check: {'PASS' if not check_tracked_secrets() else 'FAIL'}")
    print(f"Startup independence: {'PASS' if not check_startup_independence() else 'FAIL'}")
    if failures:
        print("\nRELEASE VALIDATION: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nRELEASE VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
