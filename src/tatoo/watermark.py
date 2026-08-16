from pathlib import Path

from PIL import Image

LOGO_PATH = Path("img/logo.png")
OPACITY = 0.3


def apply_watermark(image_path: str | Path) -> Path:
    image_path = Path(image_path)
    base = Image.open(image_path)
    base_format = base.format

    logo = Image.open(LOGO_PATH).convert("RGBA")
    alpha = logo.getchannel("A").point(lambda a: int(a * OPACITY))
    logo.putalpha(alpha)

    canvas = base.convert("RGBA")
    position = (
        (canvas.width - logo.width) // 2,
        (canvas.height - logo.height) // 2,
    )
    canvas.alpha_composite(logo, dest=position)

    if base_format in ("JPEG", "WEBP"):
        canvas = canvas.convert("RGB")

    output_path = image_path.with_stem(f"{image_path.stem}_marcada")
    canvas.save(output_path, format=base_format)
    return output_path
