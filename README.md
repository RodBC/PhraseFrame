# PhraseFrame

PhraseFrame is a phrase-paced reader built around one visible loop:
**Read → Check recall → See gaps → Create cards → Review → Return to the passage**. It presents
short text segments at one focal point, preserves pause and step-back controls, and can export
the same timeline as a silent MP4.

This is a comprehension-first tool. It does **not** claim that everyone can understand dense
text at 500 WPM. Start around 250–300 WPM and lower the pace whenever meaning becomes unclear.

## Run locally

Requires Python 3.12+.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/phraseframe
```

Open <http://127.0.0.1:8000>. The first MP4 export may take a moment while the bundled FFmpeg
binary is initialized.

## Verify

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
node --check src/phraseframe/web/static/app.js
```

## Five-minute investor demo

Open `http://127.0.0.1:8000/?demo=1` to force the compact demo guide to appear.

1. Create an account and upload a short `.txt` or a PDF you are allowed to use.
2. Keep the demo default of **200 words per checkpoint**, then select **Prepare reader** and play.
3. Select **Check** (or reach an automatic stop), answer from memory, and submit once.
4. Pause on the **Recall Moment**: show the self-check score, honest 67% weak threshold (product rule), extractive
   recap, identified gaps, weak marker, and cards-created count.
5. Select **Review now**, reveal a card, grade it **Got it** or **Again**, then select
   **Return to passage** to jump to the source frame.
6. Finish on the library pulse: due reviews, average self-check score, Deep Pace (when enough checks exist), weak stops, and last read.

The score is based on submitted answers and self-rated confidence. Questions are templates and
summaries are extractive; PhraseFrame does not claim AI-generated comprehension.

## Current scope (v0.2.0)

- Paste text or upload UTF-8 `.txt` or `.pdf` files.
- Phrase-aware segmentation and punctuation-aware timing.
- Keyboard-accessible browser playback.
- Optional first-60-second preview and H.264 MP4 export.
- Email/password accounts with personal PDF library.
- Resume reading (chapter, frame, WPM, phrase size, checkpoint interval).
- Comprehension checkpoints with 2–5 template questions and self-scored feedback.
- Structured extractive summaries/gaps, weak-frame markers, and up to 4 distinct review flashcards.
- Immediate first review, idempotent card generation, SM-2 follow-up scheduling, and a dedicated
  cross-document Review screen linked back to each source frame.
- Library pulse with due reviews, average recall, weak-stop count, and last read.
- Chapter text cached at upload (fast resume without re-parsing PDFs).

These v2–v4 capabilities passed the complete local automated suite and browser investor loop on
2026-07-16. Render Starter production E2E proof remains pending; see the verification record in
[hosting](docs/HOSTING.md).

See [v1 status](docs/V1.md), [next steps](docs/nextsteps.md), [architecture](docs/ARCHITECTURE.md),
and [hosting](docs/HOSTING.md).
