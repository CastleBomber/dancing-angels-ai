# Step 3 — quality baseline

Experiment completed 2026-09-28 (America/Los_Angeles).
Five of five generations completed and technically verified. Quality measured;
no tested configuration meets the proposed visual acceptance bar.

## Predeclared protocol

Five new generations maximum, sequentially on the local Mac. Compare 40, 20,
and 30 steps at seed 42, then run the selected step count with seeds 123 and 2026.
Hold the input, prompt, resolution, duration, guidance, scheduler, shift, negative
prompt, and tiling fixed. Prefer the fastest configuration meeting the quality
bar; otherwise choose the strongest visual candidate for robustness testing and
report that no acceptable baseline was established. Break visual ties by runtime.

Reference: `assets/man.png`, SHA-256
`70a854b15828d4536c6cda0e578dddec120ca534d861836a099e816c3cf249b8`;
`models/Wan2.2-TI2V-5B-MLX-Q4`; 512 × 512; 49 frames; 24 FPS; guidance 5.0;
UniPC; shift 5.0; aggressive VAE tiling (256 pixels / 32 frames).
Use the full negative prompt from the unchanged model config, saved in every run.

Prompt:

> The same illustrated man in a red shirt, dark trousers and red shoes performs a shuffle dance in place, alternating quick heel-toe steps and sliding his feet, with gently swinging arms. Full body and feet visible throughout, stable character appearance, fixed camera.

## Quality rubric (declared before generation)

Each category scores 0 (fails), 1 (partial), or 2 (meets the criterion).

| Category | 0 | 1 | 2 |
|---|---|---|---|
| Identity | Character/clothing substantially changes | Recognizable with visible drift | Character, clothing, and proportions remain stable |
| Anatomy/detail | Severe or persistent face/hand/limb corruption | Noticeable localized defects | No distracting defects at playback scale |
| Framing | Feet/body repeatedly cropped or camera moves substantially | Brief crop/drift | Full body and feet visible, fixed camera |
| Temporal consistency | Abrupt discontinuities or sustained flicker | Some morphing or unstable contact | Coherent poses and transitions with stable ground contact |
| Shuffle-like motion | Static or unrelated motion | Generic stepping/dance, ambiguous footwork | Repeated alternating footwork with visible sliding/heel-toe-like movement |

Proposed visual bar: at least 8/10, no zero categories, and motion score 2.
The selected settings must meet this bar across all three tested seeds to be
called a robust baseline within this small experiment. This does not establish
generalization to other images, longer clips, or exact Shuffle choreography.

Technical acceptance is separate: decode every frame without error and verify
512 × 512, 49 frames, 24 FPS. Runtime is reported, not conflated with visual quality.
Use full frame sequences and playback where available; distinguish mechanical
playback success from human real-time viewing and document assessment limits.

## Preflight

- Image hash and complete model configuration match step two.
- Weight file sizes match the recorded conversion evidence.
- Python 3.11.15; MLX 0.32.0; mlx-video 0.0.1; PyTorch 2.13.0;
  Transformers 5.14.1; NumPy 2.4.6; OpenCV 5.0.0.93; Pillow 12.3.0.
- macOS 26.6.2 (step two used 26.5.2); do not attribute cross-date timing changes
  solely to settings.
- Apple M4 Pro, 24 GiB unified memory; about 646 GiB free disk.
- Sandboxed Metal computation failed before generation. Approved access outside
  the sandbox passed a GPU matrix computation. This is not a generation attempt.
- Current CLI shebang points to this repository. Historical metadata retains the
  old repository paths; new runs use the current root explicitly.
- Existing user changes organizing documentation and artwork are preserved.

Run artifacts and machine-readable preflight: ignored `outputs/v5-step3/`.

## Reference reproduction

The new 40-step seed-42 MP4 is byte-for-byte identical to step two:
SHA-256 `709466c9caa86617eef0a36578ca21da5fbb5da41c0c78292921596288972af5`.
Wall runtime: 610.714 seconds, versus the historical 687.980 seconds. This is
one observation per date, not a controlled system-performance benchmark.

The complete 49-frame review reveals defects missed by sparse sampling:
an abrupt change from the source pose at frame 0 to frame 1; near-held pose
groups followed by visible jumps; facial and hand distortion; and bottom-edge
shoe cropping around frames 20–25. The recognizable dance does not establish
sustained heel-toe/sliding Shuffle footwork. This stricter assessment does not
invalidate step two's first-playable-video milestone.

Browser playback was started successfully: readyState 4, duration 2.041667 s,
paused false, playback position observed at 0.971985 s, no media error.

## Step-count comparison and selection

Scores below follow the rubric declared above; they are qualitative agent
assessments, not calibrated perceptual metrics or human ratings.

| Steps | Seed | Wall seconds | Identity | Anatomy | Framing | Temporal | Motion | Total | Visual bar |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 40 | 42 | 610.714 | 1 | 1 | 1 | 0 | 1 | 4/10 | Fail |
| 20 | 42 | 370.820 | 1 | 0 | 0 | 0 | 1 | 2/10 | Fail |
| 30 | 42 | 508.299 | 1 | 0 | 1 | 0 | 1 | 3/10 | Fail |
| 40 | 123 | 601.764 | 1 | 0 | 2 | 0 | 1 | 4/10 | Fail |
| 40 | 2026 | 613.142 | 1 | 0 | 0 | 0 | 1 | 2/10 | Fail |

20 steps saved 39.3% wall time against the fresh 40-step run, but introduced
conspicuous ghosted heads/limbs, colored facial patches, and repeated head crops.
30 steps saved 16.8%, but detached/ghosted shoes and legs remain conspicuous
(for example frames 5–8, 22, and 29–33), along with abrupt pose changes.
All three clips passed full decode and browser playback checks.

Selection recorded before the additional runs: 40 steps, seeds 123 and 2026.
No candidate meets the visual bar; 40 steps is the strongest available visual
reference, with fewer severe anatomy defects. It is not an accepted product
preset. One timing per setting is insufficient to characterize runtime variance;
the system was not isolated from other desktop activity or thermal effects.

Seed 123: full-body framing improves, but severe neon patches affect the
trousers, arms, face, hands, and background. Colored bands and trails appear
throughout the clip. Foot crossing and stance changes are generic dance motion.
The equal total score to seed 42 conceals a different defect profile; it is not
equivalent visual quality, and its zero anatomy/temporal scores fail the bar.

Seed 2026: parts of the body disappear at frame 1; faces/hands ghost or deform
at several transitions. Feet repeatedly cross the lower image boundary around
frames 14–27. Foot crossing is visible, but sustained Shuffle is not established.
All 49 frames decode correctly, and browser playback succeeds.

## Outcome and recommended reference

User viewing feedback after delivery: 40 steps / seed 42 is the least wonky;
40 steps / seed 123 has an appealing EDM-like effect. The 20-step and 30-step
seed-42 clips and the 40-step seed-2026 clip were rejected for random fidgeting
and body parts appearing in isolated frames. Preserve seed 123 as an aesthetic
reference; its appeal does not establish controllable effects or motion fidelity.

The bounded measurement work is complete. **No acceptable quality baseline was
established: 0/5 clips passed the visual bar, including 0/3 at 40 steps.**
This is an evidence baseline, not approval to advertise convincing Shuffle or
production-quality character animation. Steps 4–8 remain planned.

Retain **512 × 512, 49 frames, 40 steps, seed 42** as the diagnostic reference.
It preserves the most useful prior result and reproduced exactly. Lower step
counts saved time but caused more severe ghosting in the controlled seed-42
comparison. Additional seeds show substantial instability even at 40 steps.
Do not change application defaults based on these failed-quality comparisons.

Total generation wall time across five runs: 2,704.739 seconds (45m 04.739s).
The three 40-step runs ranged from 601.764 to 613.142 seconds. These figures
exclude subsequent frame extraction and review. Each run starts a fresh process;
model loading is included, but this is not a benchmark of a future persistent API.

Smallest proposed follow-up (not executed): **one prompt-only comparison** at
40 steps / seed 42, keeping every other setting fixed. Replace the action prompt
with: “The same illustrated man in a red shirt, dark trousers and red shoes
performs two slow alternating heel-toe shuffle steps in place. Small foot slides,
upright torso, arms relaxed at his sides. Full body and both feet visible throughout,
stable character appearance, fixed camera.” Compare against the saved reference
using the same rubric. This tests whether simpler movement reduces ambiguity
and defects; it is not a promised fix for temporal or decoder artifacts. Stop if
it does not improve the measured result, and investigate the generation/decoding
path before expanding to more seeds or spending time on a broad search.

## Playable artifacts and memory

Local comparison player: [HTML](../../outputs/v5-step3/index.html).
While the local server is running: [open player](http://127.0.0.1:8765/).
Restart it from the repository root with
`.venv-mlx/bin/python -m http.server 8765 --bind 127.0.0.1 --directory outputs/v5-step3`.

| Run | MP4 | All frames | MLX peak GiB | Process peak RSS GiB |
|---|---|---|---:|---:|
| 40 / seed 42 | [Play](../../outputs/v5-step3/20260928-183547-steps40-seed42/shuffle.mp4) | [Inspect](../../outputs/v5-step3/20260928-183547-steps40-seed42/all-frames.png) | 23.84 | 5.14 |
| 20 / seed 42 | [Play](../../outputs/v5-step3/20260928-184615-steps20-seed42/shuffle.mp4) | [Inspect](../../outputs/v5-step3/20260928-184615-steps20-seed42/all-frames.png) | 23.84 | 5.13 |
| 30 / seed 42 | [Play](../../outputs/v5-step3/20260928-185243-steps30-seed42/shuffle.mp4) | [Inspect](../../outputs/v5-step3/20260928-185243-steps30-seed42/all-frames.png) | 23.84 | 5.30 |
| 40 / seed 123 | [Play](../../outputs/v5-step3/20260928-191113-steps40-seed123/shuffle.mp4) | [Inspect](../../outputs/v5-step3/20260928-191113-steps40-seed123/all-frames.png) | 23.84 | 5.36 |
| 40 / seed 2026 | [Play](../../outputs/v5-step3/20260928-192128-steps40-seed2026/shuffle.mp4) | [Inspect](../../outputs/v5-step3/20260928-192128-steps40-seed2026/all-frames.png) | 23.84 | 5.21 |

Each directory contains `metadata.json` (full command, settings, model config,
environment, times, and memory), `generation.log`, `shuffle.mp4`,
`verification.json` (ffprobe metadata, full ffmpeg decode, SHA-256),
`contact-sheet.png`, `all-frames.png`, all 49 extracted PNGs, and `review.json`.
`outputs/v5-step3/summary.json` aggregates results. All media/run scripts remain
ignored. Original inputs, model files, and step-two evidence were not modified.

Every MP4 is H.264/yuv420p, 512 × 512, 49 frames, 24 FPS, 2.041667 seconds.
All passed full ffmpeg decode and independent OpenCV frame counting. The final
browser check observed all five players at readyState 4, paused false, advancing
to approximately 0.372 seconds with no media errors.

No application code or defaults changed; application unit tests were not needed.
Experiment scripts passed Python syntax checks, and artifact checks passed.
The V5D roadmap uses “MEASURED — Quality below target”; V5C is archived.
[Roadmap image-generation prompt and method](archive/roadmap-v5D-image-prompt.md).

## Reproduction

The 40-step, seed-42 clip is the diagnostic reference. Keep the original image
and model config unchanged. The installed backend defaults to UniPC and reads
shift 5.0, the complete negative prompt, and 24 FPS from that verified config.
The experimental recorder passed scheduler, shift, and negative prompt explicitly;
its output exactly matches the existing application path's historical output.

```bash
cd /Users/cbombs/github/dancing-angels-ai
PYTHONPATH=src .venv-mlx/bin/python -m dancing_angels_ai create \
  --image assets/man.png \
  --model models/Wan2.2-TI2V-5B-MLX-Q4 \
  --action dance \
  --prompt 'The same illustrated man in a red shirt, dark trousers and red shoes performs a shuffle dance in place, alternating quick heel-toe steps and sliding his feet, with gently swinging arms. Full body and feet visible throughout, stable character appearance, fixed camera.' \
  --width 512 --height 512 --frames 49 --steps 40 \
  --seed 42 --guide-scale 5.0 --tiling aggressive \
  --output outputs/v5-step3/reproduction/shuffle.mp4
```

This requires Metal access. The command uses the current repository interpreter
and module path, avoiding stale launchers. It intentionally writes a separate
reproduction output. Change only `--steps` to reproduce the comparison or only
`--seed` for a robustness run, and use a distinct output path each time.

The historical experiment recorder is `outputs/v5-step3/run-man-reference.py` (arguments:
`--steps 40 --seed 42`). It also saves settings, timing, logs, memory counters,
verification, and contact sheets. Its companion `verify.py` extracts every frame.

2026-10-08: `run.py` now defaults to woman-1 for new experiments. The preserved
`run-man-reference.py` retains the original image, prompt and preflight references.

## Assessment limits

- Agent inspection covers all 49 frames per clip in sequence sheets, with
  detailed rendered-frame inspection of the reference. Browser media state
  confirms actual playback, not just that a player element exists.
- This is not a human real-time viewing session or an expert choreography rating.
  No exact Shuffle reproduction is claimed.
- Scores are deliberately coarse; category failures matter more than a tied sum.
- One Hero image and two-second clips do not establish quality for other subjects
  or sustained movement. Three seeds at the selected step count are a small sample.
- MLX peak allocated bytes and macOS process peak RSS are distinct counters.
  They must not be added or interpreted as total system memory or swap usage.

2026-10-25: [Woman-1 follow-up completed](roadmap-v5-step3-quality-followup.md).
Input framing fixed; temporal-tile comparison did not pass quality. Historical
man results above are unchanged. Current roadmap V5G remains below target.
