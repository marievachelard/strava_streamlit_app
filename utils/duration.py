def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def format_duration_diff(seconds_diff):
    sign = "+" if seconds_diff >= 0 else "-"
    seconds_diff = abs(seconds_diff)
    hours = int(seconds_diff // 3600)
    minutes = int((seconds_diff % 3600) // 60)
    return f"{sign}{hours}h {minutes}min"
