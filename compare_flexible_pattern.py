import re


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
    end_keyword = config.get("end_keyword", "")
    ignore_time = config.get("ignore_time", True)

    print(f"Debug: start_keyword = {start_keyword}")
    print(f"Debug: end_keyword = {end_keyword}")
    print(f"Debug: ignore_time = {ignore_time}")

    def extract_content(lines, file_label):
        content = {}
        current_key = None
        current_content = []
        for i, line in enumerate(lines):
            print(f"Debug {file_label}: Processing line {i}: {line}")
            if start_keyword in line:
                print(f"Debug {file_label}: start_keyword found in line {i}")
                if current_key:
                    content[current_key] = ("\n".join(current_content), start_line)
                current_key = line.strip()
                current_content = [line.strip()]
                start_line = i
                if end_keyword and end_keyword in line:
                    print(f"Debug {file_label}: end_keyword found in the same line")
                    content[current_key] = ("\n".join(current_content), start_line)
                    current_key = None
                    current_content = []
            elif current_key:
                current_content.append(line.strip())
                if end_keyword and end_keyword in line:
                    print(f"Debug {file_label}: end_keyword found in line {i}")
                    content[current_key] = ("\n".join(current_content), start_line)
                    current_key = None
                    current_content = []

        if current_key:
            content[current_key] = ("\n".join(current_content), start_line)

        print(f"Debug {file_label}: All extracted content: {content}")
        return content

    def normalize_content(content):
        if ignore_time:
            # Remove time information (e.g., 2w6d, 00:06:35)
            content = re.sub(r"\s+\d+:\d+:\d+|\s+\d+[wdhms]+", "", content)
        return " ".join(content.split())

    content_a = extract_content(lines_a, "File A")
    content_b = extract_content(lines_b, "File B")

    results = []
    all_keys = set(content_a.keys()) | set(content_b.keys())

    for key in all_keys:
        full_content_a, line_a = content_a.get(key, ("Not found", -1))
        full_content_b, line_b = content_b.get(key, ("Not found", -1))

        normalized_content_a = normalize_content(full_content_a)
        normalized_content_b = normalize_content(full_content_b)

        print(f"Debug: Comparing - Key: {key}")
        print(f"Debug: Normalized content A: {normalized_content_a}")
        print(f"Debug: Normalized content B: {normalized_content_b}")

        result = "TRUE" if normalized_content_a == normalized_content_b else "FALSE"

        ip_mask = re.search(r"(\d+\.\d+\.\d+\.\d+(/\d+)?)", key)
        keyword_text = (
            ip_mask.group(1) if ip_mask else key.split()[1]
        )  # start_keywordの次の要素を使用

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

    print(f"Debug: Final results: {results}")
    return results
