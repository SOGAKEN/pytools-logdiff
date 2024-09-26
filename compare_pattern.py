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
    use_regex = config.get("regex", True)  # デフォルトはTrue（後方互換性のため）
    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)

    if use_regex:
        match_a = re.search(pattern, content_a, re.MULTILINE)
        match_b = re.search(pattern, content_b, re.MULTILINE)
        if match_a or match_b:
            content_a = match_a.group(1) if match_a else "Not found"
            content_b = match_b.group(1) if match_b else "Not found"
            line_a = content_a[: match_a.start()].count("\n") + 1 if match_a else "N/A"
            line_b = content_b[: match_b.start()].count("\n") + 1 if match_b else "N/A"
    else:
        # 単純なキーワードマッチ
        match_a = next((i for i, line in enumerate(lines_a) if pattern in line), None)
        match_b = next((i for i, line in enumerate(lines_b) if pattern in line), None)
        if match_a is not None or match_b is not None:
            content_a = lines_a[match_a] if match_a is not None else "Not found"
            content_b = lines_b[match_b] if match_b is not None else "Not found"
            line_a = match_a + 1 if match_a is not None else "N/A"
            line_b = match_b + 1 if match_b is not None else "N/A"
        else:
            return []

    result = "TRUE" if content_a == content_b else "FALSE"
    return [
        {
            "id": id_counter,
            "block": block_number,
            "block_type": block_type,
            "keyword": keyword,
            "file_a_content": content_a,
            "file_b_content": content_b,
            "file_a_line": cumulative_lines_a + line_a if line_a != "N/A" else "N/A",
            "file_b_line": cumulative_lines_b + line_b if line_b != "N/A" else "N/A",
            "result": result,
        }
    ]
