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
    lines_a = block_a.split("\n")[1:]  # Skip the first line (block identifier)
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
                    "file_a_line": cumulative_lines_a
                    + i
                    + 2,  # +2 for block identifier and 0-based index
                    "file_b_line": cumulative_lines_b + i + 2,
                    "result": result,
                }
            )
            id_counter += 1

    for keyword, config in block_config.items():
        if isinstance(config, dict):
            if "multi_pattern" in config:
                multi_pattern_results = compare_multi_pattern(
                    lines_a,
                    lines_b,
                    keyword,
                    config["multi_pattern"],
                    id_counter,
                    block_number,
                    block_type,
                    cumulative_lines_a,
                    cumulative_lines_b,
                )
                results.extend(multi_pattern_results)
                id_counter += len(multi_pattern_results)
            elif "pattern" in config:
                pattern_results = compare_pattern(
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
                results.extend(pattern_results)
                id_counter += len(pattern_results)
            elif "continuous" in config:
                continuous_results = compare_continuous(
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
                results.extend(continuous_results)
                id_counter += len(continuous_results)
            elif "split" in config:
                split_results = compare_split(
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
                results.extend(split_results)
                id_counter += len(split_results)
            elif "multi_line" in config:
                multi_line_results = compare_multi_line(
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
                results.extend(multi_line_results)
                id_counter += len(multi_line_results)

    return results
