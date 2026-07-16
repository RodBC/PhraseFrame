"""Pure stop-point detection for comprehension checkpoints."""

from phraseframe.core.models import TimedFrame


def stop_frame_indices(
    frames: tuple[TimedFrame, ...],
    *,
    every_n_words: int | None,
    chapter_end_indices: tuple[int, ...] = (),
) -> tuple[int, ...]:
    """Return frame indices where reading should pause for a checkpoint."""

    stops: set[int] = set()

    if every_n_words and every_n_words > 0 and frames:
        cumulative = 0
        next_stop = every_n_words
        for frame in frames:
            cumulative += frame.word_count
            while cumulative >= next_stop:
                stops.add(frame.index)
                next_stop += every_n_words

    for index in chapter_end_indices:
        if frames and 0 <= index < len(frames):
            stops.add(index)

    return tuple(sorted(stops))
