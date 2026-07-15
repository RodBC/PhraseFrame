# Architecture

PhraseFrame uses ports and adapters so playback behavior does not depend on FastAPI, a document
format, or a video library.

## Boundaries

- `core`: immutable models plus pure normalization, chunking, and timing.
- `services`: use-case orchestration and POC limits.
- `adapters`: UTF-8 extraction and Pillow/MoviePy rendering.
- `web`: validation, HTTP transport, templates, and browser playback.

The browser and renderer consume one timeline containing phrase text, duration, and cumulative
start time. This prevents exported timing from drifting away from the interactive preview.

## Extension rules

New formats implement `DocumentExtractor`; they do not alter the core. A production renderer
implements `VideoRenderer` and can run in a queue. Persistence, accounts, and analytics remain
outside the core. Document contents should be treated as private and must not be logged.
