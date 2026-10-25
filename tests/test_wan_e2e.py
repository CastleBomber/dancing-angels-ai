"""Opt-in real-model acceptance test for a configured CUDA worker."""

import os
import unittest
from pathlib import Path

from dancing_angels_ai.cli import main
from dancing_angels_ai.video import inspect_video


@unittest.skipUnless(
    os.environ.get("RUN_WAN_E2E") == "1",
    "set RUN_WAN_E2E=1 on the configured CUDA worker",
)
class WanEndToEndTests(unittest.TestCase):
    def test_character_follows_walk_driver(self) -> None:
        wan_repository = os.environ.get("WAN22_REPO")
        checkpoint = os.environ.get("WAN22_CHECKPOINT")
        if not wan_repository or not checkpoint:
            self.fail("WAN22_REPO and WAN22_CHECKPOINT are required")

        output = Path(
            os.environ.get(
                "WAN22_E2E_OUTPUT",
                "outputs/woman-1-walking.mp4",
            )
        )
        status = main(
            [
                "animate",
                "--image",
                "assets/woman-1.png",
                "--motion",
                "assets/walk.mp4",
                "--output",
                str(output),
                "--wan-repo",
                wan_repository,
                "--checkpoint",
                checkpoint,
                "--wan-python",
                os.environ.get("WAN22_PYTHON", "python"),
            ]
        )

        self.assertEqual(status, 0)
        self.assertGreater(inspect_video(output).frame_count, 0)


if __name__ == "__main__":
    unittest.main()
