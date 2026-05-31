"""
Helper utilities
"""
import re
import sys


def format_duration(milliseconds: int) -> str:
    """
    Format duration in milliseconds to human readable string

    Args:
        milliseconds: Duration in milliseconds

    Returns:
        Formatted duration string
    """
    if milliseconds < 1000:
        return f"{milliseconds}ms"

    seconds = milliseconds / 1000
    if seconds < 60:
        return f"{seconds:.2f}s"

    minutes = seconds / 60
    return f"{minutes:.2f}m"


def sanitize_filename(name: str) -> str:
    """
    Sanitize string for use as filename

    Args:
        name: Input string

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[^\w\s-]', '', name).strip()
    # Replace spaces and hyphens with underscore
    sanitized = re.sub(r'[-\s]+', '_', sanitized).lower()
    return sanitized


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Prompt user for confirmation

    Args:
        message: Confirmation message
        default: Default value if user just presses enter

    Returns:
        True if confirmed, False otherwise
    """
    default_str = "Y/n" if default else "y/N"
    prompt = f"{message} [{default_str}]: "

    try:
        response = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False

    if not response:
        return default

    return response in ('y', 'yes')


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length

    Args:
        s: Input string
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def print_table(headers: list, rows: list, max_col_width: int = 30) -> None:
    """
    Print data as formatted table

    Args:
        headers: Column headers
        rows: Data rows
        max_col_width: Maximum column width
    """
    if not rows:
        print("No data to display")
        return

    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(header)
        for row in rows:
            if i < len(row):
                cell_str = str(row[i])
                max_width = max(max_width, min(len(cell_str), max_col_width))
        col_widths.append(max_width)

    # Print header
    header_line = " | ".join(
        h.ljust(w) for h, w in zip(headers, col_widths)
    )
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in rows:
        formatted_row = []
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cell_str = str(cell)
                if len(cell_str) > max_col_width:
                    cell_str = cell_str[:max_col_width - 3] + "..."
                formatted_row.append(cell_str.ljust(col_widths[i]))
        print(" | ".join(formatted_row))
