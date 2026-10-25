# Step 4 — local generation API

Completed **2026-10-07** (America/Los_Angeles). Step five has not started.

## Delivered

- FastAPI service under `src/dancing_angels_ai/api/`, bound to localhost.
- Image upload → persistent job → one MLX worker → HTTP MP4 retrieval.
- Two waiting slots; queue overflow returns 429. Records and inputs are isolated
  per job in ignored `outputs/api/jobs/`.
- PNG/JPEG/WebP validation, body/pixel limits, decoded format/MIME matching,
  structured failures, process timeout, and restart recovery.
- Existing MLX adapter reused; CLI defaults, Wan integration, and website unchanged.
- Installed dependencies were reused; optional API requirements declared in `setup.cfg`.
- [Startup commands, curl examples, endpoint table, and lifecycle details](../local-api.md).

## Verification

| Check | Result |
|---|---|
| Final automated suite | 26 tests: 25 passed, 1 opt-in CUDA test skipped |
| API tests | 10 passed: lifecycle, queue/serialization, uploads, failures, shutdown, restart, locks, timeout, range retrieval, invalid video |
| Health/readiness | All model/config/import/Metal/worker checks passed |
| Upload response | HTTP 202 in 0.010874 s; returned queued job immediately |
| Real generations | Exactly one |
| Download | HTTP 200; H.264/yuv420p, 512×512, 49 frames, 24 FPS, 2.041667 s |
| Decode | Full ffmpeg decode and independent frame checks passed |
| Range | HTTP 206 for bytes 0–31; bytes matched the full download |
| Restart | Completed job retained; MP4 identical; readiness passed |
| Browser playback | API-served video played through to 2.041667 s; ended=true, readyState=4, no error |
| Malformed request | HTTP 400 on the restarted final server; no new job |

A first upload was rejected with 415 before a job was created: `assets/man.png`
is actually WebP content. Resubmission used `image/webp` with identical source
bytes, SHA-256 `70a854b15828d4536c6cda0e578dddec120ca534d861836a099e816c3cf249b8`.
No image conversion or model changes were made.

Job: `30ef0076a26f43e684852ec24512d600`.
Preset: `shuffle-diagnostic-v1` — exact step-three prompt, 40 steps, seed 42,
guidance 5.0, aggressive tiling, UniPC, shift 5.0, recorded negative prompt and
Q4 model configuration. The source image is preserved as `input.webp`.

The MP4 is **byte-for-byte identical to the step-three reference**:
`709466c9caa86617eef0a36578ca21da5fbb5da41c0c78292921596288972af5`
(608,506 bytes). This establishes pipeline equivalence, not improved visual
quality. All previously recorded anatomy, continuity, and choreography limitations
remain. No additional quality experiment was performed.

## Timing limitation

The job reports 697.192 seconds using the monotonic timer. Its UTC start/finish
clock difference is 4,348.830 seconds; HTTP observation gaps reached 2,084.766
seconds. The execution environment paused during the run; the specific cause was
not determined. Do not treat this as a controlled speed benchmark. The generation
timeout and reported runtime use the monotonic clock, whose behavior across system
suspension differs from calendar elapsed time on this Mac.

## Artifacts

- [Downloaded, verified MP4](../../outputs/v5-step4/downloaded-shuffle.mp4).
- [Live API video](http://127.0.0.1:8000/jobs/30ef0076a26f43e684852ec24512d600/video)
  while the local server is running.
- [Job record](../../outputs/api/jobs/30ef0076a26f43e684852ec24512d600/job.json),
  [generation log](../../outputs/api/jobs/30ef0076a26f43e684852ec24512d600/generation.log),
  [exact command](../../outputs/api/jobs/30ef0076a26f43e684852ec24512d600/command.json).
- Ignored `outputs/v5-step4/`: environment, readiness, submission/headers,
  HTTP observations, final job, download verification, restart verification,
  browser playback state, server log, final test log, and acceptance runner.
- Environment: macOS 26.6.2, Python 3.11.15, MLX 0.32.0, mlx-video 0.0.1,
  FastAPI 0.140.0, Starlette 1.3.1, Uvicorn 0.51.0, python-multipart 0.0.32,
  Pillow 12.3.0. About 623 GiB disk space was free at preflight.

V5E marks step four complete and step five next. V5D and its image prompt are
archived. [V5E image prompt](archive/roadmap-v5E-image-prompt.md); built-in imagegen used.
No API/frontend connection, UI job-state work, deployment, or model tuning was done.
