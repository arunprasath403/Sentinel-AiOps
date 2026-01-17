def analyze_logs(log_lines: list[str]) -> dict:
    error_count = 0
    warning_count = 0
    key_errors = []

    for line in log_lines:
        if "ERROR" in line:
            error_count += 1
            key_errors.append(line.split("ERROR")[1].strip())
        elif "WARN" in line:
            warning_count += 1

    return {
        "error_count": error_count,
        "warning_count": warning_count,
        "key_errors": key_errors,
        "summary": "Multiple errors detected in logs" if error_count > 0 else "No critical log errors"
    }
