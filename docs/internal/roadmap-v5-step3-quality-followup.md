# Step 3 quality investigation — 2026-10-21

Status: bounded comparison completed 2026-10-25. **Visual quality remains below target; Step 3 quality is not resolved.**

## Scope and predeclared controls

Use `assets/woman-1.png`, per AGENTS.md and the handoff. Preserve the original,
all five historical man clips, and the user-liked seed-123 EDM result.
The saved 40-step/seed-42 man clip remains a historical diagnostic reference;
it is not the control for the new character because image and prompt differ.

Maximum four new generations, sequential: prepared woman reference at seed 42,
then a candidate changing only temporal VAE tile size from 32 to 64 frames.
Keep spatial tiles 256 px, spatial overlap 64 px, temporal overlap 8 frames,
512×512, 49 frames, 24 FPS, 40 steps, guidance 5, UniPC, shift 5,
the existing Q4 model and full negative prompt. Use the shared neutral Shuffle
prompt from `src/dancing_angels_ai/reference.py` unchanged in both trials.
Only if the candidate passes: test seeds 123 and 2026. No unlimited search.

Existing acceptance rubric: identity, anatomy/detail, framing, temporal consistency,
Shuffle motion each 0–2. Require ≥8/10, no zeros, motion 2; robust only across all
three seeds. Technical decoding/playback success is separate from visual acceptance.

## Confirmed findings versus hypotheses

- Confirmed input defect: the installed loader drops alpha and fills/center-crops
  the portrait. Lower legs/shoes fall outside the 512×512 crop. This is a defect
  for this input, not evidence about vector-brush quality.
- Implemented opt-in preparation in `src/dancing_angels_ai/preparation.py`:
  crop to nonzero alpha bounds, proportionally fit inside 416×416, center in a
  512×512 white RGB canvas with at least 48 px clearance. Source is unchanged.
  Tests cover transparency, foot preservation, proportions, empty input, opaque
  images, and overwrite rejection. Exact pixels entering MLX match the prepared PNG.
- Confirmed decoder structure: Wan22 VAE uses temporal compression 4; 49 output
  frames correspond to 13 latent frames. Aggressive decoding splits temporal
  latents and restarts each tile with `first_chunk=True`; tiles do not share
  causal feature caches. Spatial tiling also limits context. These implementation
  facts do not establish that tiling causes the observed defects.
- Hypothesis under test: one full temporal tile reduces restart/blending defects.
  Changing its size to 64 retains the 256 px spatial tiles to limit memory.
- Audited channel/time rearrangements, patchify/unpatchify, and the official
  [Wan2.2 VAE source](https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/wan/modules/vae2_2.py).
  No independently confirmed ordering bug was established. The installed all-at-once
  decoder is not proven numerically equivalent to the official cached decoder.
- The MP4 writer emits the generated frames in order at the configured FPS.
  Existing videos decode fully; corruption is visible in their decoded frames.
  No evidence currently supports blaming browser playback or container decoding.
- Historical continuity statistics measure per-frame pixel changes and timestamps.
  These are diagnostics, not quality scores or proof of a decoder cause.

Artifacts, immutable dependency-source snapshots, full hashes, exact input,
preparation transform, protocol and per-run records:
`outputs/v5-step3-quality-20261021/` (ignored).

## Results

Checkpoint verified 2026-10-25:

- Prepared woman reference completed 2026-10-21 in 640.363 seconds (monotonic).
- Output: `outputs/v5-step3-quality-20261021/temporal32-seed42/shuffle.mp4`.
- Full decoding passed: 49 frames, 512×512, 24 FPS. Contact sheets and normalized
  latents are saved. This is technical acceptance only.
- Candidate has not run; visual scoring, comparison and browser playback review
  remain unfinished. No quality pass or robustness claim.
- Protocol amended before reference completion: reuse identical saved latents for
  the temporal64 candidate; report decoder-only timing separately from total runtime.
- V5F roadmap reflects this checkpoint; V5E is archived. No new generation was
  launched during the October 25 roadmap update.


## Final comparison — 2026-10-25

The candidate finished using the exact saved normalized latents; no diffusion rerun.
Source artwork, model files and installed dependency source hashes all matched the
October 21 records. The resumed preflight recorded about 624 GiB free disk.
Both runs use the same prepared image, prompt, model, seed and latent tensor.
Only temporal tile size changed (32 → 64); overlap and spatial tiling stayed fixed.

| Output | Identity | Anatomy | Framing | Temporal | Shuffle | Total | Timing |
|---|---:|---:|---:|---:|---:|---:|---|
| Reference: temporal32 | 1 | 0 | 2 | 0 | 1 | 4/10, fail | 640.363 s full generation |
| Candidate: temporal64 | 1 | 0 | 2 | 0 | 1 | 4/10, fail | 144.872 s VAE load + decode + MP4 write only |

**0/2 passed.** The candidate is not an improvement under the existing rubric.
Seeds 123 and 2026 were not run because the acceptance gate failed. The entire
follow-up used one full generation and one additional controlled decode, producing
two clips; no further generation search was started. All historical results remain.

Timing scopes differ: candidate timing excludes text encoding, image encoding and
diffusion; it cannot be compared to 640.363 s as a speedup. Reference log reports
93.2 s for VAE loading/decoding before MP4 writing; dates and system activity differ,
so neither timing is a controlled end-to-end benchmark.

MLX peak allocated memory: reference 25,595,729,288 bytes; candidate 10,946,307,968.
Process peak RSS: reference 3,530,686,464 bytes; candidate 2,638,725,120.
Candidate runs decoder only. These counters are distinct, not additive, and not
measurements of total system memory or swap.

### Visual findings and interpretation

- All 49 frames of each clip inspected in sequential sheets. Detailed rendered
  frames inspected for severe defects (reference5; candidate25 and41).
- Preparation fixes input cropping/transparency. Both generated clips retain full
  body framing within the canvas; this does not solve anatomy or motion.
- Hair/clothing palette remains recognizable, but face and body proportions drift.
- Severe fused, fragmented and distorted limbs/shoes: frames1–6,13–18,25–26,
  29–33 and37–42. Hands and face break apart; legs/torso repeatedly squash.
- Abrupt pose changes alternate with near-held frame pairs. Kicks and knee lifts
  do not establish coherent repeated heel-toe/sliding Shuffle footwork.
- Larger temporal tiles retain the same severe early and later defects. Mean
  absolute decoded RGB pixel difference across clips is 1.080/255; that is a
  descriptive comparison, not a perceptual quality measure.
- Therefore removing temporal tile restarts alone is insufficient. This does not
  rule out spatial tiling, all-at-once VAE behavior, or defective generated latents.
  No additional implementation root cause has been proven.

Both clips pass ffmpeg full decoding, independent OpenCV count and metadata checks:
512×512,49 frames,24 FPS,2.041667 s. Browser playback was initiated on both, observed
advancing around0.231 s, and verified ended at2.041667 s with readyState4/no errors.
This confirms playback, not a human real-time or expert choreography evaluation.
Agent rubric scores are coarse qualitative judgments; no exact Shuffle claim.

### Deliverables and recommendation

- [Local comparison player](../../outputs/v5-step3-quality-20261021/index.html)
- [Reference MP4](../../outputs/v5-step3-quality-20261021/temporal32-seed42/shuffle.mp4)
- [Candidate MP4](../../outputs/v5-step3-quality-20261021/temporal64-seed42/shuffle.mp4)
- [Reference all frames](../../outputs/v5-step3-quality-20261021/temporal32-seed42/all-frames.png)
- [Candidate all frames](../../outputs/v5-step3-quality-20261021/temporal64-seed42/all-frames.png)

Keep explicit preparation for future tests. Retain temporal32 as the diagnostic
reference; do not promote temporal64 as a quality fix or change application presets.
No acceptable animation baseline exists yet.

Smallest useful next experiment (not executed): decode the same saved latents once
with a full512 px spatial tile, keeping temporal64 and every other variable fixed.
Monitor memory on the24 GiB Mac; preserve a failure if it cannot fit. This isolates
spatial tile context without another diffusion run. If defects persist, prioritize
a small official cached-VAE versus MLX numerical parity check before prompt/seed
searches. Neither hypothesis is a proven fix.

### Reproduction and checks

Prepare a new copy (existing outputs deliberately refuse overwrite):

```bash
PYTHONPATH=src .venv-mlx/bin/python -m dancing_angels_ai.preparation \
  --image assets/woman-1.png --output outputs/reproduction/woman-prepared.png
```

Recorded reference command/settings: per-run `metadata.json`. The ignored
`run.py --temporal-frames 32 --seed 42` recorder reproduces reference settings;
use a fresh output directory rather than overwrite the completed run.
`decode_candidate.py` documents the exact candidate decode from saved normalized
latents and refuses to reuse its existing output directory. Both scripts and
complete dependency snapshots are preserved alongside the results.

Final checks:27 tests passed,1 optional CUDA test skipped; `git diff --check` passed.
Production change is opt-in character preparation under `src/dancing_angels_ai/`;
API, website, model, dependency installation and generation defaults unchanged.
V5G records TESTED / Quality below target; V5F image and prompt archived.

Direct reference reproduction (new output path; same settings):

```bash
PYTHONPATH=src .venv-mlx/bin/python -m dancing_angels_ai create \
  --image outputs/v5-step3-quality-20261021/woman-prepared.png \
  --model models/Wan2.2-TI2V-5B-MLX-Q4 --action dance \
  --prompt 'The same illustrated character performs a shuffle dance in place, alternating quick heel-toe steps and sliding their feet, with gently swinging arms. Full body and feet visible throughout, stable character appearance, fixed camera.' \
  --width 512 --height 512 --frames 49 --steps 40 \
  --seed 42 --guide-scale 5.0 --tiling aggressive \
  --output outputs/reproduction/woman-reference.mp4
```

The verified existing model config supplies shift 5, full negative prompt and
24 FPS; installed scheduler defaults to UniPC. This reference is diagnostic,
not an approved animation preset. Metal access is required. The saved experiment
metadata also retains the explicit scheduler/shift/negative-prompt invocation.
