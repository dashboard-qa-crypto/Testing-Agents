"""Test result analyzer with AI-powered suggestions."""

import re
from typing import Dict, Any, List

from src.agent import TestResult


class TestAnalyzer:
    """Analyzes test results and provides intelligent suggestions."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self.common_patterns = {
            "assertion": r"AssertionError|assert .+ ==",
            "import": r"ImportError|ModuleNotFoundError",
            "attribute": r"AttributeError",
            "type": r"TypeError",
            "value": r"ValueError",
            "key": r"KeyError",
            "index": r"IndexError",
            "timeout": r"TimeoutError|timeout",
            "connection": r"ConnectionError|Connection refused",
            "permission": r"PermissionError|Permission denied",
        }

    def analyze(self, result: TestResult) -> Dict[str, Any]:
        """Analyze test results and provide suggestions.

        Args:
            result: TestResult object to analyze

        Returns:
            Dictionary containing analysis and suggestions
        """
        analysis = {
            "summary": self._generate_summary(result),
            "error_types": self._categorize_errors(result),
            "suggestions": self._generate_suggestions(result),
            "coverage_analysis": self._analyze_coverage(result),
        }

        return analysis

    def _generate_summary(self, result: TestResult) -> str:
        """Generate a summary of the test results.

        Args:
            result: TestResult object

        Returns:
            Summary string
        """
        if result.total == 0:
            return "No tests were executed."

        summary_parts = [
            f"Total: {result.total} tests",
            f"Passed: {result.passed} ({result.success_rate():.1f}%)",
        ]

        if result.failed > 0:
            summary_parts.append(f"Failed: {result.failed}")
        if result.errors > 0:
            summary_parts.append(f"Errors: {result.errors}")
        if result.skipped > 0:
            summary_parts.append(f"Skipped: {result.skipped}")

        summary_parts.append(f"Duration: {result.duration:.2f}s")

        if result.coverage > 0:
            summary_parts.append(f"Coverage: {result.coverage:.1f}%")

        return " | ".join(summary_parts)

    def _categorize_errors(self, result: TestResult) -> Dict[str, int]:
        """Categorize errors by type.

        Args:
            result: TestResult object

        Returns:
            Dictionary mapping error types to counts
        """
        error_types: Dict[str, int] = {}
        output = result.stdout + result.stderr

        for error_type, pattern in self.common_patterns.items():
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                error_types[error_type] = len(matches)

        return error_types

    def _generate_suggestions(self, result: TestResult) -> List[str]:
        """Generate suggestions based on test results.

        Args:
            result: TestResult object

        Returns:
            List of suggestions
        """
        suggestions = []
        output = result.stdout + result.stderr

        # Check for common error patterns
        if re.search(self.common_patterns["import"], output):
            suggestions.append(
                "Import errors detected. Check that all dependencies are installed "
                "and PYTHONPATH is configured correctly."
            )

        if re.search(self.common_patterns["assertion"], output):
            suggestions.append(
                "Assertion failures detected. Review the test expectations and "
                "ensure the code behavior matches the test cases."
            )

        if re.search(self.common_patterns["attribute"], output):
            suggestions.append(
                "Attribute errors detected. Verify that objects have the expected "
                "attributes and methods."
            )

        if re.search(self.common_patterns["type"], output):
            suggestions.append(
                "Type errors detected. Check function arguments and return types "
                "match expectations."
            )

        if re.search(self.common_patterns["timeout"], output):
            suggestions.append(
                "Timeout errors detected. Consider increasing timeout values or "
                "optimizing slow operations."
            )

        if re.search(self.common_patterns["connection"], output):
            suggestions.append(
                "Connection errors detected. Ensure external services are running "
                "and network is accessible."
            )

        # Coverage suggestions
        if result.coverage > 0 and result.coverage < 70:
            suggestions.append(
                f"Code coverage is low ({result.coverage:.1f}%). Consider adding "
                "more tests to improve coverage."
            )

        # Performance suggestions
        if result.total > 0:
            avg_time = result.duration / result.total
            if avg_time > 1.0:
                suggestions.append(
                    f"Average test time is high ({avg_time:.2f}s per test). "
                    "Consider optimizing slow tests or using test fixtures."
                )

        # Success suggestions
        if result.has_failures():
            failure_rate = (result.failed + result.errors) / result.total * 100
            if failure_rate > 50:
                suggestions.append(
                    "More than 50% of tests are failing. Consider reviewing recent "
                    "changes or running tests in isolation to identify root causes."
                )
        else:
            suggestions.append("All tests passed! Great job!")

        return suggestions

    def _analyze_coverage(self, result: TestResult) -> Dict[str, Any]:
        """Analyze code coverage.

        Args:
            result: TestResult object

        Returns:
            Coverage analysis
        """
        analysis = {
            "percentage": result.coverage,
            "status": "unknown",
            "recommendation": "",
        }

        if result.coverage >= 90:
            analysis["status"] = "excellent"
            analysis["recommendation"] = "Coverage is excellent. Maintain this level."
        elif result.coverage >= 80:
            analysis["status"] = "good"
            analysis["recommendation"] = "Coverage is good. Consider targeting 90%+."
        elif result.coverage >= 70:
            analysis["status"] = "acceptable"
            analysis[
                "recommendation"
            ] = "Coverage is acceptable but could be improved."
        elif result.coverage > 0:
            analysis["status"] = "low"
            analysis["recommendation"] = "Coverage is low. Add more tests."
        else:
            analysis["status"] = "none"
            analysis["recommendation"] = "No coverage data available."

        return analysis
