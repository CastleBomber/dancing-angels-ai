# Step 2 — first local Shuffle video

Date: 2026-09-05 (America/Los_Angeles). Step 3 has not started.

## Reproducible inputs

- Image: `assets/man.png` — illustrated full-body man, red shirt, dark trousers, red shoes.
- Image SHA-256: `70a854b15828d4536c6cda0e578dddec120ca534d861836a099e816c3cf249b8`.
- Model: `models/Wan2.2-TI2V-5B-MLX-Q4`, 4-bit transformer, group size 64.
- Seed: 42; resolution: 512 × 512; guidance: 5.0; scheduler: UniPC; shift: 5.0.
- VAE tiling: aggressive (256-pixel spatial tiles, 32-frame temporal tiles).
- Output: 24 FPS. Default model negative prompt retained; full model config saved with retry metadata.
- Environment: macOS 26.5.2 arm64, Python 3.11.15, MLX 0.32.0, mlx-video 0.0.1, PyTorch 2.13.0, Transformers 5.14.1, NumPy 2.4.6, OpenCV 5.0.0.93.

Prompt:

> The same illustrated man in a red shirt, dark trousers and red shoes performs a shuffle dance in place, alternating quick heel-toe steps and sliding his feet, with gently swinging arms. Full body and feet visible throughout, stable character appearance, fixed camera.

## Attempt 1 — playable, visual quality failed

- Directory: `outputs/v5-step2/20260904-235922/`.
- Settings: 17 frames, 10 steps.
- Wall runtime: 136.154 seconds; backend-reported runtime: 131.3 seconds.
- Exit: 0. Video: `shuffle.mp4`, 309,200 bytes, H.264/yuv420p, 512 × 512, 24 FPS, 17 decoded frames, 0.708333 seconds.
- Verification: ffprobe counted all 17 frames; full `ffmpeg -v error -xerror` decode succeeded.
- Visual inspection: contact sheet sampled frames 0, 2, …, 16. Red shirt/dark trousers broadly persist, but face/hands exhibit bright yellow-green artifacts; limbs, shoes, and body shape distort. Motion is a squat/turn/leg spread, not a convincing Shuffle.
- Result: technical generation works; identity fidelity and requested motion fail visual acceptance. Clip too short to judge sustained footwork.
- Original MP4, `generation.log`, `metadata.json`, and `frames-contact-sheet.png` retained without alteration.

## Attempt 2 — bounded recovery

- Directory: `outputs/v5-step2/20260905-000224/`.
- Same image, prompt, seed, model, guidance, and tiling; 49 frames, 40 steps.
- Rationale: first clip was too short and used only 10 steps. Retry uses the model's configured 40-step count and approximately two seconds of output.
- This is a recovery attempt, not a controlled quality baseline: two settings changed together.
- Wall runtime: 687.980 seconds (11m 28s); backend-reported runtime: 683.7 seconds.
- Exit: 0. Video: `shuffle.mp4`, 608,506 bytes, H.264/yuv420p, 512 × 512, 24 FPS, 49 decoded frames, 2.041667 seconds.
- SHA-256: `709466c9caa86617eef0a36578ca21da5fbb5da41c0c78292921596288972af5`.
- Verification: ffprobe counted all 49 frames; full `ffmpeg -v error -xerror` decode succeeded with no errors.
- Visual inspection: contact sheet sampled frames 0, 6, …, 48. Hero remains recognizable, with consistent red shirt, dark trousers, red shoes, and full-body framing. Visible movements include alternating steps, crossed legs, knee lifts, and swinging arms. These are shuffle-like dance movements, not verified exact heel-toe Shuffle choreography.
- Improvement: the severe neon-face/body artifacts from attempt 1 are largely absent. Remaining defects: hands/fingers and facial details drift or distort; occasional faint colored background artifacts remain. No claim of production quality.
- Retained files: `shuffle.mp4`, `generation.log`, `metadata.json`, `verification.json`, `frames-contact-sheet.png`.
- Playback verification means successful decoding of every frame; visual assessment is based on sampled frames, not a real-time human viewing session.

## Outcome

Step 2 complete as the first playable, prompt-driven dance generation milestone.
Two attempts preserved; no application-code changes or original-asset edits needed.
Step 3 quality baselining has not started. This run does not establish exact motion
fidelity or isolate which retry setting caused the visual improvement.

To reproduce the retry from the repository root:

```bash
.venv-mlx/bin/python outputs/v5-step2/run-man-reference.py --frames 49 --steps 40
```

The runner saves each attempt separately, including its complete CLI argument list.
Media and run scripts remain under ignored `outputs/`; this report tracks the evidence.

2026-10-08: the historical runner was preserved under `run-man-reference.py`;
`run.py` now defaults to the user's woman-1 image for new experiments.
