"""Privacy-safe learning event recording and aggregate metrics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from phraseframe.db.store import LibraryStore

DEEP_PACE_MIN_SAMPLES = 5
DEEP_PACE_RECENCY_DAYS = 30
DEEP_PACE_THRESHOLD = 0.70


@dataclass(frozen=True, slots=True)
class DeepPaceResult:
    wpm: int | None
    sample_count: int
    message: str


class AnalyticsService:
    """Record typed learning events and compute honest product metrics."""

    EVENT_PREPARE = "prepare"
    EVENT_CHECKPOINT_SUBMIT = "checkpoint_submit"
    EVENT_WEAK_STOP_REPAIR = "weak_stop_repair"
    EVENT_REVIEW_GRADE = "review_grade"
    EVENT_RETURN_TO_PASSAGE = "return_to_passage"
    EVENT_RESUME = "resume"

    def record(
        self,
        store: LibraryStore,
        user_id: int,
        event_type: str,
        *,
        document_id: str | None = None,
        chapter_index: int | None = None,
        frame_index: int | None = None,
        wpm: int | None = None,
        self_check_score: float | None = None,
        card_grade: str | None = None,
        due_interval: int | None = None,
    ) -> None:
        store.record_learning_event(
            user_id,
            event_type,
            document_id=document_id,
            chapter_index=chapter_index,
            frame_index=frame_index,
            wpm=wpm,
            self_check_score=self_check_score,
            card_grade=card_grade,
            due_interval=due_interval,
        )

    def deep_pace(self, store: LibraryStore, user_id: int) -> DeepPaceResult:
        cutoff = (datetime.now(tz=UTC) - timedelta(days=DEEP_PACE_RECENCY_DAYS)).isoformat()
        rows = store.checkpoint_scores_with_wpm(user_id, since=cutoff)
        if len(rows) < DEEP_PACE_MIN_SAMPLES:
            return DeepPaceResult(
                wpm=None,
                sample_count=len(rows),
                message=(
                    "Not enough checks yet — complete a few recall checks to find your Deep Pace."
                ),
            )

        by_wpm: dict[int, list[float]] = {}
        for wpm, score in rows:
            bucket = int(round(wpm / 10) * 10)
            by_wpm.setdefault(bucket, []).append(score)

        best_wpm: int | None = None
        for wpm in sorted(by_wpm):
            scores = by_wpm[wpm]
            if len(scores) < 2:
                continue
            average = sum(scores) / len(scores)
            if average >= DEEP_PACE_THRESHOLD:
                best_wpm = wpm

        if best_wpm is None:
            return DeepPaceResult(
                wpm=None,
                sample_count=len(rows),
                message="Not enough checks yet at ≥70% self-check score for any pace band.",
            )
        return DeepPaceResult(
            wpm=best_wpm,
            sample_count=len(rows),
            message=f"Your Deep Pace: {best_wpm} WPM (rolling self-check ≥70%, n={len(rows)}).",
        )

    def aggregate_summary(self, store: LibraryStore, user_id: int) -> dict[str, object]:
        deep = self.deep_pace(store, user_id)
        return {
            "deep_pace_wpm": deep.wpm,
            "deep_pace_message": deep.message,
            "deep_pace_sample_count": deep.sample_count,
            "time_to_first_check_ms": store.aggregate_time_to_first_check(user_id),
            "weak_stop_same_day_review_rate": store.aggregate_weak_stop_review_rate(user_id),
            "again_rate": store.aggregate_again_rate(user_id),
            "resume_d1_rate": store.aggregate_resume_rate(user_id, days=1),
            "resume_d7_rate": store.aggregate_resume_rate(user_id, days=7),
            "wpm_band_scores": store.aggregate_wpm_band_scores(user_id),
        }
