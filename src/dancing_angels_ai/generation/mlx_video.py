"""Apple-Silicon image-to-video adapter for MLX-Video."""

from dataclasses import dataclass
import json
from pathlib import Path
import tempfile
from typing import Dict, Sequence

from dancing_angels_ai.commands import CommandRunner, run_command
from dancing_angels_ai.preparation import prepare_generation_input
from dancing_angels_ai.video import VideoValidationError, inspect_video


class MlxVideoGenerationError(RuntimeError):
    """Raised when the local MLX backend cannot produce a valid video."""


ACTION_PROMPTS: Dict[str, str] = {
    "walk": (
        "The same character walks naturally forward, full body visible, "
        "stable appearance, fixed camera."
    ),
    "run": (
        "The same character runs naturally forward, full body visible, "
        "stable appearance, fixed camera."
    ),
    "jump": (
        "The same character performs one natural jump and lands, full body "
        "visible, stable appearance, fixed camera."
    ),
    "dance": (
        "The same character performs an energetic dance, full body visible, "
        "stable appearance, fixed camera."
    ),
}


def prompt_for_action(action: str) -> str:
    """Return the tested default prompt for a supported movement."""
    try:
        return ACTION_PROMPTS[action]
    except KeyError as error:
        supported = ", ".join(sorted(ACTION_PROMPTS))
        raise ValueError(
            f"unsupported action {action!r}; choose one of: {supported}"
        ) from error


@dataclass(frozen=True)
class MlxVideoConfig:
    """Runtime paths and conservative defaults for a 24 GB Apple-silicon Mac."""

    model_directory: Path
    python_executable: str = ".venv-mlx/bin/python"
    working_directory: Path = Path(".")
    width: int = 512
    height: int = 512
    num_frames: int = 17
    steps: int = 10
    guide_scale: float = 5.0
    seed: int = 42
    tiling: str = "aggressive"

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if self.width % 32 or self.height % 32:
            raise ValueError("width and height must be divisible by 32")
        if self.num_frames <= 0 or self.num_frames % 4 != 1:
            raise ValueError("num_frames must equal 4n+1")
        if self.steps <= 0:
            raise ValueError("steps must be positive")
        if self.tiling not in {
            "auto",
            "none",
            "default",
            "aggressive",
            "conservative",
            "spatial",
            "temporal",
        }:
            raise ValueError(f"unsupported tiling mode: {self.tiling}")


class MlxVideoBackend:
    """Generate short image-to-video clips locally through MLX-Video."""

    def __init__(
        self,
        config: MlxVideoConfig,
        runner: CommandRunner = run_command,
    ) -> None:
        self.config = config
        self.runner = runner

    def generate(self, image: Path, prompt: str, output: Path) -> Path:
        """Generate and validate an MP4, replacing the destination atomically."""
        image = Path(image).expanduser().resolve()
        output = Path(output).expanduser().resolve()
        self._require_file(image, "character image")
        self._validate_model()
        if not prompt.strip():
            raise MlxVideoGenerationError("prompt must not be empty")

        output.parent.mkdir(parents=True, exist_ok=True)
        # Keep the original upload and a reproducible preparation record per run.
        input_directory = Path(tempfile.mkdtemp(prefix=f"{output.stem}-input-", dir=output.parent))
        preparation = prepare_generation_input(
            image, input_directory / "prepared.png", self.config.width, self.config.height,
        )
        (input_directory / "preparation.json").write_text(json.dumps(preparation, indent=2) + "\n")
        model_image = Path(preparation["output"])
        partial = output.with_name(f".{output.stem}.partial{output.suffix}")
        partial.unlink(missing_ok=True)
        try:
            self.runner(
                self.build_command(model_image, prompt, partial),
                self.config.working_directory.expanduser().resolve(),
            )
            inspect_video(partial)
            partial.replace(output)
        except VideoValidationError as error:
            partial.unlink(missing_ok=True)
            raise MlxVideoGenerationError(str(error)) from error
        except Exception:
            partial.unlink(missing_ok=True)
            raise
        return output

    def build_command(
        self,
        image: Path,
        prompt: str,
        output: Path,
    ) -> Sequence[str]:
        """Build the current MLX-Video Wan2.2 TI2V command."""
        return [
            self.config.python_executable,
            "-m",
            "mlx_video.models.wan_2.generate",
            "--model-dir",
            str(self.config.model_directory.expanduser().resolve()),
            "--image",
            str(Path(image).expanduser().resolve()),
            "--prompt",
            prompt,
            "--width",
            str(self.config.width),
            "--height",
            str(self.config.height),
            "--num-frames",
            str(self.config.num_frames),
            "--steps",
            str(self.config.steps),
            "--guide-scale",
            str(self.config.guide_scale),
            "--seed",
            str(self.config.seed),
            "--tiling",
            self.config.tiling,
            "--output-path",
            str(Path(output).expanduser().resolve()),
        ]

    def _validate_model(self) -> None:
        model = self.config.model_directory.expanduser().resolve()
        if not model.is_dir():
            raise MlxVideoGenerationError(f"MLX model not found: {model}")
        for filename in (
            "config.json",
            "model.safetensors",
            "t5_encoder.safetensors",
            "vae.safetensors",
        ):
            self._require_file(model / filename, f"MLX model file {filename}")

    @staticmethod
    def _require_file(path: Path, label: str) -> None:
        if not path.is_file():
            raise MlxVideoGenerationError(f"{label} not found: {path}")
