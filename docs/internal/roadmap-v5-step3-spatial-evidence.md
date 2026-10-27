# Step 3 spatial decoding investigation — 2026-10-26

**Experiment complete; visual quality still fails.** Whole-frame decoding did not
remove distorted anatomy or jerky motion. Two small numerical comparisons agree
with the official decoder; no implementation defect was confirmed. No production
code, API, website, model, or generation default was changed.

## Protocol and inputs

Read AGENTS.md, current status, woman handoff and prior follow-up evidence first.
Budget recorded before execution: at most two candidate decodes, with a second
only for a confirmed decoder correction; two additional seeds only after a pass.
Used one candidate decode, zero diffusion generations and zero additional seeds.
Preserved all earlier experiments, including the historical man seed-123 clip.

Control: `outputs/v5-step3-quality-20261021/temporal64-seed42/`.
Candidate: `outputs/v5-step3-spatial-20261026/spatial512-temporal64-seed42/`.
Both reuse `outputs/v5-step3-quality-20261021/temporal32-seed42/normalized-latents.npy`.
Only spatial tile size changed, 256 → 512 pixels. Temporal64, temporal overlap8
and spatial overlap64 stayed fixed. At this input size, tile512 bypasses tiling
and decodes the entire latent volume. Saved latents are diagnostic reuse, not a
requirement for animating future images.

- Source woman-1 SHA256: `8bdcd679d1d838809a730c2813569e7a798f716799ac15075ae90feb8f548aab`.
- Prepared input SHA256: `b125154e9317a4c71a868b9f9d34c6ad933d23a461a509a94ba9f62041959db1`.
- Saved latent SHA256: `b9b3b34f710041faf5edc4b87774d5d3b294bb6bad6f703ecf054751da919484`.
- Existing Wan2.2 TI2V 5B MLX Q4, group64; 512×512, 49 frames, 24 FPS,
  40 diffusion steps, seed42, guidance5, UniPC, shift5. No diffusion rerun.
- Exact inherited prompt: “The same illustrated character performs a shuffle dance
  in place, alternating quick heel-toe steps and sliding their feet, with gently
  swinging arms. Full body and feet visible throughout, stable character appearance,
  fixed camera.” Full unchanged negative prompt and model configuration are in
  candidate `metadata.json` and the preceding experiment's metadata.

Preflight confirmed source/model/dependency hashes match the earlier snapshots,
macOS26.6.2 arm64 on M4 Pro with 24GiB physical memory and 665,275,518,976 free disk
bytes. Metal execution succeeded. Python3.11.15, MLX0.32.0, mlx-video0.0.1,
torch2.13.0, NumPy2.4.6, Pillow12.3.0, OpenCV5.0.0.93, transformers5.14.1.
The candidate metadata retains the older environment snapshot separately from
the fresh `resume_preflight`; its inherited free-disk field is not today's probe.
Paths resolve in the renamed repository; historical records remain unchanged.

## Results and acceptance

Existing rubric: five dimensions scored 0–2; pass requires ≥8/10, no zero and
Shuffle2. Robustness additionally requires three passing seeds.

| Decoder | Load/decode/write | Identity | Anatomy | Framing | Continuity | Shuffle | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Spatial256 / temporal64 control | 144.872 s | 1 | 0 | 2 | 0 | 1 | 4/10 fail |
| Spatial512 / temporal64 candidate | 56.145 s | 1 | 0 | 2 | 0 | 1 | 4/10 fail |

These are decoder-only timings, not full generation times or controlled runtime
benchmarks. The original woman diffusion reference took 640.363 s end to end.
Candidate supervisor time including verification was 61.612 s.

All49 candidate frames were reviewed in sequence/contact sheets, with frame25
inspected at full size. Comparison against the previously reviewed control found
the same face/limb collapse, fused or enlarged shoes, body squashing, ghosting,
abrupt pose changes and held frame pairs. Full-body framing remains intact.
Kicks/knee lifts do not establish coherent heel-toe Shuffle or exact choreography.
Mean absolute decoded RGB difference versus control: 0.799698 on a 0–255 scale.
This small difference is not itself a quality metric. Agent scores are qualitative;
contact sheets can miss subtle transient details. Browser playback completion is
technical evidence, not proof of visual acceptability.

FFmpeg full decode, ffprobe and OpenCV checks passed: 49 frames, 512×512, 24 FPS,
2.041667 s. Both videos played to their ends in the in-app browser, with no media
error, readyState4 and correct dimensions. Candidate MP4 SHA256:
`78eb8669756c85d4f559b5584bd4a840d7a6a9726d433efed373b09cb206b657`.

MLX peak allocation: 25,246,228,088 bytes (23.51GiB); process peak RSS:
2,644,787,200 bytes (2.46GiB). These measure different things and must not be added
or interpreted as total system memory. A 20GiB MLX limit and 512MiB cache were
requested, but observed allocation exceeded that requested limit; it was not a
reliable hard cap. No OOM occurred. Whole-frame decoding is not recommended as
the default given unchanged quality and high measured allocation.

## Decoder correctness checks

Compared the installed MLX implementation against
[official Wan2.2 VAE source](https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/wan/modules/vae2_2.py),
downloaded and preserved with SHA256
`eab5ce4aa1ce03af2978f2a8e8364c419f5fbb8535d265ac86b0b02ddcf0c1f6`.

| Fixture | Maximum absolute difference | Result |
|---|---:|---|
| Same random weights, small full decoder, 17 frames | 1.89245e-6 | All frames agree at atol/rtol1e-4 |
| Original trained checkpoint versus converted weights, saved-latent crop, 9 frames | 1.76840e-5 | Agree at atol/rtol1e-3 |

The trained fixture uses the first3 temporal latent positions and spatial crop
15:17,15:17, producing nine32×32 RGB frames. Mean difference was 6.27177e-7.
Original PyTorch weights loaded strictly; both implementations received the same
denormalized input. This tests decoder math and conversion on a small fixture,
not independent latent normalization, full-resolution behavior, image encoding,
conditioning, denoising or every input. These checks weaken the decoder-bug
hypothesis; they do not prove the entire pipeline correct or the model at fault.

The first synthetic test failed because `einops` was unavailable; its log remains.
Installed einops0.8.1 only into the ignored experiment's `test-deps/`, then reran
successfully. No application dependency changed. No confirmed defect justified
a patch, a second candidate, or further seeds. Existing application tests were
not rerun because application code was unchanged; prior 27-pass results are historical.

## Artifacts and reproduction

[Playable comparison](http://127.0.0.1:8766/v5-step3-spatial-20261026/)
(requires the existing local static server). Persistent files:

- [Before MP4](../../outputs/v5-step3-quality-20261021/temporal64-seed42/shuffle.mp4)
- [After MP4](../../outputs/v5-step3-spatial-20261026/spatial512-temporal64-seed42/shuffle.mp4)
- [All49 frames](../../outputs/v5-step3-spatial-20261026/spatial512-temporal64-seed42/all-frames.png)
- [Settings/environment](../../outputs/v5-step3-spatial-20261026/spatial512-temporal64-seed42/metadata.json)

Ignored experiment root also contains protocol/preflight, supervisor timing,
generation log, verification JSON, individual frames, contact sheet, review,
browser-playback JSON, comparison summary, official source, parity scripts,
parity results/logs and trained numerical output arrays. These large/local
artifacts are intentionally absent from Git; this report preserves conclusions.

Executed from repository root:

```bash
.venv-mlx/bin/python outputs/v5-step3-spatial-20261026/decode_spatial.py
PYTHONPATH=outputs/v5-step3-spatial-20261026/test-deps .venv-mlx/bin/python outputs/v5-step3-spatial-20261026/parity.py
PYTHONPATH=outputs/v5-step3-spatial-20261026/test-deps .venv-mlx/bin/python outputs/v5-step3-spatial-20261026/trained_parity.py
```

The decode script refuses an existing result directory. For a fresh reproduction,
copy the experiment script and preflight JSON into a new sibling output directory;
never delete existing results. Metal-capable execution is required. Its preserved
opening docstring incorrectly says temporal-only; actual settings/code and this
report record spatial-only. Scripts remain immutable experiment evidence.

## Recommendation

Keep Step3 TESTED / quality below target. The requested spatial test and bounded
decoder investigation are complete; the visual-quality problem is unresolved.
Retain prepared-input reference settings for diagnosis; no production-quality
baseline is established. Smallest useful next experiment: compare image-encoder
output and conditioning tensor construction against the official implementation
on a small deterministic fixture before spending time on another generation.
If those agree, investigate denoising/quantization next. These are hypotheses,
not established causes or promises that a further prompt will fix quality.

V5H records these results. V5G image/prompt are archived; steps1,2,4 remain
complete and steps5–8 planned. No API or website work was performed.

## Subsequent checkpoint — Step3A

The proposed image-encoder/conditioning checks were completed on2026-10-26.
They passed for the woman reference; a separate backend preparation bypass was
fixed. See [Step3A evidence](roadmap-v5-step3a-input-evidence.md). Spatial results
above remain unchanged; motion still fails.
