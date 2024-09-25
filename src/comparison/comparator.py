import re


def compare_logs(file_a, file_b, config):
    with open(file_a, "r") as f_a, open(file_b, "r") as f_b:
        content_a = f_a.read()
        content_b = f_b.read()

    block_identifier = detect_block_identifier(content_a)
    if not block_identifier:
        raise ValueError("ブロック識別子を検出できませんでした。")

    blocks_a = re.split(rf"(?={re.escape(block_identifier)}\s*#)", content_a)
    blocks_b = re.split(rf"(?={re.escape(block_identifier)}\s*#)", content_b)

    results = []
    id_counter = 1

    if "global" in config:
        global_result = compare_global(
            content_a, content_b, config["global"], id_counter
        )
        results.extend(global_result)
        id_counter += len(global_result)

    cumulative_lines_a = 0
    cumulative_lines_b = 0

    for i, (block_a, block_b) in enumerate(zip(blocks_a, blocks_b), 1):
        block_type = get_block_type(block_a, block_identifier)
        if block_type in config:
            block_config = config[block_type]
            block_result = compare_block(
                block_a,
                block_b,
                block_config,
                id_counter,
                i,
                block_type,
                block_identifier,
                cumulative_lines_a,
                cumulative_lines_b,
            )
            results.extend(block_result)
            id_counter += len(block_result)

        cumulative_lines_a += len(block_a.split("\n"))
        cumulative_lines_b += len(block_b.split("\n"))

    return results


def detect_block_identifier(content):
    first_lines = content.split("\n")[:10]
    for line in first_lines:
        match = re.match(r"^(\S+)\s*#", line)
        if match:
            return match.group(1)
    return None


def get_block_type(block, block_identifier):
    first_line = block.split("\n")[0]
    match = re.search(rf"{re.escape(block_identifier)}\s*#\s*(.*)", first_line)
    return match.group(1).strip() if match else ""


def compare_global(content_a, content_b, global_config, id_counter):
    results = []
    lines_a = content_a.splitlines()
    lines_b = content_b.splitlines()

    skip_empty_lines = global_config.get("skip_empty_lines", False)
    if skip_empty_lines:
        lines_a = [line for line in lines_a if line.strip()]
        lines_b = [line for line in lines_b if line.strip()]

    for keyword_config in global_config.get("keywords", []):
        name = keyword_config["name"]
        pattern = keyword_config["pattern"]
        is_regex = keyword_config.get("regex", False)
        lines_after = keyword_config.get("lines_after", 0)

        for i in range(min(len(lines_a), len(lines_b))):
            line_a = lines_a[i]
            line_b = lines_b[i]

            match_a = re.search(pattern, line_a) if is_regex else pattern in line_a
            match_b = re.search(pattern, line_b) if is_regex else pattern in line_b

            if match_a or match_b:
                end_line = min(i + lines_after + 1, len(lines_a), len(lines_b))
                content_a = "\n".join(lines_a[i:end_line])
                content_b = "\n".join(lines_b[i:end_line])

                result = "TRUE" if content_a == content_b else "FALSE"
                results.append(
                    {
                        "id": id_counter,
                        "block": "global",
                        "block_type": "global",
                        "keyword": name,
                        "file_a_content": content_a,
                        "file_b_content": content_b,
                        "file_a_line": i + 1,
                        "file_b_line": i + 1,
                        "result": result,
                    }
                )
                id_counter += 1
                break

    return results


def compare_block(
    block_a,
    block_b,
    block_config,
    id_counter,
    block_number,
    block_type,
    block_identifier,
    cumulative_lines_a,
    cumulative_lines_b,
):
    results = []
    lines_a = block_a.split("\n")[1:]
    lines_b = block_b.split("\n")[1:]

    skip_patterns = block_config.get("skip_patterns", [])
    skip_sections = block_config.get("skip_sections", [])
    skip_empty_lines = block_config.get("skip_empty_lines", False)

    lines_a = skip_sections_in_lines(lines_a, skip_sections)
    lines_b = skip_sections_in_lines(lines_b, skip_sections)

    lines_a = [
        line
        for line in lines_a
        if not any(re.search(pattern, line) for pattern in skip_patterns)
    ]
    lines_b = [
        line
        for line in lines_b
        if not any(re.search(pattern, line) for pattern in skip_patterns)
    ]

    if skip_empty_lines:
        lines_a = [line for line in lines_a if line.strip()]
        lines_b = [line for line in lines_b if line.strip()]

    if "compare_all" in block_config and block_config["compare_all"]:
        for i, (line_a, line_b) in enumerate(zip(lines_a, lines_b)):
            result = "TRUE" if line_a.strip() == line_b.strip() else "FALSE"
            results.append(
                {
                    "id": id_counter,
                    "block": block_number,
                    "block_type": block_type,
                    "keyword": "All lines",
                    "file_a_content": line_a.strip(),
                    "file_b_content": line_b.strip(),
                    "file_a_line": cumulative_lines_a + i + 2,
                    "file_b_line": cumulative_lines_b + i + 2,
                    "result": result,
                }
            )
            id_counter += 1

    for keyword, config in block_config.items():
        if isinstance(config, dict):
            if "pattern" in config:
                results.extend(
                    compare_pattern(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)
            elif "continuous" in config:
                results.extend(
                    compare_continuous(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)
            elif "split" in config:
                results.extend(
                    compare_split(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)
            elif "multi_line" in config:
                results.extend(
                    compare_multi_line(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)
            elif "exact" in config:
                results.extend(
                    compare_exact(
                        lines_a,
                        lines_b,
                        keyword,
                        config,
                        id_counter,
                        block_number,
                        block_type,
                        cumulative_lines_a,
                        cumulative_lines_b,
                    )
                )
                id_counter += len(results)

    return results


def skip_sections_in_lines(lines, skip_sections):
    result = []
    skip = False
    for line in lines:
        for start, end in skip_sections:
            if re.search(start, line):
                skip = True
            elif re.search(end, line):
                skip = False
                break
        if not skip:
            result.append(line)
    return result


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
    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)
    matches_a = list(re.finditer(pattern, content_a, re.MULTILINE))
    matches_b = list(re.finditer(pattern, content_b, re.MULTILINE))

    results = []
    for i, (match_a, match_b) in enumerate(zip(matches_a, matches_b)):
        content_a = match_a.group(1) if match_a else "Not found"
        content_b = match_b.group(1) if match_b else "Not found"
        result = "TRUE" if content_a == content_b else "FALSE"
        results.append(
            {
                "id": id_counter + i,
                "block": block_number,
                "block_type": block_type,
                "keyword": f"{keyword} ({i+1})",
                "file_a_content": content_a,
                "file_b_content": content_b,
                "file_a_line": (
                    cumulative_lines_a + content_a[: match_a.start()].count("\n") + 2
                    if match_a
                    else "N/A"
                ),
                "file_b_line": (
                    cumulative_lines_b + content_b[: match_b.start()].count("\n") + 2
                    if match_b
                    else "N/A"
                ),
                "result": result,
            }
        )
    return results


def compare_continuous(
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
    pattern = config["continuous"]
    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)
    matches_a = list(re.finditer(pattern, content_a, re.MULTILINE))
    matches_b = list(re.finditer(pattern, content_b, re.MULTILINE))

    results = []
    for i, (match_a, match_b) in enumerate(zip(matches_a, matches_b)):
        result = "TRUE" if match_a.group(0) == match_b.group(0) else "FALSE"
        results.append(
            {
                "id": id_counter + i,
                "block": block_number,
                "block_type": block_type,
                "keyword": f"{keyword} ({i+1})",
                "file_a_content": match_a.group(0),
                "file_b_content": match_b.group(0),
                "file_a_line": cumulative_lines_a
                + content_a[: match_a.start()].count("\n")
                + 2,
                "file_b_line": cumulative_lines_b
                + content_b[: match_b.start()].count("\n")
                + 2,
                "result": result,
            }
        )
    return results


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

    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)
    match_a = re.search(pattern, content_a, re.MULTILINE)
    match_b = re.search(pattern, content_b, re.MULTILINE)

    results = []
    if match_a and match_b:
        items_a = re.split(r"[,\s]+", match_a.group(1))
        items_b = re.split(r"[,\s]+", match_b.group(1))
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
                        "file_a_line": cumulative_lines_a
                        + content_a[: match_a.start()].count("\n")
                        + 2,
                        "file_b_line": cumulative_lines_b
                        + content_b[: match_b.start()].count("\n")
                        + 2,
                        "result": result,
                    }
                )
    return results


def compare_multi_line(
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
    start_pattern = config["multi_line"]["start"]
    end_pattern = config["multi_line"]["end"]
    skip_lines = config["multi_line"].get("skip", 0)

    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)
    matches_a = list(
        re.finditer(
            f"{start_pattern}(.*?){end_pattern}", content_a, re.DOTALL | re.MULTILINE
        )
    )
    matches_b = list(
        re.finditer(
            f"{start_pattern}(.*?){end_pattern}", content_b, re.DOTALL | re.MULTILINE
        )
    )

    results = []
    for i, (match_a, match_b) in enumerate(zip(matches_a, matches_b)):
        lines_a = match_a.group(1).strip().split("\n")[skip_lines:]
        lines_b = match_b.group(1).strip().split("\n")[skip_lines:]

        for j, (line_a, line_b) in enumerate(zip(lines_a, lines_b)):
            result = "TRUE" if line_a.strip() == line_b.strip() else "FALSE"
            results.append(
                {
                    "id": id_counter + i * len(lines_a) + j,
                    "block": block_number,
                    "block_type": block_type,
                    "keyword": f"{keyword} ({i+1}, 行 {j+1})",
                    "file_a_content": line_a.strip(),
                    "file_b_content": line_b.strip(),
                    "file_a_line": cumulative_lines_a
                    + content_a[: match_a.start()].count("\n")
                    + skip_lines
                    + j
                    + 2,
                    "file_b_line": cumulative_lines_b
                    + content_b[: match_b.start()].count("\n")
                    + skip_lines
                    + j
                    + 2,
                    "result": result,
                }
            )
    return results


def compare_exact(
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
    exact_config = config["exact"]
    start_keyword = exact_config.get("start_keyword", "")
    end_keyword = exact_config.get("end_keyword", "")

    content_a = "\n".join(lines_a)
    content_b = "\n".join(lines_b)

    start_index_a = content_a.find(start_keyword) if start_keyword else 0
    start_index_b = content_b.find(start_keyword) if start_keyword else 0
    end_index_a = (
        content_a.find(end_keyword, start_index_a) if end_keyword else len(content_a)
    )
    end_index_b = (
        content_b.find(end_keyword, start_index_b) if end_keyword else len(content_b)
    )

    if start_index_a == -1 or start_index_b == -1:
        return []

    content_a = content_a[start_index_a:end_index_a]
    content_b = content_b[start_index_b:end_index_b]

    result = "TRUE" if content_a.strip() == content_b.strip() else "FALSE"
    return [
        {
            "id": id_counter,
            "block": block_number,
            "block_type": block_type,
            "keyword": keyword,
            "file_a_content": content_a.strip(),
            "file_b_content": content_b.strip(),
            "file_a_line": cumulative_lines_a
            + content_a[:start_index_a].count("\n")
            + 2,
            "file_b_line": cumulative_lines_b
            + content_b[:start_index_b].count("\n")
            + 2,
            "result": result,
        }
    ]
