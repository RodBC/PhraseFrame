from phraseframe.adapters.documents import DocumentExtractionService
from phraseframe.services.library import LibraryService, metadata_payload


def test_metadata_payload_returns_chapter_metadata_only() -> None:
    service = LibraryService(DocumentExtractionService())
    document = service.extract(b"Chapter one.\n\nChapter two.", "notes.txt")
    payload = metadata_payload(document, chapter_index=0, text="Chapter one.")
    assert payload["text"] == "Chapter one."
    assert payload["chapters"][0]["title"] == "Full text"
    assert "text" not in payload["chapters"][0]
