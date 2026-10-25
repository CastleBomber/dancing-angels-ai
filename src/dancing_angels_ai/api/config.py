"""Fixed diagnostic preset and local API configuration."""
from dataclasses import dataclass
import json
from pathlib import Path

from dancing_angels_ai.reference import SHUFFLE_PROMPT
PRESET = {
    "name": "shuffle-diagnostic-v2", "width": 512, "height": 512,
    "frames": 49, "steps": 40, "seed": 42, "guide_scale": 5.0,
    "tiling": "aggressive", "scheduler": "unipc", "shift": 5.0, "fps": 24,
    "quality_note": "Character-neutral prompt; quality unverified for the new artwork. Portrait framing requires review.",
}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_REQUEST_BYTES = MAX_IMAGE_BYTES + 64 * 1024


def reference_model_config():
    return json.loads(Path(__file__).with_name("model-reference.json").read_text())


@dataclass(frozen=True)
class Settings:
    project_root: Path
    queue_slots: int = 2
    generation_timeout: float = 1800

    def __post_init__(self):
        object.__setattr__(self, "project_root", self.project_root.expanduser().resolve())
        if self.queue_slots < 1 or self.generation_timeout <= 0:
            raise ValueError("queue slots and generation timeout must be positive")

    @property
    def jobs_directory(self):
        return self.project_root / "outputs/api/jobs"

    @property
    def lock_path(self):
        return self.project_root / "outputs/.mlx-api.lock"

    @property
    def model_directory(self):
        return self.project_root / "models/Wan2.2-TI2V-5B-MLX-Q4"

    @property
    def python_executable(self):
        return str(self.project_root / ".venv-mlx/bin/python")
