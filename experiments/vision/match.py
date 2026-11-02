"""Baseline de recherche d'un motif, à résolution et apparence fixes."""

import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from PIL import Image, ImageDraw


def locate(scene, template, threshold=0.98, roi=None):
    """Score = 1 - erreur RGB absolue moyenne / 255 ; ce n'est pas une probabilité."""
    if not 0 <= threshold <= 1:
        raise ValueError("Le seuil doit être compris entre 0 et 1.")
    left, top, right, bottom = roi or (0, 0, *scene.size)
    if not (0 <= left < right <= scene.width and 0 <= top < bottom <= scene.height):
        raise ValueError("La zone de recherche doit être incluse dans l'image.")
    pixels = np.asarray(scene.convert("RGB"), dtype=np.int16)[top:bottom, left:right]
    pattern = np.asarray(template.convert("RGB"), dtype=np.int16)
    height, width = pattern.shape[:2]
    if height > pixels.shape[0] or width > pixels.shape[1]:
        raise ValueError("Le motif est plus grand que la zone de recherche.")
    if float(pattern.std(axis=(0, 1)).max()) < 5:
        raise ValueError("Le motif est trop uniforme pour être discriminant.")
    best_error, best_xy = float("inf"), None
    # Une seule rangée de fenêtres à la fois pour limiter la mémoire temporaire.
    for y in range(pixels.shape[0] - height + 1):
        windows = np.lib.stride_tricks.sliding_window_view(
            pixels[y:y + height], (height, width), axis=(0, 1)
        )[0].transpose(0, 2, 3, 1)
        errors = np.abs(windows - pattern).mean(axis=(1, 2, 3))
        x = int(errors.argmin())
        if errors[x] < best_error:
            best_error = float(errors[x])
            best_xy = (x + left, y + top)
    score = 1 - best_error / 255
    return {
        "found": score >= threshold,
        "bbox": [*best_xy, width, height] if score >= threshold else None,
        "score": score,
        "threshold": threshold,
    }


def demo_images():
    rng = np.random.default_rng(42)
    template = Image.fromarray(rng.integers(20, 240, (9, 7, 3), dtype=np.uint8))
    scene = Image.new("RGB", (128, 96), (32, 32, 32))
    scene.paste(template, (53, 37))
    return scene, template


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Images synthétiques uniquement")
    parser.add_argument("--image", type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--roi", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    parser.add_argument("--threshold", type=float, default=0.98)
    parser.add_argument("--out-dir", type=Path, default=Path("runs/vision"))
    args = parser.parse_args()
    if args.demo and (args.image or args.template):
        parser.error("Utiliser --demo ou --image et --template.")
    if not args.demo and not (args.image and args.template):
        parser.error("Fournir --image et --template, ou --demo.")
    if args.demo:
        scene, template = demo_images()
    else:
        with Image.open(args.image) as source:
            scene = source.convert("RGB")
        with Image.open(args.template) as source:
            template = source.convert("RGB")
    started = perf_counter()
    try:
        result = locate(scene, template, args.threshold, args.roi)
    except ValueError as error:
        parser.error(str(error))
    result["elapsed_ms"] = round((perf_counter() - started) * 1000, 3)
    result["source"] = "synthetic" if args.demo else str(args.image)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.demo:
        scene.save(args.out_dir / "input.png")
        template.save(args.out_dir / "template.png")
    overlay = scene.copy()
    if result["found"]:
        x, y, w, h = result["bbox"]
        ImageDraw.Draw(overlay).rectangle((x, y, x + w - 1, y + h - 1), outline="red", width=2)
    overlay.save(args.out_dir / "overlay.png")
    output = json.dumps(result, indent=2)
    (args.out_dir / "result.json").write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
