# Hosting PhraseFrame v2+

> **Status:** the complete investor loop is built and tested locally. No successful Render
> Starter E2E has been recorded yet, so production proof remains pending.

## Production requirements

v2 (PDF library, accounts, resume) and v3 (checkpoints) need **persistent storage**.
Render **Free** tier does not provide a persistent disk — data is lost on redeploy or sleep.

Use **Render Starter** (or equivalent) with a mounted volume.

## Render Starter setup

| Setting | Value |
|---|---|
| Runtime | Docker |
| Branch | `main` |
| Port | `8000` (via `PORT` env) |
| Instance | Starter (512 MB+ RAM) |
| Disk | Mount at `/data` (≥ 1 GB) |

### Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `PHRASEFRAME_DATA_DIR` | Yes | `/data` — SQLite DB + uploaded PDFs |
| `PHRASEFRAME_SECRET_KEY` | Recommended | JWT signing. If omitted, the app writes `/data/.secret_key` on first boot. |
| `PORT` | Auto | Set by Render |

The Docker entrypoint re-chowns `/data` on each boot so the non-root app user can write to a Render-mounted disk.

Checkpoint questions use **template generation only** — no LLM API key is required.

### Disk mount

1. In Render dashboard → your Web Service → **Disks**.
2. Add disk: mount path `/data`, size 1 GB (or more).
3. Set `PHRASEFRAME_DATA_DIR=/data`.
4. Redeploy.

The `Dockerfile` declares `VOLUME ["/data"]`, creates `/data/documents` with correct permissions,
and checks `GET /health` on Render's `$PORT`.

## How to redeploy

1. Push changes to `main`.
2. Render auto-deploys from the linked repository.
3. Run the north-star E2E checklist:

| Step | Action | Expected |
|---|---|---|
| 1 | Sign in, upload 100+ page PDF | Fast metadata response; chapters listed |
| 2 | Read 20+ frames, refresh, click **Continue** | Same chapter, frame, WPM, phrase size |
| 3 | Keep checkpoints at the 200-word demo default, pause, answer | First submit leaves the Recall Moment visible with score, summary, gaps, cards count, and explicit resume |
| 4 | Close browser, reopen next day, **Continue** | Full session restored including checkpoint settings |
| 5 | Weak checkpoint → **Review now** | Up to 4 immediately due cards; dashboard updates; card generation is idempotent |
| 6 | Reveal and grade a card, then **Return to passage** | SM-2 schedules the next review; reader opens the source document at the weak frame |

Also verify:

- Page load and sign-in
- PDF upload (metadata-only response should be fast)
- Resume uses cached chapter files (no re-parse on every read)
- `GET /health` returns `{"status":"ok"}`
- Attention Loop stage follows Read, Check, Gaps/Cards, and Review
- Recall Moment stays visible until **Continue reading** is selected
- Narrow mobile layout has no horizontal overflow
- Browser console has no uncaught errors

## Local verification record

| Environment | Automated checks | Browser investor loop | Status |
|---|---|---|---|
| Local (2026-07-16) | Ruff, formatting, mypy, 59 pytest tests at 87.75% coverage, JS syntax | Account → TXT preparation → checkpoint → persistent Recall Moment → weak markers → immediate queue → Got it / Again → source frame; 390 px layout; no app console errors | Proven |
| Render Starter | Same deployed revision | Full checklist above with persistent `/data` | Not yet proven |

## Privacy and production boundary

On a hosted deployment, uploaded PDFs and reading progress are stored on the server disk
for signed-in users. Guest `/api/extract` still processes files in memory for the session only.

Before inviting customers:

- keep the hosted-processing notice visible in the UI;
- add request-size, concurrency, timeout, and rate limits;
- avoid access logs containing source text;
- run a dependency and FFmpeg license review;
- add a retention/privacy policy.

## Alternatives

- **Fly.io / VPS**: mount a volume, same env vars.
- **Local**: default `PHRASEFRAME_DATA_DIR=data` in project root.

Free tiers remain suitable for v1 TXT demos only, not PDF libraries with accounts.
