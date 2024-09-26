import tkinter as tk
from tkinter import ttk

# ... (その他のインポートと関数は変更なし)


def create_gui():
    global root, file_entries_a, file_entries_b, show_true_var

    root = tk.Tk()
    root.title("高度なログファイル比較ツール")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    file_selection_frame = ttk.Frame(main_frame)
    file_selection_frame.pack(fill="x", expand=False, pady=(0, 10))

    file_notebook = ttk.Notebook(file_selection_frame)
    file_notebook.pack(fill="x", expand=True)

    file_entries_a = []
    file_entries_b = []

    for i in range(5):
        frame = ttk.Frame(file_notebook)
        file_notebook.add(frame, text=f"セット {i+1}")

        file_a_label = ttk.Label(frame, text="ファイルA:")
        file_a_label.grid(row=0, column=0, padx=5, pady=5)
        file_a_entry = ttk.Entry(frame, width=50)
        file_a_entry.grid(row=0, column=1, padx=5, pady=5)
        file_a_button = ttk.Button(
            frame, text="選択", command=lambda e=file_a_entry: select_file(e)
        )
        file_a_button.grid(row=0, column=2, padx=5, pady=5)

        file_b_label = ttk.Label(frame, text="ファイルB:")
        file_b_label.grid(row=1, column=0, padx=5, pady=5)
        file_b_entry = ttk.Entry(frame, width=50)
        file_b_entry.grid(row=1, column=1, padx=5, pady=5)
        file_b_button = ttk.Button(
            frame, text="選択", command=lambda e=file_b_entry: select_file(e)
        )
        file_b_button.grid(row=1, column=2, padx=5, pady=5)

        file_entries_a.append(file_a_entry)
        file_entries_b.append(file_b_entry)

    # TRUEの結果を表示するかどうかを指定するチェックボックス
    show_true_var = tk.BooleanVar(value=True)
    show_true_checkbox = ttk.Checkbutton(
        file_selection_frame, text="TRUEの結果を表示する", variable=show_true_var
    )
    show_true_checkbox.pack(pady=5)

    compare_button = ttk.Button(
        file_selection_frame, text="比較", command=compare_files
    )
    compare_button.pack(pady=10)

    # 結果表示用のNotebook
    global result_notebook
    result_notebook = ttk.Notebook(main_frame)
    result_notebook.pack(fill="both", expand=True)


# ... (その他の関数は変更なし)

if __name__ == "__main__":
    create_gui()
    root.mainloop()
