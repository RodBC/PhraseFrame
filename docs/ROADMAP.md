# Roadmap

## Stage 1 — validated POC

TXT input, interactive phrase playback, comprehension guidance, deterministic MP4 export, and
automated checks.

## Stage 2 — books

- Local PDF and EPUB adapters with page or chapter selection.
- Header, footer, hyphenation, and page-number cleanup.
- PyMuPDF licensing review before commercial distribution.
- OCR fallback for image-only pages.
- Reading-position persistence and bookmarks.

The supplied *Think* PDF can be processed from the user's local copy, but its text or derived
videos must not be bundled or distributed by PhraseFrame.

## Stage 3 — adaptive product

- Optional comprehension checkpoints and user-calibrated pacing.
- Semantic phrase segmentation benchmarked against the deterministic fallback.
- Background render workers, cancellation, and progress.
- Accounts and encrypted sync only after a privacy and threat-model review.
- Installable PWA and mobile packaging after keyboard, touch, and accessibility testing.

## Commercial readiness gates

Trademark search, dependency/license audit, accessibility review, privacy policy, observability
without document-content logging, abuse limits, rendering cost tests, and user research measuring
retention rather than reported speed alone.
