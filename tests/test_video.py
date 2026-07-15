from pathlib import Path

from moviepy import VideoFileClip

from phraseframe.adapters.video import PillowMoviePyRenderer
from phraseframe.core.models import TimedFrame, Timeline


def test_renderer_creates_playable_mp4(tmp_path: Path) -> None:
    timeline = Timeline(
        frames=(
            TimedFrame(
                index=0,
                text="A focused phrase",
                word_count=3,
                duration_ms=180,
                starts_at_ms=0,
                boundary="sentence",
            ),
        ),
        word_count=3,
        duration_ms=180,
        wpm=300,
    )
    output = PillowMoviePyRenderer().render(timeline, tmp_path / "short.mp4")
    assert output.exists()
    assert output.stat().st_size > 1_000
    with VideoFileClip(str(output)) as clip:
        assert 0.15 <= clip.duration <= 0.25


def test_renderer_rejects_empty_timeline(tmp_path: Path) -> None:
    empty = Timeline(frames=(), word_count=0, duration_ms=0, wpm=300)
    try:
        PillowMoviePyRenderer().render(empty, tmp_path / "empty.mp4")
    except ValueError as error:
        assert "empty timeline" in str(error)
    else:
        raise AssertionError("Expected empty timeline to be rejected")
