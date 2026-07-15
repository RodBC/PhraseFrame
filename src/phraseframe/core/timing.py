"""Deterministic conversion from phrase chunks to playback frames."""

from phraseframe.core.models import PhraseChunk, ReadingSettings, TimedFrame, Timeline


def _duration_ms(chunk: PhraseChunk, settings: ReadingSettings) -> int:
    base = 60_000 * chunk.word_count / settings.wpm
    multiplier = 1.0
    if chunk.boundary == "clause":
        multiplier *= settings.comma_pause
    elif chunk.boundary == "sentence":
        multiplier *= settings.sentence_pause
    elif chunk.boundary == "paragraph":
        multiplier *= settings.paragraph_pause
    if any(len(word.strip(".,;:!?—–-()[]{}\"'")) >= 12 for word in chunk.text.split()):
        multiplier *= settings.long_word_pause
    return max(120, round(base * multiplier))


def build_timeline(chunks: tuple[PhraseChunk, ...], settings: ReadingSettings) -> Timeline:
    """Create frames with stable integer timings and cumulative offsets."""

    frames: list[TimedFrame] = []
    cursor_ms = 0
    for index, chunk in enumerate(chunks):
        duration_ms = _duration_ms(chunk, settings)
        frames.append(
            TimedFrame(
                index=index,
                text=chunk.text,
                word_count=chunk.word_count,
                duration_ms=duration_ms,
                starts_at_ms=cursor_ms,
                boundary=chunk.boundary,
            )
        )
        cursor_ms += duration_ms

    return Timeline(
        frames=tuple(frames),
        word_count=sum(frame.word_count for frame in frames),
        duration_ms=cursor_ms,
        wpm=settings.wpm,
    )
