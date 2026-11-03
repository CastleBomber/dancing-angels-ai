# Step 3B Q8 investigation — 2026-10-28

**Q8 conversion passed; visual comparison was not completed. Step3B remains
below target.** Two process launches stopped at the experiment's memory guard
while encoding text, before the Q8 transformer loaded or diffusion began. There
is no new MP4, contact sheet, visual score or seed validation. This is not a
confirmed OS out-of-memory failure or proof that Q8 cannot run on this Mac.

## Scope and predeclared controls

Read AGENTS.md, woman handoff, current status, Step3A/3B evidence and the original
rubric. User authorized one Q8 comparison followed by two fixed additional seeds
only if the first candidate passed; maximum three sequential generations.
Original models, images and experiments (including historical man/EDM results)
are preserved. No cloud service, model download, application/API/website change,
Git commit or GitHub push was performed.

Reference: `outputs/v5-step3-quality-20261021/temporal32-seed42/shuffle.mp4`.
Same original checkpoint and prepared woman image;512×512,49 frames,24 FPS,
40 steps,seed42,guidance5,UniPC,shift5. Aggressive VAE tiling:spatial256/overlap64,
temporal32/overlap8. Change only targeted transformer quantization4→8 bits,
group64. Same nonquantized tensors, text encoder, VAE, full negative prompt and
model settings. Allocator-only retry change is disclosed below.

Exact positive prompt:

> The same illustrated character performs a shuffle dance in place, alternating quick heel-toe steps and sliding their feet, with gently swinging arms. Full body and feet visible throughout, stable character appearance, fixed camera.

Both runs retain complete negative prompt and settings in metadata. Acceptance
unchanged:identity, anatomy, framing, continuity, Shuffle each0–2; total≥8,
no zeros, Shuffle2. Seed123 then2026 were conditional on a visual pass; neither
was run. Count both aborted launches conservatively as two process attempts;
zero videos generated and no third attempt started.

## Feasibility and preserved Q8 model

M4 Pro24GiB, macOS26.6.2 arm64, Python3.11.15, MLX0.32.0, mlx-video0.0.1.
Metal computation succeeded. Roughly620.6GiB disk free at preflight. Initial
memory inspection reported55% free and6.94GiB system swap used. Original source,
prepared image and Q4 file hashes match recorded evidence; dependency-source
hashes match October27. Absolute paths resolve in the renamed repository.

Prepared image SHA256:
`b125154e9317a4c71a868b9f9d34c6ad933d23a461a509a94ba9f62041959db1`.
Original woman SHA256:
`8bdcd679d1d838809a730c2813569e7a798f716799ac15075ae90feb8f548aab`.

Converted original checkpoint tensors individually, using installed sanitization
and MLX quantization; did not requantize Q4 values. Original tensors cast to BF16
as in existing conversion. All300 targeted layers reproduce existing Q4 weights,
scales and biases exactly. All526 remaining tensors are unchanged, including the
computed positional-frequency buffer. Q8 has1426 tensors, validated container
length/offsets, and identical configuration except quantization.bits=8.

| Item | Result |
|---|---:|
| Q4 transformer bytes |2,945,950,389|
| Q8 transformer bytes |5,399,618,813|
| Extra transformer storage |2,453,668,424 bytes (~2.29GiB)|
| Successful conversion elapsed |63.533s|
| Conversion MLX peak allocation |8,829,297,692 bytes|
| Mean per-layer relative L2 error vs BF16, Q4 |0.090762|
| Mean per-layer relative L2 error vs BF16, Q8 |0.007134|

The error figures are unweighted means across300 matrices, **not visual-quality
scores**. Q8 represents weights more closely; no evidence yet connects that
improvement to the animation defects.

Model: `models/Wan2.2-TI2V-5B-MLX-Q8/`. T5 and VAE are symlinks to unchanged Q4
files, avoiding duplicate storage and guaranteeing the same encoder/decoder
weights. Full original shard hashes, Q4/Q8 hashes and per-layer measurements are
in `conversion.json`. Preserve the Q4 target directory when using these links.

First conversion stopped on a tensor-inventory assertion: the original checkpoint
omits the model-generated `freqs` buffer stored by the normal MLX converter.
The corrected converter copies the identical Q4 buffer. Failed log/script and
empty incomplete model directory are preserved; no production defect was found.

## Launch outcomes and memory limit

Before launch, recorded1800s timeout, minimum30GiB free disk and abort if sampled
system swap increased more than8GiB. System memory was sampled every15s. The
estimate allowed one monitored trial but did not establish a memory-fit guarantee.
The text encoder is loaded before the Q8 transformer, and its unchanged loader
upcasts BF16 T5 weights to FP32 (about21.16GiB for weights alone).

| Launch | Elapsed | System swap increase | Last reported free memory | Outcome |
|---|---:|---:|---:|---|
| Original allocator policy |15.112s|13.29GiB|32%|Guard terminated process during text encoding|
| Cache capped256MiB |15.536s|10.19GiB|18%|Same guard; stopped during text encoding|

After documenting the first failure, made exactly one technical retry with
`mx.set_cache_limit(256 * 1024 * 1024)`. This changes temporary allocator caching,
not model weights, precision, prompt, math or RNG. It was confined to the ignored
experiment wrapper. No guard was relaxed. Both child processes exited-15 after
the recorder sent SIGTERM; neither reached transformer loading, initial latent
capture or a denoising step. Both failure folders and logs are preserved.

Swap figures are system-wide and include other applications; the reported free
percentage is from macOS memory_pressure, not a proof that all working sets fit.
The8GiB threshold is an experiment policy, **not a measured hardware limit**.
No claim is made that the machine would inevitably crash without it. MLX/process
peak counters were unavailable because termination prevented final instrumentation;
sampled system data is retained. These15-second failures are not video-generation
runtime benchmarks. The previous Q4 reference successfully used this same T5
stage; differences in current system pressure/caching have not been isolated.

## Quality and playable artifacts

| Configuration | Identity | Anatomy | Framing | Continuity | Shuffle | Result |
|---|---:|---:|---:|---:|---:|---|
| Historical Q4 reference |1|0|2|0|1|4/10; below target|
| Q8 |—|—|—|—|—|Not evaluated; no output frames|

Revisited all49 reference frames: fragmented faces/hands, merged or disconnected
legs/shoes, abrupt pose changes and held pairs persist. Full-body framing remains
intact; generic kicks do not establish repeated coherent Shuffle footwork.
No exact choreography claim. Reference playback verification is recorded in the
local artifact folder. There are no Q8 frames to decode, play or visually assess;
per-run verification/review files explicitly record this absence rather than
inventing a score. Visual assessment remains an agent's frame-sequence review,
not a new human choreography rating.

- [Local status/player](http://127.0.0.1:8766/v5-step3b-q8-20261028/)
- [Persistent HTML](../../outputs/v5-step3b-q8-20261028/index.html)
- [Historical before MP4](../../outputs/v5-step3-quality-20261021/temporal32-seed42/shuffle.mp4)
- [Historical all49 frames](../../outputs/v5-step3-quality-20261021/temporal32-seed42/all-frames.png)
- [Machine-readable results](../../outputs/v5-step3b-q8-20261028/summary.json)

## Decision and smallest useful next experiment

**Do not change the application's Q4 default or mark3B passed.** The Q8 comparison
is unresolved because the recorded memory guard prevented reaching it. Q4
quantization remains a hypothesis; conversion checks do not establish the
cause of distorted anatomy/jitter.3A remains passed in its recorded scope;
3C remains pending.

Next local diagnostic: a **text-encoding-only memory experiment**, no diffusion.
Investigate processing FP32 T5 one block at a time, releasing unneeded weights,
while retaining exact tokenization, arithmetic and RNG consumption. Verify outputs
against the existing implementation on a controlled fixture before attempting the
full prompt. Record full-prompt memory and resulting embeddings. Only after this
fits the agreed memory envelope should the original Q8 comparison resume.
Do not silently lower T5 precision or change the prompt: either would add a second
quality variable. This is proposed work, not an implemented optimization.

A different model also deserves one independent capability benchmark if the user
chooses cloud costs/uploads or larger hardware. Its purpose would be to assess
whether the same artwork/action can meet the rubric; it would **not** isolate Q4
quantization. No provider/model is newly selected or tested in this experiment,
and local Wan work should not expand into an unlimited search.

## Reproduction and preservation

Ignored experiment folder: `outputs/v5-step3b-q8-20261028/`. Contains protocol,
preflight, conversion attempts/logs/results, instrumentation, two aborted run
folders, complete metadata, system-memory samples, explicit unavailable-output
verification, review records, summary and local status player.

Commands executed from repository root (Metal access required):

```bash
.venv-mlx/bin/python outputs/v5-step3b-q8-20261028/preflight.py
.venv-mlx/bin/python -u outputs/v5-step3b-q8-20261028/convert_q8.py
.venv-mlx/bin/python -u outputs/v5-step3b-q8-20261028/run.py --seed 42
```

The first run was archived as `seed42-aborted-text-encoding`; the retry remains
`seed42`. Scripts refuse existing model/run output directories. To reproduce,
copy experiment scripts/protocol/preflight/conversion records to a fresh sibling
output directory and reuse the preserved Q8 model; do not overwrite evidence or
blindly repeat the failed launches. The initial wrapper is saved separately.
`run.py` enforces a passing seed42 review before other seeds can execute.

No application code changed; no regression-suite rerun is claimed. Experiment
scripts compile; conversion/provenance/container checks passed. V5K documents
the memory-guard stop, with V5J image/prompt archived. Step3 remains TESTED /
motion below target. Stopped after the bounded3B investigation.

## Subsequent scope update — 2026-11-02

The user now prioritizes walk, run and jump before dance or reference-animation
work. No new experiment accompanied this update. The memory-guard results above
are unchanged; Q8 quality remains unknown.
[New movement plan and prospective criteria](roadmap-v5-basic-movements-plan.md).
