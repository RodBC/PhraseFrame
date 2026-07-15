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

    def __post_init__(self) -> None:
        if not 100 <= self.wpm <= 800:
            raise ValueError("WPM must be between 100 and 800.")
        if not 1 <= self.target_words <= self.max_words <= 10:
            raise ValueError("Chunk sizes must satisfy 1 <= target <= max <= 10.")
        if not 10 <= self.max_characters <= 100:
            raise ValueError("Maximum characters must be between 10 and 100.")


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
