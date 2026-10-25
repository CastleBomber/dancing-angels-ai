"""Tests for the public command-line contract."""

import unittest
from pathlib import Path

from dancing_angels_ai.cli import build_parser


class CliTests(unittest.TestCase):
    def test_documented_acceptance_command_parses(self) -> None:
        args = build_parser().parse_args(
            [
                "animate",
                "--image",
                "assets/woman-1.png",
                "--motion",
                "assets/walk.mp4",
                "--output",
                "outputs/woman-1-walking.mp4",
                "--wan-repo",
                "/opt/Wan2.2",
                "--checkpoint",
                "/models/Wan2.2-Animate-14B",
            ]
        )

        self.assertEqual(args.image, Path("assets/woman-1.png"))
        self.assertEqual(args.motion, Path("assets/walk.mp4"))
        self.assertEqual(args.output, Path("outputs/woman-1-walking.mp4"))
        self.assertTrue(args.retarget)
        self.assertEqual(args.fps, -1)

    def test_mac_create_command_parses(self) -> None:
        args = build_parser().parse_args(
            [
                "create",
                "--image",
                "assets/woman-1.png",
                "--action",
                "walk",
                "--output",
                "outputs/woman-1-walking-mlx.mp4",
            ]
        )

        self.assertEqual(args.command, "create")
        self.assertEqual(args.image, Path("assets/woman-1.png"))
        self.assertEqual(args.action, "walk")
        self.assertEqual(args.frames, 17)
        self.assertEqual(args.steps, 10)

    def test_doctor_command_parses_without_runtime_paths(self) -> None:
        args = build_parser().parse_args(["doctor"])

        self.assertEqual(args.command, "doctor")
        self.assertEqual(args.backend, "mlx")
        self.assertEqual(args.image, Path("assets/woman-1.png"))
        self.assertEqual(args.motion, Path("assets/walk.mp4"))


if __name__ == "__main__":
    unittest.main()
