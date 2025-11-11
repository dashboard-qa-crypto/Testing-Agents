"""Helper utility functions."""

import re
from typing import Dict, List, Tuple


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def colorize(text: str, color: str) -> str:
    """Colorize text for terminal output.

    Args:
        text: Text to colorize
        color: Color name (red, green, yellow, blue, cyan)

    Returns:
        Colorized text with ANSI codes
    """
    try:
        from colorama import Fore, Style

        color_map = {
            "red": Fore.RED,
            "green": Fore.GREEN,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "cyan": Fore.CYAN,
            "magenta": Fore.MAGENTA,
            "white": Fore.WHITE,
        }

        color_code = color_map.get(color.lower(), "")
        return f"{color_code}{text}{Style.RESET_ALL}"
    except ImportError:
        return text


def parse_test_output(output: str) -> Dict[str, any]:
    """Parse test output to extract useful information.

    Args:
        output: Raw test output string

    Returns:
        Dictionary containing parsed information
    """
    info = {
        "test_files": [],
        "test_functions": [],
        "errors": [],
        "warnings": [],
    }

    # Extract test files
    file_pattern = r"test_\w+\.py"
    info["test_files"] = list(set(re.findall(file_pattern, output)))

    # Extract test functions
    func_pattern = r"test_\w+"
    info["test_functions"] = list(set(re.findall(func_pattern, output)))

    # Extract error messages
    error_lines = [line for line in output.split("\n") if "ERROR" in line or "Error:" in line]
    info["errors"] = error_lines

    # Extract warnings
    warning_lines = [line for line in output.split("\n") if "WARNING" in line or "Warning:" in line]
    info["warnings"] = warning_lines

    return info


def extract_failure_info(output: str) -> List[Dict[str, str]]:
    """Extract detailed information about test failures.

    Args:
        output: Test output string

    Returns:
        List of dictionaries containing failure information
    """
    failures = []

    # Pattern to match pytest failure sections
    failure_pattern = r"FAILED (.+?) - (.+?)(?=\n(?:FAILED|={3,}|$))"

    matches = re.finditer(failure_pattern, output, re.DOTALL)

    for match in matches:
        test_name = match.group(1).strip()
        error_msg = match.group(2).strip()

        failures.append({"test": test_name, "error": error_msg})

    return failures


def calculate_test_metrics(passed: int, failed: int, skipped: int) -> Dict[str, float]:
    """Calculate test metrics.

    Args:
        passed: Number of passed tests
        failed: Number of failed tests
        skipped: Number of skipped tests

    Returns:
        Dictionary containing calculated metrics
    """
    total = passed + failed + skipped

    metrics = {
        "total": total,
        "pass_rate": (passed / total * 100) if total > 0 else 0.0,
        "fail_rate": (failed / total * 100) if total > 0 else 0.0,
        "skip_rate": (skipped / total * 100) if total > 0 else 0.0,
    }

    return metrics


def truncate_output(output: str, max_lines: int = 100) -> str:
    """Truncate output to a maximum number of lines.

    Args:
        output: Output string to truncate
        max_lines: Maximum number of lines to keep

    Returns:
        Truncated output
    """
    lines = output.split("\n")

    if len(lines) <= max_lines:
        return output

    # Keep first half and last half
    half = max_lines // 2
    truncated_lines = lines[:half] + [f"\n... ({len(lines) - max_lines} lines omitted) ...\n"] + lines[-half:]

    return "\n".join(truncated_lines)


def find_test_files(directory: str, pattern: str = "test_*.py") -> List[str]:
    """Find test files in a directory.

    Args:
        directory: Directory to search
        pattern: File pattern to match

    Returns:
        List of test file paths
    """
    from pathlib import Path
    import fnmatch

    test_files = []
    path = Path(directory)

    if not path.exists():
        return test_files

    for file_path in path.rglob("*.py"):
        if fnmatch.fnmatch(file_path.name, pattern):
            test_files.append(str(file_path))

    return sorted(test_files)
