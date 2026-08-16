from tatoo.gui import (
    _make_thumbnail_image,
    _populate_selected_area,
    _process_files,
    build_window,
)


def test_build_window_creates_expected_widgets():
    root = build_window()
    try:
        assert root.title() == "tatoo"
        assert str(root.select_button["text"]) == "Selecionar imagem(ns)"
        assert str(root.apply_button["text"]) == "Aplicar marca d'água"
        assert root.selected_area.winfo_exists()
        assert root.progress_label.winfo_exists()
        assert root.result_summary_label.winfo_exists()
        assert root.result_listbox.winfo_exists()
    finally:
        root.destroy()


def test_build_window_is_resizable_with_minsize():
    root = build_window()
    try:
        assert root.resizable() == (1, 1)
        assert root.minsize() == (480, 600)
    finally:
        root.destroy()


def test_make_thumbnail_image_from_valid_files(tk_root, png_image, jpg_image, webp_image):
    for image_path in (png_image, jpg_image, webp_image):
        thumbnail = _make_thumbnail_image(image_path)
        assert thumbnail.width() <= 96
        assert thumbnail.height() <= 96


def test_make_thumbnail_image_falls_back_to_placeholder(tk_root, broken_image):
    thumbnail = _make_thumbnail_image(broken_image)

    assert thumbnail.width() == 96
    assert thumbnail.height() == 96


def test_populate_selected_area_creates_one_row_per_file(png_image, broken_image):
    root = build_window()
    try:
        images = _populate_selected_area(root.selected_area, [png_image, broken_image])

        assert len(images) == 2
        assert len(root.selected_area.winfo_children()) == 2
    finally:
        root.destroy()


def test_process_files_all_succeed(png_image, jpg_image, webp_image):
    result = _process_files([png_image, jpg_image, webp_image])

    assert len(result.successes) == 3
    assert result.failures == []
    assert all(path.exists() for path in result.successes)


def test_process_files_partial_failure(png_image, broken_image):
    result = _process_files([png_image, broken_image])

    assert result.successes == [png_image.with_stem(f"{png_image.stem}_marcada")]
    assert len(result.failures) == 1
    assert result.failures[0][0] == broken_image


def test_process_files_empty_list():
    result = _process_files([])

    assert result.successes == []
    assert result.failures == []
