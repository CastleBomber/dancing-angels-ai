import tempfile
import unittest
from pathlib import Path

from PIL import Image

from dancing_angels_ai.preparation import prepare_character, prepare_generation_input


class PreparationTests(unittest.TestCase):
    def test_prepared_reference_is_not_padded_twice(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "source.png", Path(directory) / "prepared.png"
            Image.new("RGB", (512, 512), "red").save(source)
            record = prepare_generation_input(source, output, 512, 512)
            self.assertFalse(record["prepared"])
            self.assertEqual(Path(record["output"]), source.resolve())
            self.assertFalse(output.exists())

    def test_rectangular_target_preserves_artwork_and_orientation(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "source.png", Path(directory) / "prepared.png"
            image = Image.new("RGB", (40, 80), "red")
            exif = Image.Exif()
            exif[274] = 6
            image.save(source, exif=exif)
            record = prepare_generation_input(source, output, 320, 160)
            self.assertTrue(record["prepared"])
            self.assertEqual(record["alpha_bounds"], [0, 0, 80, 40])
            self.assertEqual(record["fitted_size"], [260, 130])
            with Image.open(output) as prepared:
                self.assertEqual(prepared.size, (320, 160))
                self.assertEqual(prepared.getpixel((160, 80)), (255, 0, 0))

    def test_transparent_portrait_preserves_feet_and_composites_alpha(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "source.png", Path(directory) / "prepared.png"
            image = Image.new("RGBA", (100, 200), (0, 0, 0, 0))
            image.paste((255, 0, 0, 255), (30, 60, 70, 160))
            image.paste((0, 255, 0, 255), (30, 160, 70, 180))
            image.putpixel((50, 100), (0, 0, 255, 128))
            image.save(source)
            original = source.read_bytes()
            record = prepare_character(source, output, size=160, margin=20)
            self.assertEqual(record["alpha_bounds"], [30, 60, 70, 180])
            self.assertEqual(record["fitted_size"], [40, 120])
            with Image.open(output) as prepared:
                self.assertEqual(prepared.mode, "RGB")
                self.assertEqual(prepared.getpixel((0, 0)), (255, 255, 255))
                self.assertEqual(prepared.getpixel((80, 135)), (0, 255, 0))
                self.assertEqual(prepared.getpixel((80, 60)), (127, 127, 255))
            self.assertEqual(source.read_bytes(), original)
            with self.assertRaises(FileExistsError):
                prepare_character(source, source)
            with self.assertRaises(FileExistsError):
                prepare_character(source, output)

    def test_empty_alpha_rejected_and_opaque_canvas_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "source.png", Path(directory) / "prepared.png"
            Image.new("RGBA", (20, 40)).save(source)
            with self.assertRaises(ValueError):
                prepare_character(source, output)
            Image.new("RGB", (20, 40), "red").save(source)
            record = prepare_character(source, output)
            self.assertEqual(record["alpha_bounds"], [0, 0, 20, 40])
            self.assertEqual(record["fitted_size"], [208, 416])
