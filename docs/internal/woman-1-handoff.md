# Next Step 3 tests — user's own artwork

Prepared 2026-10-08. Updated 2026-10-25: preparation and the first controlled comparison are complete; quality remains below target. See [follow-up results](roadmap-v5-step3-quality-followup.md).

## Current input
- Use `assets/woman-1.png` for every new test. Preserve the original unchanged.
- User-created in ToonSquid with a vector brush; PNG contains raster pixels, not editable vector paths.
- PNG, RGBA, 1080×1920, 76,574 bytes.
- SHA-256: `8bdcd679d1d838809a730c2813569e7a798f716799ac15075ae90feb8f548aab`.
- Nontransparent artwork bounds: `(158, 581, 859, 1807)`; large empty top margin.
- Red/pink shirt, blue trousers, green shoes, dark hair/linework. Do not prescribe the old man's dark trousers/red shoes.
- Shared character-neutral Shuffle prompt: `src/dancing_angels_ai/reference.py`.

## First fix before generating
The installed MLX loader (`wan_2/i2v_utils.py::preprocess_image`) converts RGBA
directly to RGB, resizes to fill, and center-crops. At 512×512 this portrait becomes
512×910, cropped at y=199..711: visible lower legs/shoes are lost. Dropping alpha
also does not deliberately composite a background, risking dark linework against
dark hidden RGB pixels. These are input preparation issues, not evidence that
vector artwork animates worse or better.

Prepare a separate, reproducible input from the original: explicit light opaque
background, full visible figure centered with head/feet clearance in a 512×512
canvas, preserved proportions and artwork. Inspect the exact model input before
spending GPU time. Save source/prepared hashes and transform settings. Implement
and test preprocessing in `src/dancing_angels_ai/`; do not silently edit the original
or patch the installed dependency. The opt-in preparation fix is implemented in `src/dancing_angels_ai/preparation.py` and tested. Use the saved prepared copy or reproduce its recorded transform.

## Controlled testing handoff
Adapt the prompt from task “6B - execute”:
1. Read this note and the [existing rubric/evidence](roadmap-v5-step3-evidence.md).
2. Use woman-1 for all new runs; old man clips (including seed 123) are historical
   diagnostics only. A different image and prompt cannot prove a brush-type benefit
   or count as a controlled before/after against the man.
3. Investigate input framing/alpha first, then temporal decoding, VAE tiling and
   continuity. Separate confirmed causes from hypotheses.
4. Keep the existing model and reference numeric settings: 512×512, 49 frames,
   24 FPS, 40 steps, seed 42, guidance 5, UniPC, shift 5, aggressive tiling.
   Establish a woman-specific reference, then change one variable per comparison.
5. Keep the original maximum-four sequential-generation budget: reference and
   controlled candidate first; two extra seeds only if a candidate passes the rubric.
6. Evaluate every frame and actual playback; record runtime, identity, anatomy,
   cropping, continuity and recognizable Shuffle. Preserve all old evidence.
7. Update quality status only after measured results; no unrelated website work.

## Recorders and defaults
- Doctor defaults and current documented examples now use woman-1.
- API preset `shuffle-diagnostic-v2` uses the neutral prompt. Restart the API to
  apply it; stored v1 jobs are unchanged. This preset has not been visually validated.
- Both ignored `outputs/v5-step2/run.py` and `outputs/v5-step3/run.py` default to
  woman-1 and accept `--image`, `--prompt`, `--dry-run`.
- Their former man-specific versions are preserved as `run-man-reference.py` in
  each directory. Historical reproduction commands in evidence remain unchanged.
- Step 3 records fresh input hashes, prompt and environment rather than reusing
  the old man's hash or historical machine probes.

Safe preparation check (does not generate):
```bash
.venv-mlx/bin/python outputs/v5-step3/run.py --steps 40 --seed 42 --dry-run
```
Pass the inspected prepared copy using `--image`; do not run new tests on the unprepared portrait.

Vector-source explanation: https://toonsquid.com/handbook/export/image/
