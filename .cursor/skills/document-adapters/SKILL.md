---
name: document-adapters
description: Adds and maintains local document extraction adapters for PhraseFrame. Use when supporting TXT, PDF, EPUB, OCR, chapter selection, or document cleanup.
---

# Document adapters

1. Implement `DocumentExtractor`; do not put format logic in routes or `core`.
2. Validate extension, size, encoding, and empty output with user-facing errors.
3. Never log document contents.
4. Preserve paragraph boundaries and return plain Unicode text.
5. Add fixtures created for the project; never commit copyrighted source books.
6. Review library and bundled-binary licenses before adding a format commercially.
7. Test malformed, oversized, Unicode, and representative layout cases.
