---
name: product-vision
description: Guides PhraseFrame product evolution from v1 POC to PDF reading, accounts, comprehension checkpoints, flashcards, and focus tooling. Use when planning features, writing specs, or implementing v2+ capabilities.
---

# Product vision

## v1 status (done)

PhraseFrame v1 is deployed (Render + Docker). It proves phrase-RSVP with fixed focal point, pacing controls, TXT input, MP4 export, and honest science UX. See `docs/V1.md`.

## Product principle

PhraseFrame is a **focus and comprehension tool**, not a speed-reading gimmick. Keep the eye at one focal point; deliver meaningful phrase chunks at controlled pacing; verify understanding at stop points.

## v2 — PDF + account + resume

- PDF upload and text extraction (PyMuPDF adapter).
- User accounts and personal document library.
- Persist PDF reference + reading position + settings.
- Resume exactly where the user stopped.

## v3 — Active comprehension

- Stop points: chapter end, every X words, manual pause.
- Generate 2–5 questions per stop point (literal, inferential, connection).
- Pause reading for checkpoint; adjust pacing on poor comprehension.

## v4 — Review loop

- Summarize misunderstood passages.
- Generate flashcards from gaps.
- Spaced-repetition review queue.
- Dashboard: progress, comprehension rate, pending reviews.

## v5 — Full product

Reading → checkpoint → gap summary → flashcards → resume → longitudinal tracking.

## Constraints

- Never promise effortless comprehension at 500+ WPM.
- Do not bundle or redistribute copyrighted PDFs.
- Do not log document text in production.
- Keep `core` pure; add features via services and adapters.
- Measure retention and comprehension, not reported speed alone.

## Reference

- `docs/nextsteps.md` — structured roadmap
- `docs/V1.md` — current state
- `docs/SCIENCE.md` — evidence base
