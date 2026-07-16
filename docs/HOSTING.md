# Free POC hosting

## Current production (v1)

PhraseFrame v1 is hosted on **Render** as a Free Web Service, deployed from
`git@github.com:RodBC/PhraseFrame.git` using the root `Dockerfile`.

| Setting | Value |
|---|---|
| Runtime | Docker |
| Branch | `main` |
| Port | `8000` (via `PORT` env) |
| Instance | Free (512 MB RAM, 0.1 CPU) |

Render sleeps after 15 idle minutes and can take about a minute to wake. That is acceptable for
the current POC demo.

## How to redeploy

1. Push changes to `main` on GitHub.
2. Render auto-deploys from the linked repository.
3. Test: page load, reader playback, short MP4 export.

## Alternatives tried or available

- **Koyeb**: Docker + GitHub supported, but repo connection was problematic in practice.
- **Render**: chosen for v1; straightforward GitHub + Dockerfile deploy.

Free CPU is only 0.1 vCPU, so MP4 exports are much slower than local. Keep the 60-second limit
enabled for public demos.

## Privacy and production boundary

“Local-first” applies only when users run PhraseFrame on their own computer. On a hosted version,
text is sent to the host for processing even though it is not intentionally persisted. Before
inviting customers:

- replace the local privacy label with an accurate hosted-processing notice;
- add request-size, concurrency, timeout, and rate limits;
- avoid access logs containing source text or query data;
- run a dependency and FFmpeg license review;
- add a retention/privacy policy and abuse protections.

Free tiers are suitable for demos, not reliable commercial service or long book exports.
