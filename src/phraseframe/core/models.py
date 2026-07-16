"""Framework-independent domain models."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReadingSettings:
    """Controls phrase segmentation and pacing."""

    wpm: int = 300
    target_words: int = 4
    max_words: int = 6
    max_characters: int = 42
    comma_pause: float = 1.18
    sentence_pause: float = 1.45
    paragraph_pause: float = 1.75
    long_word_pause: float = 1.12
    stop_every_words: int | None = None

    def __post_init__(self) -> None:
        if not 100 <= self.wpm <= 800:
            raise ValueError("WPM must be between 100 and 800.")
        if not 1 <= self.target_words <= self.max_words <= 10:
            raise ValueError("Chunk sizes must satisfy 1 <= target <= max <= 10.")
        if not 10 <= self.max_characters <= 100:
            raise ValueError("Maximum characters must be between 10 and 100.")
        if self.stop_every_words is not None and not 50 <= self.stop_every_words <= 5000:
            raise ValueError("Stop interval must be between 50 and 5000 words, or off.")


@dataclass(frozen=True, slots=True)
class PhraseChunk:
    """A readable segment and its structural boundary."""

    text: str
    word_count: int
    boundary: str = "none"


@dataclass(frozen=True, slots=True)
class TimedFrame:
    """A phrase with deterministic display timing."""

    index: int
    text: str
    word_count: int
    duration_ms: int
    starts_at_ms: int
    boundary: str


@dataclass(frozen=True, slots=True)
class Timeline:
    """Complete playback data shared by browser and video renderer."""

    frames: tuple[TimedFrame, ...]
    word_count: int
    duration_ms: int
    wpm: int
    stop_frames: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class DocumentChapter:
    """A navigable section inside an extracted document."""

    title: str
    page_start: int
    page_end: int


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    """Normalized text and chapter metadata from a supported source file."""

    title: str
    pages: tuple[str, ...]
    chapters: tuple[DocumentChapter, ...]
    source_format: str

    @property
    def full_text(self) -> str:
        return "\n\n".join(page for page in self.pages if page.strip())

    def text_for_chapter(self, index: int) -> str:
        if not 0 <= index < len(self.chapters):
            raise ValueError("Chapter index is out of range.")
        chapter = self.chapters[index]
        return "\n\n".join(
            page for page in self.pages[chapter.page_start : chapter.page_end] if page.strip()
        )
