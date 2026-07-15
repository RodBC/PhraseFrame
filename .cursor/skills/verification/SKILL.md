---
name: phraseframe-verification
description: Verifies PhraseFrame core, HTTP, browser playback, responsive layout, and MP4 output. Use after changing application behavior or before release.
---

# PhraseFrame verification

Run:

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
```

Then smoke-test:

1. Paste and upload UTF-8 text.
2. Prepare at 250, 300, 350, and 500 WPM.
3. Play, pause, step backward, restart, and use keyboard controls.
4. Verify high-speed guidance and the completion reflection.
5. Export a short MP4 and inspect duration, readability, and playback.
6. Check desktop and narrow mobile viewports.
