import pytest

from phraseframe.core.chunking import chunk_text, count_words, normalize_text
from phraseframe.core.models import PhraseChunk, ReadingSettings
from phraseframe.core.timing import build_timeline
from phraseframe.services.reader import ReaderService


def test_normalize_preserves_paragraphs_and_unicode() -> None:
    source = "  Café\u00a0readers \r\n stay focused. \r\n\r\n  A second   idea. "
    assert normalize_text(source) == "Café readers stay focused.\n\nA second idea."
    assert count_words(source) == 7


def test_chunking_respects_clause_sentence_and_paragraph_boundaries() -> None:
    settings = ReadingSettings(target_words=4, max_words=6)
    chunks = chunk_text(
        "One clear idea arrives, then another ends.\n\nNew paragraphs breathe.",
        settings,
    )
    assert [chunk.text for chunk in chunks] == [
        "One clear idea arrives,",
        "then another ends.",
        "New paragraphs breathe.",
    ]
    assert [chunk.boundary for chunk in chunks] == ["clause", "paragraph", "sentence"]


def test_chunking_enforces_character_limit() -> None:
    settings = ReadingSettings(target_words=6, max_words=6, max_characters=12)
    chunks = chunk_text("small extraordinary words remain", settings)
    assert [chunk.text for chunk in chunks] == ["small", "extraordinary", "words remain"]


def test_empty_text_has_no_chunks() -> None:
    assert chunk_text(" \n \n ", ReadingSettings()) == ()


def test_timeline_has_exact_offsets_and_punctuation_pauses() -> None:
    settings = ReadingSettings(wpm=300)
    chunks = (
        PhraseChunk("one two", 2),
        PhraseChunk("three four,", 2, "clause"),
        PhraseChunk("understanding matters.", 2, "sentence"),
    )
    timeline = build_timeline(chunks, settings)
    assert [frame.duration_ms for frame in timeline.frames] == [400, 472, 650]
    assert [frame.starts_at_ms for frame in timeline.frames] == [0, 400, 872]
    assert timeline.duration_ms == 1522
    assert timeline.word_count == 6


def test_long_word_gets_additional_time() -> None:
    settings = ReadingSettings(wpm=300)
    regular = build_timeline((PhraseChunk("simple concept", 2),), settings)
    long = build_timeline((PhraseChunk("interdisciplinary concept", 2),), settings)
    assert long.duration_ms > regular.duration_ms


def test_settings_reject_incoherent_chunk_sizes() -> None:
    with pytest.raises(ValueError, match="Chunk sizes"):
        ReadingSettings(target_words=7, max_words=4)


def test_reader_service_validates_and_limits_duration() -> None:
    service = ReaderService()
    with pytest.raises(ValueError, match="Add some text"):
        service.prepare("", ReadingSettings())

    timeline = service.prepare("one two three four five six seven eight", ReadingSettings(wpm=300))
    limited = service.limit_duration(timeline, 1)
    assert limited.duration_ms == 1000
    assert limited.frames[-1].duration_ms <= timeline.frames[-1].duration_ms


def test_reader_rejects_invalid_preview_duration() -> None:
    timeline = ReaderService().prepare("some useful text", ReadingSettings())
    with pytest.raises(ValueError, match="between 1 and 600"):
        ReaderService().limit_duration(timeline, 0)
