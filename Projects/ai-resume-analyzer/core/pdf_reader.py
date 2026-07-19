"""Utilities for extracting clean text from resume PDFs."""

import re
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class InvalidPDFError(ValueError):
    """Raised when a file cannot be read as a valid PDF."""


class EncryptedPDFError(ValueError):
    """Raised when a PDF is encrypted and cannot be processed."""


class NoExtractableTextError(ValueError):
    """Raised when a PDF contains no extractable text."""


def extract_resume_text(pdf_path: str | Path) -> str:
    """Extract and clean text from every page of a resume PDF."""
    path = Path(pdf_path)

    if not path.is_file():
        raise FileNotFoundError(f"Resume PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Resume file must have a .pdf extension: {path}")

    try:
        reader = PdfReader(path)
    except (PdfReadError, OSError) as error:
        raise InvalidPDFError(f"Invalid PDF file: {path}") from error

    if reader.is_encrypted:
        raise EncryptedPDFError(f"Encrypted PDFs are not supported: {path}")

    try:
        page_text = [page.extract_text() or "" for page in reader.pages]
    except PdfReadError as error:
        raise InvalidPDFError(f"Invalid PDF file: {path}") from error

    extracted_text = "\n\n".join(page_text)
    extracted_text = extracted_text.replace("\r\n", "\n").replace("\r", "\n")
    extracted_text = "\n".join(line.rstrip() for line in extracted_text.splitlines())
    extracted_text = re.sub(r"\n{3,}", "\n\n", extracted_text).strip()

    if not extracted_text:
        raise NoExtractableTextError(f"PDF contains no extractable text: {path}")

    return extracted_text
