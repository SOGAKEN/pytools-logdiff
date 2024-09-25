import os
import sys
import toml
from tkinter import messagebox


def load_toml_config():
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            bundle_dir = sys._MEIPASS  # type: ignore
        else:
            bundle_dir = os.path.dirname(sys.executable)
    else:
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
