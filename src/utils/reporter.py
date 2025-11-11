"""Test report generation utilities."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from tabulate import tabulate

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False


class TestReporter:
    """Generates formatted test reports."""

    def __init__(self) -> None:
        """Initialize the reporter."""
        self.colors_enabled = COLORS_AVAILABLE

    def generate(self, result: Any, format: str = "text") -> str:
        """Generate a report in the specified format.

        Args:
            result: TestResult object
            format: Output format ('text', 'html', 'json')

        Returns:
            Formatted report string
        """
        if format == "text":
            return self._generate_text_report(result)
        elif format == "json":
            return self._generate_json_report(result)
        elif format == "html":
            return self._generate_html_report(result)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_text_report(self, result: Any) -> str:
        """Generate a text-based report.

        Args:
            result: TestResult object

        Returns:
            Text report
        """
        lines = []
        lines.append("=" * 70)
        lines.append("TEST EXECUTION REPORT")
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary table
        summary_data = [
            ["Total Tests", result.total],
            ["Passed", self._colorize(str(result.passed), "green")],
            ["Failed", self._colorize(str(result.failed), "red") if result.failed > 0 else "0"],
            ["Errors", self._colorize(str(result.errors), "red") if result.errors > 0 else "0"],
            ["Skipped", str(result.skipped)],
            ["Duration", f"{result.duration:.2f}s"],
        ]

        if result.coverage > 0:
            coverage_color = self._get_coverage_color(result.coverage)
            summary_data.append(
                ["Coverage", self._colorize(f"{result.coverage:.1f}%", coverage_color)]
            )

        if result.total > 0:
            success_rate = result.success_rate()
            rate_color = "green" if success_rate >= 90 else "yellow" if success_rate >= 70 else "red"
            summary_data.append(
                ["Success Rate", self._colorize(f"{success_rate:.1f}%", rate_color)]
            )

        lines.append(tabulate(summary_data, headers=["Metric", "Value"], tablefmt="grid"))
        lines.append("")

        # Status
        if result.has_failures():
            lines.append(self._colorize("STATUS: FAILED", "red"))
        else:
            lines.append(self._colorize("STATUS: PASSED", "green"))

        lines.append("=" * 70)

        return "\n".join(lines)

    def _generate_json_report(self, result: Any) -> str:
        """Generate a JSON report.

        Args:
            result: TestResult object

        Returns:
            JSON report string
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": result.total,
                "passed": result.passed,
                "failed": result.failed,
                "errors": result.errors,
                "skipped": result.skipped,
                "duration": result.duration,
                "coverage": result.coverage,
                "success_rate": result.success_rate(),
            },
            "status": "passed" if not result.has_failures() else "failed",
            "exit_code": result.exit_code,
        }

        return json.dumps(report, indent=2)

    def _generate_html_report(self, result: Any) -> str:
        """Generate an HTML report.

        Args:
            result: TestResult object

        Returns:
            HTML report string
        """
        status_class = "passed" if not result.has_failures() else "failed"
        status_text = "PASSED" if not result.has_failures() else "FAILED"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #ddd;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin: 20px 0;
        }}
        .metric {{
            padding: 15px;
            background-color: #f9f9f9;
            border-left: 4px solid #007bff;
            border-radius: 3px;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
        }}
        .status {{
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }}
        .status.passed {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status.failed {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            text-align: right;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Test Execution Report</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

        <div class="summary">
            <div class="metric">
                <div class="metric-label">Total Tests</div>
                <div class="metric-value">{result.total}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Passed</div>
                <div class="metric-value" style="color: #28a745;">{result.passed}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Failed</div>
                <div class="metric-value" style="color: #dc3545;">{result.failed}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Duration</div>
                <div class="metric-value">{result.duration:.2f}s</div>
            </div>
            <div class="metric">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">{result.success_rate():.1f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Coverage</div>
                <div class="metric-value">{result.coverage:.1f}%</div>
            </div>
        </div>

        <div class="status {status_class}">
            {status_text}
        </div>
    </div>
</body>
</html>
"""
        return html

    def _colorize(self, text: str, color: str) -> str:
        """Colorize text if colors are available.

        Args:
            text: Text to colorize
            color: Color name

        Returns:
            Colorized text or plain text if colors unavailable
        """
        if not self.colors_enabled:
            return text

        color_map = {
            "red": Fore.RED,
            "green": Fore.GREEN,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "cyan": Fore.CYAN,
        }

        color_code = color_map.get(color, "")
        return f"{color_code}{text}{Style.RESET_ALL}"

    def _get_coverage_color(self, coverage: float) -> str:
        """Get color for coverage percentage.

        Args:
            coverage: Coverage percentage

        Returns:
            Color name
        """
        if coverage >= 90:
            return "green"
        elif coverage >= 70:
            return "yellow"
        else:
            return "red"

    def save_report(self, result: Any, output_path: str, format: str = "html") -> None:
        """Save a report to a file.

        Args:
            result: TestResult object
            output_path: Path to save the report
            format: Report format
        """
        report = self.generate(result, format)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            f.write(report)
