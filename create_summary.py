def create_summary(results):
    summary = {}
    for result in results:
        block_type = result["block_type"]
        if block_type not in summary:
            summary[block_type] = {"true": 0, "false": 0}

        if result["result"] == "TRUE":
            summary[block_type]["true"] += 1
        else:
            summary[block_type]["false"] += 1

    return summary
