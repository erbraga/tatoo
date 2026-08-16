from tatoo.gui import build_window


def test_build_window_creates_expected_widgets():
    root = build_window()
    try:
        assert root.title() == "tatoo"
        assert str(root.select_button["text"]) == "Selecionar imagem"
        assert str(root.apply_button["text"]) == "Aplicar marca d'água"
        assert root.selected_label.winfo_exists()
        assert root.result_label.winfo_exists()
    finally:
        root.destroy()
