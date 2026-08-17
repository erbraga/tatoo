import shutil
import tkinter as tk
from pathlib import Path

import pytest
from PIL import Image

ROTATED_JPG_SOURCE = Path("img/20260219_110121.jpg")


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
    path = tmp_path / "teste.webp"
    Image.new("RGB", (300, 200), (80, 180, 120)).save(path, format="WEBP")
    return path


@pytest.fixture
def broken_image(tmp_path) -> Path:
    path = tmp_path / "quebrada.png"
    path.write_bytes(b"nao e uma imagem")
    return path


@pytest.fixture
def rotated_jpg_image(tmp_path) -> Path:
    path = tmp_path / ROTATED_JPG_SOURCE.name
    shutil.copy(ROTATED_JPG_SOURCE, path)
    return path


@pytest.fixture
def tk_root():
    root = tk.Tk()
    yield root
    root.destroy()
