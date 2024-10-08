def display_results(result_text, results):
    summary = create_summary(results)

    result_text.insert(tk.END, "サマリー:\n", "bold")
    for i, (block_type, counts) in enumerate(summary.items(), 1):
        result_text.insert(tk.END, f"{i}.{block_type}\t", "bold")
        result_text.insert(tk.END, f"TRUE: {counts['true']}\t", "green")
        result_text.insert(tk.END, f"FALSE: {counts['false']}\n", "red")

    result_text.insert(tk.END, "\n")

    current_block_type = None
    for result in results:
        if result["result"] == "TRUE" and not show_true_var.get():
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
