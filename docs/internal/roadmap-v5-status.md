# Roadmap V5 Status

Goal: `Character image + walk / run / jump -> local MLX -> playable MP4`

Current direction (2026-11-02): prove the three basic movements first; following a saved
reference animation (for example Mixamo) comes later. [Plan and acceptance](roadmap-v5-basic-movements-plan.md).

| Step | Goal | Status |
|---|---|---|
| 1 | Convert the MLX model | Complete — verified 2026-09-04 |
| 2 | Generate the first video | Complete — playable MP4 verified 2026-09-05; visual limitations recorded |
| 3 | Set a quality baseline | In progress — walk/run/jump untested; text-encoding memory prerequisite unresolved; historical Shuffle below target |
| 4 | Add local generation API | Complete — real HTTP job, MP4 retrieval, playback, and restart verified 2026-10-07 |
| 5 | Connect the website | Planned — not started; current focus is Step 3 quality |
| 6 | Add generation states | Planned |
| 7 | Play the real result | Planned |
| 8 | Package the Mac demo | Planned |

Acceptance gate: upload character, choose walk, run or jump, generate, and watch a clear playable MP4. All three movements must meet the visual bar; playback alone is insufficient.

## Step 3 checkpoints

| Checkpoint | Acceptance | Current status |
|---|---|---|
| 3A — Input | Correct preparation and verified image encoding/conditioning | Passed for woman reference; upload preparation integrated |
| 3B — Motion | Each of walk/run/jump ≥8/10, no zeros, requested-action score2 | Pending — three new movement targets untested; historical Shuffle still below target |
| 3C — Reliability | Repeat passing motion across seeds and different characters | Pending; no robustness claim |

## 3 basic movements

| Order | Movement | Status |
|---|---|---|
|1|Walk in place|Untested — first target|
|2|Run in place|Untested — next|
|3|Jump in place|Untested — then|

Before testing: resolve text-encoding memory use. After the basics: follow a saved
reference animation, optionally from Mixamo. This is later work; the current
prompt-only path does not accept Mixamo animations.

[3A evidence, correction, checks and limitations](roadmap-v5-step3a-input-evidence.md).
Passing3A does not mean every possible uploaded image or motion works.


New test input (2026-10-08): use the user's `assets/woman-1.png` for future runs.
One prepared woman reference has since been generated; no quality pass is claimed. Read the
[preparation and next-test handoff](woman-1-handoff.md), including the portrait
crop/transparency issue, before resuming Step 3. Historical evidence below is unchanged.

## Step 1 verification — 2026-09-04

- Original checkpoint preserved in `models/Wan2.2-TI2V-5B/`.
- Converted model: `models/Wan2.2-TI2V-5B-MLX-Q4/` (ignored by Git).
- Conversion exited 0; 300 transformer layers quantized to 4 bits, group size 64.
- All weight files passed tensor-header, shape, byte-count, and file-size checks.

| File | Tensors | Bytes | Precision |
|---|---:|---:|---|
| `model.safetensors` | 1,426 | 2,945,950,389 | Q4 targeted layers; remaining weights higher precision |
| `t5_encoder.safetensors` | 242 | 11,361,845,505 | BF16 |
| `vae.safetensors` | 196 | 2,818,778,952 | FP32 |

Conversion command:

```bash
.venv-mlx/bin/python -u -m mlx_video.models.wan_2.convert \
  --checkpoint-dir models/Wan2.2-TI2V-5B \
  --output-dir models/Wan2.2-TI2V-5B-MLX-Q4 \
  --quantize --bits 4 --group-size 64
```

The initial sandboxed attempt could not access Metal. Retrying with approved
GPU access completed successfully; no source-code changes were needed.

Readiness command: `.venv-mlx/bin/dancing-angels-ai doctor` — exit 0.

```text
[PASS] character image: assets/man.png
[PASS] MLX video model: /Users/cbombs/github/dancing-angels-ai/models/Wan2.2-TI2V-5B-MLX-Q4
[PASS] MLX model config.json
[PASS] MLX model model.safetensors
[PASS] MLX model t5_encoder.safetensors
[PASS] MLX model vae.safetensors
[PASS] MLX Python executable
[PASS] MLX Python version: 3.11.15
[PASS] Apple Silicon: Darwin arm64
[PASS] MLX imports: mlx=0.32.0, mlx-video=0.0.1
READY
```

Stopped before Step 2: no video generation or visual-quality validation performed.
Original planning poster:
[V5A](../../roadmaps-ideas/archive/roadmap-v5A-real-generation.png). Previous update:
[V5B](../../roadmaps-ideas/archive/roadmap-v5B-real-generation-updated.png). Previous rebrand:
[V5C](../../roadmaps-ideas/archive/roadmap-v5C-dancing-angels-real-generation-updated.png).
Quality baseline: [V5D](../../roadmaps-ideas/archive/roadmap-v5D-quality-baseline.png).
Previous roadmap: [V5E](../../roadmaps-ideas/archive/roadmap-v5E-local-api.png).
Previous roadmap: [V5F](../../roadmaps-ideas/archive/roadmap-v5F-quality-followup.png).
Previous roadmap: [V5G](../../roadmaps-ideas/archive/roadmap-v5G-quality-results.png).
Previous roadmap: [V5H](../../roadmaps-ideas/archive/roadmap-v5H-decoder-checks.png).
Previous roadmap: [V5I](../../roadmaps-ideas/archive/roadmap-v5I-input-verified.png).
Previous roadmap: [V5J](../../roadmaps-ideas/archive/roadmap-v5J-motion-tested.png).
Previous roadmap: [V5K](../../roadmaps-ideas/archive/roadmap-v5K-q8-memory-check.png).
Current roadmap: [V5L](../../roadmaps-ideas/roadmap/roadmap-v5L-basic-movements.png).

## Step 2 verification — 2026-09-05

- Generated `outputs/v5-step2/20260905-000224/shuffle.mp4`: 512 × 512, 49 frames, 24 FPS, 2.041667 seconds.
- Seed 42; 40 steps; wall runtime 687.980 seconds (11m 28s).
- Full MP4 decode passed; sampled frames visually inspected.
- Hero clothing and overall identity mostly preserved; shuffle-like stepping visible. Hand/face distortion and motion-fidelity limitations remain.
- Failed-quality 10-step smoke clip preserved alongside the successful retry.
- [Inputs, settings, runtimes, playback checks, and visual findings](roadmap-v5-step2-evidence.md).
- Step 2 completes the first playable generation milestone, not a claim of production-quality or exact Shuffle reproduction. Stopped before Step 3.

## Step 3 quality baseline — 2026-09-28

- Completed exactly five sequential generations: 40, 20, and 30 steps at seed 42;
  then 40 steps at seeds 123 and 2026. Total generation time: 45m 05s.
- All five MP4s passed full-frame decode and browser playback checks.
- The 40-step seed-42 reference reproduced step two byte-for-byte, in 10m 11s.
  Retain it as a diagnostic reference. 20 and 30 steps were faster but introduced
  more severe visual defects at the controlled seed.
- **No configuration met the visual bar.** Anatomy/identity distortion, abrupt
  temporal changes, cropping, and uncertain Shuffle footwork remain. Additional
  seeds showed substantial instability, including severe neon artifacts.
- [Results, playable clips, settings, rubric, and reproduction command](roadmap-v5-step3-evidence.md).
- V5D marks the baseline as measured with quality below target; V5C is archived.
  A single prompt-only follow-up is proposed in the evidence report, not executed.
- Stopped after step three. Steps 4–8 remain planned; no application-code or
  default-setting changes, API work, or website integration were performed.

## Step 4 local API — 2026-10-07

- Completed a localhost API for uploads, persistent jobs, status, and MP4 retrieval.
  One GPU worker, two waiting slots, validated inputs, bounded execution, and
  explicit failure/restart behavior.
- Exactly one fresh generation through HTTP; the retrieved MP4 matches the
  step-three reference byte-for-byte. Full decode, range requests, browser playback,
  and retrieval after server restart passed.
- Final tests: 25 passed, 1 opt-in CUDA test skipped. No visual-quality improvement
  is claimed; step-three defects remain.
- [Evidence and playable result](roadmap-v5-step4-evidence.md).
  [Startup and API commands](../local-api.md).
- V5E recorded this milestone; V5L is now current. Stopped after step four; website integration
  is next, and steps six through eight remain planned.

## Step 3 follow-up checkpoint — 2026-10-25

- Current focus: complete the bounded visual-quality investigation; quality has not passed.
- Prepared woman-1 on an opaque white canvas with full-body clearance; source preserved.
- One new reference completed on October 21: 40 steps, seed 42, 640.363 seconds.
  All 49 frames decode successfully at 512×512 / 24 FPS.
- Temporal-tile comparison, all-frame scoring and browser playback review remain pending.
  Saved normalized latents allow the decoder comparison without repeating diffusion.
- No additional seeds or candidate result exist at this checkpoint.
- [Investigation evidence](roadmap-v5-step3-quality-followup.md).
- V5F marks Step 3 IN PROGRESS, Step 5 PLANNED; Steps 1, 2 and 4 remain complete.
  V5E and its prompt are archived. No new generation was launched for this roadmap update.


## Step 3 follow-up result — 2026-10-25

- Bounded comparison finished; **visual quality remains unresolved**.
- Fixed portrait framing/transparency; both woman clips keep full-body framing.
- Temporal32 reference and temporal64 candidate both score 4/10, failing anatomy,
  temporal consistency and the required Shuffle-motion score.
- Candidate reused identical saved latents: 144.872 s decoder-only run; reference
  full generation 640.363 s. Different timing scopes; no speedup claim.
- Both passed all-frame decoding and browser playback. No additional seeds run.
- Next proposed experiment: one spatial-tile-only comparison using saved latents;
  then a small official-VAE parity check if distortion remains. Not yet executed.
- [Full evidence, reproduction, playable comparison](roadmap-v5-step3-quality-followup.md).
- V5G: Step 3 TESTED / Quality below target. Steps 1,2,4 remain complete;
  Steps 5–8 planned. V5F and its prompt archived. No API or website integration work.

## Step 3 spatial and decoder result — 2026-10-26

- One whole-frame decode of identical saved latents: 56.145 s; quality still4/10.
- All49 frames reviewed; full decoding and browser playback passed.
- Small synthetic and real-weight comparisons agree with the official decoder.
  No decoder bug confirmed; no speculative patch or additional seeds.
- High MLX peak allocation (23.51GiB); no default change recommended.
- Next: small image-encoder/conditioning parity check before another generation.
- [Evidence, limits, settings and playable comparison](roadmap-v5-step3-spatial-evidence.md).
- V5H retains Step3 TESTED / Quality below target. V5G image/prompt archived.
  No application code, API or website changes.

## Step 3A result — 2026-10-26

- Prepared woman image matches the earlier reference exactly; source unchanged.
- All86 encoder tensors match; full512 encoder differs from official FP32 by at
  most1.28746e-5. Masks, timesteps and conditioning blend match in tested fixtures.
- Fixed confirmed backend preparation bypass for raw uploads. Prepared RGB
  references pass through unchanged. No resampling/model/prompt changes.
-29 tests passed,1 opt-in CUDA test skipped; zero new video generations.
-3A passed within recorded scope;3B remains below target and3C pending.
- V5I current; V5H archived. Stopped after3A, no unrelated API/website changes.

## Step 3B result — 2026-10-27

- Two controlled generations completed:shift3 and guidance3, each changing one
  setting against the original woman reference. Both still4/10; neither passed.
- Scheduler/tiny-transformer/CFG checks passed; selected Q4 conversion matches
  the original checkpoint. No implementation cause confirmed; no code patch.
- All49 frames per clip reviewed; full decoding and browser playback passed.
- Recorded monotonic times:661.108s and603.855s. First run had large clock gaps;
  its wall time was8874.658s. These are not controlled speed benchmarks.
- No new seeds, third generation, model switch or3C testing.
- Next proposed test:one same-checkpoint Q8 comparison after memory feasibility.
  Compression is a hypothesis, not a confirmed cause.
- [Evidence, playable clips, limits and reproduction](roadmap-v5-step3b-motion-evidence.md).
- V5J current; V5I image/prompt archived.3A passed,3B below target,3C pending.

## Step 3B Q8 checkpoint — 2026-10-28

- Q8 converted from the original checkpoint; all300 Q4 layers reproduce exactly,
  all526 remaining tensors retained. Q4 and every earlier experiment preserved.
- Two launches stopped during text encoding at the recorded8GiB swap-increase
  guard, before Q8 transformer loading or diffusion. No new MP4 or quality score.
- One retry capped allocator cache256MiB; same math and guard. No further retries.
- This is an experiment-limit stop, not proof of a hardware OOM or Q8 infeasibility.
- Next: text-encoding-only memory reduction/parity check before resuming Q8.
  Another-model capability benchmark is an optional separate path, not executed.
-3A passed;3B below target with Q8 comparison unresolved;3C pending.
- [Evidence, failure logs and reference player](roadmap-v5-step3b-q8-evidence.md).
- V5K current; V5J image/prompt archived. No application/API/website changes.

## Basic-movement planning update — 2026-11-02

- User changed initial motion targets to walk, run and jump, in that order.
- Dedicated three-movement section added; all three marked untested.
-3B now requires each action to meet the prospective action-specific rubric.
  Historical Shuffle scores and failed Q8 launches remain unchanged.
- Text-encoding memory remains the next prerequisite; no new test was run.
- Following a saved animation, such as Mixamo, is separate later work.
- V5L current; V5K image/prompt archived. No application or integration changes.
- [Plan, criteria and later reference-animation explanation](roadmap-v5-basic-movements-plan.md).
