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
    use_regex = split_config.get("regex", True)  # デフォルトはTrue（後方互換性のため）

    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)

    if use_regex:
        match_a = re.search(pattern, content_a, re.MULTILINE)
        match_b = re.search(pattern, content_b, re.MULTILINE)
        if match_a and match_b:
            items_a = re.split(r"\s+", match_a.group(1).strip())
            items_b = re.split(r"\s+", match_b.group(1).strip())
            line_a = content_a[: match_a.start()].count("\n") + 2
            line_b = content_b[: match_b.start()].count("\n") + 2
        else:
            return []
    else:
        lines_with_pattern_a = [i for i, line in enumerate(lines_a) if pattern in line]
        lines_with_pattern_b = [i for i, line in enumerate(lines_b) if pattern in line]
        if lines_with_pattern_a and lines_with_pattern_b:
            line_a = lines_with_pattern_a[0] + 1
            line_b = lines_with_pattern_b[0] + 1
            items_a = lines_a[line_a - 1].split(pattern)[1].strip().split()
            items_b = lines_b[line_b - 1].split(pattern)[1].strip().split()
        else:
            return []

    results = []
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
                    "file_a_line": cumulative_lines_a + line_a,
                    "file_b_line": cumulative_lines_b + line_b,
                    "result": result,
                }
            )
    return results
