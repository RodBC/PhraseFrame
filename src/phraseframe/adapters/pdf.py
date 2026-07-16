"""PDF document adapter using PyMuPDF."""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

import fitz

from phraseframe.core.models import DocumentChapter, ExtractedDocument

_PAGE_NUMBER = re.compile(r"^\s*\d{1,4}\s*$")
_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w)")
_MULTI_BLANK = re.compile(r"\n{3,}")


class PdfDocumentExtractor:
    """Extract and clean text from PDF files with chapter detection."""

    max_bytes = 25_000_000

    def extract(self, content: bytes, filename: str) -> ExtractedDocument:
        if Path(filename).suffix.lower() != ".pdf":
            raise ValueError("Only .pdf files are supported.")
        if not content:
            raise ValueError("The selected file is empty.")
        if len(content) > self.max_bytes:
            raise ValueError("PDF files must be smaller than 25 MB.")
        if not content.startswith(b"%PDF"):
            raise ValueError("The selected file does not appear to be a PDF.")

        try:
            document = fitz.open(stream=content, filetype="pdf")
        except Exception as error:
            message = "The PDF could not be opened. It may be corrupted or encrypted."
            raise ValueError(message) from error

        try:
            pages = tuple(
                _clean_page_text(document.load_page(index).get_text("text"))
                for index in range(document.page_count)
            )
            if not any(page.strip() for page in pages):
                raise ValueError("No readable text was found in this PDF.")
            title = document.metadata.get("title") or Path(filename).stem
            chapters = _chapters_from_outline(document, len(pages))
            return ExtractedDocument(
                title=title.strip() or Path(filename).stem,
                pages=pages,
                chapters=chapters,
                source_format="pdf",
            )
        finally:
            document.close()


def _clean_page_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = _HYPHEN_BREAK.sub(r"\1\2", text)
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if _PAGE_NUMBER.match(stripped):
            continue
        lines.append(stripped)
    text = "\n".join(lines)
    text = _MULTI_BLANK.sub("\n\n", text)
    return text.strip()


def _chapters_from_outline(document: fitz.Document, page_count: int) -> tuple[DocumentChapter, ...]:
    outline = document.get_toc(simple=True)
    if not outline:
        return (DocumentChapter("Full document", 0, page_count),)

    entries: list[tuple[str, int]] = []
    for level, title, page in outline:
        if level != 1:
            continue
        page_index = max(0, min(page_count - 1, page - 1))
        cleaned_title = title.strip() or f"Section {len(entries) + 1}"
        if entries and entries[-1][1] == page_index:
            continue
        entries.append((cleaned_title, page_index))

    if not entries:
        for _level, title, page in outline:
            page_index = max(0, min(page_count - 1, page - 1))
            cleaned_title = title.strip() or f"Section {len(entries) + 1}"
            if entries and entries[-1][1] == page_index:
                continue
            entries.append((cleaned_title, page_index))

    chapters: list[DocumentChapter] = []
    for index, (title, page_start) in enumerate(entries):
        page_end = entries[index + 1][1] if index + 1 < len(entries) else page_count
        if page_end <= page_start:
            page_end = min(page_count, page_start + 1)
        chapters.append(DocumentChapter(title=title, page_start=page_start, page_end=page_end))
    return tuple(chapters)


def build_sample_pdf() -> bytes:
    """Create a tiny PDF fixture for tests."""

    document = fitz.open()
    first = document.new_page()
    first.insert_text((72, 72), "Chapter One\n\nPhraseFrame reads PDFs with chapter outlines.")
    second = document.new_page()
    second.insert_text((72, 72), "Chapter Two\n\nEach section can be selected before reading.")
    document.set_toc(
        [
            [1, "Chapter One", 1],
            [1, "Chapter Two", 2],
        ]
    )
    buffer = BytesIO()
    document.save(buffer)
    document.close()
    return buffer.getvalue()
