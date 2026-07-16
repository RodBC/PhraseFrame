import pytest

from phraseframe.adapters.documents import DocumentExtractionService
from phraseframe.adapters.pdf import PdfDocumentExtractor, build_sample_pdf


def test_extracts_pdf_with_chapters() -> None:
    adapter = PdfDocumentExtractor()
    document = adapter.extract(build_sample_pdf(), "sample.pdf")
    assert document.source_format == "pdf"
    assert len(document.chapters) == 2
    assert "PhraseFrame reads PDFs" in document.text_for_chapter(0)
    assert "Each section can be selected" in document.text_for_chapter(1)


@pytest.mark.parametrize(
    ("content", "filename", "message"),
    [
        (b"", "empty.pdf", "empty"),
        (b"not a pdf", "notes.pdf", "does not appear to be a PDF"),
        (b"%PDF", "notes.txt", "Only .pdf"),
    ],
)
def test_rejects_invalid_pdf(content: bytes, filename: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        PdfDocumentExtractor().extract(content, filename)


def test_document_service_routes_by_extension() -> None:
    service = DocumentExtractionService()
    text_document = service.extract(b"Hello from text.", "notes.txt")
    pdf_document = service.extract(build_sample_pdf(), "book.pdf")
    assert text_document.source_format == "txt"
    assert text_document.full_text == "Hello from text."
    assert pdf_document.source_format == "pdf"
    assert len(pdf_document.chapters) == 2
