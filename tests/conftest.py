import shutil
from pathlib import Path

import pytest
from PIL import Image

REAL_WEBP_SOURCE = Path("img/20260226_114501.webp")


@pytest.fixture
def png_image(tmp_path) -> Path:
    path = tmp_path / "teste.png"
    Image.new("RGB", (300, 200), (200, 100, 50)).save(path, format="PNG")
    return path


@pytest.fixture
def jpg_image(tmp_path) -> Path:
    path = tmp_path / "teste.jpg"
    Image.new("RGB", (300, 200), (50, 100, 200)).save(path, format="JPEG")
    return path


@pytest.fixture
def webp_image(tmp_path) -> Path:
    path = tmp_path / REAL_WEBP_SOURCE.name
    shutil.copy(REAL_WEBP_SOURCE, path)
    return path


@pytest.fixture
def broken_image(tmp_path) -> Path:
    path = tmp_path / "quebrada.png"
    path.write_bytes(b"nao e uma imagem")
    return path
