"""Application service for building and slicing reading timelines."""

from dataclasses import replace

from phraseframe.core.chunking import chunk_text, normalize_text
from phraseframe.core.models import ReadingSettings, Timeline
from phraseframe.core.timing import build_timeline


class ReaderService:
    """Coordinate pure text, chunking, and timing operations."""

    max_characters = 100_000

    def prepare(self, text: str, settings: ReadingSettings) -> Timeline:
        normalized = normalize_text(text)
        if not normalized:
            raise ValueError("Add some text before preparing the reader.")
        if len(normalized) > self.max_characters:
            raise ValueError("For this POC, text is limited to 100,000 characters.")
        return build_timeline(chunk_text(normalized, settings), settings)

    def limit_duration(self, timeline: Timeline, seconds: int | None) -> Timeline:
        if seconds is None:
            return timeline
        if not 1 <= seconds <= 600:
            raise ValueError("Preview duration must be between 1 and 600 seconds.")

        limit_ms = seconds * 1000
        kept = []
        for frame in timeline.frames:
            if frame.starts_at_ms >= limit_ms:
                break
            remaining = limit_ms - frame.starts_at_ms
            kept.append(replace(frame, duration_ms=min(frame.duration_ms, remaining)))
        duration_ms = sum(frame.duration_ms for frame in kept)
        return Timeline(
            frames=tuple(kept),
            word_count=sum(frame.word_count for frame in kept),
            duration_ms=duration_ms,
            wpm=timeline.wpm,
        )
