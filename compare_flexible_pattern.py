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
        content = None
        start_line = -1
        for i, line in enumerate(lines):
            print(f"Debug {file_label}: Processing line {i}: {line}")
            if start_keyword in line:
                print(f"Debug {file_label}: start_keyword found in line {i}")
                content = [line.strip()]
                start_line = i
                if end_keyword and end_keyword in line:
                    print(f"Debug {file_label}: end_keyword found in the same line")
                    break
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    content.append(next_line)
                    if end_keyword and end_keyword in next_line:
                        print(f"Debug {file_label}: end_keyword found in line {j}")
                        break
                break  # Stop after finding the first match

        if content:
            content = "\n".join(content)
            print(f"Debug {file_label}: Extracted content: {content}")
        else:
            print(f"Debug {file_label}: No content extracted")
        return content, start_line

    def normalize_content(content):
        if content is None:
            return None
        # Remove whitespace and newlines
        content = re.sub(r"\s+", " ", content)
        if ignore_time:
            # Remove time information (e.g., 2w6d, 00:06:35)
            content = re.sub(r"\s+\d+:\d+:\d+|\s+\d+[wdhms]+", "", content)
        return content.strip()

    content_a, line_a = extract_content(lines_a, "File A")
    content_b, line_b = extract_content(lines_b, "File B")

    normalized_content_a = normalize_content(content_a)
    normalized_content_b = normalize_content(content_b)

    print(f"Debug: Normalized content A: {normalized_content_a}")
    print(f"Debug: Normalized content B: {normalized_content_b}")

    if normalized_content_a is None and normalized_content_b is None:
        result = "TRUE"  # Both files don't have the content
    elif normalized_content_a is None or normalized_content_b is None:
        result = "FALSE"  # One file has the content, the other doesn't
    else:
        result = "TRUE" if normalized_content_a == normalized_content_b else "FALSE"

    ip_mask = re.search(r"(\d+\.\d+\.\d+\.\d+(/\d+)?)", start_keyword)
    keyword_text = ip_mask.group(1) if ip_mask else start_keyword.split()[1]

    results = [
        {
            "id": id_counter,
            "block": block_number,
            "block_type": block_type,
            "keyword": f"{keyword} ({keyword_text})",
            "file_a_content": content_a if content_a is not None else "Not found",
            "file_b_content": content_b if content_b is not None else "Not found",
            "file_a_line": cumulative_lines_a + line_a + 1 if line_a != -1 else "N/A",
            "file_b_line": cumulative_lines_b + line_b + 1 if line_b != -1 else "N/A",
            "result": result,
        }
    ]

    print(f"Debug: Final results: {results}")
    return results
