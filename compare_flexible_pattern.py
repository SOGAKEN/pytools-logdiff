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
    start_keyword = config["start_keyword"]
    end_keyword = config["end_keyword"]
    compare_range = config.get("compare_range", [0, -1])
    use_regex = config.get("regex", True)

    def extract_content(lines):
        content = {}
        current_key = None
        current_content = []
        for i, line in enumerate(lines):
            if use_regex:
                start_match = re.search(start_keyword, line)
                end_match = re.search(end_keyword, line)
            else:
                start_match = start_keyword in line
                end_match = end_keyword in line

            if start_match:
                if current_key:
                    content[current_key] = (
                        " ".join(current_content),
                        i - len(current_content),
                    )
                current_key = line.strip()
                current_content = [line.strip()]
            elif current_key:
                current_content.append(line.strip())
                if end_match:
                    content[current_key] = (
                        " ".join(current_content),
                        i - len(current_content) + 1,
                    )
                    current_key = None
                    current_content = []

        if current_key:
            content[current_key] = (
                " ".join(current_content),
                len(lines) - len(current_content),
            )

        return content

    content_a = extract_content(lines_a)
    content_b = extract_content(lines_b)

    results = []
    all_keys = set(content_a.keys()) | set(content_b.keys())

    for key in all_keys:
        full_content_a, line_a = content_a.get(key, ("Not found", -1))
        full_content_b, line_b = content_b.get(key, ("Not found", -1))

        parts_a = full_content_a.split()
        parts_b = full_content_b.split()

        start = compare_range[0]
        end = compare_range[1] if compare_range[1] != -1 else None

        compared_content_a = " ".join(parts_a[start:end])
        compared_content_b = " ".join(parts_b[start:end])

        result = "TRUE" if compared_content_a == compared_content_b else "FALSE"

        results.append(
            {
                "id": id_counter,
                "block": block_number,
                "block_type": block_type,
                "keyword": f"{keyword} ({key.split()[0]})",  # キーの最初の部分（例：IPアドレス）を使用
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

    return results
