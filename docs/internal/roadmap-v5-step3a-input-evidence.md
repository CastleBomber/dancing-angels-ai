# Step 3A — image preparation and conditioning, 2026-10-26

**PASS for the prepared woman reference and tested input path.** Image encoding
and conditioning agree with official Wan within predeclared tolerances. Fixed a
confirmed integration gap: normal MLX generation previously bypassed the existing
preparation utility. Motion remains below target; this is not a Step 3B pass.

## Gates and results

| Check | Acceptance | Measured result |
|---|---|---|
| Source/preparation | Source unchanged; full figure, opaque background, correct proportions | Pass; prepared PNG matches previous reference byte-for-byte |
| RGB normalization/layout | Absolute tolerance1e-6 | Exact match; `[1,1,512,512,3]`, range[-1,1] |
| Encoder weight conversion | All expected tensors present, correct shapes/values | All86 match original trained weights exactly after layout conversion |
| Small trained encoder | FP32 atol/rtol1e-3, declared before execution | Max error3.51667e-6; mean9.69478e-7 |
| Full512 trained encoder | Same tolerance; run after small fixture passes | Max error1.28746e-5; mean1.61001e-6 |
| Masks/timesteps | Exact agreement | Pass;3328 tokens,256 frozen first-frame tokens |
| Conditioning blend | Same input, absolute tolerance1e-6 | Exact match; first latent preserved, future latents unchanged by restoration |
| Actual adapter input | Raw and prepared woman reach identical verified pixels | Pass; captured commands, no diffusion launched |
| Application regression suite | Required checks pass |29 passed,1 opt-in CUDA test skipped |

Protocol was saved before numerical testing in
`outputs/v5-step3a-input-20261026/protocol.json`. Tests ran sequentially. No new
animation was generated: the adapter correction produces exactly the prepared
input already used in the existing49-frame woman video. Repeating that generation
would not test a new model input or explain its remaining motion defects.

## Confirmed problem and focused correction

Before: API upload bytes → saved original → `MlxRuntime.generate` →
`MlxVideoBackend.generate` → dependency `preprocess_image` → encoder.
The backend passed the raw portrait directly; the preparation utility was opt-in.
For woman-1, direct RGB conversion discards alpha and the square center crop cuts
off the lower legs. Earlier experimental runners explicitly prepared the image,
so this gap does **not** explain the latest prepared woman's4/10 motion score.

After: the same backend prepares inputs before constructing the MLX command.
Transparent/differently sized images use the existing alpha bounds, proportional
LANCZOS resize and white composition. Rectangular targets are supported, using
the same proportional margin. EXIF orientation is applied before fitting.
Already sized, correctly oriented RGB images pass through unchanged, avoiding
double padding of saved references. Originals remain untouched; each run retains
a unique `*-input-*/preparation.json` and, when needed, `prepared.png` beside its
output. A running API needs restarting to load this backend change; no running
server was restarted or website altered in this task.

Regression tests check that the actual backend command receives visible feet and
white-background RGB pixels, source bytes survive, metadata exists, an existing
reference is not padded twice, and a rectangular EXIF-oriented input is fitted
correctly. An initial test failed only because macOS `/var` and `/private/var`
paths were compared without resolving aliases; the corrected test passes.

No image-format request is imposed on users. Source PNGs remain PNGs. LANCZOS is
unchanged; nearest-neighbor was not introduced. No model, prompt, scheduler,
guidance, steps, seed or tiling defaults changed. API endpoints and website code
were untouched. Existing man experiments, including seed123, remain preserved.

## Numerical procedure and boundaries

Sources inspected and saved locally:

- [Official TI2V pipeline](https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/wan/textimage2video.py): SHA256 `228f2fabf23014ed41ec6b8cd713d5be7371bb558501c71a62a0258b491a877b`.
- [Official VAE](https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/wan/modules/vae2_2.py): SHA256 `eab5ce4aa1ce03af2978f2a8e8364c419f5fbb8535d265ac86b0b02ddcf0c1f6`.
- [Official mask utilities](https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/wan/utils/utils.py): SHA256 `905850d9814ac99222b4dbb28016abcd6306e5ca161493b498b1c4afb5a99e89`.

The original trained checkpoint's encoder/conv1 weights loaded strictly into the
official PyTorch CPU encoder. The existing converted encoder loaded through the
installed MLX loader; its permissive loader was independently checked for every
expected key, shape and value. No missing or random encoder weights were found.

Compared a32×32 center crop first, then the complete512×512 prepared image, using
identical FP32 inputs and weights. Official patchification, encoder temporal
cache and independently extracted official mean/std constants produced normalized
latents `[1,1,32,32,48]`; MLX agreed. Timings excluding weight loading:0.194 s small,
2.012 s full. Peak MLX allocation3,817,056,548 bytes; this is not total system RAM.

For conditioning, used the official `masks_like` function extracted verbatim,
the installed MLX `build_i2v_mask`, and source-audited initialization/timestep/
restoration equations. At latent shape `[48,13,32,32]`, first-frame mask is zero,
future-frame mask one. Tokens sample the2×2 patch grid in temporal/spatial order.
Image latent occupies time0; later positions retain identical test noise. A
post-update fixture verifies first-frame restoration and preservation of future
latents. Installed CFG code duplicates the same time-token row for conditioned
and unconditioned batches, matching the two official forward calls semantically.

This is component/math parity and an adapter-command capture, **not** a complete
official GPU generation comparison or a live transformer interception. Official
CUDA mixed precision, text embeddings, denoising, attention, Q4 behavior and
scheduler output were not numerically compared. The same NumPy noise was supplied
to both blend calculations; identical seeds across different RNG libraries are
not assumed to create identical noise. Opaque images with complex backgrounds
have no foreground segmentation; arbitrary artwork is not yet validated.

## Reproduction and artifacts

Environment: M4 Pro24GiB, macOS26.6.2 arm64, Python3.11.15, MLX0.32.0,
mlx-video0.0.1, PyTorch2.13.0; existing model/config and environment retained.
Free disk at start663,311,519,744 bytes. Metal computations succeeded.

- Source woman SHA256: `8bdcd679d1d838809a730c2813569e7a798f716799ac15075ae90feb8f548aab`.
- Prepared PNG SHA256: `b125154e9317a4c71a868b9f9d34c6ad933d23a461a509a94ba9f62041959db1`.
- Preparation: alpha bounds158,581,859,1807; fitted238×416 at137,48;
  white512×512 canvas, margin48, LANCZOS. Inspected full-size prepared image.
- Original model: `models/Wan2.2-TI2V-5B/Wan2.2_VAE.pth`.
- Converted model: `models/Wan2.2-TI2V-5B-MLX-Q4/vae.safetensors`.

Local ignored folder `outputs/v5-step3a-input-20261026/` retains protocol,
official sources, check scripts, logs, complete results/hashes, prepared image,
exact model input, both encoder-output arrays, adapter command captures and
initial/final test records. They are intentionally not uploaded with user assets.
The tracked report preserves the results and limitations.

Executed from repository root:

```bash
PYTHONPATH=outputs/v5-step3-spatial-20261026/test-deps .venv-mlx/bin/python -u outputs/v5-step3a-input-20261026/check_input.py
.venv-mlx/bin/python outputs/v5-step3a-input-20261026/check_adapter.py
.venv-mlx/bin/python -m pytest -q
```

The first script refuses to overwrite its prepared image. To repeat, copy its
script, protocol and official utility source into a fresh sibling output directory.
It depends on the preserved official VAE source and isolated einops0.8.1 from the
earlier diagnostic. GPU access is required; models must be available locally.
Application tests use fixtures and do not launch diffusion. The saved check script
is single-use diagnostic evidence; reusable application preparation lives under
`src/dancing_angels_ai/`.

## Checkpoint decision

- **3A Input: passed** for woman reference, preparation integration and tested
  FP32 encoder/conditioning fixtures. No image-conditioning defect remains in
  those tested paths.
- **3B Motion: below target**, prior4/10 result unchanged. Next bounded work
  should investigate denoising/quantization or a simple-motion control, with a
  predeclared budget and acceptance criteria. Neither hypothesis is confirmed.
- **3C Reliability: pending**. Requires passing motion across seeds and character
  examples, including simpler drawings; a single image cannot establish this.

Stopped after3A. V5I shows these separate gates; V5H image/prompt archived.

## Subsequent Step 3B checkpoint — 2026-10-27

Input checks above remain valid. Two controlled motion trials completed without
meeting the visual bar. See [Step3B evidence](roadmap-v5-step3b-motion-evidence.md).
