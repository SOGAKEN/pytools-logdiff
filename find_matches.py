def find_matches(lines, pattern, use_regex):
    matches = []
    for i, line in enumerate(lines):
        if use_regex:
            if re.search(pattern, line):
                matches.append((i, line))
        elif pattern in line:
            matches.append((i, line))
    return matches
