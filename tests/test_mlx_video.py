"""Tests for the Apple-silicon image-to-video adapter."""

import tempfile
import unittest
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np
from PIL import Image

from dancing_angels_ai.generation.mlx_video import (
    MlxVideoBackend,
    MlxVideoConfig,
    prompt_for_action,
)


class MlxVideoBackendTests(unittest.TestCase):
    def test_build_command_uses_current_module_path(self) -> None:
        config = MlxVideoConfig(model_directory=Path("model"))
        command = MlxVideoBackend(config).build_command(
            Path("character.png"),
            prompt_for_action("walk"),
            Path("result.mp4"),
        )

        self.assertEqual(
            command[1:3],
            ["-m", "mlx_video.models.wan_2.generate"],
        )
        self.assertIn("--image", command)
        self.assertIn("--output-path", command)

    def test_defaults_are_a_small_mac_smoke_test(self) -> None:
        config = MlxVideoConfig(model_directory=Path("model"))

        self.assertEqual(config.width, 512)
        self.assertEqual(config.height, 512)
        self.assertEqual(config.num_frames, 17)
        self.assertEqual(config.steps, 10)
        self.assertEqual(config.tiling, "aggressive")

    def test_generate_validates_and_atomically_publishes_video(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            model = root / "model"
            model.mkdir()
            for filename in (
                "config.json",
                "model.safetensors",
                "t5_encoder.safetensors",
                "vae.safetensors",
            ):
                (model / filename).write_bytes(b"test")
            image = root / "character.png"
            portrait = Image.new("RGBA", (100, 200), (0, 0, 0, 0))
            portrait.paste((255, 0, 0, 255), (30, 60, 70, 160))
            portrait.paste((0, 255, 0, 255), (30, 160, 70, 180))
            portrait.save(image)
            original = image.read_bytes()
            output = root / "result.mp4"

            def fake_runner(command: Sequence[str], cwd: Path) -> None:
                del cwd
                model_image = Path(command[command.index("--image") + 1])
                self.assertNotEqual(model_image, image)
                with Image.open(model_image) as prepared:
                    self.assertEqual(prepared.size, (512, 512))
                    self.assertEqual(prepared.mode, "RGB")
                    self.assertEqual(prepared.getpixel((0, 0)), (255, 255, 255))
                    self.assertEqual(prepared.getpixel((256, 450)), (0, 255, 0))
                self.assertTrue((model_image.parent / "preparation.json").is_file())
                output_index = command.index("--output-path") + 1
                partial = Path(command[output_index])
                writer = cv2.VideoWriter(
                    str(partial),
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    8.0,
                    (64, 64),
                )
                self.assertTrue(writer.isOpened())
                writer.write(np.zeros((64, 64, 3), dtype=np.uint8))
                writer.write(np.ones((64, 64, 3), dtype=np.uint8) * 255)
                writer.release()

            backend = MlxVideoBackend(
                MlxVideoConfig(
                    model_directory=model,
                    working_directory=root,
                ),
                runner=fake_runner,
            )
            result = backend.generate(
                image,
                prompt_for_action("walk"),
                output,
            )

            self.assertEqual(result, output.resolve())
            self.assertTrue(output.is_file())
            self.assertFalse((root / ".result.partial.mp4").exists())
            self.assertEqual(image.read_bytes(), original)

    def test_frame_count_must_be_four_n_plus_one(self) -> None:
        with self.assertRaisesRegex(ValueError, r"4n\+1"):
            MlxVideoConfig(
                model_directory=Path("model"),
                num_frames=16,
            )


if __name__ == "__main__":
    unittest.main()
