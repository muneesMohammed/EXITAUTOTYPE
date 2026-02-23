#!/usr/bin/env python3
"""Tkinter UI for uploading a PDF/image and printing all decoded QR text/data."""

from __future__ import annotations

import json
import tkinter as tk
from dataclasses import asdict
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from qr_data_extractor import extract_qr_link_data


class QRExtractorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("QR Document Reader")
        self.root.geometry("900x620")

        self.file_var = tk.StringVar()
        self.download_json_var = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self) -> None:
        top = tk.Frame(self.root, padx=12, pady=12)
        top.pack(fill="x")

        tk.Label(top, text="Document (PDF/Image):").grid(row=0, column=0, sticky="w")

        entry = tk.Entry(top, textvariable=self.file_var, width=80)
        entry.grid(row=1, column=0, padx=(0, 8), pady=8, sticky="we")

        tk.Button(top, text="Upload", command=self.pick_file, width=12).grid(
            row=1, column=1, pady=8
        )

        tk.Checkbutton(
            top,
            text="Download JSON when QR contains URL",
            variable=self.download_json_var,
        ).grid(row=2, column=0, sticky="w", pady=(2, 8))

        tk.Button(top, text="Scan & Print All Text", command=self.run_scan, width=25).grid(
            row=2, column=1, sticky="e"
        )

        top.grid_columnconfigure(0, weight=1)

        self.output = ScrolledText(self.root, wrap="word", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._set_output(
            "Upload a PDF/image, then click 'Scan & Print All Text'.\n"
            "The app will print decoded QR text and parsed variables."
        )

    def _set_output(self, text: str) -> None:
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)

    def pick_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select PDF or image",
            filetypes=[
                ("Documents", "*.pdf *.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
                ("All Files", "*.*"),
            ],
        )
        if selected:
            self.file_var.set(selected)

    def run_scan(self) -> None:
        file_path = Path(self.file_var.get().strip())
        if not file_path:
            messagebox.showwarning("Missing file", "Please upload/select a file first.")
            return
        if not file_path.exists():
            messagebox.showerror("File not found", f"File does not exist:\n{file_path}")
            return

        try:
            results = extract_qr_link_data(
                file_path,
                include_downloaded_json=self.download_json_var.get(),
            )
        except RuntimeError as exc:
            messagebox.showerror("Scan failed", str(exc))
            return
        except Exception as exc:  # pragma: no cover - last-resort UI guard
            messagebox.showerror("Unexpected error", str(exc))
            return

        if not results:
            self._set_output("No QR code found in the selected document.")
            return

        blocks: list[str] = []
        for idx, item in enumerate(results, start=1):
            item_json = json.dumps(asdict(item), indent=2, ensure_ascii=False)
            blocks.append(f"QR #{idx}\n{item_json}")

        all_text = "\n\n".join(blocks)
        self._set_output(all_text)


def main() -> int:
    root = tk.Tk()
    QRExtractorApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
