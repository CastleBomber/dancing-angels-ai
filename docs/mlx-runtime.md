# Apple-Silicon Runtime

This is the primary local path for the Golden Goal. It generates movement from
a character image and an action prompt. It does not copy an exact driver video.

## One-time setup

```bash
brew install uv ffmpeg
uv venv --python 3.11 .venv-mlx
uv pip install --python .venv-mlx/bin/python -r requirements-mlx.txt
uv pip install --python .venv-mlx/bin/python -e .
```

Download the official checkpoint with the current `hf` CLI:

```bash
HF_HUB_DISABLE_XET=1 .venv-mlx/bin/hf download \
  Wan-AI/Wan2.2-TI2V-5B \
  --local-dir models/Wan2.2-TI2V-5B
```

Convert and quantize it for unified memory:

```bash
.venv-mlx/bin/python -m mlx_video.models.wan_2.convert \
  --checkpoint-dir models/Wan2.2-TI2V-5B \
  --output-dir models/Wan2.2-TI2V-5B-MLX-Q4 \
  --quantize --bits 4 --group-size 64
```

## Readiness and first test

```bash
source .venv-mlx/bin/activate
dancing-angels-ai doctor

dancing-angels-ai create \
  --image assets/woman-1.png \
  --action walk \
  --output outputs/woman-1-walking-mlx.mp4
```

A successful test prints the absolute output path and leaves a playable MP4.
The default 512x512, 17-frame, 10-step settings are a smoke test for a 24 GB
Mac. Increase frames, resolution, and steps only after this succeeds.
