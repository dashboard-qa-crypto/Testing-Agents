"""Tests for the test analyzer."""

import pytest
from src.analyzer import TestAnalyzer
from src.agent import TestResult


class TestTestAnalyzer:
    """Test cases for the TestAnalyzer class."""

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = TestAnalyzer()
        assert analyzer.common_patterns is not None
        assert "assertion" in analyzer.common_patterns

    def test_generate_summary_no_tests(self):
        """Test summary generation with no tests."""
        analyzer = TestAnalyzer()
        result = TestResult(total=0)

        summary = analyzer._generate_summary(result)
        assert "No tests were executed" in summary

    def test_generate_summary_all_passed(self):
        """Test summary generation with all tests passing."""
        analyzer = TestAnalyzer()
        result = TestResult(passed=10, total=10, duration=2.5)

        summary = analyzer._generate_summary(result)
        assert "Total: 10 tests" in summary
        assert "Passed: 10" in summary
        assert "Duration: 2.50s" in summary

    def test_generate_summary_with_failures(self):
        """Test summary generation with failures."""
        analyzer = TestAnalyzer()
        result = TestResult(passed=8, failed=2, total=10, duration=3.0)

        summary = analyzer._generate_summary(result)
        assert "Failed: 2" in summary

    def test_categorize_errors_import_error(self):
        """Test error categorization for import errors."""
        analyzer = TestAnalyzer()
        result = TestResult(
            stdout="ImportError: No module named 'foo'",
            stderr=""
        )

        errors = analyzer._categorize_errors(result)
        assert "import" in errors

    def test_categorize_errors_assertion_error(self):
        """Test error categorization for assertion errors."""
        analyzer = TestAnalyzer()
        result = TestResult(
            stdout="AssertionError: expected 5 but got 10",
            stderr=""
        )

        errors = analyzer._categorize_errors(result)
        assert "assertion" in errors

    def test_generate_suggestions_import_error(self):
        """Test suggestion generation for import errors."""
        analyzer = TestAnalyzer()
        result = TestResult(
            stdout="ImportError: No module named 'foo'",
            failed=1,
            total=1
        )

        suggestions = analyzer._generate_suggestions(result)
        assert any("Import errors" in s for s in suggestions)

    def test_generate_suggestions_all_passed(self):
        """Test suggestions when all tests pass."""
        analyzer = TestAnalyzer()
        result = TestResult(passed=10, total=10)

        suggestions = analyzer._generate_suggestions(result)
        assert any("All tests passed" in s for s in suggestions)

    def test_generate_suggestions_low_coverage(self):
        """Test suggestions for low coverage."""
        analyzer = TestAnalyzer()
        result = TestResult(passed=10, total=10, coverage=50.0)

        suggestions = analyzer._generate_suggestions(result)
        assert any("coverage is low" in s.lower() for s in suggestions)

    def test_analyze_coverage_excellent(self):
        """Test coverage analysis for excellent coverage."""
        analyzer = TestAnalyzer()
        result = TestResult(coverage=95.0)

        analysis = analyzer._analyze_coverage(result)
        assert analysis["status"] == "excellent"

    def test_analyze_coverage_good(self):
        """Test coverage analysis for good coverage."""
        analyzer = TestAnalyzer()
        result = TestResult(coverage=85.0)

        analysis = analyzer._analyze_coverage(result)
        assert analysis["status"] == "good"

    def test_analyze_coverage_low(self):
        """Test coverage analysis for low coverage."""
        analyzer = TestAnalyzer()
        result = TestResult(coverage=60.0)

        analysis = analyzer._analyze_coverage(result)
        assert analysis["status"] == "low"

    def test_full_analysis(self):
        """Test complete analysis."""
        analyzer = TestAnalyzer()
        result = TestResult(
            passed=8,
            failed=2,
            total=10,
            duration=5.0,
            coverage=75.0
        )

        analysis = analyzer.analyze(result)

        assert "summary" in analysis
        assert "error_types" in analysis
        assert "suggestions" in analysis
        assert "coverage_analysis" in analysis
