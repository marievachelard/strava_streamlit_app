from components.kpi_card import display_kpi_card
from utils.duration import format_duration, format_duration_diff

def display_kpi_with_comparison(col, icon, label, value, comparison, unit="", is_duration=False):
    if is_duration:
        formatted_value = format_duration(value)
        formatted_diff = format_duration_diff(comparison["diff"])
    else:
        formatted_value = f"{value:.2f} {unit}" if isinstance(value, float) else f"{value} {unit}".strip()
        formatted_diff = f"{comparison['diff']:+.1f} {unit}".strip()

    subtitle = f"{formatted_diff} ({comparison['percent_diff']:+.1f}%)"
    display_kpi_card(col, icon, label, formatted_value, subtitle=subtitle)
