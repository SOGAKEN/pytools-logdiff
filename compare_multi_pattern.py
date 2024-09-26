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
    use_regex = config.get("regex", True)
    compare_range = config.get("compare_range", None)

    results = []
    matches_a = find_matches(lines_a, pattern, use_regex)
    matches_b = find_matches(lines_b, pattern, use_regex)

    max_matches = max(len(matches_a), len(matches_b))
    matches_a += [("N/A", "Not found")] * (max_matches - len(matches_a))
    matches_b += [("N/A", "Not found")] * (max_matches - len(matches_b))

    for i, ((line_a, content_a), (line_b, content_b)) in enumerate(
        zip(matches_a, matches_b)
    ):
        try:
            if compare_range:
                content_a_trimmed = extract_compare_range(content_a, compare_range)
                content_b_trimmed = extract_compare_range(content_b, compare_range)
            else:
                content_a_trimmed = content_a.strip()
                content_b_trimmed = content_b.strip()

            result = "TRUE" if content_a_trimmed == content_b_trimmed else "FALSE"
        except Exception as e:
            print(f"Error processing line: {e}")
            content_a_trimmed = content_a.strip()
            content_b_trimmed = content_b.strip()
            result = "ERROR"

        results.append(
            {
                "id": id_counter + i,
                "block": block_number,
                "block_type": block_type,
                "keyword": keyword,
                "file_a_content": content_a.strip(),
                "file_b_content": content_b.strip(),
                "file_a_line": cumulative_lines_a
                + (line_a + 1 if line_a != "N/A" else 0),
                "file_b_line": cumulative_lines_b
                + (line_b + 1 if line_b != "N/A" else 0),
                "result": result,
            }
        )

    return results
