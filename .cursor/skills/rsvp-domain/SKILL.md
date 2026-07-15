---
name: rsvp-domain
description: Implements PhraseFrame chunking, pacing, reader controls, and scientific product wording. Use when changing the reading engine, timeline, speed controls, onboarding, or comprehension claims.
---

# RSVP domain

1. Read `docs/SCIENCE.md` before changing claims or defaults.
2. Keep `core` deterministic and framework-independent.
3. Compute base frame duration as `60_000 * word_count / wpm`.
4. Preserve clause, sentence, and paragraph pauses explicitly.
5. Give readers pause, backward navigation, and speed control.
6. Never claim guaranteed comprehension or treatment of attention disorders.
7. Test exact timing and boundaries after behavior changes.
