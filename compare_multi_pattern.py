import re


def compare_multi_pattern(lines_a, lines_b, keyword, config):
    pattern = config["pattern"]
    use_regex = config.get("regex", True)  # デフォルトをTrueに変更
    compare_range = config.get("compare_range", None)

    results = []
    matches_a = find_matches(lines_a, pattern, use_regex)
    matches_b = find_matches(lines_b, pattern, use_regex)

    # マッチした行数が異なる場合のハンドリング
    max_matches = max(len(matches_a), len(matches_b))
    matches_a += [("N/A", "Not found")] * (max_matches - len(matches_a))
    matches_b += [("N/A", "Not found")] * (max_matches - len(matches_b))

    for (line_a, content_a), (line_b, content_b) in zip(matches_a, matches_b):
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
                "keyword": keyword,
                "file_a_content": content_a.strip(),
                "file_b_content": content_b.strip(),
                "file_a_line": line_a + 1 if line_a != "N/A" else "N/A",
                "file_b_line": line_b + 1 if line_b != "N/A" else "N/A",
                "result": result,
            }
        )

    return results


def find_matches(lines, pattern, use_regex):
    matches = []
    for i, line in enumerate(lines):
        if use_regex:
            if re.search(pattern, line):
                matches.append((i, line))
        elif pattern in line:
            matches.append((i, line))
    return matches


def extract_compare_range(content, compare_range):
    start, end = compare_range
    parts = content.split()
    if start == 0 and end == -1:
        return " ".join(parts)
    elif end == -1:
        return " ".join(parts[start:])
    else:
        return " ".join(parts[start : end + 1])
