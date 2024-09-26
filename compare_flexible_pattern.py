def compare_flexible_pattern(
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
    ip_addresses = config.get("ip_addresses", [])
    start_keyword = config["start_keyword"]
    end_keyword = config["end_keyword"]
    use_regex = config.get("regex", True)
    escape_start_keyword = config.get("escape_start_keyword", False)
    include_end_keyword = config.get("include_end_keyword", True)
    ignore_time = config.get("ignore_time", True)

    print(f"Debug: Config - {config}")  # デバッグ出力

    def escape_regex(pattern):
        return re.escape(pattern) if escape_start_keyword else pattern

    def extract_content(lines, file_label):
        content = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            print(f"Debug: Checking line in {file_label} - {line}")  # デバッグ出力
            for ip in ip_addresses:
                if use_regex:
                    full_pattern = f"{escape_regex(start_keyword)}{re.escape(ip)}"
                    start_match = re.search(full_pattern, line)
                    print(
                        f"Debug: Regex pattern for {ip} - {full_pattern}"
                    )  # デバッグ出力
                else:
                    full_pattern = f"{start_keyword}{ip}"
                    start_match = full_pattern in line
                    print(
                        f"Debug: String pattern for {ip} - {full_pattern}"
                    )  # デバッグ出力

                if start_match:
                    print(
                        f"Debug: Match found for {ip} in {file_label}"
                    )  # デバッグ出力
                    current_key = line
                    current_content = [line]
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if use_regex:
                            end_match = re.search(escape_regex(end_keyword), next_line)
                        else:
                            end_match = end_keyword in next_line

                        current_content.append(next_line)

                        if end_match:
                            if not include_end_keyword:
                                current_content.pop()
                            print(
                                f"Debug: End pattern found for {ip} in {file_label}"
                            )  # デバッグ出力
                            break
                        j += 1
                    content[current_key] = ("\n".join(current_content), i)
                    i = j
                    break
            i += 1
        print(f"Debug: Extracted content from {file_label} - {content}")  # デバッグ出力
        return content

    def normalize_content(content):
        if ignore_time:
            # 経過時間を示す部分を削除
            content = re.sub(r",\s*\d+[wdhms:]+,", ",", content)
        # 空白と改行を取り除く
        return re.sub(r"\s+", "", content)

    content_a = extract_content(lines_a, "File A")
    content_b = extract_content(lines_b, "File B")

    results = []
    all_keys = set(content_a.keys()) | set(content_b.keys())

    for key in all_keys:
        full_content_a, line_a = content_a.get(key, ("Not found", -1))
        full_content_b, line_b = content_b.get(key, ("Not found", -1))

        # 内容を正規化
        normalized_content_a = normalize_content(full_content_a)
        normalized_content_b = normalize_content(full_content_b)

        result = "TRUE" if normalized_content_a == normalized_content_b else "FALSE"

        # キーワードを抽出（IPアドレスとサブネットマスク）
        ip_mask = re.search(r"(\d+\.\d+\.\d+\.\d+/\d+)", key)
        keyword_text = ip_mask.group(1) if ip_mask else key.split()[0]

        results.append(
            {
                "id": id_counter,
                "block": block_number,
                "block_type": block_type,
                "keyword": f"{keyword} ({keyword_text})",
                "file_a_content": full_content_a,
                "file_b_content": full_content_b,
                "file_a_line": (
                    cumulative_lines_a + line_a + 1 if line_a != -1 else "N/A"
                ),
                "file_b_line": (
                    cumulative_lines_b + line_b + 1 if line_b != -1 else "N/A"
                ),
                "result": result,
            }
        )
        id_counter += 1

    print(f"Debug: Final results - {results}")  # デバッグ出力
    return results
