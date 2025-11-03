def parse_time_str(t: str) -> float:
    """
    Parse time string in hh:mm:ss[.ms], mm:ss[.ms] or ss[.ms] to seconds (float).
    """
    parts = t.strip().split(":")
    try:
        parts = [float(p) for p in parts]
    except ValueError:
        raise ValueError(f"Invalid time component in '{t}'")
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return parts[0] * 60.0 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600.0 + parts[1] * 60.0 + parts[2]
    raise ValueError(f"Invalid time format: '{t}'")
