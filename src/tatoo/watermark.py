from pathlib import Path

from PIL import Image, ImageOps

LOGO_PATH = Path("img/logo.png")
OPACITY = 0.3


def apply_watermark(image_path: str | Path) -> Path:
    image_path = Path(image_path)
    base = Image.open(image_path)
    base = ImageOps.exif_transpose(base)

    logo = Image.open(LOGO_PATH).convert("RGBA")
    alpha = logo.getchannel("A").point(lambda a: int(a * OPACITY))
    logo.putalpha(alpha)

    canvas = base.convert("RGBA")
    position = (
        (canvas.width - logo.width) // 2,
        (canvas.height - logo.height) // 2,
    )
    canvas.alpha_composite(logo, dest=position)
    canvas = canvas.convert("RGB")

    original_ext = image_path.suffix.lstrip(".").lower()
    output_path = image_path.with_name(f"{image_path.stem}_{original_ext}_marcada.webp")
    canvas.save(output_path, format="WEBP", quality=75)
    return output_path
