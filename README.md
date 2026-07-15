# PhraseFrame

PhraseFrame is a local-first, phrase-paced reader. It presents short text segments at one
focal point, supports pause and step-back controls, and can export the same timeline as a
silent MP4.

This is a comprehension-first POC. It does **not** claim that everyone can understand dense
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
```

## Current scope

- Paste text or upload UTF-8 `.txt` files.
- Phrase-aware segmentation and punctuation-aware timing.
- Keyboard-accessible browser playback.
- Optional first-60-second preview and H.264 MP4 export.
- No accounts, analytics, remote uploads, PDF, EPUB, or OCR yet.

See [the architecture](docs/ARCHITECTURE.md), [research notes](docs/SCIENCE.md),
[free-hosting guide](docs/HOSTING.md), and [roadmap](docs/ROADMAP.md).
# PhraseFrame
