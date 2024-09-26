def compare_multi_pattern(
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
    use_regex = config.get("regex", False)

    results = []
    matches_a = []
    matches_b = []

    for i, line in enumerate(lines_a):
        if use_regex:
            if re.search(pattern, line):
                matches_a.append((i, line))
        elif pattern in line:
            matches_a.append((i, line))

    for i, line in enumerate(lines_b):
        if use_regex:
            if re.search(pattern, line):
                matches_b.append((i, line))
        elif pattern in line:
            matches_b.append((i, line))

    for (i_a, line_a), (i_b, line_b) in zip(matches_a, matches_b):
        result = "TRUE" if line_a.strip() == line_b.strip() else "FALSE"
        results.append(
            {
                "id": id_counter,
                "block": block_number,
                "block_type": block_type,
                "keyword": keyword,
                "file_a_content": line_a.strip(),
                "file_b_content": line_b.strip(),
                "file_a_line": cumulative_lines_a + i_a + 1,
                "file_b_line": cumulative_lines_b + i_b + 1,
                "result": result,
            }
        )
        id_counter += 1

    return results
