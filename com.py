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
    # ... (existing code)

    for keyword, config in block_config.items():
        if isinstance(config, dict):
            if "flexible_pattern" in config:
                flexible_results = compare_flexible_pattern(
                    lines_a,
                    lines_b,
                    keyword,
                    config["flexible_pattern"],
                    id_counter,
                    block_number,
                    block_type,
                    cumulative_lines_a,
                    cumulative_lines_b,
                )
                results.extend(flexible_results)
                id_counter += len(flexible_results)
            # ... (other comparison types)

    return results
