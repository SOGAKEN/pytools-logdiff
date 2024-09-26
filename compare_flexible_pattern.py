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
    ignore_time = config.get("ignore_time", True)

    def extract_content(lines):
        content = {}
        current_key = None
        for i, line in enumerate(lines):
            if start_keyword in line:
                if current_key:
                    content[current_key] = (current_content, start_line)
                current_key = line.strip()
                current_content = line.strip()
                start_line = i
            elif current_key and end_keyword in line:
                current_content += " " + line.strip()
                content[current_key] = (current_content, start_line)
                current_key = None
            elif current_key:
                current_content += " " + line.strip()
        if current_key:
            content[current_key] = (current_content, start_line)
        return content

    def normalize_content(content):
        if ignore_time:
            # Remove time information (e.g., 2w6d, 00:06:35)
            content = re.sub(r"\s+\d+:\d+:\d+|\s+\d+[wdhms]+", "", content)
        return " ".join(content.split())

    content_a = extract_content(lines_a)
    content_b = extract_content(lines_b)

    results = []
    all_keys = set(content_a.keys()) | set(content_b.keys())

    for key in all_keys:
        full_content_a, line_a = content_a.get(key, ("Not found", -1))
        full_content_b, line_b = content_b.get(key, ("Not found", -1))

        normalized_content_a = normalize_content(full_content_a)
        normalized_content_b = normalize_content(full_content_b)

        result = "TRUE" if normalized_content_a == normalized_content_b else "FALSE"

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

    return results
