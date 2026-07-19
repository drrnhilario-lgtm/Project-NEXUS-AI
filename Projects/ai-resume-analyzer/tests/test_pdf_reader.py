"""Regression tests for safe PDF extraction."""

import tempfile
import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pypdf import PdfWriter

from core.pdf_reader import InvalidPDFError, NoExtractableTextError
from core.pdf_reader import extract_resume_text


def make_text_pdf(pages: list[str]) -> bytes:
    """Build a tiny standards-compliant PDF without external fixture packages."""
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>"]
    page_ids = [3 + index * 2 for index in range(len(pages))]
    objects.append(f'<< /Type /Pages /Kids [{" ".join(f"{item} 0 R" for item in page_ids)}] /Count {len(pages)} >>'.encode())
    font_id = 3 + len(pages) * 2
    for index, text in enumerate(pages):
        page_id = 3 + index * 2
        content_id = page_id + 1
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1")
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>".encode())
        objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(output)); output.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(output); output.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    output.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:]))
    output.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(output)


class PDFReaderTests(unittest.TestCase):
    def write_temp(self, data: bytes, suffix: str = ".pdf") -> Path:
        handle = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        handle.write(data); handle.close()
        return Path(handle.name)

    def test_valid_pdf_returns_string(self) -> None:
        result = extract_resume_text(self.write_temp(make_text_pdf(["Python resume"])))
        self.assertIsInstance(result, str)
        self.assertIn("Python resume", result)

    def test_multi_page_pdf_extracts_every_page(self) -> None:
        result = extract_resume_text(self.write_temp(make_text_pdf(["Page one", "Page two"])))
        self.assertIn("Page one", result); self.assertIn("Page two", result)

    def test_empty_pdf_is_controlled(self) -> None:
        writer = PdfWriter()
        path = self.write_temp(b"")
        with path.open("wb") as stream: writer.write(stream)
        with self.assertRaises(NoExtractableTextError): extract_resume_text(path)

    def test_blank_pages_are_controlled(self) -> None:
        writer = PdfWriter(); writer.add_blank_page(width=612, height=792)
        path = self.write_temp(b"")
        with path.open("wb") as stream: writer.write(stream)
        with self.assertRaises(NoExtractableTextError): extract_resume_text(path)

    def test_corrupt_pdf_is_controlled(self) -> None:
        with self.assertRaises(InvalidPDFError): extract_resume_text(self.write_temp(b"not a pdf"))

    def test_unsupported_extension(self) -> None:
        with self.assertRaises(ValueError): extract_resume_text(self.write_temp(b"data", ".txt"))

    def test_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError): extract_resume_text(Path(tempfile.gettempdir()) / "nexus-missing-test.pdf")

    def test_source_file_is_not_deleted_or_replaced(self) -> None:
        path = self.write_temp(make_text_pdf(["Stable source"])); before = path.read_bytes()
        extract_resume_text(path)
        self.assertTrue(path.exists()); self.assertEqual(path.read_bytes(), before)

    def test_failure_creates_no_neighbor_temporary_files(self) -> None:
        path = self.write_temp(b"broken")
        before = set(path.parent.iterdir())
        with self.assertRaises(InvalidPDFError): extract_resume_text(path)
        self.assertEqual(set(path.parent.iterdir()), before)


if __name__ == "__main__": unittest.main()
