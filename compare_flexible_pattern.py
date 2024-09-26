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

    print(f"Debug: start_keyword = {start_keyword}")
    print(f"Debug: end_keyword = {end_keyword}")

    def extract_content(lines, file_label):
        content = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            print(f"Debug {file_label}: Processing line {i}: {line}")
            if start_keyword in line:
                print(f"Debug {file_label}: Start keyword found in line {i}")
                current_content = [line]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    current_content.append(next_line)
                    print(f"Debug {file_label}: Adding line {j}: {next_line}")
                    if end_keyword in next_line:
                        print(f"Debug {file_label}: End keyword found in line {j}")
                        break
                    j += 1

                # 抽出した内容を1行または2行に整形
                if len(current_content) > 2:
                    formatted_content = (
                        current_content[0] + " " + " ".join(current_content[1:])
                    )
                else:
                    formatted_content = " ".join(current_content)

                print(f"Debug {file_label}: Formatted content: {formatted_content}")
                content[line] = (formatted_content, i)
                i = j
            i += 1
        print(f"Debug {file_label}: Extracted content: {content}")
        return content

    content_a = extract_content(lines_a, "File A")
    content_b = extract_content(lines_b, "File B")

    print(f"Debug: content_a = {content_a}")
    print(f"Debug: content_b = {content_b}")

    results = []
    all_keys = set(content_a.keys()) | set(content_b.keys())

    for key in all_keys:
        full_content_a, line_a = content_a.get(key, ("Not found", -1))
        full_content_b, line_b = content_b.get(key, ("Not found", -1))

        result = "TRUE" if full_content_a == full_content_b else "FALSE"

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

    print(f"Debug: results = {results}")
    return results
