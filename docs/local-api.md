# Local generation API

A local API around the existing MLX backend. One active generation and two waiting
jobs; no website integration or cloud deployment. The `shuffle-diagnostic-v2`
preset has known anatomy, temporal, and motion-fidelity defects.

## Start

From the project root, after completing [MLX setup](mlx-runtime.md):

```bash
cd /Users/cbombs/github/dancing-angels-ai
# Only needed if the API dependencies are not already installed:
uv pip install --python .venv-mlx/bin/python -e '.[api]'

PYTHONPATH=src .venv-mlx/bin/python -m dancing_angels_ai.api \
  --project-root /Users/cbombs/github/dancing-angels-ai --port 8000
```

The server binds to `127.0.0.1`, uses one process, and needs Metal access. Do not
run multiple uvicorn workers. An advisory lock prevents multiple API processes
for this project from running the GPU worker. It does not coordinate unrelated
CLI experiments; avoid launching those alongside API generation.

## Endpoints

| Method | Endpoint | Result |
|---|---|---|
| GET | `/health` | 200: server liveness, readiness flag, queue counts, preset |
| GET | `/ready` | 200 or 503: startup model/config/import/Metal checks and live worker health |
| POST | `/jobs` | 202: uploaded image accepted, job ID and `Location` header |
| GET | `/jobs/{id}` | Status, times, preset, input hash, errors, output metadata/URL |
| GET | `/jobs/{id}/video` | Completed MP4, with HTTP byte-range support |

`queued → running → succeeded` or `failed`. There is no invented percentage or
visual-quality guarantee. Queue status is available immediately; generation takes
about ten minutes on the tested 24 GB M4 Pro. Readiness hardware/model probes run
at startup, while worker liveness is checked on every readiness request. Restart
the API after repairing a failed startup prerequisite.

## Submit, poll, retrieve

```bash
curl --fail http://127.0.0.1:8000/ready

curl --fail --silent --show-error \
  -F 'image=@assets/woman-1.png;type=image/png' \
  -F 'action=shuffle' \
  http://127.0.0.1:8000/jobs > /tmp/dancing-angels-job.json

DANCE_JOB_ID=$(.venv-mlx/bin/python -c \
  'import json; print(json.load(open("/tmp/dancing-angels-job.json"))["id"])')

curl --fail "http://127.0.0.1:8000/jobs/$DANCE_JOB_ID"

# Once status is succeeded:
curl --fail "http://127.0.0.1:8000/jobs/$DANCE_JOB_ID/video" \
  --output /tmp/dancing-angels-shuffle.mp4
```

The current reference is the user's `assets/woman-1.png`, a true PNG. The v2
prompt follows the uploaded character without prescribing male features or the
old clothing. Existing v1 job records retain their original prompt and preset.
Restart a running API to pick up the new preset.

**Before quality testing:** this transparent portrait needs safe framing and
explicit background handling; the current MLX square crop cuts off the lower
legs. See [the next-test handoff](internal/woman-1-handoff.md). No video quality
claim has been established for the new image or v2 prompt.

## Input and failure contract

- Exactly one `image` file and one `action=shuffle` field; no settings overrides.
- PNG, JPEG, or single-frame WebP, up to 10 MiB; each side 64–4096 pixels.
- Multipart overhead allowance: 64 KiB. Both declared and chunked body sizes are
  bounded before parsing. File content is decoded and its actual format checked.
- 400: malformed multipart/request or invalid Host; 413: body/file too large;
  415: unsupported media type or image MIME mismatch; 422: invalid image/action/fields.
- 429: queue full (`Retry-After: 10`); 503: runtime unavailable.
- 404: unknown job; 409: job has no successful output; 410: completed output missing.
- Browser POSTs from another origin are rejected. Cross-origin website access
  belongs to step five; command-line clients do not need CORS.

## Storage and lifecycle

Each job has an isolated UUID directory under ignored `outputs/api/jobs/`:
`input.png|jpg|webp`, `job.json`, `generation.log`, `command.json`, and `result.mp4`.
Records include the full prompt, preset, reference model config, input hash, times,
output SHA-256, and complete decode validation. The command log contains the
explicit UniPC scheduler, shift 5.0, and recorded negative prompt.

The preset is 512×512, 49 frames, 24 FPS, 40 steps, seed 42, guidance 5.0,
aggressive tiling, and the unchanged Q4 model. The application CLI smoke defaults
remain unchanged. Startup rejects a model config differing from the recorded
reference; generated videos must pass full ffmpeg decoding and frame validation
before the API reports success.

Jobs persist as atomically replaced JSON records. Failed runs retain logs. On
shutdown, active generation is terminated and waiting jobs fail as interrupted.
On restart, abandoned queued/running jobs become `failed` with an `interrupted`
error; they are never silently regenerated. Finished jobs remain queryable.
Generation has a 30-minute subprocess timeout.

If the API is killed abruptly, its model subprocess retains the worker lock. A
restart refuses to start until that child exits, preventing duplicate API GPU
work. The lock file's presence alone does not indicate an active lock; deleting it
is not a recovery procedure. Restart once the old process finishes. Store access
is intended for trusted local use; there is no public-service authentication.

## Verify without GPU generation

The tests also require `httpx` in the test environment (the local MLX environment
already includes it):

```bash
PYTHONPATH=src .venv-mlx/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

API tests use a fake runtime to cover upload validation, queue bounds, serial
execution, failure and shutdown paths, restart recovery, process locks, timeouts,
and HTTP video/range retrieval. The separate real acceptance evidence is in
[step-four evidence](internal/roadmap-v5-step4-evidence.md).
