# Wan2.2-Animate Runtime

Dancing Angels AI intentionally wraps the official Wan implementation instead of
reimplementing its face or pose conditioning.

## Requirements

- Linux host with NVIDIA CUDA.
- Python 3.10 or newer for the isolated Wan environment.
- Official [Wan2.2 repository](https://github.com/Wan-Video/Wan2.2).
- Official
  [Wan2.2-Animate-14B checkpoint](https://huggingface.co/Wan-AI/Wan2.2-Animate-14B),
  approximately 72.4 GB.

The local Apple Silicon machine has neither CUDA nor the model files, so it can
test orchestration and media validation but cannot run real Animate-14B
inference.

## Worker Setup

Run on the CUDA machine:

```bash
git clone https://github.com/Wan-Video/Wan2.2.git
cd Wan2.2
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_animate.txt
pip install moviepy
pip install "huggingface_hub[cli]"
huggingface-cli download Wan-AI/Wan2.2-Animate-14B \
  --local-dir ./Wan2.2-Animate-14B
```

The adapter contract was verified against official Wan2.2 commit
`42bf4cfaa384bc21833865abc2f9e6c0e67233dc` (March 17, 2026). Treat the
current upstream checkout and requirements as authoritative if they change.

## Acceptance Test

From this repository, with paths pointing to the CUDA worker's local checkout:

```bash
export WAN22_REPO=/path/to/Wan2.2
export WAN22_CHECKPOINT=/path/to/Wan2.2/Wan2.2-Animate-14B
export WAN22_PYTHON=/path/to/Wan2.2/.venv/bin/python

dancing-angels-ai doctor

dancing-angels-ai animate \
  --image assets/woman-1.png \
  --motion assets/walk.mp4 \
  --output outputs/woman-1-walking.mp4
```

`dancing-angels-ai doctor` must end with `READY`. It checks the source scripts, both
preprocessing ONNX models (including Wan's external-data ViTPose directory),
the four Animate transformer shards, tokenizer/model files, Wan imports,
Python 3.10+, and NVIDIA CUDA.

Successful acceptance means:

1. Conditioning contains readable, frame-aligned `src_pose.mp4` and
   `src_face.mp4`; face frames are 512x512.
2. `outputs/woman-1-walking.mp4` is readable and nonempty.
3. Visual inspection shows the character from `woman-1.png` performing the motion
   from `walk.mp4`.

The same run is available as an opt-in automated smoke test:

```bash
RUN_WAN_E2E=1 PYTHONPATH=src \
  python -m unittest discover -s tests -p 'test_wan_e2e.py' -v
```

Basic pose retargeting is enabled by default. Add `--use-flux` only when the
optional FLUX checkpoint is installed and enhanced retargeting is desired.

The production contract follows Wan's
[preprocessing guide](https://github.com/Wan-Video/Wan2.2/blob/main/wan/modules/animate/preprocess/UserGuider.md)
and [official inference command](https://github.com/Wan-Video/Wan2.2#run-wan-animate).
