def save_to_csv(all_results):
    if getattr(sys, "frozen", False):
        # 実行可能ファイルとして実行されている場合
        output_dir = os.path.dirname(sys.executable)
    else:
        # 通常のPythonスクリプトとして実行されている場合
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
                # 'block' キーを削除したディクショナリを作成
                row = {k: v for k, v in result.items() if k != "block"}
                writer.writerow(row)

    messagebox.showinfo(
        "成功", f"結果をCSVファイルに保存しました。\n保存先ディレクトリ: {output_dir}"
    )
