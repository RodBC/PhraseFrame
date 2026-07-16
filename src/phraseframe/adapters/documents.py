"""Format-aware document extraction."""

from pathlib import Path

from phraseframe.adapters.pdf import PdfDocumentExtractor
from phraseframe.adapters.text import TextDocumentExtractor
from phraseframe.core.models import DocumentChapter, ExtractedDocument


class DocumentExtractionService:
    """Route uploads to the correct adapter by file extension."""

    max_bytes = max(TextDocumentExtractor.max_bytes, PdfDocumentExtractor.max_bytes)

    def __init__(self) -> None:
        self._text = TextDocumentExtractor()
        self._pdf = PdfDocumentExtractor()

    def extract(self, content: bytes, filename: str) -> ExtractedDocument:
        suffix = Path(filename).suffix.lower()
        if suffix == ".txt":
            text = self._text.extract(content, filename)
            return ExtractedDocument(
                title=Path(filename).stem,
                pages=(text,),
                chapters=(DocumentChapter("Full text", 0, 1),),
                source_format="txt",
            )
        if suffix == ".pdf":
            return self._pdf.extract(content, filename)
        raise ValueError("Supported uploads: .txt and .pdf.")
