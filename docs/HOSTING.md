# Hosting PhraseFrame v2+

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
| `PHRASEFRAME_SECRET_KEY` | Yes | JWT signing (long random string) |
| `PHRASEFRAME_LLM_API_KEY` | No | Optional LLM for checkpoint questions |
| `PORT` | Auto | Set by Render |

### Disk mount

1. In Render dashboard → your Web Service → **Disks**.
2. Add disk: mount path `/data`, size 1 GB (or more).
3. Set `PHRASEFRAME_DATA_DIR=/data`.
4. Redeploy.

The `Dockerfile` declares `VOLUME ["/data"]` and creates `/data/documents` with correct permissions.

## How to redeploy

1. Push changes to `main`.
2. Render auto-deploys from the linked repository.
3. Verify:
   - Page load and sign-in
   - PDF upload (metadata-only response should be fast)
   - Read 20+ frames, refresh, **Continue** restores position
   - Checkpoint pause when `stop_every_words` is enabled

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
