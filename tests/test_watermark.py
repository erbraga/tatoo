from PIL import Image

from tatoo.watermark import apply_watermark


def test_watermark_png(png_image):
    output = apply_watermark(png_image)

    assert output.name == "teste_png_marcada.webp"
    assert output.exists()
    with Image.open(output) as marked:
        assert marked.format == "WEBP"


def test_watermark_jpg(jpg_image):
    output = apply_watermark(jpg_image)

    assert output.name == "teste_jpg_marcada.webp"
    assert output.exists()
    with Image.open(output) as marked:
        assert marked.format == "WEBP"


def test_watermark_webp(webp_image):
    output = apply_watermark(webp_image)

    assert output.name == f"{webp_image.stem}_webp_marcada.webp"
    assert output.exists()
    with Image.open(output) as marked:
        assert marked.format == "WEBP"


def test_watermark_respects_exif_orientation(rotated_jpg_image):
    output = apply_watermark(rotated_jpg_image)

    with Image.open(output) as marked:
        assert marked.size == (1848, 4000)
