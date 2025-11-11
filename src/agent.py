"""Main testing agent implementation."""

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.config import Config
from src.analyzer import TestAnalyzer
from src.utils.reporter import TestReporter


@dataclass
class TestResult:
    """Represents the result of a test run."""

    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    total: int = 0
    duration: float = 0.0
    coverage: float = 0.0
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    failures: List[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize failures list if not provided."""
        if self.failures is None:
            self.failures = []

    def has_failures(self) -> bool:
        """Check if there are any failures.

        Returns:
            True if there are failures, False otherwise
        """
        return self.failed > 0 or self.errors > 0

    def success_rate(self) -> float:
        """Calculate the success rate.

        Returns:
            Success rate as a percentage
        """
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100


class TestingAgent:
    """An intelligent testing agent that runs and analyzes tests."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the testing agent.

        Args:
            config: Configuration for the agent. If None, uses default config.
        """
        self.config = config or Config()
        self.analyzer = TestAnalyzer()
        self.reporter = TestReporter()

    def run_tests(
        self,
        path: Optional[str] = None,
        pattern: Optional[str] = None,
        markers: Optional[List[str]] = None,
        coverage: bool = True,
    ) -> TestResult:
        """Run tests and return results.

        Args:
            path: Specific path to test. If None, uses configured test directory.
            pattern: Pattern to match test files.
            markers: List of pytest markers to filter tests.
            coverage: Whether to collect coverage data.

        Returns:
            TestResult object containing test execution results
        """
        start_time = time.time()

        # Build the command
        cmd = self._build_command(path, pattern, markers, coverage)

        if self.config.verbose:
            print(f"Running command: {' '.join(cmd)}")

        # Run the tests
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                cwd=Path.cwd(),
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                exit_code=-1,
                stderr=f"Tests exceeded timeout of {self.config.timeout} seconds",
                duration=time.time() - start_time,
            )

        duration = time.time() - start_time

        # Parse the results
        test_result = self._parse_results(result, duration)

        return test_result

    def _build_command(
        self,
        path: Optional[str],
        pattern: Optional[str],
        markers: Optional[List[str]],
        coverage: bool,
    ) -> List[str]:
        """Build the test command based on configuration.

        Args:
            path: Path to test directory or file
            pattern: Pattern to match test files
            markers: Pytest markers to filter tests
            coverage: Whether to collect coverage

        Returns:
            Command as a list of strings
        """
        if self.config.test_framework == "pytest":
            cmd = [sys.executable, "-m", "pytest"]

            # Add path
            if path:
                cmd.append(path)
            elif self.config.test_directory:
                cmd.append(self.config.test_directory)

            # Add verbose flag
            if self.config.verbose:
                cmd.append("-v")

            # Add parallel execution
            if self.config.parallel:
                cmd.extend(["-n", str(self.config.max_workers)])

            # Add fail fast
            if self.config.fail_fast:
                cmd.append("-x")

            # Add coverage
            if coverage:
                cmd.extend(["--cov=src", "--cov-report=term", "--cov-report=json"])

            # Add pattern
            if pattern:
                cmd.extend(["-k", pattern])

            # Add markers
            if markers:
                for marker in markers:
                    cmd.extend(["-m", marker])

        elif self.config.test_framework == "unittest":
            cmd = [sys.executable, "-m", "unittest"]
            if path:
                cmd.append(path)
            if self.config.verbose:
                cmd.append("-v")
        else:
            raise ValueError(f"Unsupported test framework: {self.config.test_framework}")

        return cmd

    def _parse_results(self, result: subprocess.CompletedProcess, duration: float) -> TestResult:
        """Parse test results from command output.

        Args:
            result: Completed process result
            duration: Test execution duration

        Returns:
            Parsed TestResult object
        """
        output = result.stdout + result.stderr

        test_result = TestResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration=duration,
        )

        # Parse pytest output
        if self.config.test_framework == "pytest":
            # Look for the summary line (e.g., "5 passed, 2 failed in 1.23s")
            for line in output.split("\n"):
                if "passed" in line or "failed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            test_result.passed = int(parts[i - 1])
                        elif part == "failed":
                            test_result.failed = int(parts[i - 1])
                        elif part == "skipped":
                            test_result.skipped = int(parts[i - 1])
                        elif part == "error" or part == "errors":
                            test_result.errors = int(parts[i - 1])

            # Parse coverage from coverage.json if it exists
            coverage_file = Path.cwd() / "coverage.json"
            if coverage_file.exists():
                import json

                with open(coverage_file) as f:
                    cov_data = json.load(f)
                    test_result.coverage = cov_data.get("totals", {}).get(
                        "percent_covered", 0.0
                    )

        test_result.total = (
            test_result.passed + test_result.failed + test_result.skipped
        )

        return test_result

    def analyze_failures(self, result: TestResult) -> Dict[str, Any]:
        """Analyze test failures and provide suggestions.

        Args:
            result: TestResult object with failures

        Returns:
            Analysis results with suggestions
        """
        return self.analyzer.analyze(result)

    def generate_report(self, result: TestResult, format: str = "text") -> str:
        """Generate a test report.

        Args:
            result: TestResult object
            format: Report format ('text', 'html', 'json')

        Returns:
            Formatted report string
        """
        return self.reporter.generate(result, format)

    def run_and_report(
        self,
        path: Optional[str] = None,
        pattern: Optional[str] = None,
        markers: Optional[List[str]] = None,
        coverage: bool = True,
    ) -> TestResult:
        """Run tests and automatically generate a report.

        Args:
            path: Specific path to test
            pattern: Pattern to match test files
            markers: List of pytest markers
            coverage: Whether to collect coverage

        Returns:
            TestResult object
        """
        result = self.run_tests(path, pattern, markers, coverage)

        # Generate and print report
        report = self.generate_report(result)
        print(report)

        # If there are failures, provide analysis
        if result.has_failures():
            analysis = self.analyze_failures(result)
            print("\n" + "=" * 70)
            print("FAILURE ANALYSIS")
            print("=" * 70)
            for suggestion in analysis.get("suggestions", []):
                print(f"  • {suggestion}")

        return result


def main() -> int:
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Testing Agent - Intelligent test runner")
    parser.add_argument("--path", help="Path to test directory or file")
    parser.add_argument("--pattern", help="Pattern to match test files")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage collection")
    parser.add_argument("--config", help="Path to configuration file")

    args = parser.parse_args()

    # Load configuration
    if args.config:
        config = Config.from_file(args.config)
    else:
        config = Config()

    # Override with CLI arguments
    if args.verbose:
        config.verbose = True
    if args.parallel:
        config.parallel = True

    # Create agent and run tests
    agent = TestingAgent(config)
    result = agent.run_and_report(
        path=args.path,
        pattern=args.pattern,
        coverage=not args.no_coverage,
    )

    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
