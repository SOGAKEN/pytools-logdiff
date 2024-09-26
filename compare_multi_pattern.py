def compare_multi_pattern(lines_a, lines_b, keyword, config):
    pattern = config["pattern"]
    use_regex = config.get("regex", False)

    results = []
    matches_a = find_matches(lines_a, pattern, use_regex)
    matches_b = find_matches(lines_b, pattern, use_regex)

    for (line_a, content_a), (line_b, content_b) in zip(matches_a, matches_b):
        # "Normal" までの部分のみを抽出
        content_a_trimmed = re.sub(r"(Temp:.+Normal).*", r"\1", content_a.strip())
        content_b_trimmed = re.sub(r"(Temp:.+Normal).*", r"\1", content_b.strip())

        result = "TRUE" if content_a_trimmed == content_b_trimmed else "FALSE"
        results.append(
            {
                "keyword": keyword,
                "file_a_content": content_a.strip(),  # 元の内容も保持
                "file_b_content": content_b.strip(),  # 元の内容も保持
                "file_a_line": line_a + 1,
                "file_b_line": line_b + 1,
                "result": result,
            }
        )

    return results
