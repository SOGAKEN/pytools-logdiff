from tkinter import ttk, scrolledtext, font


def create_result_tabs(result_notebook, all_results, show_true):
    for child in result_notebook.winfo_children():
        child.destroy()

    for set_name, results in all_results.items():
        frame = ttk.Frame(result_notebook)
        result_notebook.add(frame, text=set_name)

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

        display_results(result_text, results, show_true)


def display_results(result_text, results, show_true):
    summary = create_summary(results)

    result_text.insert("end", "サマリー:\n", "bold")
    for i, (block_type, counts) in enumerate(summary.items(), 1):
        result_text.insert("end", f"{i}.{block_type}\t", "bold")
        result_text.insert("end", f"TRUE: {counts['true']}\t", "green")
        result_text.insert("end", f"FALSE: {counts['false']}\n", "red")

    result_text.insert("end", "\n")

    current_block_type = None
    for result in results:
        if result["result"] == "TRUE" and not show_true:
            continue

        if result["block_type"] != current_block_type:
            current_block_type = result["block_type"]
            result_text.insert(
                "end", f"\nブロックタイプ: {current_block_type}\n", "bold"
            )

        result_text.insert(
            "end", f"ID: {result['id']}, キーワード: {result['keyword']}\n"
        )
        result_text.insert(
            "end",
            f"ファイルA ({result['file_a_line']}行目): {result['file_a_content']}\n",
        )
        result_text.insert(
            "end",
            f"ファイルB ({result['file_b_line']}行目): {result['file_b_content']}\n",
        )
        if result["result"] == "TRUE":
            result_text.insert("end", f"結果: {result['result']}\n\n", "green")
        else:
            result_text.insert("end", f"結果: {result['result']}\n\n", "red")


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
