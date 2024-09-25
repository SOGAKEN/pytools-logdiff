import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from comparison.comparator import compare_logs
from comparison.config_loader import load_toml_config
from utils.file_operations import save_to_csv

from .result_display import create_result_tabs


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("ログファイル比較ツール")
        self.show_true_var = tk.BooleanVar(value=True)
        self.file_entries_a = []
        self.file_entries_b = []
        self.result_notebook = None
        self.all_results = {}

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_file_selection(main_frame)
        self.create_result_area(main_frame)

    def create_file_selection(self, parent):
        file_selection_frame = ttk.Frame(parent)
        file_selection_frame.pack(fill="x", expand=False, pady=(0, 10))

        file_notebook = ttk.Notebook(file_selection_frame)
        file_notebook.pack(fill="x", expand=True)

        for i in range(5):
            self.create_file_set(file_notebook, i)

        show_true_checkbox = ttk.Checkbutton(
            file_selection_frame, text="TRUEを表示", variable=self.show_true_var
        )
        show_true_checkbox.pack(pady=5)

        compare_button = ttk.Button(
            file_selection_frame, text="比較", command=self.compare_files
        )
        compare_button.pack(pady=10)

    def create_file_set(self, notebook, index):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=f"セット {index+1}")

        for j, label in enumerate(["ファイルA:", "ファイルB:"]):
            ttk.Label(frame, text=label).grid(row=j, column=0, padx=5, pady=5)
            entry = ttk.Entry(frame, width=50)
            entry.grid(row=j, column=1, padx=5, pady=5)
            ttk.Button(
                frame, text="選択", command=lambda e=entry: self.select_file(e)
            ).grid(row=j, column=2, padx=5, pady=5)

            if j == 0:
                self.file_entries_a.append(entry)
            else:
                self.file_entries_b.append(entry)

    def create_result_area(self, parent):
        result_frame = ttk.Frame(parent)
        result_frame.pack(fill="both", expand=True)

        self.result_notebook = ttk.Notebook(result_frame)
        self.result_notebook.pack(fill="both", expand=True)

    def select_file(self, entry):
        filename = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
        entry.delete(0, tk.END)
        entry.insert(0, filename)

    def compare_files(self):
        config = load_toml_config()
        if not config:
            messagebox.showerror("エラー", "設定ファイルを読み込めませんでした。")
            return

        self.all_results = {}
        for i in range(5):
            file_a = self.file_entries_a[i].get()
            file_b = self.file_entries_b[i].get()
            if file_a and file_b:
                try:
                    results = compare_logs(file_a, file_b, config)
                    self.all_results[f"Set {i+1}"] = results
                except ValueError as e:
                    messagebox.showerror("エラー", f"セット {i+1}: {str(e)}")
                except Exception as e:
                    messagebox.showerror(
                        "エラー",
                        f"セット {i+1}: 予期せぬエラーが発生しました。\n{str(e)}",
                    )

        if self.all_results:
            create_result_tabs(
                self.result_notebook, self.all_results, self.show_true_var.get()
            )
            save_to_csv(self.all_results)
        else:
            messagebox.showwarning(
                "警告",
                "比較するファイルが選択されていないか、すべての比較でエラーが発生しました。",
            )


def create_gui():
    root = tk.Tk()
    MainWindow(root)
    return root
