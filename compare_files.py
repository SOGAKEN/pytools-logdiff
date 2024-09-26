def compare_files():
    config = load_toml_config()
    if not config:
        messagebox.showerror("エラー", "設定ファイルを読み込めませんでした。")
        return

    global all_results
    all_results = []
    for i in range(5):
        file_a = file_entries_a[i].get()
        file_b = file_entries_b[i].get()
        if file_a and file_b:
            try:
                results = compare_logs(file_a, file_b, config)
                all_results.extend(results)
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
