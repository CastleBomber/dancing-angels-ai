# Step 3B motion investigation — 2026-10-27

**Bounded experiment complete; Step3B still fails visual quality.** Neither
candidate improved the recorded rubric score. Two generations completed; stopped
without additional seeds, speculative code patches or a model switch.

## Scope and acceptance

Read AGENTS.md, current roadmap, woman handoff and Step3/3A evidence. Keep the
verified woman input and existing Wan2.2 TI2V5B MLX Q4 model. Preserve historical
man results, including the seed123 EDM result. Budget: at most two sequential
video generations, no additional seeds and no unrelated API/website work.

Reference: `outputs/v5-step3-quality-20261021/temporal32-seed42/shuffle.mp4`.
Reference settings:512×512,49 frames,24 FPS,40 steps,seed42,guidance5,UniPC,shift5;
aggressive VAE tiling spatial256/overlap64,temporal32/overlap8. Same character-neutral
Shuffle prompt, complete negative prompt and model configuration retained in each
run's metadata. Source woman SHA256:
`8bdcd679d1d838809a730c2813569e7a798f716799ac15075ae90feb8f548aab`.
Prepared input SHA256:
`b125154e9317a4c71a868b9f9d34c6ad933d23a461a509a94ba9f62041959db1`.

Existing rubric: identity, anatomy, framing, temporal consistency and recognizable
Shuffle each0–2. Require ≥8/10, no zeros and Shuffle2. Successful decoding/playback
does not satisfy visual acceptance. Passing one seed would complete only3B;
cross-seed/image reliability remains3C.

## Numerical checks before generation

Saved protocol/tolerances before testing in the ignored experiment folder.
Both schedules used40 steps. Scheduler update tolerance:atol/rtol1e-4;
sigma tolerance1e-6; timesteps exact. Transformer FP32 tolerance:atol/rtol1e-3.

| Check | Largest absolute difference | Result |
|---|---:|---|
| UniPC shift5,40 updates |5.96046e-7| Pass |
| UniPC shift3,40 updates |9.53674e-7| Pass |
| Sigma schedule, either shift |5.96046e-8| Pass; integer timesteps identical |
| Small two-block transformer |1.78814e-7| Pass |
| Cached text/KV/RoPE transformer path |1.78814e-7| Pass |
| Guidance5 combined predictions |8.04663e-7| Pass |

Scheduler inputs were identical deterministic predictions and initial samples.
The transformer fixture used identical random weights, a nonzero output head,
per-token timesteps, padded text and the two CFG branches. It exercised patch
ordering, time modulation, attention, output rearrangement and cache reuse.
Official FlashAttention dispatch was replaced with PyTorch CPU SDPA for this
small fixture. It does not establish CUDA mixed-precision equivalence, correctness
of every trained parameter or full-resolution Q4 denoising behavior.

Four actual trained matrices were checked: first/last block self-attention Q and
FFN output projection. Requantizing the original BF16 weights reproduced stored
Q4 weights, scales and biases exactly. Relative weight L2 quantization error was
8.62%,9.63%,9.33%,9.21%, respectively. These errors are measurements, not proven
causes of visible defects or a quality acceptance threshold. No conversion bug
was found in the sampled matrices; this is not a full-model numerical audit.

Official sources:
[UniPC](https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/wan/utils/fm_solvers_unipc.py),
[transformer](https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/wan/modules/model.py),
[TI2V pipeline](https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/wan/textimage2video.py).
Exact fetched files and hashes are retained locally. diffusers0.35.1 was installed
only into the ignored test-deps directory; the application environment is unchanged.

No confirmed implementation defect justified a code patch. Settings trials below
test hypotheses rather than imply the root cause was established.

## Controlled trials

1. **Shift3**: change only shift5→3. Official TI2V documentation recommends shift3
   for480p; testing it at512 square is an explicitly recorded extrapolation.
   Hypothesis: a more appropriate schedule may reduce abrupt poses and anatomy
   collapse. Same guidance5 and all other reference settings. Timeout1800s,
   one generation, no retries, same visual bar.

   Result:4/10, unchanged. All49 frames reviewed, with frame14 inspected at512.
   Severe face/hand/leg fragmentation and disconnected shoes persist, with
   abrupt pose changes and held frame pairs. Full-body framing remains intact.
   Reference and candidate played to their ends in the browser with no errors.
2. **Guidance3**: after the first trial failed, change only guidance5→3 against
   the original reference; restore shift5. Hypothesis: weaker guidance may reduce
   exaggerated anatomy while retaining Shuffle. No new prompt or image. This is
   the final allowed generation, regardless of its outcome.

First run timing:661.108 monotonic seconds, but8874.658 timestamp wall seconds
(17:31:33→19:59:28 PDT). The log contains large clock gaps; their cause was not
established. Python's monotonic timeout did not expire. Do not treat this run as
a speed benchmark. Recorded peak MLX allocation25,595,729,288 bytes and peak
process RSS3,537,895,424 bytes measure different things, not total system memory.

Second run:603.855 monotonic seconds,603.884 timestamp wall seconds. Peak MLX
allocation25,595,729,288 bytes; peak process RSS5,679,054,848 bytes. Both runs
completed40 finite denoising updates. These counters do not establish total RAM
or swap use. No controlled speedup claim is justified.

## Visual results and verification

| Clip | Identity | Anatomy | Framing | Continuity | Shuffle | Total | Full-run monotonic time |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original shift5 / guidance5 |1|0|2|0|1|4/10 fail|640.363 s, historical |
| Attempt1 shift3 / guidance5 |1|0|2|0|1|4/10 fail|661.108 s* |
| Attempt2 shift5 / guidance3 |1|0|2|0|1|4/10 fail|603.855 s |

*Attempt1 had the clock gaps described above; wall time was approximately148min.

All49 frames of each new clip were inspected in ordered contact sheets. Detailed
512px review included shift3 frame14 and guidance3 frame5. Also revisited the
reference's all-frame sheet. Both candidates preserve overall palette and hair,
but faces change shape, hands fragment and legs fuse/disconnect. Guidance3 has
skirt-like merged legs at1–2,7–10,17–20,25–26,34–35,37–38 and41–42. Severe fragmentation
appears early and later, not just at one transition. Full-body framing is retained.
Repeated/near-held frame pairs alternate with abrupt pose jumps. Kicks and knee
lifts do not establish coherent repeated heel-toe Shuffle. No exact choreography
claim is supported. Lower guidance does not fix the observed defects.

All three comparison videos were played in the in-app browser, observed advancing
around0.259s and verified ended at2.041667s with readyState4,512×512 and no media
error. Both new clips independently pass FFmpeg full decoding, ffprobe metadata
and OpenCV49-frame checks at24FPS. Playback verification is technical evidence;
visual scoring remains an agent's coarse frame-sequence assessment, not expert
real-time choreography evaluation. No new human quality rating was obtained.

Initial latent arrays from both new trials are byte-for-byte equal, shape
`[1,48,13,32,32]`; no extra RNG calls were introduced. The historical reference
did not save initial noise, so its equality cannot be directly checked. Model,
input and recorded dependency-source hashes matched the reference; same seed and
loading path were retained. Exact settings/logs are preserved per run.

MP4 SHA256:

- Shift3: `c62d7265b878c5e7af7bab93735dca24e4245fc7179ce94be7937c2c3afd83e4`.
- Guidance3: `27842e386dafac7b11acadc85833062126bfe81e1c54630f1bc3023abbccf061`.

## Decision and smallest next experiment

**Do not promote either setting.** Retain the original configuration as a
diagnostic reference; it is not an acceptable motion baseline.3A remains passed
within its recorded scope,3B below target,3C pending.

Strongest remaining blocker: unstable anatomy/temporal motion in the generated
content, with no confirmed cause in the tested input, decoder, small-transformer
or scheduler paths. Quantization loss, full trained-model mixed-precision behavior
and this model's suitability for the artwork remain hypotheses. The checks do
not prove that Q4 compression caused the failure.

Smallest useful next visual experiment: one same-checkpoint Q8-versus-Q4
comparison using the original woman's seed42/settings, after checking conversion
and memory feasibility on this Mac. Change only transformer precision; preserve
the current Q4 files. This directly tests whether compression is materially
affecting motion, rather than spending another batch on prompts or seeds.
It has **not** been run or promised to fix quality. If Q8 cannot fit safely, stop
and report that constraint rather than start an uncontrolled conversion/search.

No application code changed, so the application suite was not rerun; the
previous29-pass result belongs to3A. The new numerical checks above passed.
Only evidence, a local experiment player and roadmap tracking were updated.
Stopped after3B; no API integration, website integration or3C work performed.

## Playable artifacts and reproduction

[Comparison player](http://127.0.0.1:8766/v5-step3b-motion-20261027/)
requires the existing local static server. Persistent local files:

- [Reference MP4](../../outputs/v5-step3-quality-20261021/temporal32-seed42/shuffle.mp4)
- [Shift3 MP4](../../outputs/v5-step3b-motion-20261027/shift3/shuffle.mp4)
- [Guidance3 MP4](../../outputs/v5-step3b-motion-20261027/guidance3/shuffle.mp4)
- [Shift3 all frames](../../outputs/v5-step3b-motion-20261027/shift3/all-frames.png)
- [Guidance3 all frames](../../outputs/v5-step3b-motion-20261027/guidance3/all-frames.png)

Each run retains complete metadata/environment/settings, generation log, MP4,
FFmpeg/ffprobe verification, contact sheet, individual frames, all-frame sheet,
initial/final latents, denoising diagnostics, timing audit and visual review.
Browser observations are recorded in the experiment root. Large artifacts,
models and user assets remain ignored; this tracked report preserves findings.

Executed from repository root:

```bash
PYTHONPATH=outputs/v5-step3b-motion-20261027/test-deps .venv-mlx/bin/python outputs/v5-step3b-motion-20261027/check_math.py
.venv-mlx/bin/python outputs/v5-step3b-motion-20261027/check_quantization.py
.venv-mlx/bin/python outputs/v5-step3b-motion-20261027/run.py --trial shift3
.venv-mlx/bin/python outputs/v5-step3b-motion-20261027/run.py --trial guidance3
```

The recorder refuses existing run directories. For reproduction, copy `run.py`,
`generate_instrumented.py`, `preflight.json` and the relevant `*-protocol.json`
into a fresh sibling directory under outputs. Run its command there; retain all
existing results. Metal access and the preserved local models/reference metadata
are required. Mathematical checks additionally use saved official sources and
the isolated diffusers dependency. No new model downloads were performed.

V5J records the two failed quality trials and proposed precision comparison;
V5I image/prompt are archived. Step3 remains TESTED / motion below target.

## Local artifacts

Ignored folder: `outputs/v5-step3b-motion-20261027/`. Protocols, preflight, source
hashes, numerical test scripts/logs/results and per-run metadata are retained.
Model/source hashes matched the reference before generation; Metal succeeded.
M4 Pro24GiB, macOS26.6.2 arm64, Python3.11.15, MLX0.32.0, mlx-video0.0.1.
Free disk at preflight620.27GiB. Application source starts at commit2cf74a9.

Generation instrumentation saves initial/final latents and finite/RMS diagnostics
without consuming random numbers or changing model parameters. Timings include
diagnostic capture overhead and are not controlled speed benchmarks.

## Subsequent Q8 checkpoint — 2026-10-28

Q8 conversion verified; two launches stopped at the experiment's memory guard
during unchanged text encoding, before Q8 loaded. No new frames, Q8 score or
additional seeds. This does not prove Q8 cannot run. Next proposed work is a
text-encoding-only memory/parity experiment.3B remains below target;3C pending.
[Latest Q8 evidence and preserved failures](roadmap-v5-step3b-q8-evidence.md).
