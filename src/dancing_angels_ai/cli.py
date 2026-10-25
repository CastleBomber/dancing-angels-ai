"""Command-line interface for end-to-end character animation."""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from dancing_angels_ai.commands import ExternalCommandError
from dancing_angels_ai.conditioning import (
    WanAnimatePreprocessor,
    WanPreprocessConfig,
    WanPreprocessError,
)
from dancing_angels_ai.domain import AnimationRequest
from dancing_angels_ai.generation import (
    ACTION_PROMPTS,
    MlxVideoBackend,
    MlxVideoConfig,
    MlxVideoGenerationError,
    WanAnimateBackend,
    WanGenerationConfig,
    WanGenerationError,
    prompt_for_action,
)
from dancing_angels_ai.pipeline import AnimationPipeline
from dancing_angels_ai.readiness import check_mlx_runtime, check_wan_runtime
from dancing_angels_ai.reference import DEFAULT_CHARACTER_IMAGE


def build_parser() -> argparse.ArgumentParser:
    """Build the public CLI parser."""
    parser = argparse.ArgumentParser(
        prog="dancing-angels-ai",
        description="Animate a character image with a human driver video.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    animate = subparsers.add_parser(
        "animate",
        help="Run official Wan2.2-Animate preprocessing and generation.",
    )
    animate.add_argument("--image", required=True, type=Path)
    animate.add_argument("--motion", required=True, type=Path)
    animate.add_argument("--output", required=True, type=Path)
    animate.add_argument(
        "--wan-repo",
        type=Path,
        default=_environment_path("WAN22_REPO"),
        help="Wan2.2 checkout (or set WAN22_REPO).",
    )
    animate.add_argument(
        "--checkpoint",
        type=Path,
        default=_environment_path("WAN22_CHECKPOINT"),
        help="Wan2.2-Animate-14B checkpoint (or set WAN22_CHECKPOINT).",
    )
    animate.add_argument(
        "--work-dir",
        type=Path,
        help="Conditioning directory; defaults beside the output.",
    )
    animate.add_argument(
        "--wan-python",
        default=os.environ.get("WAN22_PYTHON", sys.executable),
        help="Python from the isolated Wan environment.",
    )
    animate.add_argument(
        "--resolution",
        nargs=2,
        type=int,
        metavar=("WIDTH", "HEIGHT"),
        default=(1280, 720),
    )
    animate.add_argument(
        "--fps",
        type=int,
        default=-1,
        help="-1 preserves the driver FPS.",
    )
    animate.add_argument(
        "--no-retarget",
        action="store_false",
        dest="retarget",
        help="Disable Wan's basic pose retargeting.",
    )
    animate.set_defaults(retarget=True)
    animate.add_argument(
        "--use-flux",
        action="store_true",
        help="Use optional enhanced FLUX pose retargeting.",
    )
    animate.add_argument(
        "--offload-model",
        action="store_true",
        help="Enable Wan model CPU offloading.",
    )
    animate.add_argument(
        "--convert-model-dtype",
        action="store_true",
        help="Convert Wan model parameters to its configured dtype.",
    )
    animate.add_argument(
        "--t5-cpu",
        action="store_true",
        help="Keep Wan's T5 encoder on CPU.",
    )
    animate.add_argument(
        "--conditioning-frames",
        type=int,
        choices=(1, 5),
        default=1,
        help="Prior frames used for segment continuity.",
    )

    create = subparsers.add_parser(
        "create",
        help="Create a short movement video locally on Apple Silicon.",
    )
    create.add_argument("--image", required=True, type=Path)
    create.add_argument(
        "--action",
        choices=tuple(ACTION_PROMPTS),
        default="walk",
    )
    create.add_argument(
        "--prompt",
        help="Override the action's default movement prompt.",
    )
    create.add_argument("--output", required=True, type=Path)
    create.add_argument(
        "--model",
        type=Path,
        default=Path(
            os.environ.get(
                "ANGELS_MLX_MODEL",
                "models/Wan2.2-TI2V-5B-MLX-Q4",
            )
        ),
    )
    create.add_argument(
        "--mlx-python",
        default=os.environ.get(
            "ANGELS_MLX_PYTHON",
            ".venv-mlx/bin/python",
        ),
    )
    create.add_argument("--width", type=int, default=512)
    create.add_argument("--height", type=int, default=512)
    create.add_argument("--frames", type=int, default=17)
    create.add_argument("--steps", type=int, default=10)
    create.add_argument("--guide-scale", type=float, default=5.0)
    create.add_argument("--seed", type=int, default=42)
    create.add_argument(
        "--tiling",
        choices=(
            "auto",
            "none",
            "default",
            "aggressive",
            "conservative",
            "spatial",
            "temporal",
        ),
        default="aggressive",
    )

    doctor = subparsers.add_parser(
        "doctor",
        help="Check the selected generation backend's readiness.",
    )
    doctor.add_argument(
        "--backend",
        choices=("mlx", "wan"),
        default="mlx",
        help="Check Mac-local MLX by default; choose wan for CUDA.",
    )
    doctor.add_argument("--image", type=Path, default=DEFAULT_CHARACTER_IMAGE)
    doctor.add_argument(
        "--model",
        type=Path,
        default=Path(
            os.environ.get(
                "ANGELS_MLX_MODEL",
                "models/Wan2.2-TI2V-5B-MLX-Q4",
            )
        ),
    )
    doctor.add_argument(
        "--mlx-python",
        default=os.environ.get(
            "ANGELS_MLX_PYTHON",
            ".venv-mlx/bin/python",
        ),
    )
    doctor.add_argument("--motion", type=Path, default=Path("assets/walk.mp4"))
    doctor.add_argument(
        "--wan-repo",
        type=Path,
        default=_environment_path("WAN22_REPO"),
        help="Wan2.2 checkout (or set WAN22_REPO).",
    )
    doctor.add_argument(
        "--checkpoint",
        type=Path,
        default=_environment_path("WAN22_CHECKPOINT"),
        help="Wan2.2-Animate-14B checkpoint (or set WAN22_CHECKPOINT).",
    )
    doctor.add_argument(
        "--wan-python",
        default=os.environ.get("WAN22_PYTHON", sys.executable),
        help="Python from the isolated Wan environment.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Run the CLI and return a process exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "create":
        try:
            config = MlxVideoConfig(
                model_directory=args.model,
                python_executable=args.mlx_python,
                working_directory=Path.cwd(),
                width=args.width,
                height=args.height,
                num_frames=args.frames,
                steps=args.steps,
                guide_scale=args.guide_scale,
                seed=args.seed,
                tiling=args.tiling,
            )
            prompt = args.prompt or prompt_for_action(args.action)
            video = MlxVideoBackend(config).generate(
                args.image,
                prompt,
                args.output,
            )
        except (
            ExternalCommandError,
            FileNotFoundError,
            MlxVideoGenerationError,
            ValueError,
        ) as error:
            parser.exit(2, f"dancing-angels-ai: error: {error}\n")
        print(video)
        return 0

    if args.command == "doctor":
        if args.backend == "mlx":
            report = check_mlx_runtime(
                model_directory=args.model,
                python_executable=args.mlx_python,
                character_image=args.image,
            )
        else:
            report = check_wan_runtime(
                wan_repository=args.wan_repo,
                checkpoint_directory=args.checkpoint,
                python_executable=args.wan_python,
                character_image=args.image,
                driver_video=args.motion,
            )
        print(report.render())
        return 0 if report.ready else 1

    if args.wan_repo is None:
        parser.error("--wan-repo or WAN22_REPO is required")
    if args.checkpoint is None:
        parser.error("--checkpoint or WAN22_CHECKPOINT is required")

    request = AnimationRequest(
        character_image=args.image,
        driver_video=args.motion,
        output_video=args.output,
    )
    output = args.output.expanduser().resolve()
    work_dir = args.work_dir or (
        output.parent / f"{output.stem}_conditioning"
    )

    try:
        preprocess_config = WanPreprocessConfig(
            wan_repository=args.wan_repo,
            checkpoint_directory=args.checkpoint,
            python_executable=args.wan_python,
            resolution_width=args.resolution[0],
            resolution_height=args.resolution[1],
            fps=args.fps,
            retarget=args.retarget,
            use_flux=args.use_flux,
        )
        generation_config = WanGenerationConfig(
            wan_repository=args.wan_repo,
            checkpoint_directory=args.checkpoint,
            python_executable=args.wan_python,
            previous_conditioning_frames=args.conditioning_frames,
            offload_model=args.offload_model,
            convert_model_dtype=args.convert_model_dtype,
            t5_cpu=args.t5_cpu,
        )
        pipeline = AnimationPipeline(
            pose_preprocessor=None,
            conditioning_preprocessor=WanAnimatePreprocessor(preprocess_config),
            backend=WanAnimateBackend(generation_config),
        )
        result = pipeline.run(request, work_dir)
    except (
        ExternalCommandError,
        FileNotFoundError,
        ValueError,
        WanGenerationError,
        WanPreprocessError,
    ) as error:
        parser.exit(2, f"dancing-angels-ai: error: {error}\n")

    print(result.video)
    return 0


def _environment_path(name: str) -> Optional[Path]:
    value = os.environ.get(name)
    return Path(value) if value else None


if __name__ == "__main__":
    sys.exit(main())
