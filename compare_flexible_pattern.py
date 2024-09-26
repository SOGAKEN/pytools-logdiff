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
    use_regex = config.get("regex", True)
    escape_start_keyword = config.get("escape_start_keyword", False)
    include_end_keyword = config.get("include_end_keyword", True)

    def escape_regex(pattern):
        return re.escape(pattern) if escape_start_keyword else pattern

    def extract_content(lines):
        content = {}
        current_key = None
        current_content = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if use_regex:
                start_match = re.search(escape_regex(start_keyword), line)
            else:
                start_match = start_keyword in line

            if start_match:
                if current_key:
                    content[current_key] = (
                        "\n".join(current_content),
                        i - len(current_content),
                    )
                current_key = line
                current_content = [line]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if use_regex:
                        end_match = re.search(end_keyword, next_line)
                    else:
                        end_match = end_keyword in next_line

                    current_content.append(next_line)

                    if end_match:
                        if not include_end_keyword:
                            current_content.pop()
                        break
                    j += 1
                i = j
            i += 1

        if current_key:  # 最後のエントリを処理
            content[current_key] = (
                "\n".join(current_content),
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

        # 内容を正規化（余分な空白を削除）
        normalized_content_a = " ".join(full_content_a.split())
        normalized_content_b = " ".join(full_content_b.split())

        result = "TRUE" if normalized_content_a == normalized_content_b else "FALSE"

        results.append(
            {
                "id": id_counter,
                "block": block_number,
                "block_type": block_type,
                "keyword": f"{keyword} ({key.split()[0]})",
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
