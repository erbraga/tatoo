from tatoo.gui import _process_files, build_window


def test_build_window_creates_expected_widgets():
    root = build_window()
    try:
        assert root.title() == "tatoo"
        assert str(root.select_button["text"]) == "Selecionar imagem(ns)"
        assert str(root.apply_button["text"]) == "Aplicar marca d'água"
        assert root.selected_listbox.winfo_exists()
        assert root.progress_label.winfo_exists()
        assert root.result_summary_label.winfo_exists()
        assert root.result_listbox.winfo_exists()
    finally:
        root.destroy()


def test_build_window_is_resizable_with_minsize():
    root = build_window()
    try:
        assert root.resizable() == (1, 1)
        assert root.minsize() == (420, 420)
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
