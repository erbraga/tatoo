import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tatoo.watermark import apply_watermark

FILETYPES = [("Imagens", "*.png *.jpg *.jpeg *.webp")]
NO_FILE_SELECTED = "Nenhuma imagem selecionada"


def build_window() -> tk.Tk:
    root = tk.Tk()
    root.title("tatoo")
    root.geometry("360x220")
    root.resizable(False, False)

    selected_path = tk.StringVar(value=NO_FILE_SELECTED)
    result_text = tk.StringVar(value="")

    def select_image() -> None:
        path = filedialog.askopenfilename(title="Selecionar imagem", filetypes=FILETYPES)
        if path:
            selected_path.set(path)
            result_text.set("")

    def apply_to_selected() -> None:
        path = selected_path.get()
        if not path or path == NO_FILE_SELECTED:
            messagebox.showerror("Erro", "Selecione uma imagem antes de aplicar a marca d'água.")
            return
        try:
            output_path = apply_watermark(path)
        except Exception as exc:  # noqa: BLE001 - qualquer falha vira erro visível na GUI
            messagebox.showerror("Erro ao aplicar marca d'água", str(exc))
            return
        result_text.set(f"Gerado: {output_path}")

    frame = ttk.Frame(root, padding=16)
    frame.grid()

    select_button = ttk.Button(frame, text="Selecionar imagem", command=select_image)
    select_button.grid(column=0, row=0, sticky="ew")

    selected_label = ttk.Label(frame, textvariable=selected_path, wraplength=320)
    selected_label.grid(column=0, row=1, sticky="w", pady=(4, 12))

    apply_button = ttk.Button(frame, text="Aplicar marca d'água", command=apply_to_selected)
    apply_button.grid(column=0, row=2, sticky="ew")

    result_label = ttk.Label(frame, textvariable=result_text, wraplength=320)
    result_label.grid(column=0, row=3, sticky="w", pady=(12, 0))

    root.select_button = select_button
    root.apply_button = apply_button
    root.selected_label = selected_label
    root.result_label = result_label

    return root
