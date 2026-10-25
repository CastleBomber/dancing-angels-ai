"""Readiness checks for an official Wan2.2-Animate CUDA runtime."""

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence

from dancing_angels_ai.reference import DEFAULT_CHARACTER_IMAGE


@dataclass(frozen=True)
class ProbeResult:
    """Captured result of a non-interactive runtime probe."""

    returncode: int
    stdout: str = ""
    stderr: str = ""


Probe = Callable[[Sequence[str], Path], ProbeResult]


@dataclass(frozen=True)
class ReadinessCheck:
    """One actionable readiness assertion."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class WanRuntimeReport:
    """Complete readiness result for preprocessing and generation."""

    checks: Sequence[ReadinessCheck]

    @property
    def ready(self) -> bool:
        return all(check.passed for check in self.checks)

    def render(self) -> str:
        lines = [
            f"[{'PASS' if check.passed else 'FAIL'}] "
            f"{check.name}: {check.detail}"
            for check in self.checks
        ]
        lines.append("READY" if self.ready else "NOT READY")
        return "\n".join(lines)


def check_mlx_runtime(
    model_directory: Path,
    python_executable: str,
    character_image: Path = DEFAULT_CHARACTER_IMAGE,
    probe: Optional[Probe] = None,
) -> WanRuntimeReport:
    """Inspect the local Apple-silicon image-to-video runtime."""
    probe = probe or probe_command
    checks: List[ReadinessCheck] = []
    _check_file(checks, "character image", character_image)

    model = model_directory.expanduser().resolve()
    _check_directory(checks, "MLX video model", model)
    for filename in (
        "config.json",
        "model.safetensors",
        "t5_encoder.safetensors",
        "vae.safetensors",
    ):
        _check_file(checks, f"MLX model {filename}", model / filename)

    executable = _resolve_executable(python_executable)
    checks.append(
        ReadinessCheck(
            "MLX Python executable",
            executable is not None,
            str(executable) if executable is not None else python_executable,
        )
    )
    if executable is not None:
        code = (
            "import importlib.metadata,json,platform,sys,mlx;"
            "print(json.dumps({'python':sys.version.split()[0],"
            "'system':platform.system(),'machine':platform.machine(),"
            "'mlx':importlib.metadata.version('mlx'),'mlx_video':"
            "importlib.metadata.version('mlx-video')}))"
        )
        result = probe([str(executable), "-c", code], Path.cwd())
        if result.returncode != 0:
            checks.append(
                ReadinessCheck("MLX imports", False, _probe_error(result))
            )
        else:
            try:
                payload = json.loads(result.stdout.strip().splitlines()[-1])
                python_ok = tuple(
                    int(part) for part in payload["python"].split(".")[:2]
                ) >= (3, 11)
                apple_ok = (
                    payload["system"] == "Darwin"
                    and payload["machine"] == "arm64"
                )
                checks.append(
                    ReadinessCheck(
                        "MLX Python version",
                        python_ok,
                        payload["python"],
                    )
                )
                checks.append(
                    ReadinessCheck(
                        "Apple Silicon",
                        apple_ok,
                        f"{payload['system']} {payload['machine']}",
                    )
                )
                checks.append(
                    ReadinessCheck(
                        "MLX imports",
                        True,
                        (
                            f"mlx={payload['mlx']}, "
                            f"mlx-video={payload['mlx_video']}"
                        ),
                    )
                )
            except (IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                checks.append(
                    ReadinessCheck(
                        "MLX imports",
                        False,
                        f"invalid probe: {error}",
                    )
                )

    return WanRuntimeReport(checks)


def check_wan_runtime(
    wan_repository: Optional[Path],
    checkpoint_directory: Optional[Path],
    python_executable: str,
    character_image: Path = DEFAULT_CHARACTER_IMAGE,
    driver_video: Path = Path("assets/walk.mp4"),
    probe: Optional[Probe] = None,
) -> WanRuntimeReport:
    """Inspect files, imports, and CUDA without loading model weights."""
    probe = probe or probe_command
    checks: List[ReadinessCheck] = []

    _check_file(checks, "character image", character_image)
    _check_file(checks, "driver video", driver_video)

    repository = (
        wan_repository.expanduser().resolve()
        if wan_repository is not None
        else None
    )
    checkpoint = (
        checkpoint_directory.expanduser().resolve()
        if checkpoint_directory is not None
        else None
    )
    preprocess_script = (
        repository
        / "wan"
        / "modules"
        / "animate"
        / "preprocess"
        / "preprocess_data.py"
        if repository is not None
        else None
    )
    generate_script = repository / "generate.py" if repository is not None else None

    _check_directory(checks, "Wan repository", repository)
    _check_file(checks, "Wan preprocessing script", preprocess_script)
    _check_file(checks, "Wan generator", generate_script)
    _check_file(
        checks,
        "Wan animation requirements",
        repository / "requirements_animate.txt"
        if repository is not None
        else None,
    )
    _check_directory(checks, "Animate-14B checkpoint", checkpoint)

    if checkpoint is not None:
        required_files = [
            "config.json",
            "diffusion_pytorch_model.safetensors.index.json",
            "Wan2.1_VAE.pth",
            "models_t5_umt5-xxl-enc-bf16.pth",
            "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth",
            "process_checkpoint/det/yolov10m.onnx",
        ]
        for relative_path in required_files:
            _check_file(
                checks,
                f"checkpoint {relative_path}",
                checkpoint / relative_path,
            )
        for relative_path in ("google/umt5-xxl", "xlm-roberta-large"):
            _check_directory(
                checks,
                f"checkpoint {relative_path}",
                checkpoint / relative_path,
            )

        pose_path = (
            checkpoint
            / "process_checkpoint"
            / "pose2d"
            / "vitpose_h_wholebody.onnx"
        )
        pose_model = pose_path / "end2end.onnx" if pose_path.is_dir() else pose_path
        _check_file(checks, "checkpoint whole-body pose model", pose_model)

        shards = sorted(checkpoint.glob("diffusion_pytorch_model-*.safetensors"))
        checks.append(
            ReadinessCheck(
                "Animate transformer shards",
                len(shards) == 4,
                f"found {len(shards)} of 4",
            )
        )

    executable = _resolve_executable(python_executable)
    checks.append(
        ReadinessCheck(
            "Wan Python executable",
            executable is not None,
            str(executable) if executable is not None else python_executable,
        )
    )

    if executable is not None:
        _check_python_cuda(checks, str(executable), probe)
        if preprocess_script is not None and preprocess_script.is_file():
            _check_script_import(
                checks,
                "Wan preprocessing imports",
                [str(executable), str(preprocess_script), "--help"],
                preprocess_script.parent,
                probe,
            )
        if generate_script is not None and generate_script.is_file():
            _check_script_import(
                checks,
                "Wan generator imports",
                [str(executable), str(generate_script), "--help"],
                repository,
                probe,
            )

    return WanRuntimeReport(checks)


def probe_command(command: Sequence[str], cwd: Path) -> ProbeResult:
    """Run a short readiness probe and capture diagnostics."""
    try:
        result = subprocess.run(
            list(command),
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return ProbeResult(returncode=1, stderr=str(error))
    return ProbeResult(result.returncode, result.stdout, result.stderr)


def _check_python_cuda(
    checks: List[ReadinessCheck],
    executable: str,
    probe: Probe,
) -> None:
    code = (
        "import json,sys,torch;"
        "print(json.dumps({'python':sys.version.split()[0],"
        "'torch':torch.__version__,'cuda':torch.cuda.is_available(),"
        "'devices':torch.cuda.device_count()}))"
    )
    result = probe([executable, "-c", code], Path.cwd())
    if result.returncode != 0:
        checks.append(
            ReadinessCheck(
                "Wan Python + PyTorch",
                False,
                _probe_error(result),
            )
        )
        return
    try:
        payload = json.loads(result.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as error:
        checks.append(
            ReadinessCheck("Wan Python + PyTorch", False, f"invalid probe: {error}")
        )
        return
    python_ok = tuple(int(part) for part in payload["python"].split(".")[:2]) >= (3, 10)
    checks.append(
        ReadinessCheck(
            "Wan Python version",
            python_ok,
            payload["python"],
        )
    )
    checks.append(
        ReadinessCheck(
            "NVIDIA CUDA",
            bool(payload["cuda"]) and int(payload["devices"]) > 0,
            f"torch={payload['torch']}, devices={payload['devices']}",
        )
    )


def _check_script_import(
    checks: List[ReadinessCheck],
    name: str,
    command: Sequence[str],
    cwd: Path,
    probe: Probe,
) -> None:
    result = probe(command, cwd)
    checks.append(
        ReadinessCheck(
            name,
            result.returncode == 0,
            "available" if result.returncode == 0 else _probe_error(result),
        )
    )


def _check_file(
    checks: List[ReadinessCheck],
    name: str,
    path: Optional[Path],
) -> None:
    checks.append(
        ReadinessCheck(
            name,
            path is not None and path.is_file(),
            str(path) if path is not None else "not configured",
        )
    )


def _check_directory(
    checks: List[ReadinessCheck],
    name: str,
    path: Optional[Path],
) -> None:
    checks.append(
        ReadinessCheck(
            name,
            path is not None and path.is_dir(),
            str(path) if path is not None else "not configured",
        )
    )


def _resolve_executable(executable: str) -> Optional[Path]:
    path = Path(executable).expanduser()
    if path.parent != Path("."):
        return path.absolute() if path.is_file() else None
    resolved = shutil.which(executable)
    return Path(resolved).absolute() if resolved else None


def _probe_error(result: ProbeResult) -> str:
    output = (result.stderr or result.stdout).strip()
    if not output:
        return f"exited with status {result.returncode}"
    return output.splitlines()[-1][:240]
