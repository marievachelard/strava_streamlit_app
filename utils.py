from components.kpi_card import display_kpi_card

def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}min"

def format_duration_diff(seconds_diff):
    sign = "+" if seconds_diff >= 0 else "-"
    seconds_diff = abs(seconds_diff)
    hours = int(seconds_diff // 3600)
    minutes = int((seconds_diff % 3600) // 60)
    return f"{sign}{hours}h {minutes}min"

def display_kpi_with_comparison(col, icon, label, value, comparison, unit="", is_duration=False):
    if is_duration:
        formatted_value = format_duration(value)
        formatted_diff = format_duration_diff(comparison["diff"])
    else:
        formatted_value = f"{value:.2f} {unit}" if isinstance(value, float) else f"{value} {unit}".strip()
        formatted_diff = f"{comparison['diff']:+.1f} {unit}".strip()

    subtitle = f"{formatted_diff} ({comparison['percent_diff']:+.1f}%)"
    display_kpi_card(col, icon, label, formatted_value, subtitle=subtitle)
