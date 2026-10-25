"""Use the existing MLX adapter with logged, bounded subprocess execution."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

import cv2

from dancing_angels_ai.generation.mlx_video import MlxVideoBackend, MlxVideoConfig
from dancing_angels_ai.readiness import check_mlx_runtime
from .config import PRESET, reference_model_config


class GenerationStopped(RuntimeError):
    pass


class MlxRuntime:
    def __init__(self, settings):
        self.settings = settings

    def _verify_config(self):
        path = self.settings.model_directory / "config.json"
        config = json.loads(path.read_text())
        if config != reference_model_config():
            raise ValueError("Model config differs from the recorded step-three reference")
        return config

    def readiness(self):
        report = check_mlx_runtime(
            self.settings.model_directory, self.settings.python_executable,
        )
        # Uploads need not depend on the example Hero remaining on disk.
        checks = [vars(c) for c in report.checks if c.name != "character image"]
        try:
            self._verify_config()
            checks.append({"name": "reference configuration", "passed": True})
        except (OSError, ValueError) as error:
            checks.append({"name": "reference configuration", "passed": False,
                           "detail": str(error)})
        checks.append({"name": "ffmpeg", "passed": shutil.which("ffmpeg") is not None})
        try:
            code = (
                "import json,mlx.core as mx; x=mx.ones((2,2)); y=x@x; mx.eval(y); "
                "print(json.dumps({'metal':mx.metal.is_available(),'value':y[0,0].item()}))"
            )
            result = subprocess.run(
                [self.settings.python_executable, "-c", code],
                capture_output=True, text=True, timeout=30,
            )
            passed = result.returncode == 0 and json.loads(result.stdout)['value'] == 2
            detail = "GPU computation passed" if passed else result.stderr[-500:]
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
            passed, detail = False, str(error)
        checks.append({"name": "Metal computation", "passed": passed, "detail": detail})
        return {"ready": all(c['passed'] for c in checks), "checks": checks}

    def generate(self, image, prompt, output, log_path, stop, lock_fd):
        config = self._verify_config()
        settings = self.settings

        def runner(command, cwd):
            command = list(command) + [
                "--scheduler", "unipc", "--shift", "5.0",
                "--negative-prompt", config["sample_neg_prompt"],
            ]
            output.with_name("command.json").write_text(json.dumps(command, indent=2) + "\n")
            # Child retains the instance lock if the API is killed abruptly.
            with log_path.open("a") as log:
                process = subprocess.Popen(
                    command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                    env={**os.environ, "PYTHONUNBUFFERED": "1", "HF_HUB_OFFLINE": "1"},
                    start_new_session=True, pass_fds=(lock_fd,),
                )
                deadline = time.monotonic() + settings.generation_timeout
                try:
                    while process.poll() is None:
                        if stop.wait(0.2):
                            raise GenerationStopped("API stopped during generation; submit a new job")
                        if time.monotonic() >= deadline:
                            raise TimeoutError("Generation exceeded its time limit; inspect generation.log")
                    if process.returncode:
                        raise RuntimeError(
                            f"MLX exited with status {process.returncode}; inspect generation.log"
                        )
                finally:
                    if process.poll() is None:
                        try:
                            os.killpg(process.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass  # Child exited between poll() and termination.
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                            process.wait()

        backend = MlxVideoBackend(MlxVideoConfig(
            model_directory=settings.model_directory,
            python_executable=settings.python_executable,
            working_directory=settings.project_root,
            width=512, height=512, num_frames=49, steps=40,
            guide_scale=5.0, seed=42, tiling="aggressive",
        ), runner=runner)
        backend.generate(image, prompt, output)
        return validate_output(output)


def validate_output(output: Path):
    """Never advertise success based on only a readable first frame."""
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(output), "-f", "null", "-"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode:
        raise ValueError("Generated MP4 failed full decoding: " + result.stderr[-500:])
    capture = cv2.VideoCapture(str(output))
    try:
        fps = capture.get(cv2.CAP_PROP_FPS)
        count = 0
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if frame.shape[:2] != (PRESET['height'], PRESET['width']):
                raise ValueError("Generated video has unexpected dimensions")
            count += 1
    finally:
        capture.release()
    if count != PRESET['frames'] or abs(fps - PRESET['fps']) > 0.01:
        raise ValueError(f"Generated video has unexpected frame count/FPS: {count}/{fps}")
    return {"width": 512, "height": 512, "frames": count, "fps": fps,
            "bytes": output.stat().st_size,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "full_decode": True}
