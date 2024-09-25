import csv
import datetime
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, font, messagebox, scrolledtext, ttk

import toml


def detect_block_identifier(content):
    first_lines = content.split("\n")[:10]
    for line in first_lines:
        match = re.match(r"^(\S+)\s*#", line)
        if match:
            return match.group(1)
    return None


def compare_logs(file_a, file_b, config):
    with open(file_a, "r") as f_a, open(file_b, "r") as f_b:
        content_a = f_a.read()
        content_b = f_b.read()

    block_identifier = detect_block_identifier(content_a)
    if not block_identifier:
        raise ValueError("ブロック識別子を検出できませんでした。")

    blocks_a = re.split(rf"(?={re.escape(block_identifier)}\s*#)", content_a)
    blocks_b = re.split(rf"(?={re.escape(block_identifier)}\s*#)", content_b)

    results = []
    id_counter = 1

    # グローバル比較
    if "global" in config:
        global_result = compare_global(
            content_a, content_b, config["global"], id_counter
        )
        results.extend(global_result)
        id_counter += len(global_result)

    cumulative_lines_a = 0
    cumulative_lines_b = 0

    # ブロック単位の比較
    for i, (block_a, block_b) in enumerate(zip(blocks_a, blocks_b), 1):
        block_type = get_block_type(block_a, block_identifier)
        if block_type in config:
            block_config = config[block_type]
            block_result = compare_block(
                block_a,
                block_b,
                block_config,
                id_counter,
                i,
                block_type,
                block_identifier,
                cumulative_lines_a,
                cumulative_lines_b,
            )
            results.extend(block_result)
            id_counter += len(block_result)

        cumulative_lines_a += len(block_a.split("\n"))
        cumulative_lines_b += len(block_b.split("\n"))

    return results


def get_block_type(block, block_identifier):
    first_line = block.split("\n")[0]
    match = re.search(rf"{re.escape(block_identifier)}\s*#\s*(.*)", first_line)
    return match.group(1).strip() if match else ""


def compare_global(content_a, content_b, global_config, id_counter):
    results = []
    lines_a = content_a.splitlines()
    lines_b = content_b.splitlines()

    print(
        f"Global comparison started. Total lines in file A: {len(lines_a)}, file B: {len(lines_b)}"
    )

    skip_empty_lines = global_config.get("skip_empty_lines", False)
    if skip_empty_lines:
        lines_a = [line for line in lines_a if line.strip()]
        lines_b = [line for line in lines_b if line.strip()]
        print(
            f"Skipped empty lines. Remaining lines in file A: {len(lines_a)}, file B: {len(lines_b)}"
        )

    for keyword_config in global_config.get("keywords", []):
        name = keyword_config["name"]
        pattern = keyword_config["pattern"]
        is_regex = keyword_config.get("regex", False)
        lines_after = keyword_config.get("lines_after", 0)

        print(
            f"Processing keyword: {name}, pattern: {pattern}, regex: {is_regex}, lines_after: {lines_after}"
        )

        for i in range(min(len(lines_a), len(lines_b))):
            line_a = lines_a[i]
            line_b = lines_b[i]

            match_a = re.search(pattern, line_a) if is_regex else pattern in line_a
            match_b = re.search(pattern, line_b) if is_regex else pattern in line_b

            if match_a or match_b:
                print(f"Match found at line {i+1}")
                end_line = min(i + lines_after + 1, len(lines_a), len(lines_b))
                content_a = "\n".join(lines_a[i:end_line])
                content_b = "\n".join(lines_b[i:end_line])

                result = "TRUE" if content_a == content_b else "FALSE"
                results.append(
                    {
                        "id": id_counter,
                        "block": "global",
                        "block_type": "global",
                        "keyword": name,
                        "file_a_content": content_a,
                        "file_b_content": content_b,
                        "file_a_line": i + 1,
                        "file_b_line": i + 1,
                        "result": result,
                    }
                )
                print(f"Comparison result: {result}")
                print(f"Content A: {content_a}")
                print(f"Content B: {content_b}")
                id_counter += 1
                break  # 最初のマッチのみを処理

    print(f"Global comparison finished. Total results: {len(results)}")
    return results


def compare_block(
    block_a,
    block_b,
    block_config,
    id_counter,
    block_number,
    block_type,
    block_identifier,
    cumulative_lines_a,
    cumulative_lines_b,
):
    results = []
    lines_a = block_a.split("\n")[1:]  # Skip the first line (block identifier)
    lines_b = block_b.split("\n")[1:]

    skip_patterns = block_config.get("skip_patterns", [])
    skip_sections = block_config.get("skip_sections", [])
    skip_empty_lines = block_config.get("skip_empty_lines", False)

    lines_a = skip_sections_in_lines(lines_a, skip_sections)
    lines_b = skip_sections_in_lines(lines_b, skip_sections)

    lines_a = [
        line
        for line in lines_a
        if not any(re.search(pattern, line) for pattern in skip_patterns)
    ]
    lines_b = [
        line
        for line in lines_b
        if not any(re.search(pattern, line) for pattern in skip_patterns)
    ]

    if skip_empty_lines:
        lines_a = [line for line in lines_a if line.strip()]
        lines_b = [line for line in lines_b if line.strip()]

    if "compare_all" in block_config and block_config["compare_all"]:
        for i, (line_a, line_b) in enumerate(zip(lines_a, lines_b)):
            result = "TRUE" if line_a.strip() == line_b.strip() else "FALSE"
            results.append(
                {
                    "id": id_counter,
                    "block": block_number,
                    "block_type": block_type,
                    "keyword": "All lines",
                    "file_a_content": line_a.strip(),
                    "file_b_content": line_b.strip(),
                    "file_a_line": cumulative_lines_a
                    + i
                    + 2,  # +2 for block identifier and 0-based index
                    "file_b_line": cumulative_lines_b + i + 2,
                    "result": result,
                }
            )
            id_counter += 1

    for keyword, config in block_config.items():
        if isinstance(config, dict):
            if "pattern" in config:
                results.extend(
                    compare_pattern(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)
            elif "continuous" in config:
                results.extend(
                    compare_continuous(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)
            elif "split" in config:
                results.extend(
                    compare_split(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)
            elif "multi_line" in config:
                results.extend(
                    compare_multi_line(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)
            elif "exact" in config:
                results.extend(
                    compare_exact(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)

    return results


def skip_sections_in_lines(lines, skip_sections):
    result = []
    skip = False
    for line in lines:
        for start, end in skip_sections:
            if re.search(start, line):
                skip = True
            elif re.search(end, line):
                skip = False
                break
        if not skip:
            result.append(line)
    return result


def compare_pattern(
    lines_a,
    lines_b,
    keyword,
    config,
    id_counter,
    block_number,
    block_type,
    cumulative_lines_a,
    cumulative_lines_b,
):
    pattern = config["pattern"]
    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)
    matches_a = list(re.finditer(pattern, content_a, re.MULTILINE))
    matches_b = list(re.finditer(pattern, content_b, re.MULTILINE))

    results = []
    for i, (match_a, match_b) in enumerate(zip(matches_a, matches_b)):
        content_a = match_a.group(1) if match_a else "Not found"
        content_b = match_b.group(1) if match_b else "Not found"
        result = "TRUE" if content_a == content_b else "FALSE"
        results.append(
            {
                "id": id_counter + i,
                "block": block_number,
                "block_type": block_type,
                "keyword": f"{keyword} ({i+1})",
                "file_a_content": content_a,
                "file_b_content": content_b,
                "file_a_line": (
                    cumulative_lines_a + content_a[: match_a.start()].count("\n") + 2
                    if match_a
                    else "N/A"
                ),
                "file_b_line": (
                    cumulative_lines_b + content_b[: match_b.start()].count("\n") + 2
                    if match_b
                    else "N/A"
                ),
                "result": result,
            }
        )
    return results


def compare_continuous(
    lines_a,
    lines_b,
    keyword,
    config,
    id_counter,
    block_number,
    block_type,
    cumulative_lines_a,
    cumulative_lines_b,
):
    pattern = config["continuous"]
    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)
    matches_a = list(re.finditer(pattern, content_a, re.MULTILINE))
    matches_b = list(re.finditer(pattern, content_b, re.MULTILINE))

    results = []
    for i, (match_a, match_b) in enumerate(zip(matches_a, matches_b)):
        result = "TRUE" if match_a.group(0) == match_b.group(0) else "FALSE"
        results.append(
            {
                "id": id_counter + i,
                "block": block_number,
                "block_type": block_type,
                "keyword": f"{keyword} ({i+1})",
                "file_a_content": match_a.group(0),
                "file_b_content": match_b.group(0),
                "file_a_line": cumulative_lines_a
                + content_a[: match_a.start()].count("\n")
                + 2,
                "file_b_line": cumulative_lines_b
                + content_b[: match_b.start()].count("\n")
                + 2,
                "result": result,
            }
        )
    return results


def compare_split(
    lines_a,
    lines_b,
    keyword,
    config,
    id_counter,
    block_number,
    block_type,
    cumulative_lines_a,
    cumulative_lines_b,
):
    split_config = config["split"]
    pattern = split_config["pattern"]
    indices = split_config["indices"]

    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)
    match_a = re.search(pattern, content_a, re.MULTILINE)
    match_b = re.search(pattern, content_b, re.MULTILINE)

    results = []
    if match_a and match_b:
        items_a = re.split(r"[,\s]+", match_a.group(1))
        items_b = re.split(r"[,\s]+", match_b.group(1))
        for i, idx in enumerate(indices):
            if idx <= len(items_a) and idx <= len(items_b):
                result = "TRUE" if items_a[idx - 1] == items_b[idx - 1] else "FALSE"
                results.append(
                    {
                        "id": id_counter + i,
                        "block": block_number,
                        "block_type": block_type,
                        "keyword": f"{keyword} (項目 {idx})",
                        "file_a_content": items_a[idx - 1],
                        "file_b_content": items_b[idx - 1],
                        "file_a_line": cumulative_lines_a
                        + content_a[: match_a.start()].count("\n")
                        + 2,
                        "file_b_line": cumulative_lines_b
                        + content_b[: match_b.start()].count("\n")
                        + 2,
                        "result": result,
                    }
                )
    return results


def compare_multi_line(
    lines_a,
    lines_b,
    keyword,
    config,
    id_counter,
    block_number,
    block_type,
    cumulative_lines_a,
    cumulative_lines_b,
):
    start_pattern = config["multi_line"]["start"]
    end_pattern = config["multi_line"]["end"]
    skip_lines = config["multi_line"].get("skip", 0)

    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)
    matches_a = list(
        re.finditer(
            f"{start_pattern}(.*?){end_pattern}", content_a, re.DOTALL | re.MULTILINE
        )
    )
    matches_b = list(
        re.finditer(
            f"{start_pattern}(.*?){end_pattern}", content_b, re.DOTALL | re.MULTILINE
        )
    )

    results = []
    for i, (match_a, match_b) in enumerate(zip(matches_a, matches_b)):
        lines_a = match_a.group(1).strip().split("\n")[skip_lines:]
        lines_b = match_b.group(1).strip().split("\n")[skip_lines:]

        for j, (line_a, line_b) in enumerate(zip(lines_a, lines_b)):
            result = "TRUE" if line_a.strip() == line_b.strip() else "FALSE"
            results.append(
                {
                    "id": id_counter + i * len(lines_a) + j,
                    "block": block_number,
                    "block_type": block_type,
                    "keyword": f"{keyword} ({i+1}, 行 {j+1})",
                    "file_a_content": line_a.strip(),
                    "file_b_content": line_b.strip(),
                    "file_a_line": cumulative_lines_a
                    + content_a[: match_a.start()].count("\n")
                    + skip_lines
                    + j
                    + 2,
                    "file_b_line": cumulative_lines_b
                    + content_b[: match_b.start()].count("\n")
                    + skip_lines
                    + j
                    + 2,
                    "result": result,
                }
            )
    return results


def compare_exact(
    lines_a,
    lines_b,
    keyword,
    config,
    id_counter,
    block_number,
    block_type,
    cumulative_lines_a,
    cumulative_lines_b,
):
    exact_config = config["exact"]
    start_keyword = exact_config.get("start_keyword", "")
    end_keyword = exact_config.get("end_keyword", "")

    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)

    start_index_a = content_a.find(start_keyword) if start_keyword else 0
    start_index_b = content_b.find(start_keyword) if start_keyword else 0
    end_index_a = (
        content_a.find(end_keyword, start_index_a) if end_keyword else len(content_a)
    )
    end_index_b = (
        content_b.find(end_keyword, start_index_b) if end_keyword else len(content_b)
    )

    if start_index_a == -1 or start_index_b == -1:
        return []

    content_a = content_a[start_index_a:end_index_a]
    content_b = content_b[start_index_b:end_index_b]

    result = "TRUE" if content_a.strip() == content_b.strip() else "FALSE"
    return [
        {
            "id": id_counter,
            "block": block_number,
            "block_type": block_type,
            "keyword": keyword,
            "file_a_content": content_a.strip(),
            "file_b_content": content_b.strip(),
            "file_a_line": cumulative_lines_a
            + content_a[:start_index_a].count("\n")
            + 2,
            "file_b_line": cumulative_lines_b
            + content_b[:start_index_b].count("\n")
            + 2,
            "result": result,
        }
    ]


def load_toml_config():
    if getattr(sys, "frozen", False):
        # PyInstallerでバンドルされている場合
        if hasattr(sys, "_MEIPASS"):
            bundle_dir = sys._MEIPASS  # type: ignore
        else:
            bundle_dir = os.path.dirname(sys.executable)
    else:
        # 通常のPythonスクリプトとして実行されている場合
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(bundle_dir, "config.toml")

    try:
        with open(config_path, "r") as f:
            config = toml.load(f)

        for block, block_config in config.items():
            if "skip_sections" in block_config:
                block_config["skip_sections"] = [
                    (section["start"], section["end"])
                    for section in block_config["skip_sections"]
                ]

            if "skip_empty_lines" not in block_config:
                block_config["skip_empty_lines"] = False

        return config
    except Exception as e:
        messagebox.showerror(
            "エラー", f"設定ファイルの読み込みに失敗しました: {str(e)}"
        )
    return None


def select_file(entry):
    filename = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)


def compare_files():
    config = load_toml_config()
    if not config:
        messagebox.showerror("エラー", "設定ファイルを読み込めませんでした。")
        return

    global all_results
    all_results = {}
    for i in range(5):
        file_a = file_entries_a[i].get()
        file_b = file_entries_b[i].get()
        if file_a and file_b:
            try:
                results = compare_logs(file_a, file_b, config)
                all_results[f"Set {i+1}"] = results
            except ValueError as e:
                messagebox.showerror("エラー", f"セット {i+1}: {str(e)}")
            except Exception as e:
                messagebox.showerror(
                    "エラー", f"セット {i+1}: 予期せぬエラーが発生しました。\n{str(e)}"
                )

    if all_results:
        create_result_tabs()
        save_to_csv(all_results)
    else:
        messagebox.showwarning(
            "警告",
            "比較するファイルが選択されていないか、すべての比較でエラーが発生しました。",
        )


def create_result_tabs():
    for child in result_notebook.winfo_children():
        child.destroy()

    for set_name, results in all_results.items():
        frame = ttk.Frame(result_notebook)
        result_notebook.add(frame, text=set_name)

        # TRUEの表示・非表示切り替えチェックボックス
        show_true_var = tk.BooleanVar(value=True)
        show_true_checkbox = ttk.Checkbutton(
            frame,
            text="TRUEを表示",
            variable=show_true_var,
            command=lambda f=frame, r=results, v=show_true_var: update_result_display(
                f, r, v
            ),
        )
        show_true_checkbox.pack(pady=5)

        fixed_font = font.nametofont("TkFixedFont")
        result_text = scrolledtext.ScrolledText(
            frame, height=30, width=100, font=fixed_font
        )
        result_text.pack(expand=True, fill="both")

        result_text.config(
            tabs=(
                "5c",
                "10c",
                "5c",
            )
        )

        result_text.tag_configure(
            "bold", font=(fixed_font.cget("family"), fixed_font.cget("size"), "bold")
        )
        result_text.tag_configure("green", foreground="green")
        result_text.tag_configure("red", foreground="red")

        display_results(result_text, results, show_true_var.get())


def update_result_display(frame, results, show_true_var):
    for widget in frame.winfo_children():
        if isinstance(widget, scrolledtext.ScrolledText):
            widget.delete("1.0", tk.END)
            display_results(widget, results, show_true_var.get())
            break


def display_results(result_text, results, show_true):
    summary = create_summary(results)

    result_text.insert(tk.END, "サマリー:\n", "bold")
    for i, (block_type, counts) in enumerate(summary.items(), 1):
        result_text.insert(tk.END, f"{i}.{block_type}\t", "bold")
        result_text.insert(tk.END, f"TRUE: {counts['true']}\t", "green")
        result_text.insert(tk.END, f"FALSE: {counts['false']}\n", "red")

    result_text.insert(tk.END, "\n")

    current_block_type = None
    for result in results:
        if result["result"] == "TRUE" and not show_true:
            continue

        if result["block_type"] != current_block_type:
            current_block_type = result["block_type"]
            result_text.insert(
                tk.END, f"\nブロックタイプ: {current_block_type}\n", "bold"
            )

        result_text.insert(
            tk.END, f"ID: {result['id']}, キーワード: {result['keyword']}\n"
        )
        result_text.insert(
            tk.END,
            f"ファイルA ({result['file_a_line']}行目): {result['file_a_content']}\n",
        )
        result_text.insert(
            tk.END,
            f"ファイルB ({result['file_b_line']}行目): {result['file_b_content']}\n",
        )
        if result["result"] == "TRUE":
            result_text.insert(tk.END, f"結果: {result['result']}\n\n", "green")
        else:
            result_text.insert(tk.END, f"結果: {result['result']}\n\n", "red")


def create_summary(results):
    summary = {}
    for result in results:
        block_type = result["block_type"]
        if block_type not in summary:
            summary[block_type] = {"true": 0, "false": 0}

        if result["result"] == "TRUE":
            summary[block_type]["true"] += 1
        elif result["result"] == "FALSE":
            summary[block_type]["false"] += 1

    return summary


def save_to_csv(all_results):
    if getattr(sys, "frozen", False):
        output_dir = os.path.dirname(sys.executable)
    else:
        output_dir = os.path.dirname(os.path.abspath(__file__))

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    for set_name, results in all_results.items():
        set_name_for_filename = set_name.replace(" ", "")
        filename = os.path.join(
            output_dir, f"comparison_results_{timestamp}_{set_name_for_filename}.csv"
        )

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "id",
                "block",
                "block_type",
                "keyword",
                "file_a_content",
                "file_b_content",
                "file_a_line",
                "file_b_line",
                "result",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

    messagebox.showinfo(
        "成功", f"結果をCSVファイルに保存しました。\n保存先ディレクトリ: {output_dir}"
    )


# GUIの作成
root = tk.Tk()
root.title("ログファイル比較ツール")

# メインフレームの作成
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# ファイル選択部分（上部）
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

compare_button = ttk.Button(file_selection_frame, text="比較", command=compare_files)
compare_button.pack(pady=10)

# 比較結果部分（下部）
result_frame = ttk.Frame(main_frame)
result_frame.pack(fill="both", expand=True)

result_notebook = ttk.Notebook(result_frame)
result_notebook.pack(fill="both", expand=True)

all_results = {}  # グローバル変数として結果を保存

if __name__ == "__main__":
    root.mainloop()
