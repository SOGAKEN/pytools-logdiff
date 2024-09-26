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
    indices = split_config.get("indices", [])
    use_regex = split_config.get("regex", True)
    limit_keyword = split_config.get("limit_keyword", None)

    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)

    def process_line(line, pattern, limit_keyword):
        if limit_keyword:
            parts = line.split(limit_keyword, 1)
            if len(parts) > 1:
                line = parts[0] + limit_keyword
        if use_regex:
            match = re.search(pattern, line)
            if match:
                return re.split(r"\s+", match.group(1).strip())
        else:
            if pattern in line:
                return line.split(pattern)[1].strip().split()
        return None

    def find_matching_line(lines, pattern):
        for i, line in enumerate(lines):
            if use_regex:
                if re.search(pattern, line):
                    return i, line
            else:
                if pattern in line:
                    return i, line
        return None, None

    line_num_a, matching_line_a = find_matching_line(lines_a, pattern)
    line_num_b, matching_line_b = find_matching_line(lines_b, pattern)

    if matching_line_a is None or matching_line_b is None:
        return []

    items_a = process_line(matching_line_a, pattern, limit_keyword)
    items_b = process_line(matching_line_b, pattern, limit_keyword)

    if items_a is None or items_b is None:
        return []

    results = []
    if indices:
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
                        "file_a_line": cumulative_lines_a + line_num_a + 1,
                        "file_b_line": cumulative_lines_b + line_num_b + 1,
                        "result": result,
                    }
                )
    else:
        # インデックスが指定されていない場合、全項目を比較
        for i, (item_a, item_b) in enumerate(zip(items_a, items_b)):
            result = "TRUE" if item_a == item_b else "FALSE"
            results.append(
                {
                    "id": id_counter + i,
                    "block": block_number,
                    "block_type": block_type,
                    "keyword": f"{keyword} (項目 {i+1})",
                    "file_a_content": item_a,
                    "file_b_content": item_b,
                    "file_a_line": cumulative_lines_a + line_num_a + 1,
                    "file_b_line": cumulative_lines_b + line_num_b + 1,
                    "result": result,
                }
            )

    return results
