import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from tatoo.watermark import apply_watermark

FILETYPES = [("Imagens", "*.png *.jpg *.jpeg *.webp")]
MIN_WIDTH = 420
MIN_HEIGHT = 420


@dataclass
class BatchResult:
    successes: list[Path] = field(default_factory=list)
    failures: list[tuple[Path, str]] = field(default_factory=list)


def _process_files(
    paths: list[Path],
    on_progress: Callable[[int, int], None] | None = None,
) -> BatchResult:
    result = BatchResult()
    total = len(paths)
    for index, path in enumerate(paths, start=1):
        if on_progress is not None:
            on_progress(index, total)
        try:
            output_path = apply_watermark(path)
        except Exception as exc:  # noqa: BLE001 - qualquer falha vira item da lista de falhas
            result.failures.append((path, str(exc)))
            continue
        result.successes.append(output_path)
    return result


def _result_lines(result: BatchResult) -> list[str]:
    lines = [f"OK: {path.name}" for path in result.successes]
    lines.extend(f"Falhou: {path.name} ({error})" for path, error in result.failures)
    return lines


def _set_listbox_items(listbox: tk.Listbox, items: list[str]) -> None:
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)


def _make_listbox_with_scrollbar(parent: ttk.Frame, row: int) -> tk.Listbox:
    container = ttk.Frame(parent)
    container.grid(column=0, row=row, sticky="nsew", pady=(4, 12))
    container.columnconfigure(0, weight=1)
    container.rowconfigure(0, weight=1)

    listbox = tk.Listbox(container)
    listbox.grid(column=0, row=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(container, orient="vertical", command=listbox.yview)
    scrollbar.grid(column=1, row=0, sticky="ns")
    listbox.configure(yscrollcommand=scrollbar.set)

    return listbox


def build_window() -> tk.Tk:
    root = tk.Tk()
    root.title("tatoo")
    root.geometry(f"{MIN_WIDTH}x{MIN_HEIGHT}")
    root.resizable(True, True)
    root.minsize(MIN_WIDTH, MIN_HEIGHT)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    selected_paths: list[Path] = []
    progress_text = tk.StringVar(value="")
    result_summary_text = tk.StringVar(value="")

    frame = ttk.Frame(root, padding=16)
    frame.grid(column=0, row=0, sticky="nsew")
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)
    frame.rowconfigure(5, weight=1)

    select_button = ttk.Button(frame, text="Selecionar imagem(ns)")
    select_button.grid(column=0, row=0, sticky="ew")

    selected_listbox = _make_listbox_with_scrollbar(frame, row=1)

    apply_button = ttk.Button(frame, text="Aplicar marca d'água")
    apply_button.grid(column=0, row=2, sticky="ew")

    progress_label = ttk.Label(frame, textvariable=progress_text)
    progress_label.grid(column=0, row=3, sticky="w", pady=(12, 4))

    result_summary_label = ttk.Label(frame, textvariable=result_summary_text)
    result_summary_label.grid(column=0, row=4, sticky="w")

    result_listbox = _make_listbox_with_scrollbar(frame, row=5)

    def select_images() -> None:
        paths = filedialog.askopenfilenames(title="Selecionar imagem(ns)", filetypes=FILETYPES)
        if paths:
            selected_paths.clear()
            selected_paths.extend(Path(p) for p in paths)
            _set_listbox_items(selected_listbox, [p.name for p in selected_paths])
            progress_text.set("")
            result_summary_text.set("")
            _set_listbox_items(result_listbox, [])

    def report_progress(index: int, total: int) -> None:
        progress_text.set(f"Processando {index} de {total}...")
        root.update_idletasks()

    def apply_to_selected() -> None:
        if not selected_paths:
            messagebox.showerror(
                "Erro", "Selecione ao menos uma imagem antes de aplicar a marca d'água."
            )
            return
        result = _process_files(selected_paths, on_progress=report_progress)
        progress_text.set("")
        total = len(result.successes) + len(result.failures)
        result_summary_text.set(f"{len(result.successes)} de {total} processadas com sucesso")
        _set_listbox_items(result_listbox, _result_lines(result))

    select_button.configure(command=select_images)
    apply_button.configure(command=apply_to_selected)

    root.select_button = select_button
    root.apply_button = apply_button
    root.selected_listbox = selected_listbox
    root.progress_label = progress_label
    root.result_summary_label = result_summary_label
    root.result_listbox = result_listbox

    return root
