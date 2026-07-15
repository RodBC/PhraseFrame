# Free POC hosting

## Recommendation: Koyeb

Koyeb's free web instance currently provides 512 MB RAM, 0.1 vCPU, and 2 GB ephemeral SSD. It
accepts Docker services, sleeps after one hour without traffic, and typically wakes in a few
seconds. That makes it a better POC fit than Render's roughly one-minute cold start.

1. Put this project in a private GitHub repository. The PDF is excluded by `.gitignore` and must
   never be pushed.
2. In Koyeb, create a Web Service from that repository.
3. Select `Dockerfile`, the Free instance, and either Washington, D.C. or Frankfurt.
4. Set the exposed port to `8000`; the container also honors a platform-provided `PORT`.
5. Deploy and test TXT upload, playback, and a short MP4.

Free CPU is only 0.1 vCPU, so MP4 exports will be much slower than local exports. Keep the
60-second limit enabled for public demos and expect only one practical render at a time.

## Alternative: Render

Render can deploy the same Dockerfile as a free Web Service. Its free instance also has 512 MB
RAM and 0.1 CPU, but it sleeps after 15 idle minutes and can take about a minute to wake. The
ephemeral filesystem is fine because PhraseFrame deletes temporary outputs and stores no state.

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
