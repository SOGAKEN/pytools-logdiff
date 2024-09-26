def extract_compare_range(content, compare_range):
    parts = content.split()
    result = []
    for i in compare_range:
        if i < len(parts):
            result.append(parts[i])
    return " ".join(result)
