from PIL import Image

from tatoo.watermark import apply_watermark


def test_watermark_png(png_image):
    output = apply_watermark(png_image)

    assert output.name == "teste_marcada.png"
    assert output.exists()
    with Image.open(png_image) as original, Image.open(output) as marked:
        assert marked.size == original.size
        assert marked.tobytes() != original.convert(marked.mode).tobytes()


def test_watermark_jpg(jpg_image):
    output = apply_watermark(jpg_image)

    assert output.name == "teste_marcada.jpg"
    assert output.exists()
    with Image.open(jpg_image) as original, Image.open(output) as marked:
        assert marked.size == original.size
        assert marked.tobytes() != original.convert(marked.mode).tobytes()


def test_watermark_webp(webp_image):
    output = apply_watermark(webp_image)

    assert output.name == webp_image.stem + "_marcada.webp"
    assert output.exists()
    with Image.open(webp_image) as original, Image.open(output) as marked:
        assert marked.size == original.size
        assert marked.tobytes() != original.convert(marked.mode).tobytes()
