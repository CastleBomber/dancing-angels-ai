"""Deterministic, opt-in character preparation; never modify the source artwork."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps


def prepare_character(source: Path, output: Path, size: int = 512, margin: int = 48) -> dict:
    """Fit visible artwork on white, preserving proportions and head/foot clearance.

    Alpha bounds identify artwork for transparent images. Opaque images retain
    their complete canvas; this function does not infer a foreground mask.
    """
    source, output = Path(source), Path(output)
    if size <= 0 or margin < 0 or margin * 2 >= size:
        raise ValueError("size must be positive with room inside the margins")
    if output.exists() or output.resolve() == source.resolve():
        raise FileExistsError("use a new output path; originals are never overwritten")
    with Image.open(source) as original:
        if getattr(original, "n_frames", 1) != 1:
            raise ValueError("expected a single-frame image")
        rgba = ImageOps.exif_transpose(original).convert("RGBA")
    bounds = rgba.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("image contains no visible artwork")
    artwork = rgba.crop(bounds)
    scale = min((size - 2 * margin) / artwork.width, (size - 2 * margin) / artwork.height)
    fitted = (max(1, round(artwork.width * scale)), max(1, round(artwork.height * scale)))
    artwork = artwork.resize(fitted, Image.Resampling.LANCZOS)
    offset = ((size - fitted[0]) // 2, (size - fitted[1]) // 2)
    canvas = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    canvas.alpha_composite(artwork, offset)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        canvas.convert("RGB").save(stream, format="PNG")
    return {
        "source": str(source.resolve()), "output": str(output.resolve()),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "prepared_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "source_size": list(rgba.size), "alpha_bounds": list(bounds),
        "size": size, "margin": margin, "scale": scale,
        "fitted_size": list(fitted), "offset": list(offset),
        "background": [255, 255, 255], "resampling": "LANCZOS",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--margin", type=int, default=48)
    args = parser.parse_args()
    print(json.dumps(prepare_character(args.image, args.output, args.size, args.margin), indent=2))


if __name__ == "__main__":
    main()
