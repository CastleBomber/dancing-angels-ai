# Dancing Angels AI

Turn a user-provided character image into walking, running, jumping, or dancing video.

## Golden Path: Apple Silicon

The first supported vertical slice is prompt-driven image-to-video generation:

`character image + action -> local MLX generation -> MP4`

After the local model is prepared:

```bash
source .venv-mlx/bin/activate
dancing-angels-ai doctor

dancing-angels-ai create \
  --image assets/woman-1.png \
  --action walk \
  --output outputs/woman-1-walking-mlx.mp4
```

Supported action presets: `walk`, `run`, `jump`, and `dance`. Use `--prompt`
when you want custom movement.

The MLX adapter fits transparent or differently sized images onto a white canvas,
preserving proportions and the original upload. Already sized RGB references
pass through unchanged. Each run keeps its preparation record beside the output.
Input checks pass for the woman reference; motion quality is still below target.

The default smoke-test settings are intentionally small for a 24 GB Apple-silicon
Mac: 512x512, 17 frames, 10 steps, and aggressive VAE tiling.
See [docs/mlx-runtime.md](docs/mlx-runtime.md) for one-time setup.

## Local Generation API

Submit an image, poll its job, and retrieve the generated MP4 over localhost.
The initial Shuffle preset is the step-three diagnostic reference; visual quality
remains below target. See [API startup, curl examples, and limits](docs/local-api.md).

## Optional Exact-Motion Path

The existing Wan2.2-Animate integration remains available when exact motion from
a driver video matters:

`character image + driver video -> pose/face preprocessing -> Wan-Animate -> MP4`

That backend currently requires a configured NVIDIA CUDA worker:

```bash
dancing-angels-ai doctor --backend wan

dancing-angels-ai animate \
  --image assets/woman-1.png \
  --motion assets/walk.mp4 \
  --output outputs/woman-1-walking-wan.mp4
```

See [docs/wan-runtime.md](docs/wan-runtime.md) for its external runtime.

## Repository Layout

- `src/dancing_angels_ai/`: application code and generation backends.
- `experiments/pose/`: verified pose and motion prototypes.
- `experiments/legacy_sdxl/`: preserved SDXL and ControlNet experiments.
- `roadmaps-ideas/roadmap/`: current visual roadmap.
- `roadmaps-ideas/golden-image-v5.png`: current website reference; older visuals live in `roadmaps-ideas/archive/`.
- `design/concepts/`: exploratory design comparison sheets.
- `docs/internal/`: technical status, evidence, and planning notes.
- `assets/`: local source media.
- `models/`: local model files.
- `outputs/`: generated media.

## Tests

```bash
PYTHONPATH=src .venv-mlx/bin/python -m unittest discover \
  -s tests -p 'test_*.py' -v
```
