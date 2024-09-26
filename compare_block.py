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

    for keyword, config in block_config.items():
        if isinstance(config, dict):
            if "multi_pattern" in config:
                comparison_results = compare_multi_pattern(
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
            elif "pattern" in config:
                comparison_results = compare_pattern(
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
            # 他の比較タイプがあれば追加

            results.extend(comparison_results)
            id_counter += len(comparison_results)

    return results
