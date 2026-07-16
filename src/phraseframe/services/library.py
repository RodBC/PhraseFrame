"""Library orchestration for uploads, resume, and progress."""

from dataclasses import asdict, dataclass

from phraseframe.adapters.documents import DocumentExtractionService
from phraseframe.core.models import ExtractedDocument
from phraseframe.db.store import LibraryEntry, LibraryStore, ReadingProgress


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
    text: str


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
        self._write_cache(store, user_id, stored.id, document)
        return UploadResult(
            document_id=stored.id,
            title=document.title,
            format=document.source_format,
            chapters=_chapter_meta(document),
            text=document.text_for_chapter(0),
        )

    def resume(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
    ) -> ResumeResult:
        stored = store.get_document(user_id, document_id)
        progress = store.get_progress(user_id, document_id)
        chapter_index = progress.chapter_index if progress else 0
        chapters, chapter_meta = self._load_chapters(store, user_id, document_id, stored.filename)
        self._validate_chapter_index(chapter_index, len(chapters))
        return ResumeResult(
            document_id=stored.id,
            title=stored.title,
            format=stored.source_format,
            chapters=chapter_meta,
            chapter_index=chapter_index,
            text=chapters[chapter_index],
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
        chapters, _ = self._load_chapters(store, user_id, document_id, stored.filename)
        self._validate_chapter_index(chapter_index, len(chapters))
        return chapters[chapter_index]

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
        stop_every_words: int | None = None,
    ) -> ReadingProgress:
        return store.save_progress(
            user_id,
            document_id,
            chapter_index=chapter_index,
            frame_index=frame_index,
            wpm=wpm,
            target_words=target_words,
            stop_every_words=stop_every_words,
        )

    def list_library(self, store: LibraryStore, user_id: int) -> list[LibraryEntry]:
        return store.list_documents_with_progress(user_id)

    def _load_chapters(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        filename: str,
    ) -> tuple[list[str], tuple[ChapterMeta, ...]]:
        cached_meta = store.read_chapters_meta(user_id, document_id)
        if cached_meta is not None:
            texts = []
            for index in range(len(cached_meta)):
                text = store.read_chapter_text(user_id, document_id, index)
                if text is None:
                    break
                texts.append(text)
            if len(texts) == len(cached_meta):
                chapter_meta = tuple(
                    ChapterMeta(
                        index=int(str(item["index"])),
                        title=str(item["title"]),
                        page_start=int(str(item["page_start"])),
                        page_end=int(str(item["page_end"])),
                    )
                    for item in cached_meta
                )
                return texts, chapter_meta

        content = store.read_document_bytes(user_id, document_id)
        document = self.extract(content, filename)
        self._write_cache(store, user_id, document_id, document)
        texts = [document.text_for_chapter(index) for index in range(len(document.chapters))]
        return texts, _chapter_meta(document)

    def _write_cache(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        document: ExtractedDocument,
    ) -> None:
        meta = chapter_list_payload(document)
        texts = [document.text_for_chapter(index) for index in range(len(document.chapters))]
        store.write_chapters_cache(user_id, document_id, meta, texts)

    @staticmethod
    def _validate_chapter_index(chapter_index: int, chapter_count: int) -> None:
        if chapter_index < 0 or chapter_index >= chapter_count:
            raise ValueError("Chapter index is out of range.")


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
            "stop_every_words": progress.stop_every_words,
            "updated_at": progress.updated_at,
        }
    return payload
