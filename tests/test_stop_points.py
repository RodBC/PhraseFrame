from phraseframe.core.models import PhraseChunk, ReadingSettings, TimedFrame
from phraseframe.core.stop_points import stop_frame_indices
from phraseframe.core.timing import build_timeline


def test_stop_frame_indices_marks_word_intervals_and_chapter_end() -> None:
    frames = (
        TimedFrame(0, "one two", 2, 400, 0, "none"),
        TimedFrame(1, "three four", 2, 400, 400, "none"),
        TimedFrame(2, "five six", 2, 400, 800, "sentence"),
    )
    stops = stop_frame_indices(frames, every_n_words=4, chapter_end_indices=(2,))
    assert stops == (1, 2)


def test_stop_frame_indices_can_be_word_intervals_only() -> None:
    chunks = (PhraseChunk("one", 1), PhraseChunk("two", 1), PhraseChunk("three", 1))
    timeline = build_timeline(chunks, ReadingSettings(wpm=300))
    stops = stop_frame_indices(timeline.frames, every_n_words=2, chapter_end_indices=())
    assert stops == (1,)
