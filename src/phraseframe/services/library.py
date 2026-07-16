"""Library orchestration for uploads, resume, and progress."""

from dataclasses import asdict, dataclass

from phraseframe.adapters.documents import DocumentExtractionService
from phraseframe.core.models import ExtractedDocument
from phraseframe.db.store import LibraryEntry, LibraryStore, ReadingProgress, StoredDocument


@dataclass(frozen=True, slots=True)
class ChapterMeta:
    index: int
    title: str
    page_start: int
    page_end: int


@dataclass(frozen=True, slots=True)
class UploadResult:
    document_id: str
    title: str
    format: str
    chapters: tuple[ChapterMeta, ...]


@dataclass(frozen=True, slots=True)
class ResumeResult:
    document_id: str
    title: str
    format: str
    chapters: tuple[ChapterMeta, ...]
    chapter_index: int
    text: str
    progress: ReadingProgress | None


class LibraryService:
    """Coordinate document extraction and library persistence."""

    def __init__(self, extractor: DocumentExtractionService) -> None:
        self._extractor = extractor

    def extract(self, content: bytes, filename: str) -> ExtractedDocument:
        return self._extractor.extract(content, filename)

    def upload(
        self,
        store: LibraryStore,
        user_id: int,
        content: bytes,
        filename: str,
    ) -> UploadResult:
        document = self.extract(content, filename)
        stored = store.save_document(
            user_id,
            filename,
            document.title,
            document.source_format,
            content,
        )
        return UploadResult(
            document_id=stored.id,
            title=document.title,
            format=document.source_format,
            chapters=_chapter_meta(document),
        )

    def resume(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
    ) -> ResumeResult:
        stored = store.get_document(user_id, document_id)
        content = store.read_document_bytes(user_id, document_id)
        document = self.extract(content, stored.filename)
        progress = store.get_progress(user_id, document_id)
        chapter_index = progress.chapter_index if progress else 0
        return ResumeResult(
            document_id=stored.id,
            title=document.title,
            format=document.source_format,
            chapters=_chapter_meta(document),
            chapter_index=chapter_index,
            text=document.text_for_chapter(chapter_index),
            progress=progress,
        )

    def chapter_text(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        chapter_index: int,
    ) -> str:
        stored = store.get_document(user_id, document_id)
        content = store.read_document_bytes(user_id, document_id)
        document = self.extract(content, stored.filename)
        return document.text_for_chapter(chapter_index)

    def document_meta(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
    ) -> tuple[StoredDocument, ExtractedDocument, ReadingProgress | None]:
        stored = store.get_document(user_id, document_id)
        content = store.read_document_bytes(user_id, document_id)
        document = self.extract(content, stored.filename)
        progress = store.get_progress(user_id, document_id)
        return stored, document, progress

    def save_progress(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        *,
        chapter_index: int,
        frame_index: int,
        wpm: int,
        target_words: int,
    ) -> ReadingProgress:
        return store.save_progress(
            user_id,
            document_id,
            chapter_index=chapter_index,
            frame_index=frame_index,
            wpm=wpm,
            target_words=target_words,
        )

    def list_library(self, store: LibraryStore, user_id: int) -> list[LibraryEntry]:
        return store.list_documents_with_progress(user_id)


def _chapter_meta(document: ExtractedDocument) -> tuple[ChapterMeta, ...]:
    return tuple(
        ChapterMeta(
            index=index,
            title=chapter.title,
            page_start=chapter.page_start,
            page_end=chapter.page_end,
        )
        for index, chapter in enumerate(document.chapters)
    )


def chapter_list_payload(document: ExtractedDocument) -> list[dict[str, object]]:
    return [asdict(chapter) for chapter in _chapter_meta(document)]


def metadata_payload(
    document: ExtractedDocument,
    *,
    document_id: str | None = None,
    chapter_index: int = 0,
    text: str | None = None,
    progress: ReadingProgress | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": document.title,
        "format": document.source_format,
        "chapter_index": chapter_index,
        "chapters": chapter_list_payload(document),
    }
    if document_id is not None:
        payload["document_id"] = document_id
    if text is not None:
        payload["text"] = text
    if progress is not None:
        payload["progress"] = {
            "chapter_index": progress.chapter_index,
            "frame_index": progress.frame_index,
            "wpm": progress.wpm,
            "target_words": progress.target_words,
            "updated_at": progress.updated_at,
        }
    return payload
