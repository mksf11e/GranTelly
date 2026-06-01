import argparse
from pathlib import Path

from PIL import Image, ImageOps


DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480


def prepare_display_image(input_path, output_path, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT):
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(input_path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image = ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        image = image.rotate(180)
        image.save(output_path, format="JPEG", quality=86, optimize=True)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Prepare a display-ready JPEG for the public GIMY demo.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="runtime/display.jpg")
    parser.add_argument("--width", type=int, default=DISPLAY_WIDTH)
    parser.add_argument("--height", type=int, default=DISPLAY_HEIGHT)
    args = parser.parse_args()
    output = prepare_display_image(args.input, args.output, width=args.width, height=args.height)
    print(f"saved={output}")


if __name__ == "__main__":
    main()
