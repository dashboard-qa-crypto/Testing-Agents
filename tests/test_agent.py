"""Tests for the main testing agent."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agent import TestingAgent, TestResult
from src.config import Config


class TestTestingAgent:
    """Test cases for the TestingAgent class."""

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = TestingAgent()
        assert agent.config is not None
        assert agent.analyzer is not None
        assert agent.reporter is not None

    def test_agent_with_custom_config(self):
        """Test agent initialization with custom config."""
        config = Config(verbose=True, parallel=True)
        agent = TestingAgent(config)
        assert agent.config.verbose is True
        assert agent.config.parallel is True

    def test_build_command_pytest(self):
        """Test command building for pytest."""
        config = Config(test_framework="pytest", verbose=True)
        agent = TestingAgent(config)

        cmd = agent._build_command(
            path="tests",
            pattern="test_*",
            markers=None,
            coverage=True
        )

        assert "pytest" in " ".join(cmd)
        assert "-v" in cmd
        assert "tests" in cmd

    def test_build_command_with_parallel(self):
        """Test command building with parallel execution."""
        config = Config(parallel=True, max_workers=4)
        agent = TestingAgent(config)

        cmd = agent._build_command(
            path=None,
            pattern=None,
            markers=None,
            coverage=False
        )

        assert "-n" in cmd
        assert "4" in cmd

    def test_build_command_with_markers(self):
        """Test command building with markers."""
        agent = TestingAgent()

        cmd = agent._build_command(
            path=None,
            pattern=None,
            markers=["slow", "integration"],
            coverage=False
        )

        assert "-m" in cmd

    @patch("subprocess.run")
    def test_run_tests_success(self, mock_run):
        """Test successful test execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "5 passed in 1.23s"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        agent = TestingAgent()
        result = agent.run_tests(coverage=False)

        assert result.exit_code == 0
        assert mock_run.called

    @patch("subprocess.run")
    def test_run_tests_with_failures(self, mock_run):
        """Test execution with failures."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "3 passed, 2 failed in 1.23s"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        agent = TestingAgent()
        result = agent.run_tests(coverage=False)

        assert result.exit_code == 1

    def test_parse_results_with_passed_tests(self):
        """Test parsing results with passed tests."""
        agent = TestingAgent()
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "10 passed in 2.5s"
        mock_result.stderr = ""

        result = agent._parse_results(mock_result, 2.5)

        assert result.passed == 10
        assert result.duration == 2.5

    def test_parse_results_with_mixed_outcomes(self):
        """Test parsing results with mixed outcomes."""
        agent = TestingAgent()
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "5 passed, 2 failed, 1 skipped in 3.0s"
        mock_result.stderr = ""

        result = agent._parse_results(mock_result, 3.0)

        assert result.passed == 5
        assert result.failed == 2
        assert result.skipped == 1


class TestTestResult:
    """Test cases for the TestResult class."""

    def test_result_initialization(self):
        """Test TestResult initialization."""
        result = TestResult(passed=10, failed=0, total=10)
        assert result.passed == 10
        assert result.failed == 0
        assert result.total == 10

    def test_has_failures_true(self):
        """Test has_failures with failures."""
        result = TestResult(failed=1)
        assert result.has_failures() is True

    def test_has_failures_false(self):
        """Test has_failures without failures."""
        result = TestResult(passed=10)
        assert result.has_failures() is False

    def test_success_rate_100_percent(self):
        """Test success rate calculation at 100%."""
        result = TestResult(passed=10, failed=0, total=10)
        assert result.success_rate() == 100.0

    def test_success_rate_50_percent(self):
        """Test success rate calculation at 50%."""
        result = TestResult(passed=5, failed=5, total=10)
        assert result.success_rate() == 50.0

    def test_success_rate_zero_tests(self):
        """Test success rate with zero tests."""
        result = TestResult(total=0)
        assert result.success_rate() == 0.0

    def test_failures_list_initialized(self):
        """Test that failures list is initialized."""
        result = TestResult()
        assert result.failures == []
        assert isinstance(result.failures, list)
